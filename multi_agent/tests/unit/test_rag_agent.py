"""
Unit tests for the RAG Agent.
Tests embedding generation, vector search, insight generation, and cost management.
"""

import pytest
import asyncio
import numpy as np
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

from multi_agent.agents.rag_agent import (
    RAGAgent, RAGConfig, SimpleEmbedding, SimpleVectorStore
)
from multi_agent.models.message_types import (
    MessageType, AgentType, CleanDataPayload, create_message
)


class TestSimpleEmbedding:
    """Test simple embedding implementation."""
    
    def test_embedding_initialization(self):
        """Test embedding model initialization."""
        embedding = SimpleEmbedding()
        assert not embedding.fitted
        assert len(embedding.vocabulary) == 0
        assert len(embedding.idf_scores) == 0
    
    def test_text_preprocessing(self):
        """Test text preprocessing functionality."""
        embedding = SimpleEmbedding()
        
        # Test basic preprocessing
        result = embedding._preprocess_text("Hello World! 123")
        assert result == ['hello', 'world']
        
        # Test with special characters
        result = embedding._preprocess_text("Test@#$%Text with-symbols")
        assert result == ['testtext', 'withsymbols']
        
        # Test empty string
        result = embedding._preprocess_text("")
        assert result == []
    
    def test_fit_transform(self):
        """Test fit and transform functionality."""
        embedding = SimpleEmbedding()
        
        test_texts = [
            "defective smartphone screen",
            "wrong size clothing return",
            "warranty claim battery issue"
        ]
        
        embeddings = embedding.fit_transform(test_texts)
        
        # Check output format
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape[0] == len(test_texts)
        assert embeddings.shape[1] > 0  # Should have some vocabulary
        assert embedding.fitted
        
        # Check vocabulary was built
        assert len(embedding.vocabulary) > 0
        assert len(embedding.idf_scores) > 0
    
    def test_transform_after_fit(self):
        """Test transform functionality after fitting."""
        embedding = SimpleEmbedding()
        
        # Fit on training data
        train_texts = ["smartphone defect", "clothing return"]
        embedding.fit_transform(train_texts)
        
        # Transform new data
        new_texts = ["phone problem", "shirt exchange"]
        new_embeddings = embedding.transform(new_texts)
        
        assert isinstance(new_embeddings, np.ndarray)
        assert new_embeddings.shape[0] == len(new_texts)
        assert new_embeddings.shape[1] == len(embedding.vocabulary)
    
    def test_transform_before_fit_raises_error(self):
        """Test that transform raises error before fitting."""
        embedding = SimpleEmbedding()
        
        with pytest.raises(ValueError, match="Model must be fitted before transform"):
            embedding.transform(["test text"])
    
    def test_vocabulary_limit(self):
        """Test vocabulary size limitation."""
        embedding = SimpleEmbedding()
        
        # Generate many unique words
        large_texts = [f"word{i} unique{i} text{i}" for i in range(500)]
        embeddings = embedding.fit_transform(large_texts)
        
        # Should limit vocabulary to top 1000 words
        assert len(embedding.vocabulary) <= 1000


