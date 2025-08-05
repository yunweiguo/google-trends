#!/usr/bin/env python3
"""
Database setup script for Google Trends Website Builder
Creates the database if it doesn't exist and runs initial setup
"""
import logging
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_database_if_not_exists():
    """Create the database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server (not to specific database)
        conn = psycopg2.connect(
            host=config.database.host,
            port=config.database.port,
            user=config.database.user,
            password=config.database.password,
            database='postgres'  # Connect to default postgres database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s",
            (config.database.name,)
        )
        
        if cursor.fetchone():
            logger.info(f"Database '{config.database.name}' already exists")
        else:
            # Create database
            cursor.execute(f'CREATE DATABASE "{config.database.name}"')
            logger.info(f"Database '{config.database.name}' created successfully")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        logger.error(f"Failed to create database: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False


def main():
    """Main setup function"""
    logger.info("Starting database setup...")
    
    # Create database if needed
    if not create_database_if_not_exists():
        logger.error("Failed to create database")
        return False
    
    # Now run the database initialization
    try:
        from database.init_db import main as init_db_main
        return init_db_main()
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)