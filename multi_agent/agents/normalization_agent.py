"""
Normalization Agent for cleaning and structuring retail data.
Handles data validation, cleaning, deduplication, and preparation for RAG processing.
"""

import asyncio
import re
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
import pandas as pd
import numpy as np

from src.main.python.core.base_agent import BaseAgent, AgentConfig
from src.main.python.models.message_types import (
    BaseMessage, MessageType, AgentType, 
    RawDataPayload, CleanDataPayload, create_message
)


@dataclass
class DataQualityMetrics:
    """Metrics for tracking data quality during normalization."""
    total_records: int
    cleaned_records: int
    removed_records: int
    duplicate_records: int
    invalid_records: int
    completion_rate: float
    quality_score: float


@dataclass
class NormalizationRules:
    """Configuration for data normalization rules."""
    # Text normalization
    normalize_case: bool = True
    trim_whitespace: bool = True
    standardize_categories: bool = True
    
    # Validation rules
    validate_dates: bool = True
    validate_amounts: bool = True
    validate_required_fields: bool = True
    
    # Cleaning rules
    remove_duplicates: bool = True
    fix_encoding_issues: bool = True
    standardize_phone_numbers: bool = True
    standardize_addresses: bool = True
    
    # Outlier detection
    detect_amount_outliers: bool = True
    amount_outlier_threshold: float = 3.0  # Standard deviations
    
    # Missing data handling
    fill_missing_categories: bool = True
    default_category: str = "Unknown"
    
    # Currency normalization
    normalize_currency: bool = True
    target_currency: str = "USD"