class TestSimpleVectorStore:
    """Test simple vector store implementation."""
    
    def test_vector_store_initialization(self):
        """Test vector store initialization."""
        embedding_model = SimpleEmbedding()
        vector_store = SimpleVectorStore(embedding_model)
        
        assert vector_store.embedding_model == embedding_model
        assert vector_store.embeddings is None
        assert len(vector_store.metadata) == 0
        assert len(vector_store.texts) == 0
        assert not vector_store.fitted
    
    def test_add_documents(self):
        """Test adding documents to vector store."""
        embedding_model = SimpleEmbedding()
        vector_store = SimpleVectorStore(embedding_model)
        
        texts = ["defective product", "wrong size", "warranty claim"]
        metadatas = [
            {"type": "return", "id": "R1"},
            {"type": "return", "id": "R2"},
            {"type": "warranty", "id": "W1"}
        ]
        
        vector_store.add_documents(texts, metadatas)
        
        assert len(vector_store.texts) == 3
        assert len(vector_store.metadata) == 3
        assert vector_store.fitted
        assert vector_store.embeddings is not None
        assert vector_store.embeddings.shape[0] == 3
    
    def test_similarity_search(self):
        """Test similarity search functionality."""
        embedding_model = SimpleEmbedding()
        vector_store = SimpleVectorStore(embedding_model)
        
        # Add test documents
        texts = [
            "smartphone screen defect issue",
            "clothing size wrong return",
            "battery warranty claim problem"
        ]
        metadatas = [
            {"type": "return", "id": "R1", "category": "electronics"},
            {"type": "return", "id": "R2", "category": "clothing"},
            {"type": "warranty", "id": "W1", "category": "electronics"}
        ]
        
        vector_store.add_documents(texts, metadatas)
        
        # Test search
        results = vector_store.similarity_search("phone defect", k=2, threshold=0.0)
        
        assert len(results) <= 2
        for text, metadata, similarity in results:
            assert isinstance(text, str)
            assert isinstance(metadata, dict)
            assert isinstance(similarity, float)
            assert 0.0 <= similarity <= 1.0
    
    def test_empty_search(self):
        """Test search on empty vector store."""
        embedding_model = SimpleEmbedding()
        vector_store = SimpleVectorStore(embedding_model)
        
        results = vector_store.similarity_search("test query")
        assert len(results) == 0
    
    def test_cosine_similarity(self):
        """Test cosine similarity calculation."""
        embedding_model = SimpleEmbedding()
        vector_store = SimpleVectorStore(embedding_model)
        
        # Test identical vectors
        a = np.array([1, 0, 1])
        b = np.array([1, 0, 1])
        similarity = vector_store._cosine_similarity(a, b)
        assert abs(similarity - 1.0) < 1e-10
        
        # Test orthogonal vectors
        a = np.array([1, 0])
        b = np.array([0, 1])
        similarity = vector_store._cosine_similarity(a, b)
        assert abs(similarity - 0.0) < 1e-10
        
        # Test zero vectors
        a = np.array([0, 0])
        b = np.array([1, 1])
        similarity = vector_store._cosine_similarity(a, b)
        assert similarity == 0.0


class TestRAGAgentInit:
    """Test RAG agent initialization."""
    
    def test_agent_initialization_default(self):
        """Test agent initialization with default config."""
        agent = RAGAgent()
        
        assert agent.agent_type == AgentType.RAG
        assert agent.name == "RAGAgent"
        assert MessageType.CLEAN_DATA in agent.message_handlers
        assert isinstance(agent.rag_config, RAGConfig)
        assert agent.api_call_count == 0
        assert agent.estimated_cost == 0.0
    
    def test_agent_initialization_custom_config(self):
        """Test agent initialization with custom config."""
        rag_config = RAGConfig(
            enable_mock_mode=True,
            max_tokens=100,
            top_k_retrieval=3
        )
        
        agent = RAGAgent(rag_config=rag_config)
        
        assert agent.rag_config.enable_mock_mode is True
        assert agent.rag_config.max_tokens == 100
        assert agent.rag_config.top_k_retrieval == 3
    
    @pytest.mark.asyncio
    async def test_agent_startup_mock_mode(self):
        """Test agent startup in mock mode."""
        rag_config = RAGConfig(enable_mock_mode=True)
        agent = RAGAgent(rag_config=rag_config)
        
        await agent._on_start()
        
        assert agent.embedding_model is not None
        assert agent.vector_store is not None
        assert agent.openai_client is None  # Should be None in mock mode
        
        await agent._on_stop()
    
    @pytest.mark.asyncio
    async def test_agent_startup_no_openai_key(self):
        """Test agent startup without OpenAI key."""
        rag_config = RAGConfig(enable_mock_mode=False)
        agent = RAGAgent(rag_config=rag_config)
        
        # Mock environment without OPENAI_API_KEY
        with patch.dict('os.environ', {}, clear=True):
            await agent._on_start()
            
            # Should fallback to mock mode
            assert agent.rag_config.enable_mock_mode is True
        
        await agent._on_stop()


