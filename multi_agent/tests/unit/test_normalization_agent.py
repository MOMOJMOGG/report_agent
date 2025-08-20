"""
Unit tests for the Normalization Agent.
Tests data cleaning, standardization, validation, and embeddings preparation.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import date, timedelta
from unittest.mock import Mock, patch, AsyncMock

from multi_agent.agents.normalization_agent import (
    NormalizationAgent, NormalizationRules, DataQualityMetrics
)
from multi_agent.models.message_types import (
    MessageType, AgentType, RawDataPayload, create_message
)


class TestNormalizationAgentInit:
    """Test normalization agent initialization."""
    
    def test_agent_initialization(self):
        """Test that agent initializes correctly."""
        agent = NormalizationAgent()
        
        assert agent.agent_type == AgentType.NORMALIZATION
        assert agent.name == "NormalizationAgent"
        assert MessageType.RAW_DATA in agent.message_handlers
        assert isinstance(agent.rules, NormalizationRules)
    
    def test_custom_rules_initialization(self):
        """Test agent with custom normalization rules."""
        custom_rules = NormalizationRules(
            normalize_case=False,
            remove_duplicates=False,
            detect_amount_outliers=False
        )
        
        agent = NormalizationAgent(rules=custom_rules)
        assert not agent.rules.normalize_case
        assert not agent.rules.remove_duplicates
        assert not agent.rules.detect_amount_outliers
    
    def test_default_mappings(self):
        """Test that default category and status mappings are loaded."""
        agent = NormalizationAgent()
        
        assert len(agent.category_mappings) > 0
        assert len(agent.status_mappings) > 0
        assert 'electronics' in agent.category_mappings
        assert 'complete' in agent.status_mappings


class TestNormalizationTextStandardization:
    """Test text standardization functionality."""
    
    def test_category_standardization(self):
        """Test category standardization with various inputs."""
        agent = NormalizationAgent()
        
        # Test known mappings
        assert agent._standardize_category('electronics') == 'Electronics'
        assert agent._standardize_category('tech') == 'Electronics'
        assert agent._standardize_category('clothes') == 'Clothing'
        assert agent._standardize_category('home') == 'Home & Garden'
        
        # Test unknown categories
        assert agent._standardize_category('Unknown Category') == 'Unknown Category'
        
        # Test empty/null values
        assert agent._standardize_category('') == 'Unknown'
        assert agent._standardize_category(None) == 'Unknown'
    
    def test_status_standardization(self):
        """Test status standardization with various inputs."""
        agent = NormalizationAgent()
        
        # Test known mappings
        assert agent._standardize_status('complete') == 'Resolved'
        assert agent._standardize_status('done') == 'Resolved'
        assert agent._standardize_status('pending') == 'Pending'
        assert agent._standardize_status('in progress') == 'In Progress'
        assert agent._standardize_status('escalated') == 'Escalated'
        
        # Test unknown statuses
        assert agent._standardize_status('Unknown Status') == 'Unknown Status'
        
        # Test empty/null values
        assert agent._standardize_status('') == 'Unknown'
        assert agent._standardize_status(None) == 'Unknown'
    
    def test_case_sensitivity(self):
        """Test that mappings work regardless of case."""
        agent = NormalizationAgent()
        
        assert agent._standardize_category('ELECTRONICS') == 'Electronics'
        assert agent._standardize_category('Electronics') == 'Electronics'
        assert agent._standardize_status('COMPLETE') == 'Resolved'
        assert agent._standardize_status('Complete') == 'Resolved'


class TestNormalizationDataCleaning:
    """Test data cleaning functionality."""
    
    @pytest.mark.asyncio
    async def test_returns_normalization(self):
        """Test returns data normalization."""
        agent = NormalizationAgent()
        
        # Create test data with various issues
        test_data = pd.DataFrame([
            {
                'id': 1,
                'order_id': 'ORD001',
                'product_id': 'P001',
                'return_date': '2024-01-01',
                'reason': '  defective product  ',
                'resolution_status': 'complete',
                'store_location': 'store one',
                'customer_id': 'C001',
                'amount': 100.0
            },
            {
                'id': 2,
                'order_id': 'ORD002',
                'product_id': 'P002',
                'return_date': '2024-01-02',
                'reason': 'WRONG SIZE',
                'resolution_status': 'pending',
                'store_location': 'STORE TWO',
                'customer_id': 'C002',
                'amount': 50.0
            },
            # Duplicate record
            {
                'id': 1,
                'order_id': 'ORD001',
                'product_id': 'P001',
                'return_date': '2024-01-01',
                'reason': '  defective product  ',
                'resolution_status': 'complete',
                'store_location': 'store one',
                'customer_id': 'C001',
                'amount': 100.0
            },
            # Invalid record (missing required fields)
            {
                'id': 3,
                'order_id': '',
                'product_id': 'P003',
                'return_date': '2024-01-03',
                'reason': '',
                'resolution_status': 'resolved',
                'store_location': 'Store Three',
                'customer_id': 'C003',
                'amount': -10.0  # Invalid negative amount
            }
        ])
        
        cleaned_df, metrics = await agent._normalize_returns(test_data)
        
        # Should remove duplicate and invalid records
        assert len(cleaned_df) == 2  # Only 2 valid, unique records
        assert metrics.duplicate_records == 1
        assert metrics.invalid_records >= 1  # At least the negative amount
        
        # Check text normalization
        if not cleaned_df.empty:
            assert all(cleaned_df['reason'].str.istitle())  # Proper case
            assert all(cleaned_df['store_location'].str.istitle())  # Proper case
            assert 'Resolved' in cleaned_df['resolution_status'].values
            assert 'Pending' in cleaned_df['resolution_status'].values
    
    @pytest.mark.asyncio
    async def test_warranties_normalization(self):
        """Test warranties data normalization."""
        agent = NormalizationAgent()
        
        test_data = pd.DataFrame([
            {
                'id': 1,
                'product_id': 'P001',
                'claim_date': '2024-01-01',
                'issue_description': '  screen defect  ',
                'resolution_time_days': 7,
                'status': 'complete',
                'cost': 150.0
            },
            {
                'id': 2,
                'product_id': 'P002',
                'claim_date': '2024-01-02',
                'issue_description': 'BATTERY FAILURE',
                'resolution_time_days': None,
                'status': 'in progress',
                'cost': 200.0
            },
            # Invalid record
            {
                'id': 3,
                'product_id': '',  # Missing required field
                'claim_date': '2024-01-03',
                'issue_description': '',  # Missing required field
                'resolution_time_days': -5,  # Invalid negative time
                'status': 'resolved',
                'cost': -50.0  # Invalid negative cost
            }
        ])
        
        cleaned_df, metrics = await agent._normalize_warranties(test_data)
        
        # Should remove invalid records
        assert len(cleaned_df) == 2  # Only 2 valid records
        assert metrics.invalid_records >= 1
        
        # Check text normalization
        if not cleaned_df.empty:
            descriptions = cleaned_df['issue_description'].tolist()
            assert any(desc.startswith('Screen') for desc in descriptions)  # Capitalized
            assert 'Resolved' in cleaned_df['status'].values or 'In Progress' in cleaned_df['status'].values
    
    @pytest.mark.asyncio
    async def test_products_normalization(self):
        """Test products data normalization."""
        agent = NormalizationAgent()
        
        test_data = pd.DataFrame([
            {
                'id': 'P001',
                'name': '  smartphone pro  ',
                'category': 'electronics',
                'price': 599.99,
                'brand': 'techcorp'
            },
            {
                'id': 'P002',
                'name': 'LAPTOP ULTRA',
                'category': 'tech',
                'price': 1299.99,
                'brand': 'COMPUTECH'
            },
            # Duplicate ID
            {
                'id': 'P001',
                'name': 'Different Product',
                'category': 'clothing',
                'price': 99.99,
                'brand': 'Fashion'
            },
            # Invalid record
            {
                'id': '',  # Missing required field
                'name': '',  # Missing required field
                'category': '',
                'price': -100.0,  # Invalid negative price
                'brand': 'Invalid'
            }
        ])
        
        cleaned_df, metrics = await agent._normalize_products(test_data)
        
        # Should remove duplicate ID and invalid records
        assert len(cleaned_df) == 2  # Only 2 valid, unique records
        assert metrics.duplicate_records == 1
        assert metrics.invalid_records >= 1
        
        # Check text normalization
        if not cleaned_df.empty:
            assert all(cleaned_df['name'].str.istitle())  # Proper case
            assert all(cleaned_df['brand'].str.istitle())  # Proper case
            assert 'Electronics' in cleaned_df['category'].values  # Standardized category


class TestNormalizationDataQuality:
    """Test data quality scoring and metrics."""
    
    def test_quality_score_calculation(self):
        """Test data quality score calculation."""
        agent = NormalizationAgent()
        
        # Perfect data
        perfect_df = pd.DataFrame([
            {'name': 'Product One', 'category': 'Electronics', 'price': 100.0},
            {'name': 'Product Two', 'category': 'Clothing', 'price': 50.0}
        ])
        
        score = agent._calculate_dataframe_quality(perfect_df, ['name', 'category', 'price'])
        assert score > 0.8  # Should be high quality
        
        # Poor quality data
        poor_df = pd.DataFrame([
            {'name': None, 'category': '', 'price': 100.0},
            {'name': 'product two', 'category': None, 'price': None}
        ])
        
        score = agent._calculate_dataframe_quality(poor_df, ['name', 'category', 'price'])
        assert score < 0.5  # Should be low quality
    
    def test_overall_quality_calculation(self):
        """Test overall quality score calculation."""
        agent = NormalizationAgent()
        
        # Create DataFrames with varying quality
        good_df = pd.DataFrame([
            {'reason': 'Good Reason', 'resolution_status': 'Resolved', 'amount': 100.0}
        ])
        
        poor_df = pd.DataFrame([
            {'issue_description': None, 'status': '', 'cost': None}
        ])
        
        empty_df = pd.DataFrame()
        
        # Test with mixed quality
        score = agent._calculate_overall_quality_score(good_df, poor_df, empty_df)
        assert 0.0 <= score <= 1.0
        
        # Test with all good data
        score = agent._calculate_overall_quality_score(good_df, good_df, good_df)
        assert score > 0.5


class TestNormalizationEmbeddingsPreparation:
    """Test embeddings preparation functionality."""
    
    def test_returns_embedding_preparation(self):
        """Test returns data preparation for embeddings."""
        agent = NormalizationAgent()
        
        test_df = pd.DataFrame([
            {
                'id': 1,
                'product_id': 'P001',
                'reason': 'Defective Product',
                'resolution_status': 'Resolved',
                'amount': 100.0,
                'store_location': 'Store One'
            }
        ])
        
        embedding_data = agent._prepare_returns_for_embeddings(test_df)
        
        assert len(embedding_data) == 1
        assert embedding_data[0]['type'] == 'return'
        assert 'text_content' in embedding_data[0]
        assert 'Defective Product' in embedding_data[0]['text_content']
        assert 'structured_data' in embedding_data[0]
        assert 'metadata' in embedding_data[0]
    
    def test_warranties_embedding_preparation(self):
        """Test warranties data preparation for embeddings."""
        agent = NormalizationAgent()
        
        test_df = pd.DataFrame([
            {
                'id': 1,
                'product_id': 'P001',
                'issue_description': 'Screen Defect',
                'status': 'Resolved',
                'cost': 150.0,
                'resolution_time_days': 7
            }
        ])
        
        embedding_data = agent._prepare_warranties_for_embeddings(test_df)
        
        assert len(embedding_data) == 1
        assert embedding_data[0]['type'] == 'warranty'
        assert 'Screen Defect' in embedding_data[0]['text_content']
        assert '7 days' in embedding_data[0]['text_content']
    
    def test_products_embedding_preparation(self):
        """Test products data preparation for embeddings."""
        agent = NormalizationAgent()
        
        test_df = pd.DataFrame([
            {
                'id': 'P001',
                'name': 'Smartphone Pro',
                'category': 'Electronics',
                'brand': 'TechCorp',
                'price': 599.99
            }
        ])
        
        embedding_data = agent._prepare_products_for_embeddings(test_df)
        
        assert len(embedding_data) == 1
        assert embedding_data[0]['type'] == 'product'
        assert 'Smartphone Pro' in embedding_data[0]['text_content']
        assert 'TechCorp' in embedding_data[0]['text_content']
    
    def test_text_corpus_creation(self):
        """Test normalized text corpus creation."""
        agent = NormalizationAgent()
        
        returns_df = pd.DataFrame([
            {'reason': 'Defective Product'},
            {'reason': 'Wrong Size'}
        ])
        
        warranties_df = pd.DataFrame([
            {'issue_description': 'Screen Defect'},
            {'issue_description': 'Battery Failure'}
        ])
        
        products_df = pd.DataFrame([
            {'name': 'Smartphone', 'category': 'Electronics'},
            {'name': 'Laptop', 'category': 'Electronics'}
        ])
        
        corpus = agent._create_normalized_text_corpus(returns_df, warranties_df, products_df)
        
        assert len(corpus) >= 6  # At least 2 reasons + 2 issues + 2 names
        assert 'Defective Product' in corpus
        assert 'Screen Defect' in corpus
        assert 'Smartphone' in corpus


class TestNormalizationMessageHandling:
    """Test message handling functionality."""
    
    @pytest.mark.asyncio
    async def test_handle_raw_data_success(self):
        """Test successful handling of RAW_DATA message."""
        agent = NormalizationAgent()
        
        # Create test raw data message
        raw_data = {
            "returns": [
                {
                    'id': 1,
                    'order_id': 'ORD001',
                    'product_id': 'P001',
                    'return_date': '2024-01-01',
                    'reason': 'defective',
                    'resolution_status': 'complete',
                    'store_location': 'Store One',
                    'customer_id': 'C001',
                    'amount': 100.0
                }
            ],
            "warranties": [
                {
                    'id': 1,
                    'product_id': 'P001',
                    'claim_date': '2024-01-01',
                    'issue_description': 'screen defect',
                    'resolution_time_days': 7,
                    'status': 'complete',
                    'cost': 150.0
                }
            ],
            "products": [
                {
                    'id': 'P001',
                    'name': 'smartphone',
                    'category': 'electronics',
                    'price': 599.99,
                    'brand': 'techcorp'
                }
            ],
            "metadata": {"record_count": 3}
        }
        
        message = create_message(
            MessageType.RAW_DATA,
            AgentType.DATA_FETCH,
            AgentType.NORMALIZATION,
            raw_data
        )
        
        # Mock send_message to capture response
        sent_messages = []
        agent.send_message = AsyncMock(side_effect=lambda msg: sent_messages.append(msg))
        
        # Handle message
        response = await agent.handle_raw_data(message)
        
        # Verify response
        assert response.type == MessageType.CLEAN_DATA
        assert response.metadata.sender == AgentType.NORMALIZATION
        assert response.metadata.recipient == AgentType.RAG
        
        # Verify payload structure
        payload = response.payload
        assert "structured_data" in payload
        assert "embeddings_ready" in payload
        assert "summary_stats" in payload
        
        # Verify send_message was called
        assert len(sent_messages) == 1
        assert sent_messages[0].type == MessageType.CLEAN_DATA
    
    @pytest.mark.asyncio
    async def test_handle_raw_data_error(self):
        """Test error handling in RAW_DATA message."""
        agent = NormalizationAgent()
        
        # Create malformed message
        invalid_message = create_message(
            MessageType.RAW_DATA,
            AgentType.DATA_FETCH,
            AgentType.NORMALIZATION,
            {"invalid": "data"}  # Missing required fields
        )
        
        # Mock send_message to capture error response
        sent_messages = []
        agent.send_message = AsyncMock(side_effect=lambda msg: sent_messages.append(msg))
        
        # Handle message should raise exception
        with pytest.raises(Exception):
            await agent.handle_raw_data(invalid_message)
        
        # Verify error response was sent
        assert len(sent_messages) == 1
        error_msg = sent_messages[0]
        assert error_msg.type == MessageType.TASK_FAILED


class TestNormalizationConfiguration:
    """Test normalization configuration and rules."""
    
    def test_normalization_rules_defaults(self):
        """Test default normalization rules."""
        rules = NormalizationRules()
        
        assert rules.normalize_case is True
        assert rules.trim_whitespace is True
        assert rules.standardize_categories is True
        assert rules.validate_dates is True
        assert rules.remove_duplicates is True
        assert rules.detect_amount_outliers is True
        assert rules.amount_outlier_threshold == 3.0
    
    def test_custom_normalization_rules(self):
        """Test custom normalization rules."""
        rules = NormalizationRules(
            normalize_case=False,
            remove_duplicates=False,
            amount_outlier_threshold=2.5,
            default_category="Custom Default"
        )
        
        assert rules.normalize_case is False
        assert rules.remove_duplicates is False
        assert rules.amount_outlier_threshold == 2.5
        assert rules.default_category == "Custom Default"
    
    def test_agent_stats(self):
        """Test normalization agent statistics."""
        agent = NormalizationAgent()
        
        stats = agent.get_normalization_stats()
        
        assert "agent_type" in stats
        assert "agent_name" in stats
        assert "normalization_rules" in stats
        assert "category_mappings_count" in stats
        assert "status_mappings_count" in stats
        
        assert stats["agent_type"] == AgentType.NORMALIZATION.value
        assert stats["category_mappings_count"] > 0
        assert stats["status_mappings_count"] > 0


class TestNormalizationRulesApplication:
    """Test application of normalization rules."""
    
    @pytest.mark.asyncio
    async def test_rules_disable_duplicate_removal(self):
        """Test that duplicate removal can be disabled."""
        rules = NormalizationRules(remove_duplicates=False)
        agent = NormalizationAgent(rules=rules)
        
        # Create data with duplicates
        test_data = pd.DataFrame([
            {'id': 1, 'order_id': 'ORD001', 'product_id': 'P001', 'return_date': '2024-01-01', 'reason': 'defective', 'resolution_status': 'complete', 'store_location': 'Store', 'customer_id': 'C001', 'amount': 100.0},
            {'id': 1, 'order_id': 'ORD001', 'product_id': 'P001', 'return_date': '2024-01-01', 'reason': 'defective', 'resolution_status': 'complete', 'store_location': 'Store', 'customer_id': 'C001', 'amount': 100.0}
        ])
        
        cleaned_df, metrics = await agent._normalize_returns(test_data)
        
        # Should keep duplicates
        assert len(cleaned_df) == 2
        assert metrics.duplicate_records == 0
    
    @pytest.mark.asyncio
    async def test_rules_disable_case_normalization(self):
        """Test that case normalization can be disabled."""
        rules = NormalizationRules(normalize_case=False)
        agent = NormalizationAgent(rules=rules)
        
        test_data = pd.DataFrame([
            {'id': 1, 'order_id': 'ORD001', 'product_id': 'P001', 'return_date': '2024-01-01', 'reason': 'defective product', 'resolution_status': 'complete', 'store_location': 'Store', 'customer_id': 'C001', 'amount': 100.0}
        ])
        
        cleaned_df, _ = await agent._normalize_returns(test_data)
        
        # Should not change case
        if not cleaned_df.empty:
            assert cleaned_df.iloc[0]['reason'] == 'defective product'  # No title case


@pytest.mark.integration
class TestNormalizationIntegration:
    """Integration tests for normalization agent."""
    
    @pytest.mark.asyncio
    async def test_full_normalization_workflow(self):
        """Test complete normalization workflow with realistic data."""
        agent = NormalizationAgent()
        
        # Create realistic raw data
        raw_payload = {
            "returns": [
                {
                    'id': 1,
                    'order_id': 'ORD001',
                    'product_id': 'ELEC001',
                    'return_date': '2024-07-01',
                    'reason': '  defective product  ',
                    'resolution_status': 'complete',
                    'store_location': 'new york store',
                    'customer_id': 'CUST001',
                    'amount': 599.99
                },
                {
                    'id': 2,
                    'order_id': 'ORD002',
                    'product_id': 'CLTH001',
                    'return_date': '2024-07-02',
                    'reason': 'WRONG SIZE',
                    'resolution_status': 'pending',
                    'store_location': 'LOS ANGELES STORE',
                    'customer_id': 'CUST002',
                    'amount': 89.99
                }
            ],
            "warranties": [
                {
                    'id': 1,
                    'product_id': 'ELEC001',
                    'claim_date': '2024-06-15',
                    'issue_description': '  screen defect  ',
                    'resolution_time_days': 7,
                    'status': 'complete',
                    'cost': 150.00
                }
            ],
            "products": [
                {
                    'id': 'ELEC001',
                    'name': '  smartphone pro x  ',
                    'category': 'electronics',
                    'price': 999.99,
                    'brand': 'techcorp'
                },
                {
                    'id': 'CLTH001',
                    'name': 'PREMIUM JEANS',
                    'category': 'clothes',
                    'price': 129.99,
                    'brand': 'DENIMCRAFT'
                }
            ],
            "metadata": {"record_count": 5}
        }
        
        # Create RawDataPayload
        from multi_agent.models.message_types import RawDataPayload
        payload = RawDataPayload(
            returns=raw_payload["returns"],
            warranties=raw_payload["warranties"],
            products=raw_payload["products"],
            metadata=raw_payload["metadata"]
        )
        
        # Execute normalization
        result = await agent._normalize_data(payload)
        
        # Verify structure
        assert "structured_data" in result
        assert "summary_stats" in result
        
        structured_data = result["structured_data"]
        assert "returns" in structured_data
        assert "warranties" in structured_data
        assert "products" in structured_data
        assert "normalized_text" in structured_data
        assert "quality_metrics" in structured_data
        
        # Verify embeddings preparation
        returns_embeddings = structured_data["returns"]
        assert len(returns_embeddings) > 0
        assert all("text_content" in item for item in returns_embeddings)
        assert all("metadata" in item for item in returns_embeddings)
        
        # Verify text corpus
        text_corpus = structured_data["normalized_text"]
        assert len(text_corpus) > 0
        assert any("Defective Product" in text for text in text_corpus)
        
        # Verify summary stats
        summary_stats = result["summary_stats"]
        assert "quality_metrics" in summary_stats
        assert "dataset_sizes" in summary_stats
        assert "returns_stats" in summary_stats
        assert "warranties_stats" in summary_stats
        assert "products_stats" in summary_stats