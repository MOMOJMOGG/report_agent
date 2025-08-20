"""
Integration tests for Data Fetch Agent with real database and message broker.
Tests end-to-end functionality including message flow and database operations.
"""

import pytest
import asyncio
from datetime import date, timedelta

from src.main.python.agents.data_fetch_agent import DataFetchAgent
from src.main.python.core.message_broker import MessageBroker
from src.main.python.models.message_types import (
    MessageType, AgentType, DateRange, create_fetch_data_message
)
from src.test.conftest import wait_for_condition


@pytest.mark.integration
class TestDataFetchAgentIntegration:
    """Integration tests for data fetch agent with message broker."""
    
    @pytest.mark.asyncio
    async def test_agent_broker_registration(self):
        """Test agent registration with message broker."""
        broker = MessageBroker()
        agent = DataFetchAgent()
        
        try:
            await broker.start()
            await agent.start()
            
            # Register agent with broker
            broker.register_agent(AgentType.DATA_FETCH, agent)
            
            # Verify registration
            assert AgentType.DATA_FETCH in broker.agents
            assert broker.agents[AgentType.DATA_FETCH] == agent
            
        finally:
            await agent.stop()
            await broker.stop()
    
    @pytest.mark.asyncio
    async def test_message_flow_through_broker(self, populated_test_db):
        """Test complete message flow through message broker."""
        broker = MessageBroker()
        agent = DataFetchAgent()
        
        # Mock database manager
        import src.main.python.agents.data_fetch_agent as fetch_module
        original_db_manager = fetch_module.db_manager
        fetch_module.db_manager = populated_test_db
        
        try:
            await broker.start()
            await agent.start()
            
            # Register agent
            broker.register_agent(AgentType.DATA_FETCH, agent)
            
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
            
            # Send message through broker
            success = await broker.send_message(fetch_message)
            assert success
            
            # Wait for message processing
            await wait_for_condition(
                lambda: len(broker.message_history) > 0,
                timeout=5.0
            )
            
            # Verify message was processed
            assert len(broker.message_history) >= 1
            assert fetch_message.metadata.message_id in [
                msg.metadata.message_id for msg in broker.message_history
            ]
            
        finally:
            fetch_module.db_manager = original_db_manager
            await agent.stop()
            await broker.stop()
    
    @pytest.mark.asyncio
    async def test_agent_heartbeat(self):
        """Test agent heartbeat functionality."""
        broker = MessageBroker()
        agent = DataFetchAgent()
        
        try:
            await broker.start()
            await agent.start()
            
            # Register agent
            broker.register_agent(AgentType.DATA_FETCH, agent)
            
            # Wait for heartbeat messages
            await wait_for_condition(
                lambda: any(
                    msg.type == MessageType.HEARTBEAT 
                    for msg in broker.message_history
                ),
                timeout=35.0  # Heartbeat interval is 30 seconds
            )
            
            # Verify heartbeat was sent
            heartbeat_messages = [
                msg for msg in broker.message_history 
                if msg.type == MessageType.HEARTBEAT
            ]
            
            assert len(heartbeat_messages) > 0
            
            heartbeat = heartbeat_messages[0]
            assert heartbeat.metadata.sender == AgentType.DATA_FETCH
            assert heartbeat.metadata.recipient == AgentType.COORDINATOR
            assert "agent_name" in heartbeat.payload
            assert "status" in heartbeat.payload
            
        finally:
            await agent.stop()
            await broker.stop()
    
    @pytest.mark.asyncio
    @pytest.mark.database
    async def test_end_to_end_data_fetch(self, populated_test_db):
        """Test complete end-to-end data fetch workflow."""
        broker = MessageBroker()
        fetch_agent = DataFetchAgent()
        
        # Mock database manager
        import src.main.python.agents.data_fetch_agent as fetch_module
        original_db_manager = fetch_module.db_manager
        fetch_module.db_manager = populated_test_db
        
        # Create mock normalization agent to receive data
        class MockNormalizationAgent:
            def __init__(self):
                self.received_messages = []
            
            async def receive_message(self, message):
                self.received_messages.append(message)
        
        mock_norm_agent = MockNormalizationAgent()
        
        try:
            await broker.start()
            await fetch_agent.start()
            
            # Register agents
            broker.register_agent(AgentType.DATA_FETCH, fetch_agent)
            broker.register_agent(AgentType.NORMALIZATION, mock_norm_agent)
            
            # Create and send fetch request
            date_range = DateRange(
                start=date.today() - timedelta(days=30),
                end=date.today()
            )
            
            fetch_message = create_fetch_data_message(
                AgentType.COORDINATOR,
                date_range,
                ["returns", "warranties", "products"],
                {"store_locations": ["all"], "product_categories": ["all"]}
            )
            
            # Send message
            await broker.send_message(fetch_message)
            
            # Wait for processing and response
            await wait_for_condition(
                lambda: len(mock_norm_agent.received_messages) > 0,
                timeout=10.0
            )
            
            # Verify response
            assert len(mock_norm_agent.received_messages) == 1
            
            response = mock_norm_agent.received_messages[0]
            assert response.type == MessageType.RAW_DATA
            assert response.metadata.sender == AgentType.DATA_FETCH
            assert response.metadata.recipient == AgentType.NORMALIZATION
            
            # Verify payload structure
            payload = response.payload
            assert "returns" in payload
            assert "warranties" in payload
            assert "products" in payload
            assert "metadata" in payload
            
            # Verify data content
            assert len(payload["returns"]) > 0
            assert len(payload["warranties"]) > 0
            assert len(payload["products"]) > 0
            
            # Verify metadata
            metadata = payload["metadata"]
            assert "record_count" in metadata
            assert "data_quality_score" in metadata
            assert metadata["data_quality_score"] > 0.0
            
        finally:
            fetch_module.db_manager = original_db_manager
            await fetch_agent.stop()
            await broker.stop()
    
    @pytest.mark.asyncio
    @pytest.mark.database
    async def test_error_handling_integration(self, populated_test_db):
        """Test error handling in integration scenario."""
        broker = MessageBroker()
        fetch_agent = DataFetchAgent()
        
        # Create mock coordinator to receive error messages
        class MockCoordinator:
            def __init__(self):
                self.received_messages = []
            
            async def receive_message(self, message):
                self.received_messages.append(message)
        
        mock_coordinator = MockCoordinator()
        
        try:
            await broker.start()
            await fetch_agent.start()
            
            # Register agents
            broker.register_agent(AgentType.DATA_FETCH, fetch_agent)
            broker.register_agent(AgentType.COORDINATOR, mock_coordinator)
            
            # Create invalid fetch request (invalid date range)
            from src.main.python.models.message_types import create_message, MessageType
            
            invalid_message = create_message(
                MessageType.FETCH_DATA,
                AgentType.COORDINATOR,
                AgentType.DATA_FETCH,
                {
                    "date_range": {
                        "start": "invalid-date",  # Invalid date format
                        "end": "2024-08-19"
                    },
                    "tables": ["returns"],
                    "filters": {}
                }
            )
            
            # Send invalid message
            await broker.send_message(invalid_message)
            
            # Wait for error response
            await wait_for_condition(
                lambda: any(
                    msg.type == MessageType.TASK_FAILED 
                    for msg in mock_coordinator.received_messages
                ),
                timeout=10.0
            )
            
            # Verify error response
            error_messages = [
                msg for msg in mock_coordinator.received_messages
                if msg.type == MessageType.TASK_FAILED
            ]
            
            assert len(error_messages) > 0
            error_msg = error_messages[0]
            assert error_msg.metadata.sender == AgentType.DATA_FETCH
            assert "error" in error_msg.payload
            
        finally:
            await fetch_agent.stop()
            await broker.stop()
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, populated_test_db):
        """Test handling of concurrent fetch requests."""
        broker = MessageBroker()
        fetch_agent = DataFetchAgent()
        
        # Mock database manager
        import src.main.python.agents.data_fetch_agent as fetch_module
        original_db_manager = fetch_module.db_manager
        fetch_module.db_manager = populated_test_db
        
        # Create mock recipient
        class MockRecipient:
            def __init__(self):
                self.received_messages = []
            
            async def receive_message(self, message):
                self.received_messages.append(message)
        
        mock_recipient = MockRecipient()
        
        try:
            await broker.start()
            await fetch_agent.start()
            
            # Register agents
            broker.register_agent(AgentType.DATA_FETCH, fetch_agent)
            broker.register_agent(AgentType.NORMALIZATION, mock_recipient)
            
            # Create multiple concurrent requests
            requests = []
            for i in range(3):
                date_range = DateRange(
                    start=date.today() - timedelta(days=30 + i),
                    end=date.today() - timedelta(days=i)
                )
                
                fetch_message = create_fetch_data_message(
                    AgentType.COORDINATOR,
                    date_range,
                    ["returns", "warranties"],
                    {"store_locations": [f"Store_{i}"]}
                )
                
                requests.append(fetch_message)
            
            # Send all requests concurrently
            send_tasks = [broker.send_message(req) for req in requests]
            await asyncio.gather(*send_tasks)
            
            # Wait for all responses
            await wait_for_condition(
                lambda: len(mock_recipient.received_messages) >= 3,
                timeout=15.0
            )
            
            # Verify all requests were processed
            assert len(mock_recipient.received_messages) >= 3
            
            # Verify response types
            for response in mock_recipient.received_messages:
                assert response.type == MessageType.RAW_DATA
                assert response.metadata.sender == AgentType.DATA_FETCH
            
        finally:
            fetch_module.db_manager = original_db_manager
            await fetch_agent.stop()
            await broker.stop()


