"""
Unit tests for the Data Fetch Agent.
Tests database connectivity, data fetching, filtering, and message handling.
"""

import pytest
import asyncio
from datetime import date, timedelta
from unittest.mock import Mock, patch, AsyncMock

from src.main.python.agents.data_fetch_agent import DataFetchAgent
from src.main.python.models.message_types import (
    MessageType, AgentType, DateRange, create_fetch_data_message, BaseMessage
)
from src.main.python.models.database_models import Product, Return, Warranty
from src.test.conftest import (
    assert_message_structure, create_test_message, wait_for_condition,
    generate_test_returns, generate_test_warranties
)


class TestDataFetchAgentInit:
    """Test agent initialization and configuration."""
    
    def test_agent_initialization(self):
        """Test that agent initializes correctly."""
        agent = DataFetchAgent()
        
        assert agent.agent_type == AgentType.DATA_FETCH
        assert agent.name == "DataFetchAgent"
        assert MessageType.FETCH_DATA in agent.message_handlers
        assert agent.config.max_retries == 5
        assert agent.config.timeout_seconds == 600
    
    def test_custom_config(self):
        """Test agent with custom configuration."""
        from src.main.python.core.base_agent import AgentConfig
        
        custom_config = AgentConfig(
            max_retries=3,
            timeout_seconds=300,
            heartbeat_interval=60
        )
        
        agent = DataFetchAgent(custom_config)
        assert agent.config.max_retries == 3
        assert agent.config.timeout_seconds == 300
        assert agent.config.heartbeat_interval == 60


class TestDataFetchAgentDatabase:
    """Test database-related functionality."""
    
    @pytest.mark.database
    def test_database_connection_validation(self, populated_test_db):
        """Test database connection validation on startup."""
        agent = DataFetchAgent()
        
        # Mock database manager to use test database
        with patch('src.main.python.agents.data_fetch_agent.db_manager', populated_test_db):
            # This should not raise an exception
            asyncio.run(agent._on_start())
    
    @pytest.mark.database
    def test_fetch_products(self, populated_test_db, sample_products):
        """Test fetching products from database."""
        agent = DataFetchAgent()
        session = populated_test_db.get_session()
        
        try:
            # Test fetching all products
            products = asyncio.run(agent._fetch_products(session, {}))
            assert len(products) == len(sample_products)
            assert all(isinstance(p, Product) for p in products)
            
            # Test filtering by category
            filters = {"product_categories": ["Electronics"]}
            electronics = asyncio.run(agent._fetch_products(session, filters))
            assert len(electronics) == 2  # TEST001 and TEST002
            assert all(p.category == "Electronics" for p in electronics)
            
            # Test filtering by brand
            filters = {"brands": ["TestBrand"]}
            test_brand = asyncio.run(agent._fetch_products(session, filters))
            assert len(test_brand) == 2
            assert all(p.brand == "TestBrand" for p in test_brand)
            
        finally:
            session.close()
    
    @pytest.mark.database
    def test_fetch_returns(self, populated_test_db, sample_returns, test_date_range):
        """Test fetching returns from database."""
        agent = DataFetchAgent()
        session = populated_test_db.get_session()
        
        try:
            # Test fetching all returns in date range
            returns = asyncio.run(agent._fetch_returns(session, test_date_range, {}))
            assert len(returns) == len(sample_returns)
            assert all(isinstance(r, Return) for r in returns)
            
            # Test filtering by store location
            filters = {"store_locations": ["Test Store 1"]}
            store1_returns = asyncio.run(agent._fetch_returns(session, test_date_range, filters))
            assert len(store1_returns) == 2  # Two returns from Test Store 1
            assert all(r.store_location == "Test Store 1" for r in store1_returns)
            
            # Test filtering by resolution status
            filters = {"resolution_status": ["Resolved"]}
            resolved_returns = asyncio.run(agent._fetch_returns(session, test_date_range, filters))
            assert len(resolved_returns) == 2  # Two resolved returns
            assert all(r.resolution_status == "Resolved" for r in resolved_returns)
            
        finally:
            session.close()
    
    @pytest.mark.database
    def test_fetch_warranties(self, populated_test_db, sample_warranties, test_date_range):
        """Test fetching warranties from database."""
        agent = DataFetchAgent()
        session = populated_test_db.get_session()
        
        try:
            # Test fetching all warranties in date range
            warranties = asyncio.run(agent._fetch_warranties(session, test_date_range, {}))
            assert len(warranties) == len(sample_warranties)
            assert all(isinstance(w, Warranty) for w in warranties)
            
            # Test filtering by status
            filters = {"warranty_status": ["Resolved"]}
            resolved_warranties = asyncio.run(agent._fetch_warranties(session, test_date_range, filters))
            assert len(resolved_warranties) == 1
            assert all(w.status == "Resolved" for w in resolved_warranties)
            
        finally:
            session.close()