class NormalizationAgent(BaseAgent):
    """
    Agent responsible for cleaning and normalizing retail data.
    Handles validation, standardization, and preparation for RAG processing.
    """
    
    def __init__(self, config: Optional[AgentConfig] = None, rules: Optional[NormalizationRules] = None):
        # Configure for data processing operations
        norm_config = config or AgentConfig(
            max_retries=3,
            retry_delay=1.0,
            timeout_seconds=300,
            heartbeat_interval=30
        )
        
        super().__init__(AgentType.NORMALIZATION, norm_config, "NormalizationAgent")
        
        # Normalization configuration
        self.rules = rules or NormalizationRules()
        
        # Register message handlers
        self.register_handler(MessageType.RAW_DATA, self.handle_raw_data)
        
        # Category standardization mappings
        self.category_mappings = {
            # Electronics variations
            'electronic': 'Electronics',
            'electronics': 'Electronics',
            'tech': 'Electronics',
            'technology': 'Electronics',
            'gadget': 'Electronics',
            'gadgets': 'Electronics',
            
            # Clothing variations
            'clothes': 'Clothing',
            'clothing': 'Clothing',
            'apparel': 'Clothing',
            'fashion': 'Clothing',
            'wear': 'Clothing',
            
            # Home & Garden variations
            'home': 'Home & Garden',
            'house': 'Home & Garden',
            'garden': 'Home & Garden',
            'household': 'Home & Garden',
            'appliance': 'Home & Garden',
            'appliances': 'Home & Garden',
            
            # Sports variations
            'sport': 'Sports & Outdoors',
            'sports': 'Sports & Outdoors',
            'outdoor': 'Sports & Outdoors',
            'outdoors': 'Sports & Outdoors',
            'fitness': 'Sports & Outdoors',
            
            # Beauty & Health variations
            'beauty': 'Beauty & Health',
            'health': 'Beauty & Health',
            'cosmetic': 'Beauty & Health',
            'cosmetics': 'Beauty & Health',
            'personal care': 'Beauty & Health',
            'skincare': 'Beauty & Health'
        }
        
        # Status standardization mappings
        self.status_mappings = {
            # Resolved variations
            'complete': 'Resolved',
            'completed': 'Resolved',
            'done': 'Resolved',
            'finished': 'Resolved',
            'closed': 'Resolved',
            'resolved': 'Resolved',
            
            # Pending variations
            'pending': 'Pending',
            'waiting': 'Pending',
            'review': 'Pending',
            'under review': 'Pending',
            
            # In Progress variations
            'in progress': 'In Progress',
            'processing': 'In Progress',
            'working': 'In Progress',
            'active': 'In Progress',
            
            # Escalated variations
            'escalated': 'Escalated',
            'escalate': 'Escalated',
            'urgent': 'Escalated',
            'priority': 'Escalated'
        }
    
    async def _on_start(self):
        """Initialize normalization agent."""
        self.logger.info("Normalization agent started")
        self.logger.info(f"Normalization rules: {self.rules}")
    
    async def _on_stop(self):
        """Cleanup normalization agent."""
        self.logger.info("Normalization agent stopped")
    
    async def handle_raw_data(self, message: BaseMessage) -> BaseMessage:
        """
        Handle RAW_DATA message and normalize the data.
        """
        try:
            # Parse message payload
            raw_payload = RawDataPayload(
                returns=message.payload["returns"],
                warranties=message.payload["warranties"],
                products=message.payload["products"],
                metadata=message.payload["metadata"]
            )
            
            self.logger.info(f"Normalizing data: {len(raw_payload.returns)} returns, "
                           f"{len(raw_payload.warranties)} warranties, "
                           f"{len(raw_payload.products)} products")
            
            # Normalize data
            cleaned_data = await self._normalize_data(raw_payload)
            
            # Prepare response
            response_payload = CleanDataPayload(
                structured_data=cleaned_data["structured_data"],
                embeddings_ready=True,
                summary_stats=cleaned_data["summary_stats"]
            )
            
            # Create response message
            response = create_message(
                MessageType.CLEAN_DATA,
                self.agent_type,
                AgentType.RAG,
                response_payload,
                message.metadata.correlation_id
            )
            
            await self.send_message(response)
            self.logger.info("Data normalization completed successfully")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error handling raw data: {e}")
            # Send error response
            error_response = self.create_status_message(
                AgentType.COORDINATOR,
                message.metadata.message_id,
                "failed",
                error=str(e)
            )
            await self.send_message(error_response)
            raise
    
    async def _normalize_data(self, raw_data: RawDataPayload) -> Dict[str, Any]:
        """
        Normalize raw data using configured rules.
        """
        # Convert to DataFrames for easier processing
        returns_df = pd.DataFrame(raw_data.returns) if raw_data.returns else pd.DataFrame()
        warranties_df = pd.DataFrame(raw_data.warranties) if raw_data.warranties else pd.DataFrame()
        products_df = pd.DataFrame(raw_data.products) if raw_data.products else pd.DataFrame()
        
        quality_metrics = DataQualityMetrics(
            total_records=len(raw_data.returns) + len(raw_data.warranties) + len(raw_data.products),
            cleaned_records=0,
            removed_records=0,
            duplicate_records=0,
            invalid_records=0,
            completion_rate=0.0,
            quality_score=0.0
        )
        
        # Normalize each dataset
        if not returns_df.empty:
            returns_df, returns_metrics = await self._normalize_returns(returns_df)
            quality_metrics.removed_records += returns_metrics.removed_records
            quality_metrics.duplicate_records += returns_metrics.duplicate_records
            quality_metrics.invalid_records += returns_metrics.invalid_records
        
        if not warranties_df.empty:
            warranties_df, warranties_metrics = await self._normalize_warranties(warranties_df)
            quality_metrics.removed_records += warranties_metrics.removed_records
            quality_metrics.duplicate_records += warranties_metrics.duplicate_records
            quality_metrics.invalid_records += warranties_metrics.invalid_records
        
        if not products_df.empty:
            products_df, products_metrics = await self._normalize_products(products_df)
            quality_metrics.removed_records += products_metrics.removed_records
            quality_metrics.duplicate_records += products_metrics.duplicate_records
            quality_metrics.invalid_records += products_metrics.invalid_records
        
        # Calculate final metrics
        quality_metrics.cleaned_records = len(returns_df) + len(warranties_df) + len(products_df)
        quality_metrics.completion_rate = (
            quality_metrics.cleaned_records / quality_metrics.total_records
            if quality_metrics.total_records > 0 else 0.0
        )
        quality_metrics.quality_score = self._calculate_overall_quality_score(
            returns_df, warranties_df, products_df
        )
        
        # Create embeddings-ready data structure
        structured_data = {
            "returns": self._prepare_returns_for_embeddings(returns_df),
            "warranties": self._prepare_warranties_for_embeddings(warranties_df),
            "products": self._prepare_products_for_embeddings(products_df),
            "normalized_text": self._create_normalized_text_corpus(returns_df, warranties_df, products_df),
            "quality_metrics": quality_metrics.__dict__
        }
        
        # Generate summary statistics
        summary_stats = self._generate_summary_statistics(returns_df, warranties_df, products_df, quality_metrics)
        
        return {
            "structured_data": structured_data,
            "summary_stats": summary_stats
        }
    
    async def _normalize_returns(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, DataQualityMetrics]:
        """Normalize returns data."""
        original_count = len(df)
        metrics = DataQualityMetrics(
            total_records=original_count,
            cleaned_records=0,
            removed_records=0,
            duplicate_records=0,
            invalid_records=0,
            completion_rate=0.0,
            quality_score=0.0
        )
        
        # Remove duplicates
        if self.rules.remove_duplicates:
            duplicate_mask = df.duplicated(subset=['order_id', 'product_id', 'return_date'])
            metrics.duplicate_records = duplicate_mask.sum()
            df = df[~duplicate_mask]
        
        # Validate and clean required fields
        if self.rules.validate_required_fields:
            required_fields = ['order_id', 'product_id', 'return_date', 'reason']
            for field in required_fields:
                if field in df.columns:
                    # Remove records with missing required fields
                    invalid_mask = df[field].isna() | (df[field] == '') | (df[field] == 'null')
                    metrics.invalid_records += invalid_mask.sum()
                    df = df[~invalid_mask]
        
        # Normalize text fields
        if self.rules.normalize_case and 'reason' in df.columns:
            df['reason'] = df['reason'].str.strip().str.title()
        
        # Standardize resolution status
        if 'resolution_status' in df.columns:
            df['resolution_status'] = df['resolution_status'].apply(self._standardize_status)
        
        # Validate dates
        if self.rules.validate_dates and 'return_date' in df.columns:
            df['return_date'] = pd.to_datetime(df['return_date'], errors='coerce')
            invalid_dates = df['return_date'].isna()
            metrics.invalid_records += invalid_dates.sum()
            df = df[~invalid_dates]
        
        # Validate amounts
        if self.rules.validate_amounts and 'amount' in df.columns:
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            invalid_amounts = df['amount'].isna() | (df['amount'] < 0)
            metrics.invalid_records += invalid_amounts.sum()
            df = df[~invalid_amounts]
            
            # Detect outliers
            if self.rules.detect_amount_outliers:
                z_scores = np.abs((df['amount'] - df['amount'].mean()) / df['amount'].std())
                outliers = z_scores > self.rules.amount_outlier_threshold
                self.logger.warning(f"Detected {outliers.sum()} amount outliers in returns")
                # Log outliers but don't remove them (might be legitimate high-value returns)
        
        # Clean store locations
        if 'store_location' in df.columns:
            df['store_location'] = df['store_location'].str.strip().str.title()
        
        metrics.removed_records = original_count - len(df)
        metrics.cleaned_records = len(df)
        metrics.completion_rate = metrics.cleaned_records / original_count if original_count > 0 else 0.0
        
        return df, metrics
    
    async def _normalize_warranties(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, DataQualityMetrics]:
        """Normalize warranties data."""
        original_count = len(df)
        metrics = DataQualityMetrics(
            total_records=original_count,
            cleaned_records=0,
            removed_records=0,
            duplicate_records=0,
            invalid_records=0,
            completion_rate=0.0,
            quality_score=0.0
        )
        
        # Remove duplicates
        if self.rules.remove_duplicates:
            duplicate_mask = df.duplicated(subset=['product_id', 'claim_date', 'issue_description'])
            metrics.duplicate_records = duplicate_mask.sum()
            df = df[~duplicate_mask]
        
        # Validate required fields
        if self.rules.validate_required_fields:
            required_fields = ['product_id', 'claim_date', 'issue_description']
            for field in required_fields:
                if field in df.columns:
                    invalid_mask = df[field].isna() | (df[field] == '') | (df[field] == 'null')
                    metrics.invalid_records += invalid_mask.sum()
                    df = df[~invalid_mask]
        
        # Normalize issue descriptions
        if 'issue_description' in df.columns:
            df['issue_description'] = df['issue_description'].str.strip()
            if self.rules.normalize_case:
                df['issue_description'] = df['issue_description'].str.capitalize()
        
        # Standardize status
        if 'status' in df.columns:
            df['status'] = df['status'].apply(self._standardize_status)
        
        # Validate dates
        if self.rules.validate_dates and 'claim_date' in df.columns:
            df['claim_date'] = pd.to_datetime(df['claim_date'], errors='coerce')
            invalid_dates = df['claim_date'].isna()
            metrics.invalid_records += invalid_dates.sum()
            df = df[~invalid_dates]
        
        # Validate costs
        if 'cost' in df.columns:
            df['cost'] = pd.to_numeric(df['cost'], errors='coerce')
            invalid_costs = df['cost'].isna() | (df['cost'] < 0)
            metrics.invalid_records += invalid_costs.sum()
            df = df[~invalid_costs]
        
        # Validate resolution times
        if 'resolution_time_days' in df.columns:
            df['resolution_time_days'] = pd.to_numeric(df['resolution_time_days'], errors='coerce')
            # Negative resolution times are invalid
            invalid_times = df['resolution_time_days'] < 0
            df.loc[invalid_times, 'resolution_time_days'] = None
        
        metrics.removed_records = original_count - len(df)
        metrics.cleaned_records = len(df)
        metrics.completion_rate = metrics.cleaned_records / original_count if original_count > 0 else 0.0
        
        return df, metrics
    
    async def _normalize_products(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, DataQualityMetrics]:
        """Normalize products data."""
        original_count = len(df)
        metrics = DataQualityMetrics(
            total_records=original_count,
            cleaned_records=0,
            removed_records=0,
            duplicate_records=0,
            invalid_records=0,
            completion_rate=0.0,
            quality_score=0.0
        )
        
        # Remove duplicates
        if self.rules.remove_duplicates:
            duplicate_mask = df.duplicated(subset=['id'])
            metrics.duplicate_records = duplicate_mask.sum()
            df = df[~duplicate_mask]
        
        # Validate required fields
        if self.rules.validate_required_fields:
            required_fields = ['id', 'name', 'category']
            for field in required_fields:
                if field in df.columns:
                    invalid_mask = df[field].isna() | (df[field] == '') | (df[field] == 'null')
                    metrics.invalid_records += invalid_mask.sum()
                    df = df[~invalid_mask]
        
        # Normalize product names
        if 'name' in df.columns:
            df['name'] = df['name'].str.strip()
            if self.rules.normalize_case:
                df['name'] = df['name'].str.title()
        
        # Standardize categories
        if self.rules.standardize_categories and 'category' in df.columns:
            df['category'] = df['category'].apply(self._standardize_category)
        
        # Normalize brands
        if 'brand' in df.columns:
            df['brand'] = df['brand'].str.strip()
            if self.rules.normalize_case:
                df['brand'] = df['brand'].str.title()
        
        # Validate prices
        if 'price' in df.columns:
            df['price'] = pd.to_numeric(df['price'], errors='coerce')
            invalid_prices = df['price'].isna() | (df['price'] <= 0)
            metrics.invalid_records += invalid_prices.sum()
            df = df[~invalid_prices]
        
        metrics.removed_records = original_count - len(df)
        metrics.cleaned_records = len(df)
        metrics.completion_rate = metrics.cleaned_records / original_count if original_count > 0 else 0.0
        
        return df, metrics
    
    def _standardize_category(self, category: str) -> str:
        """Standardize product category using mapping rules."""
        if pd.isna(category) or category == '':
            return self.rules.default_category if self.rules.fill_missing_categories else category
        
        category_lower = category.lower().strip()
        return self.category_mappings.get(category_lower, category.strip().title())
    
    def _standardize_status(self, status: str) -> str:
        """Standardize status values using mapping rules."""
        if pd.isna(status) or status == '':
            return 'Unknown'
        
        status_lower = status.lower().strip()
        return self.status_mappings.get(status_lower, status.strip().title())
    
    def _prepare_returns_for_embeddings(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Prepare returns data for vector embeddings."""
        if df.empty:
            return []
        
        embedding_data = []
        for _, row in df.iterrows():
            # Create rich text representation for embedding
            text_content = f"Return: {row.get('reason', 'Unknown reason')} for {row.get('product_id', 'unknown product')}. "
            text_content += f"Status: {row.get('resolution_status', 'Unknown')}. "
            text_content += f"Amount: ${row.get('amount', 0):.2f}. "
            text_content += f"Store: {row.get('store_location', 'Unknown location')}."
            
            embedding_data.append({
                "id": f"return_{row.get('id', 'unknown')}",
                "type": "return",
                "text_content": text_content,
                "structured_data": row.to_dict(),
                "metadata": {
                    "date": row.get('return_date'),
                    "amount": row.get('amount'),
                    "category": "return",
                    "product_id": row.get('product_id')
                }
            })
        
        return embedding_data
    
    def _prepare_warranties_for_embeddings(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Prepare warranties data for vector embeddings."""
        if df.empty:
            return []
        
        embedding_data = []
        for _, row in df.iterrows():
            # Create rich text representation for embedding
            text_content = f"Warranty claim: {row.get('issue_description', 'Unknown issue')} for {row.get('product_id', 'unknown product')}. "
            text_content += f"Status: {row.get('status', 'Unknown')}. "
            text_content += f"Cost: ${row.get('cost', 0):.2f}. "
            
            if row.get('resolution_time_days'):
                text_content += f"Resolution time: {row.get('resolution_time_days')} days."
            
            embedding_data.append({
                "id": f"warranty_{row.get('id', 'unknown')}",
                "type": "warranty",
                "text_content": text_content,
                "structured_data": row.to_dict(),
                "metadata": {
                    "date": row.get('claim_date'),
                    "cost": row.get('cost'),
                    "category": "warranty",
                    "product_id": row.get('product_id'),
                    "resolution_time": row.get('resolution_time_days')
                }
            })
        
        return embedding_data
    
    def _prepare_products_for_embeddings(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Prepare products data for vector embeddings."""
        if df.empty:
            return []
        
        embedding_data = []
        for _, row in df.iterrows():
            # Create rich text representation for embedding
            text_content = f"Product: {row.get('name', 'Unknown product')} by {row.get('brand', 'Unknown brand')}. "
            text_content += f"Category: {row.get('category', 'Unknown category')}. "
            text_content += f"Price: ${row.get('price', 0):.2f}."
            
            embedding_data.append({
                "id": f"product_{row.get('id', 'unknown')}",
                "type": "product",
                "text_content": text_content,
                "structured_data": row.to_dict(),
                "metadata": {
                    "category": row.get('category'),
                    "brand": row.get('brand'),
                    "price": row.get('price'),
                    "product_type": "product"
                }
            })
        
        return embedding_data
    
    def _create_normalized_text_corpus(
        self, 
        returns_df: pd.DataFrame, 
        warranties_df: pd.DataFrame, 
        products_df: pd.DataFrame
    ) -> List[str]:
        """Create a normalized text corpus for embedding and analysis."""
        corpus = []
        
        # Add return reasons
        if not returns_df.empty and 'reason' in returns_df.columns:
            corpus.extend(returns_df['reason'].dropna().tolist())
        
        # Add warranty issue descriptions
        if not warranties_df.empty and 'issue_description' in warranties_df.columns:
            corpus.extend(warranties_df['issue_description'].dropna().tolist())
        
        # Add product names and categories
        if not products_df.empty:
            if 'name' in products_df.columns:
                corpus.extend(products_df['name'].dropna().tolist())
            if 'category' in products_df.columns:
                corpus.extend(products_df['category'].dropna().unique().tolist())
        
        # Clean and normalize text
        normalized_corpus = []
        for text in corpus:
            if text and isinstance(text, str):
                # Remove extra whitespace and normalize
                normalized_text = re.sub(r'\s+', ' ', text.strip())
                if normalized_text:
                    normalized_corpus.append(normalized_text)
        
        return normalized_corpus
    
    def _calculate_overall_quality_score(
        self, 
        returns_df: pd.DataFrame, 
        warranties_df: pd.DataFrame, 
        products_df: pd.DataFrame
    ) -> float:
        """Calculate overall data quality score."""
        scores = []
        
        # Returns quality score
        if not returns_df.empty:
            returns_score = self._calculate_dataframe_quality(returns_df, ['reason', 'resolution_status', 'amount'])
            scores.append(returns_score)
        
        # Warranties quality score
        if not warranties_df.empty:
            warranties_score = self._calculate_dataframe_quality(warranties_df, ['issue_description', 'status', 'cost'])
            scores.append(warranties_score)
        
        # Products quality score
        if not products_df.empty:
            products_score = self._calculate_dataframe_quality(products_df, ['name', 'category', 'price'])
            scores.append(products_score)
        
        return np.mean(scores) if scores else 0.0
    
    def _calculate_dataframe_quality(self, df: pd.DataFrame, key_columns: List[str]) -> float:
        """Calculate quality score for a specific dataframe."""
        if df.empty:
            return 0.0
        
        quality_factors = []
        
        # Completeness score
        total_cells = len(df) * len(key_columns)
        missing_cells = sum(df[col].isna().sum() for col in key_columns if col in df.columns)
        completeness = 1.0 - (missing_cells / total_cells) if total_cells > 0 else 0.0
        quality_factors.append(completeness)
        
        # Consistency score (checking for standardized values)
        consistency_scores = []
        for col in key_columns:
            if col in df.columns and not df[col].empty:
                # Check for consistent formatting (example: proper case)
                if df[col].dtype == 'object':
                    proper_case_count = df[col].str.istitle().sum() if hasattr(df[col], 'str') else 0
                    consistency = proper_case_count / len(df[col].dropna()) if len(df[col].dropna()) > 0 else 0.0
                    consistency_scores.append(consistency)
        
        if consistency_scores:
            quality_factors.append(np.mean(consistency_scores))
        
        return np.mean(quality_factors) if quality_factors else 0.0
    
    def _generate_summary_statistics(
        self, 
        returns_df: pd.DataFrame, 
        warranties_df: pd.DataFrame, 
        products_df: pd.DataFrame,
        quality_metrics: DataQualityMetrics
    ) -> Dict[str, Any]:
        """Generate comprehensive summary statistics."""
        stats = {
            "normalization_timestamp": datetime.now().isoformat(),
            "quality_metrics": quality_metrics.__dict__,
            "dataset_sizes": {
                "returns": len(returns_df),
                "warranties": len(warranties_df),
                "products": len(products_df)
            }
        }
        
        # Returns statistics
        if not returns_df.empty:
            stats["returns_stats"] = {
                "total_amount": float(returns_df['amount'].sum()) if 'amount' in returns_df.columns else 0,
                "avg_amount": float(returns_df['amount'].mean()) if 'amount' in returns_df.columns else 0,
                "unique_products": int(returns_df['product_id'].nunique()) if 'product_id' in returns_df.columns else 0,
                "unique_customers": int(returns_df['customer_id'].nunique()) if 'customer_id' in returns_df.columns else 0,
                "status_distribution": returns_df['resolution_status'].value_counts().to_dict() if 'resolution_status' in returns_df.columns else {},
                "top_reasons": returns_df['reason'].value_counts().head(5).to_dict() if 'reason' in returns_df.columns else {}
            }
        
        # Warranties statistics
        if not warranties_df.empty:
            stats["warranties_stats"] = {
                "total_cost": float(warranties_df['cost'].sum()) if 'cost' in warranties_df.columns else 0,
                "avg_cost": float(warranties_df['cost'].mean()) if 'cost' in warranties_df.columns else 0,
                "avg_resolution_time": float(warranties_df['resolution_time_days'].mean()) if 'resolution_time_days' in warranties_df.columns else 0,
                "status_distribution": warranties_df['status'].value_counts().to_dict() if 'status' in warranties_df.columns else {},
                "top_issues": warranties_df['issue_description'].value_counts().head(5).to_dict() if 'issue_description' in warranties_df.columns else {}
            }
        
        # Products statistics
        if not products_df.empty:
            stats["products_stats"] = {
                "unique_products": len(products_df),
                "category_distribution": products_df['category'].value_counts().to_dict() if 'category' in products_df.columns else {},
                "brand_distribution": products_df['brand'].value_counts().to_dict() if 'brand' in products_df.columns else {},
                "avg_price": float(products_df['price'].mean()) if 'price' in products_df.columns else 0,
                "price_range": {
                    "min": float(products_df['price'].min()) if 'price' in products_df.columns else 0,
                    "max": float(products_df['price'].max()) if 'price' in products_df.columns else 0
                }
            }
        
        return stats
    
    def get_normalization_stats(self) -> Dict[str, Any]:
        """Get normalization agent statistics."""
        return {
            "agent_type": self.agent_type.value,
            "agent_name": self.name,
            "normalization_rules": self.rules.__dict__,
            "category_mappings_count": len(self.category_mappings),
            "status_mappings_count": len(self.status_mappings)
        }