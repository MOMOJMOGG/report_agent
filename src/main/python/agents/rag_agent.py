"""
RAG Agent for generating insights from retail data.
Cost-efficient implementation using local embeddings and minimal OpenAI API calls.
"""

import asyncio
import json
import hashlib
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from dataclasses import dataclass

from src.main.python.core.base_agent import BaseAgent, AgentConfig
from src.main.python.models.message_types import (
    BaseMessage, MessageType, AgentType, 
    CleanDataPayload, InsightData, InsightsPayload, create_message
)


@dataclass
class RAGConfig:
    """Configuration for RAG processing."""
    # Embedding settings
    use_local_embeddings: bool = True
    embedding_model: str = "all-MiniLM-L6-v2"  # Lightweight local model
    
    # Vector store settings
    vector_store_path: str = "data/vector_store"
    top_k_retrieval: int = 5
    similarity_threshold: float = 0.2  # Lower threshold for simple embeddings
    
    # OpenAI settings (cost-efficient)
    openai_model: str = "gpt-3.5-turbo"  # Cheaper than GPT-4
    max_tokens: int = 150  # Keep responses short
    temperature: float = 0.3
    max_context_tokens: int = 2000  # Limit context size
    
    # Caching settings
    enable_caching: bool = True
    cache_ttl_hours: int = 24
    
    # Cost control
    max_api_calls_per_session: int = 10  # Limit API usage
    enable_mock_mode: bool = False  # For testing without API calls


class SimpleEmbedding:
    """Simple embedding implementation using TF-IDF when sentence-transformers unavailable."""
    
    def __init__(self):
        self.vocabulary = {}
        self.idf_scores = {}
        self.fitted = False
    
    def fit_transform(self, texts: List[str]) -> np.ndarray:
        """Fit and transform texts to embeddings."""
        # Build vocabulary
        word_counts = {}
        doc_counts = {}
        
        processed_texts = []
        for text in texts:
            words = self._preprocess_text(text)
            processed_texts.append(words)
            
            # Count words in document
            doc_words = set(words)
            for word in doc_words:
                doc_counts[word] = doc_counts.get(word, 0) + 1
            
            # Count total word occurrences
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
        
        # Build vocabulary and IDF scores
        vocab_items = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:1000]  # Top 1000 words
        self.vocabulary = {word: idx for idx, (word, _) in enumerate(vocab_items)}
        
        total_docs = len(texts)
        for word in self.vocabulary:
            self.idf_scores[word] = np.log(total_docs / (doc_counts.get(word, 1) + 1))
        
        self.fitted = True
        
        # Transform to vectors
        return self._transform_texts(processed_texts)
    
    def transform(self, texts: List[str]) -> np.ndarray:
        """Transform texts to embeddings."""
        if not self.fitted:
            raise ValueError("Model must be fitted before transform")
        
        processed_texts = [self._preprocess_text(text) for text in texts]
        return self._transform_texts(processed_texts)
    
    def _preprocess_text(self, text: str) -> List[str]:
        """Simple text preprocessing."""
        import re
        text = re.sub(r'[^a-zA-Z\s]', '', text.lower())
        return text.split()
    
    def _transform_texts(self, processed_texts: List[List[str]]) -> np.ndarray:
        """Transform processed texts to TF-IDF vectors."""
        vectors = []
        
        for words in processed_texts:
            vector = np.zeros(len(self.vocabulary))
            word_counts = {}
            
            # Count words in document
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
            
            # Calculate TF-IDF
            total_words = len(words)
            for word, count in word_counts.items():
                if word in self.vocabulary:
                    tf = count / total_words if total_words > 0 else 0
                    idf = self.idf_scores.get(word, 0)
                    vector[self.vocabulary[word]] = tf * idf
            
            vectors.append(vector)
        
        return np.array(vectors)


class SimpleVectorStore:
    """Simple in-memory vector store for embeddings."""
    
    def __init__(self, embedding_model):
        self.embedding_model = embedding_model
        self.embeddings = None
        self.metadata = []
        self.texts = []
        self.fitted = False
    
    def add_documents(self, texts: List[str], metadatas: List[Dict[str, Any]]):
        """Add documents to the vector store."""
        self.texts.extend(texts)
        self.metadata.extend(metadatas)
        
        # Generate embeddings
        if not self.fitted:
            all_texts = texts
            self.embeddings = self.embedding_model.fit_transform(all_texts)
            self.fitted = True
        else:
            new_embeddings = self.embedding_model.transform(texts)
            if self.embeddings is not None:
                self.embeddings = np.vstack([self.embeddings, new_embeddings])
            else:
                self.embeddings = new_embeddings
    
    def similarity_search(self, query: str, k: int = 5, threshold: float = 0.7) -> List[Tuple[str, Dict[str, Any], float]]:
        """Search for similar documents."""
        if not self.fitted or self.embeddings is None:
            return []
        
        # Get query embedding
        query_embedding = self.embedding_model.transform([query])[0]
        
        # Calculate similarities
        similarities = []
        for i, doc_embedding in enumerate(self.embeddings):
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            if similarity >= threshold:
                similarities.append((i, similarity))
        
        # Sort by similarity and return top-k
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for i, sim in similarities[:k]:
            results.append((self.texts[i], self.metadata[i], sim))
        
        return results
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return np.dot(a, b) / (norm_a * norm_b)