class TestDataFetchAgentCaching:
    """Test query caching functionality."""
    
    def test_cache_key_generation(self):
        """Test cache key generation for queries."""
        agent = DataFetchAgent()
        
        from src.main.python.models.message_types import FetchDataPayload, DateRange
        
        payload1 = FetchDataPayload(
            date_range=DateRange(date(2024, 1, 1), date(2024, 3, 31)),
            tables=["returns", "warranties"],
            filters={"store_locations": ["Store A"]}
        )
        
        payload2 = FetchDataPayload(
            date_range=DateRange(date(2024, 1, 1), date(2024, 3, 31)),
            tables=["returns", "warranties"],
            filters={"store_locations": ["Store A"]}
        )
        
        payload3 = FetchDataPayload(
            date_range=DateRange(date(2024, 1, 1), date(2024, 3, 31)),
            tables=["returns", "warranties"],
            filters={"store_locations": ["Store B"]}  # Different filter
        )
        
        key1 = agent._generate_cache_key(payload1)
        key2 = agent._generate_cache_key(payload2)
        key3 = agent._generate_cache_key(payload3)
        
        assert key1 == key2  # Same payload should generate same key
        assert key1 != key3  # Different payload should generate different key
    
    def test_cache_operations(self):
        """Test cache operations."""
        agent = DataFetchAgent()
        
        # Initially empty
        assert len(agent.query_cache) == 0
        
        # Add to cache
        agent.query_cache["test_key"] = ({"data": "test"}, 123456789)
        assert len(agent.query_cache) == 1
        
        # Clear cache
        agent.clear_cache()
        assert len(agent.query_cache) == 0
        
        # Check cache stats
        stats = agent.get_cache_stats()
        assert stats["cache_size"] == 0
        assert stats["cache_ttl"] == 300


class TestDataFetchAgentMessageHandling:
    """Test message handling functionality."""
    
    @pytest.mark.asyncio
    async def test_handle_fetch_data_success(self, populated_test_db):
        """Test successful handling of FETCH_DATA message."""
        agent = DataFetchAgent()
        
        # Mock database manager
        with patch('src.main.python.agents.data_fetch_agent.db_manager', populated_test_db):
            # Create fetch data message
            date_range = DateRange(
                start=date.today() - timedelta(days=30),
                end=date.today()
            )
            
            fetch_message = create_fetch_data_message(
                AgentType.COORDINATOR,
                date_range,
                ["returns", "warranties", "products"]
            )
            
            # Mock send_message to capture response
            sent_messages = []
            agent.send_message = AsyncMock(side_effect=lambda msg: sent_messages.append(msg))
            
            # Handle message
            response = await agent.handle_fetch_data(fetch_message)
            
            # Verify response
            assert response.type == MessageType.RAW_DATA
            assert response.metadata.sender == AgentType.DATA_FETCH
            assert response.metadata.recipient == AgentType.NORMALIZATION
            
            # Verify payload structure
            payload = response.payload
            assert "returns" in payload
            assert "warranties" in payload
            assert "products" in payload
            assert "metadata" in payload
            
            # Verify send_message was called
            assert len(sent_messages) == 1
            assert sent_messages[0].type == MessageType.RAW_DATA
    
    @pytest.mark.asyncio
    async def test_handle_fetch_data_error(self):
        """Test error handling in FETCH_DATA message."""
        agent = DataFetchAgent()
        
        # Mock database manager to raise exception
        with patch('src.main.python.agents.data_fetch_agent.db_manager') as mock_db:
            mock_db.get_session.side_effect = Exception("Database connection failed")
            
            # Create fetch data message
            date_range = DateRange(
                start=date.today() - timedelta(days=30),
                end=date.today()
            )
            
            fetch_message = create_fetch_data_message(
                AgentType.COORDINATOR,
                date_range
            )
            
            # Mock send_message to capture error response
            sent_messages = []
            agent.send_message = AsyncMock(side_effect=lambda msg: sent_messages.append(msg))
            
            # Handle message should raise exception
            with pytest.raises(Exception, match="Database connection failed"):
                await agent.handle_fetch_data(fetch_message)
            
            # Verify error response was sent
            assert len(sent_messages) == 1
            error_msg = sent_messages[0]
            assert error_msg.type == MessageType.TASK_FAILED
            assert "Database connection failed" in error_msg.payload["error"]