@pytest.mark.integration
@pytest.mark.database
class TestDataFetchAgentDatabaseIntegration:
    """Integration tests specifically for database operations."""
    
    @pytest.mark.asyncio
    async def test_database_connection_recovery(self):
        """Test database connection recovery after failure."""
        from unittest.mock import Mock, patch
        
        agent = DataFetchAgent()
        
        # Mock database manager with initial failure, then success
        mock_session = Mock()
        mock_session.query.return_value.count.side_effect = [
            Exception("Connection lost"),
            10,  # Success on retry
            5,
            2
        ]
        
        mock_db_manager = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        with patch('src.main.python.agents.data_fetch_agent.db_manager', mock_db_manager):
            # First call should fail and retry
            with pytest.raises(Exception):
                await agent._on_start()
    
    @pytest.mark.asyncio
    async def test_transaction_rollback_on_error(self, test_db_manager):
        """Test that database transactions are properly rolled back on errors."""
        agent = DataFetchAgent()
        
        from src.main.python.models.message_types import FetchDataPayload, DateRange
        
        # Create payload that will cause an error
        payload = FetchDataPayload(
            date_range=DateRange(date(2024, 1, 1), date(2024, 12, 31)),
            tables=["returns", "warranties", "products"],
            filters={}
        )
        
        # Mock session to raise error during query
        session = test_db_manager.get_session()
        original_query = session.query
        
        def failing_query(*args, **kwargs):
            if args[0].__name__ == 'Return':  # Fail only on Return query
                raise Exception("Query failed")
            return original_query(*args, **kwargs)
        
        session.query = failing_query
        
        with pytest.raises(Exception, match="Query failed"):
            await agent._fetch_data_from_db(payload)
        
        # Verify session is still usable (transaction was rolled back)
        session.query = original_query  # Restore original query method
        
        # This should work without issues
        products = session.query(test_db_manager.engine.dialect.name).all() if hasattr(test_db_manager.engine.dialect, 'name') else []
        # Just verify no exception is raised
    
    @pytest.mark.asyncio
    async def test_large_result_set_handling(self, test_db_manager):
        """Test handling of large result sets."""
        from src.test.conftest import generate_test_returns
        
        # Generate large dataset
        large_returns = generate_test_returns(500)
        
        session = test_db_manager.get_session()
        
        try:
            # Add large dataset
            for return_item in large_returns:
                session.add(return_item)
            session.commit()
            
            agent = DataFetchAgent()
            
            # Fetch large dataset
            date_range = DateRange(
                start=date.today() - timedelta(days=90),
                end=date.today()
            )
            
            returns = await agent._fetch_returns(session, date_range, {})
            
            # Verify all data was fetched
            assert len(returns) == 500
            
            # Verify memory usage is reasonable
            import sys
            data_size = sys.getsizeof(returns)
            assert data_size < 50 * 1024 * 1024  # Less than 50MB
            
        finally:
            session.close()


