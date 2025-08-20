"""
Database configuration and management for the Multi-Agent RAG System.
Provides database connection, session management, and configuration.
"""

import os
import logging
from pathlib import Path
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from ..models.database_models import Base

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration settings."""
    
    def __init__(self, 
                 url: str = "sqlite:///data/retail_data.db",
                 echo: bool = False,
                 pool_pre_ping: bool = True):
        self.url = url
        self.echo = echo
        self.pool_pre_ping = pool_pre_ping


class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        self.config = config or DatabaseConfig()
        self.engine = None
        self.SessionLocal = None
        self._initialize()
    
    def _initialize(self):
        """Initialize database engine and session factory."""
        try:
            # Ensure data directory exists for SQLite
            if self.config.url.startswith('sqlite:'):
                db_path = self.config.url.replace('sqlite:///', '')
                db_dir = Path(db_path).parent
                db_dir.mkdir(parents=True, exist_ok=True)
            
            # Create engine
            self.engine = create_engine(
                self.config.url,
                echo=self.config.echo,
                pool_pre_ping=self.config.pool_pre_ping
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info(f"Database initialized: {self.config.url}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def create_tables(self):
        """Create all database tables."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except SQLAlchemyError as e:
            logger.error(f"Failed to create tables: {e}")
            raise
    
    def get_session(self):
        """Get a database session."""
        if self.SessionLocal is None:
            raise RuntimeError("Database not initialized")
        return self.SessionLocal()
    
    def close(self):
        """Close database connections."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connections closed")


# Global database manager instance
db_manager = None

def get_db_manager() -> DatabaseManager:
    """Get the global database manager instance."""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager

def get_db_session():
    """Get a database session (for dependency injection)."""
    manager = get_db_manager()
    session = manager.get_session()
    try:
        yield session
    finally:
        session.close()