class TestDataFetchAgentDataQuality:
    """Test data quality and validation functionality."""
    
    def test_calculate_quality_score_perfect(self):
        """Test quality score calculation with perfect data."""
        agent = DataFetchAgent()
        
        perfect_data = {
            "returns": [
                {
                    "reason": "Defective product",
                    "resolution_status": "Resolved"
                }
            ],
            "warranties": [
                {
                    "issue_description": "Screen defect",
                    "status": "Resolved"
                }
            ],
            "products": [
                {
                    "name": "Test Product",
                    "category": "Electronics"
                }
            ]
        }
        
        score = agent._calculate_quality_score(perfect_data)
        assert score == 1.0
    
    def test_calculate_quality_score_with_issues(self):
        """Test quality score calculation with data quality issues."""
        agent = DataFetchAgent()
        
        imperfect_data = {
            "returns": [
                {
                    "reason": "Defective product",
                    "resolution_status": "Resolved"
                },
                {
                    "reason": "",  # Missing reason
                    "resolution_status": "Pending"
                }
            ],
            "warranties": [
                {
                    "issue_description": "Screen defect",
                    "status": "Resolved"
                }
            ],
            "products": [
                {
                    "name": "",  # Missing name
                    "category": "Electronics"
                }
            ]
        }
        
        score = agent._calculate_quality_score(imperfect_data)
        assert score == 0.5  # 2 issues out of 4 records = 50% quality
    
    def test_generate_metadata(self):
        """Test metadata generation for fetched data."""
        agent = DataFetchAgent()
        
        from src.main.python.models.message_types import FetchDataPayload, DateRange
        
        payload = FetchDataPayload(
            date_range=DateRange(date(2024, 1, 1), date(2024, 3, 31)),
            tables=["returns", "warranties", "products"],
            filters={}
        )
        
        test_data = {
            "returns": [
                {"amount": 100.0, "product_id": "P1", "customer_id": "C1"},
                {"amount": 200.0, "product_id": "P2", "customer_id": "C2"}
            ],
            "warranties": [
                {"cost": 50.0, "resolution_time_days": 7},
                {"cost": 75.0, "resolution_time_days": 14}
            ],
            "products": [
                {"id": "P1", "name": "Product 1"},
                {"id": "P2", "name": "Product 2"}
            ]
        }
        
        metadata = agent._generate_metadata(test_data, payload)
        
        # Check basic metadata
        assert metadata["record_count"] == 6
        assert metadata["returns_count"] == 2
        assert metadata["warranties_count"] == 2
        assert metadata["products_count"] == 2
        
        # Check returns summary
        assert metadata["returns_summary"]["total_amount"] == 300.0
        assert metadata["returns_summary"]["avg_amount"] == 150.0
        assert metadata["returns_summary"]["unique_products"] == 2
        assert metadata["returns_summary"]["unique_customers"] == 2
        
        # Check warranties summary
        assert metadata["warranties_summary"]["total_cost"] == 125.0
        assert metadata["warranties_summary"]["avg_cost"] == 62.5
        assert metadata["warranties_summary"]["avg_resolution_time"] == 10.5


class TestDataFetchAgentFiltering:
    """Test advanced filtering functionality."""
    
    @pytest.mark.database
    def test_price_range_filtering(self, populated_test_db, sample_products):
        """Test product filtering by price range."""
        agent = DataFetchAgent()
        session = populated_test_db.get_session()
        
        try:
            # Filter products under $100
            filters = {"price_range": {"min": 0, "max": 100}}
            cheap_products = asyncio.run(agent._fetch_products(session, filters))
            assert len(cheap_products) == 1  # Only TEST003 (jeans at $79.99)
            assert cheap_products[0].price < 100
            
            # Filter expensive products
            filters = {"price_range": {"min": 500, "max": 2000}}
            expensive_products = asyncio.run(agent._fetch_products(session, filters))
            assert len(expensive_products) == 2  # TEST001 and TEST002
            assert all(p.price >= 500 for p in expensive_products)
            
        finally:
            session.close()
    
    @pytest.mark.database
    def test_amount_range_filtering(self, populated_test_db, test_date_range):
        """Test return filtering by amount range."""
        agent = DataFetchAgent()
        session = populated_test_db.get_session()
        
        try:
            # Filter returns under $100
            filters = {"amount_range": {"min": 0, "max": 100}}
            cheap_returns = asyncio.run(agent._fetch_returns(session, test_date_range, filters))
            assert len(cheap_returns) == 1  # Only the jeans return
            assert cheap_returns[0].amount < 100
            
        finally:
            session.close()
    
    @pytest.mark.database
    def test_resolution_time_filtering(self, populated_test_db, test_date_range):
        """Test warranty filtering by resolution time."""
        agent = DataFetchAgent()
        session = populated_test_db.get_session()
        
        try:
            # Filter warranties with resolution time under 10 days
            filters = {"resolution_time_range": {"min": 0, "max": 10}}
            quick_warranties = asyncio.run(agent._fetch_warranties(session, test_date_range, filters))
            assert len(quick_warranties) == 1  # Only the 7-day resolution
            assert quick_warranties[0].resolution_time_days <= 10
            
        finally:
            session.close()