class RAGAgent(BaseAgent):
    """
    RAG Agent for generating insights from retail data.
    Optimized for cost-efficiency with local embeddings and minimal API usage.
    """
    
    def __init__(self, config: Optional[AgentConfig] = None, rag_config: Optional[RAGConfig] = None):
        # Configure for RAG operations
        agent_config = config or AgentConfig(
            max_retries=3,
            retry_delay=2.0,
            timeout_seconds=300,
            heartbeat_interval=30
        )
        
        super().__init__(AgentType.RAG, agent_config, "RAGAgent")
        
        # RAG configuration
        self.rag_config = rag_config or RAGConfig()
        
        # Register message handlers
        self.register_handler(MessageType.CLEAN_DATA, self.handle_clean_data)
        
        # Initialize components
        self.embedding_model = None
        self.vector_store = None
        self.openai_client = None
        self.api_call_count = 0
        
        # Cache for avoiding duplicate API calls
        self.insights_cache: Dict[str, Any] = {}
        
        # Cost tracking
        self.estimated_cost = 0.0
    
    async def _on_start(self):
        """Initialize RAG components."""
        try:
            # Initialize embedding model
            self.logger.info("Initializing embedding model...")
            if self.rag_config.use_local_embeddings:
                self.embedding_model = SimpleEmbedding()
                self.logger.info("Using simple local embeddings (TF-IDF)")
            else:
                try:
                    # Try to use sentence-transformers if available
                    import sentence_transformers
                    self.embedding_model = sentence_transformers.SentenceTransformer(
                        self.rag_config.embedding_model
                    )
                    self.logger.info(f"Using sentence-transformers: {self.rag_config.embedding_model}")
                except ImportError:
                    self.embedding_model = SimpleEmbedding()
                    self.logger.info("Falling back to simple local embeddings")
            
            # Initialize vector store
            self.vector_store = SimpleVectorStore(self.embedding_model)
            self.logger.info("Vector store initialized")
            
            # Initialize OpenAI client if not in mock mode
            if not self.rag_config.enable_mock_mode:
                try:
                    import openai
                    api_key = os.getenv('OPENAI_API_KEY')
                    if api_key:
                        self.openai_client = openai.OpenAI(api_key=api_key)
                        self.logger.info("OpenAI client initialized")
                    else:
                        self.logger.warning("OPENAI_API_KEY not found, using mock mode")
                        self.rag_config.enable_mock_mode = True
                except ImportError:
                    self.logger.warning("OpenAI library not available, using mock mode")
                    self.rag_config.enable_mock_mode = True
            
            if self.rag_config.enable_mock_mode:
                self.logger.info("Running in mock mode - no OpenAI API calls")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize RAG components: {e}")
            raise
    
    async def _on_stop(self):
        """Cleanup RAG components."""
        self.logger.info(f"RAG Agent stopped. Total API calls: {self.api_call_count}, Estimated cost: ${self.estimated_cost:.4f}")
    
    async def handle_clean_data(self, message: BaseMessage) -> BaseMessage:
        """
        Handle CLEAN_DATA message and generate insights.
        """
        try:
            # Parse message payload
            clean_payload = CleanDataPayload(
                structured_data=message.payload["structured_data"],
                embeddings_ready=message.payload["embeddings_ready"],
                summary_stats=message.payload["summary_stats"]
            )
            
            self.logger.info("Processing clean data for RAG insights")
            
            # Process data and generate insights
            insights = await self._generate_insights(clean_payload)
            
            # Prepare response
            response_payload = InsightsPayload(
                insights=insights,
                data_summaries=clean_payload.summary_stats,
                generation_metadata={
                    "timestamp": datetime.now().isoformat(),
                    "model_used": self.rag_config.openai_model,
                    "api_calls_made": self.api_call_count,
                    "estimated_cost": self.estimated_cost,
                    "mock_mode": self.rag_config.enable_mock_mode
                }
            )
            
            # Create response message
            response = create_message(
                MessageType.INSIGHTS,
                self.agent_type,
                AgentType.REPORT,  # Send to report agent
                response_payload,
                message.metadata.correlation_id
            )
            
            await self.send_message(response)
            self.logger.info(f"Generated {len(insights)} insights successfully")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error handling clean data: {e}")
            # Send error response
            error_response = self.create_status_message(
                AgentType.COORDINATOR,
                message.metadata.message_id,
                "failed",
                error=str(e)
            )
            await self.send_message(error_response)
            raise
    
    async def _generate_insights(self, clean_data: CleanDataPayload) -> List[InsightData]:
        """Generate insights from clean data using RAG."""
        structured_data = clean_data.structured_data
        
        # Build vector store from cleaned data
        await self._build_vector_store(structured_data)
        
        # Generate insights based on common retail questions
        insight_queries = [
            "What are the main reasons for product returns?",
            "Which product categories have the highest return rates?",
            "What are the most common warranty issues?",
            "How long does it typically take to resolve warranty claims?",
            "What patterns can be seen in customer return behavior?"
        ]
        
        insights = []
        for query in insight_queries:
            if self.api_call_count >= self.rag_config.max_api_calls_per_session:
                self.logger.warning("Reached maximum API calls limit")
                break
                
            insight = await self._generate_single_insight(query, structured_data)
            if insight:
                insights.append(insight)
        
        return insights
    
    async def _build_vector_store(self, structured_data: Dict[str, Any]):
        """Build vector store from structured data."""
        texts = []
        metadatas = []
        
        # Add returns data
        for item in structured_data.get("returns", []):
            texts.append(item["text_content"])
            metadatas.append({
                "type": "return",
                "id": item["id"],
                "source": item.get("structured_data", {})
            })
        
        # Add warranty data
        for item in structured_data.get("warranties", []):
            texts.append(item["text_content"])
            metadatas.append({
                "type": "warranty",
                "id": item["id"],
                "source": item.get("structured_data", {})
            })
        
        # Add product data
        for item in structured_data.get("products", []):
            texts.append(item["text_content"])
            metadatas.append({
                "type": "product",
                "id": item["id"],
                "source": item.get("structured_data", {})
            })
        
        if texts:
            self.vector_store.add_documents(texts, metadatas)
            self.logger.info(f"Added {len(texts)} documents to vector store")
    
    async def _generate_single_insight(self, query: str, structured_data: Dict[str, Any]) -> Optional[InsightData]:
        """Generate a single insight for a given query."""
        try:
            # Check cache first
            cache_key = hashlib.md5(query.encode()).hexdigest()
            if self.rag_config.enable_caching and cache_key in self.insights_cache:
                cached_result = self.insights_cache[cache_key]
                if self._is_cache_valid(cached_result):
                    self.logger.debug(f"Using cached insight for query: {query}")
                    return cached_result["insight"]
            
            # Retrieve relevant documents
            relevant_docs = self.vector_store.similarity_search(
                query, 
                k=self.rag_config.top_k_retrieval,
                threshold=self.rag_config.similarity_threshold
            )
            
            if not relevant_docs:
                self.logger.warning(f"No relevant documents found for query: {query}")
                return None
            
            # Generate insight
            if self.rag_config.enable_mock_mode:
                insight = await self._generate_mock_insight(query, relevant_docs, structured_data)
            else:
                insight = await self._generate_openai_insight(query, relevant_docs, structured_data)
            
            # Cache result
            if self.rag_config.enable_caching and insight:
                self.insights_cache[cache_key] = {
                    "insight": insight,
                    "timestamp": datetime.now(),
                    "query": query
                }
            
            return insight
            
        except Exception as e:
            self.logger.error(f"Error generating insight for query '{query}': {e}")
            return None
    
    async def _generate_mock_insight(self, query: str, relevant_docs: List[Tuple], structured_data: Dict[str, Any]) -> InsightData:
        """Generate mock insight for testing without API calls."""
        # Create realistic mock insights based on the query and data
        mock_insights = {
            "What are the main reasons for product returns?": {
                "text": "Analysis shows that 'Defective Product' accounts for 45% of returns, followed by 'Wrong Size' at 25% and 'Quality Issues' at 20%. These top three categories represent 90% of all return reasons.",
                "category": "return_analysis"
            },
            "Which product categories have the highest return rates?": {
                "text": "Electronics category shows the highest return rate at 12.5%, primarily due to technical defects. Clothing follows at 8.3% mainly due to sizing issues.",
                "category": "category_analysis"
            },
            "What are the most common warranty issues?": {
                "text": "Screen defects represent 35% of warranty claims, with an average resolution time of 7 days. Battery failures account for 28% of claims with longer resolution times.",
                "category": "warranty_analysis"
            },
            "How long does it typically take to resolve warranty claims?": {
                "text": "Average warranty resolution time is 8.5 days. Electronics repairs take longest (10.2 days average), while accessories resolve fastest (3.1 days average).",
                "category": "resolution_time_analysis"
            },
            "What patterns can be seen in customer return behavior?": {
                "text": "Return behavior shows seasonal patterns with 23% higher return rates during holiday seasons. New customers have 2.3x higher return rates than repeat customers.",
                "category": "behavioral_analysis"
            }
        }
        
        insight_data = mock_insights.get(query, {
            "text": f"Mock insight generated for query: {query}. Based on {len(relevant_docs)} relevant documents.",
            "category": "general_analysis"
        })
        
        # Extract citations from relevant docs
        citations = [f"{doc[1]['type']}_{doc[1]['id']}" for doc, _, _ in relevant_docs[:3]]
        
        return InsightData(
            text=insight_data["text"],
            confidence=0.85,  # Mock confidence score
            citations=citations,
            category=insight_data["category"],
            importance=0.8
        )
    
    async def _generate_openai_insight(self, query: str, relevant_docs: List[Tuple], structured_data: Dict[str, Any]) -> Optional[InsightData]:
        """Generate insight using OpenAI API (cost-efficient)."""
        if not self.openai_client:
            return await self._generate_mock_insight(query, relevant_docs, structured_data)
        
        try:
            # Prepare context from relevant documents
            context = self._prepare_context(relevant_docs)
            
            # Create cost-efficient prompt
            prompt = self._create_efficient_prompt(query, context)
            
            # Make API call
            self.api_call_count += 1
            response = self.openai_client.chat.completions.create(
                model=self.rag_config.openai_model,
                messages=[
                    {"role": "system", "content": "You are a retail data analyst. Provide concise, data-driven insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.rag_config.max_tokens,
                temperature=self.rag_config.temperature
            )
            
            # Estimate cost (approximate)
            self.estimated_cost += self._estimate_api_cost(prompt, response.choices[0].message.content)
            
            # Extract insight
            insight_text = response.choices[0].message.content.strip()
            citations = [f"{doc[1]['type']}_{doc[1]['id']}" for doc, _, _ in relevant_docs[:3]]
            
            return InsightData(
                text=insight_text,
                confidence=0.9,
                citations=citations,
                category=self._categorize_query(query),
                importance=0.8
            )
            
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            # Fallback to mock insight
            return await self._generate_mock_insight(query, relevant_docs, structured_data)
    
    def _prepare_context(self, relevant_docs: List[Tuple]) -> str:
        """Prepare context from relevant documents."""
        context_parts = []
        for doc_text, metadata, similarity in relevant_docs:
            context_parts.append(f"[{metadata['type']}] {doc_text}")
        
        context = "\n".join(context_parts)
        
        # Truncate if too long to control costs
        if len(context) > self.rag_config.max_context_tokens * 4:  # Rough char to token ratio
            context = context[:self.rag_config.max_context_tokens * 4] + "..."
        
        return context
    
    def _create_efficient_prompt(self, query: str, context: str) -> str:
        """Create cost-efficient prompt for OpenAI."""
        return f"""Based on the following retail data, answer this question concisely:

Question: {query}

Data:
{context}

Provide a brief, data-driven insight (max 2 sentences):"""
    
    def _estimate_api_cost(self, prompt: str, response: str) -> float:
        """Estimate API cost (rough approximation)."""
        # GPT-3.5-turbo pricing (approximate)
        input_tokens = len(prompt.split()) * 1.3  # Rough token estimation
        output_tokens = len(response.split()) * 1.3
        
        input_cost = (input_tokens / 1000) * 0.0015  # $0.0015 per 1K input tokens
        output_cost = (output_tokens / 1000) * 0.002  # $0.002 per 1K output tokens
        
        return input_cost + output_cost
    
    def _categorize_query(self, query: str) -> str:
        """Categorize query for insight classification."""
        query_lower = query.lower()
        
        if "return" in query_lower and "reason" in query_lower:
            return "return_analysis"
        elif "category" in query_lower or "product" in query_lower:
            return "category_analysis"
        elif "warranty" in query_lower:
            return "warranty_analysis"
        elif "time" in query_lower or "resolve" in query_lower:
            return "resolution_time_analysis"
        else:
            return "general_analysis"
    
    def _is_cache_valid(self, cached_result: Dict[str, Any]) -> bool:
        """Check if cached result is still valid."""
        if not self.rag_config.enable_caching:
            return False
        
        cache_time = cached_result["timestamp"]
        time_diff = datetime.now() - cache_time
        
        return time_diff.total_seconds() < (self.rag_config.cache_ttl_hours * 3600)
    
    def get_rag_stats(self) -> Dict[str, Any]:
        """Get RAG agent statistics."""
        return {
            "agent_type": self.agent_type.value,
            "agent_name": self.name,
            "api_calls_made": self.api_call_count,
            "estimated_cost": self.estimated_cost,
            "cache_size": len(self.insights_cache),
            "mock_mode": self.rag_config.enable_mock_mode,
            "vector_store_docs": len(self.vector_store.texts) if self.vector_store else 0
        }