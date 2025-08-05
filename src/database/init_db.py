#!/usr/bin/env python3
"""
Database initialization script for Google Trends Website Builder
"""
import logging
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database.connection import db_manager, init_database
from src.database.migrations import run_migrations, get_migration_status

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Initialize database with tables and run migrations"""
    try:
        logger.info("Starting database initialization...")
        
        # Initialize database connection and create tables
        logger.info("Initializing database connection...")
        init_database()
        
        # Run migrations
        logger.info("Running database migrations...")
        if run_migrations():
            logger.info("All migrations applied successfully")
        else:
            logger.error("Some migrations failed")
            return False
        
        # Show migration status
        status = get_migration_status()
        logger.info(f"Migration status: {status['applied_count']} applied, {status['pending_count']} pending")
        
        # Test database connection
        if db_manager.health_check():
            logger.info("Database health check passed")
        else:
            logger.error("Database health check failed")
            return False
        
        logger.info("Database initialization completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False
    finally:
        # Clean up connections
        db_manager.close()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)