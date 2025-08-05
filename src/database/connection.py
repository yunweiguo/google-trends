"""
Database connection and session management
"""
import logging
from contextlib import contextmanager
from typing import Generator, Optional
from sqlalchemy import create_engine, event, pool
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError, DisconnectionError
from src.config import config
from src.database.models import Base

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database connection and session manager"""
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize database manager
        
        Args:
            database_url: Database connection URL. If None, uses config.
        """
        self.database_url = database_url or config.database.url
        self.engine: Optional[Engine] = None
        self.SessionLocal: Optional[sessionmaker] = None
        self._initialized = False
    
    def initialize(self) -> None:
        """Initialize database engine and session factory"""
        if self._initialized:
            return
        
        try:
            # Create engine with connection pooling
            self.engine = create_engine(
                self.database_url,
                poolclass=pool.QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,  # Validate connections before use
                pool_recycle=3600,   # Recycle connections every hour
                echo=config.api.debug,  # Log SQL queries in debug mode
            )
            
            # Add connection event listeners
            self._setup_event_listeners()
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            self._initialized = True
            logger.info("Database manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def _setup_event_listeners(self) -> None:
        """Setup SQLAlchemy event listeners for monitoring"""
        
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """Set database-specific settings on connect"""
            if 'postgresql' in self.database_url:
                # Set PostgreSQL specific settings
                with dbapi_connection.cursor() as cursor:
                    cursor.execute("SET timezone TO 'UTC'")
        
        @event.listens_for(self.engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            """Log connection checkout"""
            logger.debug("Connection checked out from pool")
        
        @event.listens_for(self.engine, "checkin")
        def receive_checkin(dbapi_connection, connection_record):
            """Log connection checkin"""
            logger.debug("Connection checked in to pool")
    
    def create_tables(self) -> None:
        """Create all database tables"""
        if not self._initialized:
            self.initialize()
        
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise
    
    def drop_tables(self) -> None:
        """Drop all database tables (use with caution!)"""
        if not self._initialized:
            self.initialize()
        
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.warning("All database tables dropped")
        except Exception as e:
            logger.error(f"Failed to drop database tables: {e}")
            raise
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get database session with automatic cleanup
        
        Yields:
            Database session
            
        Example:
            with db_manager.get_session() as session:
                # Use session here
                pass
        """
        if not self._initialized:
            self.initialize()
        
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def get_session_sync(self) -> Session:
        """Get database session for synchronous use
        
        Note: Remember to close the session manually!
        
        Returns:
            Database session
        """
        if not self._initialized:
            self.initialize()
        
        return self.SessionLocal()
    
    def health_check(self) -> bool:
        """Check database connection health
        
        Returns:
            True if database is accessible, False otherwise
        """
        try:
            with self.get_session() as session:
                from sqlalchemy import text
                session.execute(text("SELECT 1"))
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def get_connection_info(self) -> dict:
        """Get database connection information
        
        Returns:
            Dictionary with connection details
        """
        if not self._initialized:
            return {"status": "not_initialized"}
        
        try:
            pool_info = self.engine.pool.status() if hasattr(self.engine.pool, 'status') else "N/A"
            return {
                "status": "connected",
                "url": self.database_url.split('@')[-1],  # Hide credentials
                "pool_info": pool_info,
                "echo": self.engine.echo
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def close(self) -> None:
        """Close database connections and cleanup"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connections closed")
        
        self._initialized = False


# Global database manager instance
db_manager = DatabaseManager()


# Convenience functions for common operations
def get_db_session() -> Generator[Session, None, None]:
    """Get database session (convenience function)"""
    return db_manager.get_session()


def init_database() -> None:
    """Initialize database (convenience function)"""
    db_manager.initialize()
    db_manager.create_tables()


def check_database_health() -> bool:
    """Check database health (convenience function)"""
    return db_manager.health_check()


# Database dependency for FastAPI
def get_database_dependency():
    """Database dependency for FastAPI endpoints"""
    with db_manager.get_session() as session:
        yield session