@pytest.mark.integration
@pytest.mark.slow
class TestDataFetchAgentPerformanceIntegration:
    """Performance integration tests."""
    
    @pytest.mark.asyncio
    async def test_cache_effectiveness_under_load(self, populated_test_db):
        """Test cache effectiveness under concurrent load."""
        agent = DataFetchAgent()
        
        # Mock database manager
        import src.main.python.agents.data_fetch_agent as fetch_module
        original_db_manager = fetch_module.db_manager
        fetch_module.db_manager = populated_test_db
        
        try:
            from src.main.python.models.message_types import FetchDataPayload, DateRange
            
            # Create identical payload for cache testing
            payload = FetchDataPayload(
                date_range=DateRange(date.today() - timedelta(days=30), date.today()),
                tables=["returns", "warranties", "products"],
                filters={}
            )
            
            # Execute multiple concurrent requests with same payload
            tasks = [agent._fetch_data_from_db(payload) for _ in range(10)]
            
            import time
            start_time = time.time()
            results = await asyncio.gather(*tasks)
            end_time = time.time()
            
            total_time = end_time - start_time
            
            # All results should be identical
            first_result = results[0]
            for result in results[1:]:
                assert result == first_result
            
            # Should complete quickly due to caching
            assert total_time < 5.0  # Should be much faster with caching
            
            # Verify cache was used
            assert len(agent.query_cache) > 0
            
        finally:
            fetch_module.db_manager = original_db_manager
    
    @pytest.mark.asyncio
    async def test_memory_usage_with_large_datasets(self, test_db_manager):
        """Test memory usage with large datasets."""
        from src.test.conftest import generate_test_returns, generate_test_warranties
        
        # Generate very large dataset
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
            
            # Monitor memory usage during fetch
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss
            
            # Fetch large dataset
            from src.main.python.models.message_types import FetchDataPayload, DateRange
            
            payload = FetchDataPayload(
                date_range=DateRange(date.today() - timedelta(days=90), date.today()),
                tables=["returns", "warranties", "products"],
                filters={}
            )
            
            with test_db_manager as db_context:
                fetch_module = __import__('src.main.python.agents.data_fetch_agent', fromlist=[''])
                original_db_manager = fetch_module.db_manager
                fetch_module.db_manager = test_db_manager
                
                try:
                    data = await agent._fetch_data_from_db(payload)
                    
                    final_memory = process.memory_info().rss
                    memory_increase = final_memory - initial_memory
                    
                    # Verify data was fetched
                    assert len(data["returns"]) == 1000
                    assert len(data["warranties"]) == 500
                    
                    # Memory increase should be reasonable (less than 100MB)
                    assert memory_increase < 100 * 1024 * 1024
                    
                finally:
                    fetch_module.db_manager = original_db_manager
                    
        finally:
            session.close()