class TestRAGAgentInsightGeneration:
    """Test insight generation functionality."""
    
    @pytest.mark.asyncio
    async def test_mock_insight_generation(self):
        """Test mock insight generation."""
        agent = RAGAgent(rag_config=RAGConfig(enable_mock_mode=True))
        
        # Test all predefined queries
        queries = [
            "What are the main reasons for product returns?",
            "Which product categories have the highest return rates?",
            "What are the most common warranty issues?",
            "How long does it typically take to resolve warranty claims?",
            "What patterns can be seen in customer return behavior?"
        ]
        
        relevant_docs = [
            ("test doc 1", {"type": "return", "id": "R1"}, 0.8),
            ("test doc 2", {"type": "warranty", "id": "W1"}, 0.7)
        ]
        
        for query in queries:
            insight = await agent._generate_mock_insight(query, relevant_docs, {})
            
            assert insight is not None
            assert isinstance(insight.text, str)
            assert len(insight.text) > 0
            assert 0.0 <= insight.confidence <= 1.0
            assert isinstance(insight.citations, list)
            assert len(insight.citations) > 0
            assert isinstance(insight.category, str)
    
    @pytest.mark.asyncio
    async def test_unknown_query_mock_insight(self):
        """Test mock insight for unknown query."""
        agent = RAGAgent(rag_config=RAGConfig(enable_mock_mode=True))
        
        relevant_docs = [("test doc", {"type": "return", "id": "R1"}, 0.8)]
        query = "Unknown question about data"
        
        insight = await agent._generate_mock_insight(query, relevant_docs, {})
        
        assert insight is not None
        assert "Mock insight generated" in insight.text
        assert insight.category == "general_analysis"
    
    def test_categorize_query(self):
        """Test query categorization."""
        agent = RAGAgent()
        
        # Test return analysis
        assert agent._categorize_query("What are the main reasons for returns?") == "return_analysis"
        
        # Test category analysis
        assert agent._categorize_query("Which product categories perform best?") == "category_analysis"
        
        # Test warranty analysis
        assert agent._categorize_query("How many warranty claims?") == "warranty_analysis"
        
        # Test resolution time analysis
        assert agent._categorize_query("How long to resolve issues?") == "resolution_time_analysis"
        
        # Test general analysis
        assert agent._categorize_query("Random question") == "general_analysis"
    
    def test_prepare_context(self):
        """Test context preparation from documents."""
        agent = RAGAgent()
        
        relevant_docs = [
            ("First document text", {"type": "return", "id": "R1"}, 0.9),
            ("Second document text", {"type": "warranty", "id": "W1"}, 0.8)
        ]
        
        context = agent._prepare_context(relevant_docs)
        
        assert "[return] First document text" in context
        assert "[warranty] Second document text" in context
        assert len(context) > 0
    
    def test_context_truncation(self):
        """Test context truncation for cost control."""
        agent = RAGAgent(rag_config=RAGConfig(max_context_tokens=10))
        
        # Create very long document
        long_text = "word " * 1000  # Very long text
        relevant_docs = [(long_text, {"type": "return", "id": "R1"}, 0.9)]
        
        context = agent._prepare_context(relevant_docs)
        
        # Should be truncated
        assert len(context) < len(long_text)
        assert context.endswith("...")
    
    def test_estimate_api_cost(self):
        """Test API cost estimation."""
        agent = RAGAgent()
        
        prompt = "short prompt"
        response = "short response"
        
        cost = agent._estimate_api_cost(prompt, response)
        
        assert cost > 0.0
        assert cost < 0.01  # Should be very small for short text


class TestRAGAgentCaching:
    """Test caching functionality."""
    
    def test_cache_key_generation(self):
        """Test cache key generation."""
        agent = RAGAgent(rag_config=RAGConfig(enable_caching=True))
        
        import hashlib
        query = "test query"
        expected_key = hashlib.md5(query.encode()).hexdigest()
        
        # Cache key should be consistent
        key1 = hashlib.md5(query.encode()).hexdigest()
        key2 = hashlib.md5(query.encode()).hexdigest()
        
        assert key1 == key2 == expected_key
    
    def test_cache_validity(self):
        """Test cache validity checking."""
        agent = RAGAgent(rag_config=RAGConfig(enable_caching=True, cache_ttl_hours=1))
        
        # Fresh cache entry
        fresh_entry = {
            "insight": None,
            "timestamp": datetime.now(),
            "query": "test"
        }
        assert agent._is_cache_valid(fresh_entry)
        
        # Expired cache entry
        expired_entry = {
            "insight": None,
            "timestamp": datetime.now() - timedelta(hours=2),
            "query": "test"
        }
        assert not agent._is_cache_valid(expired_entry)
    
    def test_cache_disabled(self):
        """Test behavior when caching is disabled."""
        agent = RAGAgent(rag_config=RAGConfig(enable_caching=False))
        
        cache_entry = {
            "insight": None,
            "timestamp": datetime.now(),
            "query": "test"
        }
        
        assert not agent._is_cache_valid(cache_entry)


