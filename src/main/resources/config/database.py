"""
Database configuration and connection management for Multi-Agent RAG system.
"""

import os
from typing import Optional
from sqlalchemy import create_engine, Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

Base = declarative_base()

class DatabaseConfig:
    """Database configuration management."""
    
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL', 'sqlite:///data/retail_data.db')
        self.pool_size = int(os.getenv('DB_POOL_SIZE', '10'))
        self.max_overflow = int(os.getenv('DB_MAX_OVERFLOW', '20'))
        self.pool_timeout = int(os.getenv('DB_POOL_TIMEOUT', '30'))
        self.echo = os.getenv('DB_ECHO', 'false').lower() == 'true'
    
    def create_engine(self) -> Engine:
        """Create database engine with connection pooling."""
        if self.db_url.startswith('sqlite'):
            # SQLite specific configuration
            return create_engine(
                self.db_url,
                echo=self.echo,
                connect_args={"check_same_thread": False}
            )
        else:
            # PostgreSQL/MySQL configuration with pooling
            return create_engine(
                self.db_url,
                echo=self.echo,
                poolclass=QueuePool,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_timeout=self.pool_timeout,
                pool_pre_ping=True
            )

class DatabaseManager:
    """Database connection and session management."""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        self.config = config or DatabaseConfig()
        self.engine = self.config.create_engine()
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_session(self) -> Session:
        """Get database session."""
        return self.SessionLocal()
    
    def create_tables(self):
        """Create all tables."""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """Drop all tables."""
        Base.metadata.drop_all(bind=self.engine)
    
    def close(self):
        """Close database connections."""
        self.engine.dispose()

# Global database manager instance
db_manager = DatabaseManager()

def get_db() -> Session:
    """Dependency to get database session."""
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()