@pytest.mark.integration
class TestDataFetchAgentIntegration:
    """Integration tests for the data fetch agent."""
    
    @pytest.mark.asyncio
    @pytest.mark.database
    async def test_full_data_fetch_workflow(self, populated_test_db):
        """Test complete data fetch workflow."""
        agent = DataFetchAgent()
        
        with patch('src.main.python.agents.data_fetch_agent.db_manager', populated_test_db):
            await agent._on_start()
            
            # Create comprehensive fetch request
            date_range = DateRange(
                start=date.today() - timedelta(days=60),
                end=date.today()
            )
            
            filters = {
                "store_locations": ["all"],
                "product_categories": ["Electronics", "Clothing"],
                "resolution_status": ["all"]
            }
            
            fetch_message = create_fetch_data_message(
                AgentType.COORDINATOR,
                date_range,
                ["returns", "warranties", "products"],
                filters
            )
            
            # Mock message sending
            sent_messages = []
            agent.send_message = AsyncMock(side_effect=lambda msg: sent_messages.append(msg))
            
            # Execute fetch
            response = await agent.handle_fetch_data(fetch_message)
            
            # Verify comprehensive response
            assert response.type == MessageType.RAW_DATA
            
            payload = response.payload
            assert "returns" in payload
            assert "warranties" in payload
            assert "products" in payload
            assert "metadata" in payload
            
            # Verify metadata completeness
            metadata = payload["metadata"]
            assert "record_count" in metadata
            assert "data_quality_score" in metadata
            assert "returns_summary" in metadata
            assert "warranties_summary" in metadata
            
            await agent._on_stop()


@pytest.mark.slow
class TestDataFetchAgentPerformance:
    """Performance tests for the data fetch agent."""
    
    @pytest.mark.database
    def test_large_dataset_performance(self, test_db_manager):
        """Test performance with large dataset."""
        # Generate large dataset
        large_returns = generate_test_returns(1000)
        large_warranties = generate_test_warranties(500)
        
        session = test_db_manager.get_session()
        
        try:
            # Add large dataset
            for return_item in large_returns:
                session.add(return_item)
            for warranty in large_warranties:
                session.add(warranty)
            session.commit()
            
            agent = DataFetchAgent()
            
            # Measure fetch time
            import time
            start_time = time.time()
            
            date_range = DateRange(
                start=date.today() - timedelta(days=90),
                end=date.today()
            )
            
            returns = asyncio.run(agent._fetch_returns(session, date_range, {}))
            warranties = asyncio.run(agent._fetch_warranties(session, date_range, {}))
            
            end_time = time.time()
            fetch_time = end_time - start_time
            
            # Performance assertions
            assert len(returns) == 1000
            assert len(warranties) == 500
            assert fetch_time < 5.0  # Should complete within 5 seconds
            
        finally:
            session.close()
    
    def test_cache_performance_improvement(self, populated_test_db):
        """Test that caching improves performance."""
        agent = DataFetchAgent()
        
        from src.main.python.models.message_types import FetchDataPayload, DateRange
        
        payload = FetchDataPayload(
            date_range=DateRange(date.today() - timedelta(days=30), date.today()),
            tables=["returns", "warranties", "products"],
            filters={}
        )
        
        with patch('src.main.python.agents.data_fetch_agent.db_manager', populated_test_db):
            import time
            
            # First fetch (no cache)
            start_time = time.time()
            data1 = asyncio.run(agent._fetch_data_from_db(payload))
            first_fetch_time = time.time() - start_time
            
            # Second fetch (with cache)
            start_time = time.time()
            data2 = asyncio.run(agent._fetch_data_from_db(payload))
            second_fetch_time = time.time() - start_time
            
            # Cache should make second fetch faster
            assert second_fetch_time < first_fetch_time
            assert data1 == data2  # Data should be identical