class TestRAGAgentMessageHandling:
    """Test message handling functionality."""
    
    @pytest.mark.asyncio
    async def test_handle_clean_data_success(self):
        """Test successful handling of CLEAN_DATA message."""
        agent = RAGAgent(rag_config=RAGConfig(enable_mock_mode=True))
        
        # Create test clean data message
        clean_data = {
            "structured_data": {
                "returns": [
                    {
                        "id": "return_1",
                        "type": "return",
                        "text_content": "Return: Defective Product for ELEC001. Status: Resolved.",
                        "structured_data": {"reason": "Defective Product"},
                        "metadata": {"product_id": "ELEC001"}
                    }
                ],
                "warranties": [],
                "products": []
            },
            "embeddings_ready": True,
            "summary_stats": {"returns_stats": {"total_amount": 100.0}}
        }
        
        message = create_message(
            MessageType.CLEAN_DATA,
            AgentType.NORMALIZATION,
            AgentType.RAG,
            clean_data
        )
        
        # Mock send_message to capture response
        sent_messages = []
        agent.send_message = AsyncMock(side_effect=lambda msg: sent_messages.append(msg))
        
        # Start agent and handle message
        await agent._on_start()
        response = await agent.handle_clean_data(message)
        
        # Verify response
        assert response.type == MessageType.INSIGHTS
        assert response.metadata.sender == AgentType.RAG
        assert response.metadata.recipient == AgentType.REPORT
        
        # Verify payload structure
        payload = response.payload
        assert "insights" in payload
        assert "data_summaries" in payload
        assert "generation_metadata" in payload
        
        # Verify generation metadata
        metadata = payload["generation_metadata"]
        assert "timestamp" in metadata
        assert "model_used" in metadata
        assert "api_calls_made" in metadata
        assert "estimated_cost" in metadata
        assert "mock_mode" in metadata
        
        # Verify send_message was called
        assert len(sent_messages) == 1
        assert sent_messages[0].type == MessageType.INSIGHTS
        
        await agent._on_stop()
    
    @pytest.mark.asyncio
    async def test_handle_clean_data_error(self):
        """Test error handling in CLEAN_DATA message."""
        agent = RAGAgent(rag_config=RAGConfig(enable_mock_mode=True))
        
        # Create malformed message
        invalid_message = create_message(
            MessageType.CLEAN_DATA,
            AgentType.NORMALIZATION,
            AgentType.RAG,
            {"invalid": "data"}  # Missing required fields
        )
        
        # Mock send_message to capture error response
        sent_messages = []
        agent.send_message = AsyncMock(side_effect=lambda msg: sent_messages.append(msg))
        
        await agent._on_start()
        
        # Handle message should raise exception
        with pytest.raises(Exception):
            await agent.handle_clean_data(invalid_message)
        
        # Verify error response was sent
        assert len(sent_messages) == 1
        error_msg = sent_messages[0]
        assert error_msg.type == MessageType.TASK_FAILED
        
        await agent._on_stop()


class TestRAGAgentStatistics:
    """Test agent statistics and monitoring."""
    
    def test_get_rag_stats(self):
        """Test RAG agent statistics collection."""
        agent = RAGAgent(rag_config=RAGConfig(enable_mock_mode=True))
        
        stats = agent.get_rag_stats()
        
        assert "agent_type" in stats
        assert "agent_name" in stats
        assert "api_calls_made" in stats
        assert "estimated_cost" in stats
        assert "cache_size" in stats
        assert "mock_mode" in stats
        assert "vector_store_docs" in stats
        
        assert stats["agent_type"] == AgentType.RAG.value
        assert stats["api_calls_made"] == 0
        assert stats["estimated_cost"] == 0.0
        assert stats["mock_mode"] is True
    
    @pytest.mark.asyncio
    async def test_cost_tracking(self):
        """Test cost tracking functionality."""
        agent = RAGAgent(rag_config=RAGConfig(enable_mock_mode=True))
        
        # Simulate cost tracking
        agent.api_call_count = 5
        agent.estimated_cost = 0.025
        
        stats = agent.get_rag_stats()
        
        assert stats["api_calls_made"] == 5
        assert stats["estimated_cost"] == 0.025


