"""
Pytest configuration and shared fixtures for the multi-agent RAG system tests.
"""

import pytest
import asyncio
import tempfile
import os
from datetime import date, timedelta
from typing import Generator, Dict, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.main.python.models.database_models import Base, Product, Return, Warranty
from src.main.resources.config.database import DatabaseManager, DatabaseConfig
from src.main.python.core.message_broker import MessageBroker
from src.main.python.agents.data_fetch_agent import DataFetchAgent
from src.main.python.models.message_types import AgentType, MessageType, DateRange


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_db_path():
    """Create a temporary database file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_file:
        db_path = temp_file.name
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def test_db_config(temp_db_path):
    """Create a test database configuration."""
    return DatabaseConfig()


@pytest.fixture
def test_db_manager(temp_db_path):
    """Create a test database manager with temporary database."""
    # Create engine with SQLite for testing
    engine = create_engine(f'sqlite:///{temp_db_path}', echo=False)
    
    # Create custom database manager
    class TestDatabaseManager:
        def __init__(self):
            self.engine = engine
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        def get_session(self):
            return self.SessionLocal()
        
        def create_tables(self):
            Base.metadata.create_all(bind=self.engine)
        
        def drop_tables(self):
            Base.metadata.drop_all(bind=self.engine)
        
        def close(self):
            self.engine.dispose()
    
    manager = TestDatabaseManager()
    manager.create_tables()
    
    yield manager
    
    manager.close()


@pytest.fixture
def sample_products():
    """Create sample products for testing."""
    return [
        Product(
            id="TEST001",
            name="Test Smartphone",
            category="Electronics",
            price=599.99,
            brand="TestBrand"
        ),
        Product(
            id="TEST002",
            name="Test Laptop",
            category="Electronics",
            price=1299.99,
            brand="TestBrand"
        ),
        Product(
            id="TEST003",
            name="Test Jeans",
            category="Clothing",
            price=79.99,
            brand="TestFashion"
        )
    ]


@pytest.fixture
def sample_returns():
    """Create sample returns for testing."""
    base_date = date.today() - timedelta(days=30)
    
    return [
        Return(
            order_id="ORDER001",
            product_id="TEST001",
            return_date=base_date,
            reason="Defective product",
            resolution_status="Resolved",
            store_location="Test Store 1",
            customer_id="CUST001",
            amount=599.99
        ),
        Return(
            order_id="ORDER002",
            product_id="TEST002",
            return_date=base_date + timedelta(days=5),
            reason="Wrong color",
            resolution_status="Pending",
            store_location="Test Store 2",
            customer_id="CUST002",
            amount=1299.99
        ),
        Return(
            order_id="ORDER003",
            product_id="TEST003",
            return_date=base_date + timedelta(days=10),
            reason="Quality issues",
            resolution_status="Resolved",
            store_location="Test Store 1",
            customer_id="CUST003",
            amount=79.99
        )
    ]


@pytest.fixture
def sample_warranties():
    """Create sample warranties for testing."""
    base_date = date.today() - timedelta(days=45)
    
    return [
        Warranty(
            product_id="TEST001",
            claim_date=base_date,
            issue_description="Screen defect",
            resolution_time_days=7,
            status="Resolved",
            cost=150.00
        ),
        Warranty(
            product_id="TEST002",
            claim_date=base_date + timedelta(days=10),
            issue_description="Battery failure",
            resolution_time_days=None,
            status="In Progress",
            cost=200.00
        )
    ]


@pytest.fixture
def populated_test_db(test_db_manager, sample_products, sample_returns, sample_warranties):
    """Create a populated test database with sample data."""
    session = test_db_manager.get_session()
    
    try:
        # Add sample data
        for product in sample_products:
            session.add(product)
        
        for return_item in sample_returns:
            session.add(return_item)
        
        for warranty in sample_warranties:
            session.add(warranty)
        
        session.commit()
        
        yield test_db_manager
        
    finally:
        session.close()


@pytest.fixture
def test_date_range():
    """Create a test date range for the last 90 days."""
    end_date = date.today()
    start_date = end_date - timedelta(days=90)
    return DateRange(start=start_date, end=end_date)


@pytest.fixture
def test_message_broker():
    """Create a test message broker."""
    broker = MessageBroker()
    yield broker


@pytest.fixture
async def test_data_fetch_agent(test_message_broker):
    """Create a test data fetch agent."""
    agent = DataFetchAgent()
    
    # Register with broker
    test_message_broker.register_agent(AgentType.DATA_FETCH, agent)
    
    # Start broker and agent
    await test_message_broker.start()
    await agent.start()
    
    yield agent
    
    # Cleanup
    await agent.stop()
    await test_message_broker.stop()


@pytest.fixture
def mock_fetch_data_payload():
    """Create a mock fetch data payload."""
    return {
        "date_range": {
            "start": (date.today() - timedelta(days=90)).isoformat(),
            "end": date.today().isoformat()
        },
        "tables": ["returns", "warranties", "products"],
        "filters": {
            "store_locations": ["all"],
            "product_categories": ["all"]
        }
    }


@pytest.fixture
def mock_raw_data_response():
    """Create a mock raw data response."""
    return {
        "returns": [
            {
                "id": 1,
                "order_id": "ORDER001",
                "product_id": "TEST001",
                "return_date": "2024-07-20",
                "reason": "Defective product",
                "resolution_status": "Resolved",
                "store_location": "Test Store 1",
                "customer_id": "CUST001",
                "amount": 599.99
            }
        ],
        "warranties": [
            {
                "id": 1,
                "product_id": "TEST001",
                "claim_date": "2024-07-15",
                "issue_description": "Screen defect",
                "resolution_time_days": 7,
                "status": "Resolved",
                "cost": 150.00
            }
        ],
        "products": [
            {
                "id": "TEST001",
                "name": "Test Smartphone",
                "category": "Electronics",
                "price": 599.99,
                "brand": "TestBrand"
            }
        ],
        "metadata": {
            "record_count": 3,
            "date_range": {
                "start": "2024-05-20",
                "end": "2024-08-19"
            },
            "data_quality_score": 1.0
        }
    }


# Test utilities

def assert_message_structure(message, expected_type: MessageType, expected_sender: AgentType):
    """Assert that a message has the correct structure."""
    assert message.type == expected_type
    assert message.metadata.sender == expected_sender
    assert message.payload is not None
    assert message.metadata.message_id is not None
    assert message.metadata.timestamp is not None


def create_test_message(message_type: MessageType, sender: AgentType, recipient: AgentType, payload: Dict[str, Any]):
    """Create a test message with proper structure."""
    from src.main.python.models.message_types import create_message
    return create_message(message_type, sender, recipient, payload)


# Async test utilities

async def wait_for_condition(condition_func, timeout=5.0, check_interval=0.1):
    """Wait for a condition to become true within timeout."""
    import time
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if condition_func():
            return True
        await asyncio.sleep(check_interval)
    
    return False


# Mock data generators

def generate_test_returns(count: int, start_date: date = None):
    """Generate test return records."""
    if start_date is None:
        start_date = date.today() - timedelta(days=90)
    
    returns = []
    for i in range(count):
        return_date = start_date + timedelta(days=i % 90)
        returns.append(Return(
            order_id=f"ORDER{i:03d}",
            product_id=f"TEST{(i % 3) + 1:03d}",
            return_date=return_date,
            reason=["Defective product", "Wrong size", "Quality issues"][i % 3],
            resolution_status=["Resolved", "Pending", "In Progress"][i % 3],
            store_location=f"Test Store {(i % 2) + 1}",
            customer_id=f"CUST{i:03d}",
            amount=round(100 + (i * 10.5), 2)
        ))
    
    return returns


def generate_test_warranties(count: int, start_date: date = None):
    """Generate test warranty records."""
    if start_date is None:
        start_date = date.today() - timedelta(days=90)
    
    warranties = []
    for i in range(count):
        claim_date = start_date + timedelta(days=i % 90)
        warranties.append(Warranty(
            product_id=f"TEST{(i % 3) + 1:03d}",
            claim_date=claim_date,
            issue_description=["Screen defect", "Battery failure", "Hardware malfunction"][i % 3],
            resolution_time_days=7 if i % 2 == 0 else None,
            status=["Resolved", "In Progress"][i % 2],
            cost=round(50 + (i * 5.25), 2)
        ))
    
    return warranties