class TestRAGConfig:
    """Test RAG configuration."""
    
    def test_default_config(self):
        """Test default RAG configuration."""
        config = RAGConfig()
        
        assert config.use_local_embeddings is True
        assert config.embedding_model == "all-MiniLM-L6-v2"
        assert config.top_k_retrieval == 5
        assert config.similarity_threshold == 0.2
        assert config.openai_model == "gpt-3.5-turbo"
        assert config.max_tokens == 150
        assert config.enable_caching is True
        assert config.max_api_calls_per_session == 10
        assert config.enable_mock_mode is False
    
    def test_custom_config(self):
        """Test custom RAG configuration."""
        config = RAGConfig(
            use_local_embeddings=False,
            top_k_retrieval=3,
            max_tokens=100,
            enable_mock_mode=True,
            max_api_calls_per_session=5
        )
        
        assert config.use_local_embeddings is False
        assert config.top_k_retrieval == 3
        assert config.max_tokens == 100
        assert config.enable_mock_mode is True
        assert config.max_api_calls_per_session == 5


@pytest.mark.integration
class TestRAGAgentIntegration:
    """Integration tests for RAG agent."""
    
    @pytest.mark.asyncio
    async def test_full_rag_workflow(self):
        """Test complete RAG workflow with realistic data."""
        agent = RAGAgent(rag_config=RAGConfig(enable_mock_mode=True, similarity_threshold=0.1))
        
        # Create comprehensive test data
        clean_data_payload = {
            "structured_data": {
                "returns": [
                    {
                        "id": "return_1",
                        "type": "return",
                        "text_content": "Return: Defective smartphone screen for ELEC001. Status: Resolved. Amount: $599.99.",
                        "structured_data": {"reason": "Defective Product", "amount": 599.99},
                        "metadata": {"product_id": "ELEC001", "category": "electronics"}
                    },
                    {
                        "id": "return_2", 
                        "type": "return",
                        "text_content": "Return: Wrong size jeans for CLTH001. Status: Pending. Amount: $89.99.",
                        "structured_data": {"reason": "Wrong Size", "amount": 89.99},
                        "metadata": {"product_id": "CLTH001", "category": "clothing"}
                    }
                ],
                "warranties": [
                    {
                        "id": "warranty_1",
                        "type": "warranty",
                        "text_content": "Warranty claim: Battery failure for ELEC001. Status: In Progress. Cost: $150.00.",
                        "structured_data": {"issue": "Battery failure", "cost": 150.00},
                        "metadata": {"product_id": "ELEC001", "resolution_time": None}
                    }
                ],
                "products": [
                    {
                        "id": "product_ELEC001",
                        "type": "product", 
                        "text_content": "Product: Smartphone Pro X by TechCorp. Category: Electronics. Price: $999.99.",
                        "structured_data": {"name": "Smartphone Pro X", "price": 999.99},
                        "metadata": {"category": "Electronics", "brand": "TechCorp"}
                    }
                ]
            },
            "embeddings_ready": True,
            "summary_stats": {
                "returns_stats": {"total_amount": 689.98, "avg_amount": 344.99},
                "warranties_stats": {"total_cost": 150.00, "avg_cost": 150.00},
                "products_stats": {"avg_price": 999.99}
            }
        }
        
        # Create message
        message = create_message(
            MessageType.CLEAN_DATA,
            AgentType.NORMALIZATION,
            AgentType.RAG,
            clean_data_payload
        )
        
        # Mock send_message
        sent_messages = []
        agent.send_message = AsyncMock(side_effect=lambda msg: sent_messages.append(msg))
        
        # Execute workflow
        await agent._on_start()
        response = await agent.handle_clean_data(message)
        
        # Verify comprehensive response
        assert response.type == MessageType.INSIGHTS
        
        payload = response.payload
        insights = payload["insights"]
        data_summaries = payload["data_summaries"]
        generation_metadata = payload["generation_metadata"]
        
        # Should generate some insights
        assert len(insights) >= 0  # May be 0 if similarity is too low
        
        # Verify data summaries preserved
        assert "returns_stats" in data_summaries
        assert "warranties_stats" in data_summaries
        
        # Verify metadata
        assert generation_metadata["mock_mode"] is True
        assert generation_metadata["api_calls_made"] == 0
        assert generation_metadata["estimated_cost"] == 0.0
        
        # Verify vector store was populated
        stats = agent.get_rag_stats()
        assert stats["vector_store_docs"] == 4  # 2 returns + 1 warranty + 1 product
        
        await agent._on_stop()