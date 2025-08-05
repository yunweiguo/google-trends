"""
Database migration utilities and scripts
"""
import logging
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError
from src.database.connection import db_manager
from src.database.models import Base

logger = logging.getLogger(__name__)


class MigrationManager:
    """Database migration manager"""
    
    def __init__(self):
        self.migrations: List[Dict[str, Any]] = []
        self._register_migrations()
    
    def _register_migrations(self) -> None:
        """Register all available migrations"""
        self.migrations = [
            {
                'version': '001',
                'name': 'initial_schema',
                'description': 'Create initial database schema',
                'up': self._migration_001_up,
                'down': self._migration_001_down,
            },
            {
                'version': '002',
                'name': 'add_indexes',
                'description': 'Add performance indexes',
                'up': self._migration_002_up,
                'down': self._migration_002_down,
            },
            {
                'version': '003',
                'name': 'add_data_quality_tracking',
                'description': 'Add data quality and metrics tables',
                'up': self._migration_003_up,
                'down': self._migration_003_down,
            }
        ]
    
    def create_migration_table(self) -> None:
        """Create migration tracking table"""
        with db_manager.get_session() as session:
            try:
                session.execute(text("""
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        version VARCHAR(10) PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        description TEXT,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                session.commit()
                logger.info("Migration tracking table created")
            except SQLAlchemyError as e:
                logger.error(f"Failed to create migration table: {e}")
                raise
    
    def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions"""
        with db_manager.get_session() as session:
            try:
                result = session.execute(text(
                    "SELECT version FROM schema_migrations ORDER BY version"
                ))
                return [row[0] for row in result.fetchall()]
            except SQLAlchemyError:
                # Migration table doesn't exist yet
                return []
    
    def apply_migration(self, version: str) -> bool:
        """Apply a specific migration
        
        Args:
            version: Migration version to apply
            
        Returns:
            True if successful, False otherwise
        """
        migration = next((m for m in self.migrations if m['version'] == version), None)
        if not migration:
            logger.error(f"Migration {version} not found")
            return False
        
        try:
            logger.info(f"Applying migration {version}: {migration['name']}")
            
            with db_manager.get_session() as session:
                # Run the migration
                migration['up'](session)
                
                # Record the migration
                session.execute(text("""
                    INSERT INTO schema_migrations (version, name, description)
                    VALUES (:version, :name, :description)
                """), {
                    'version': version,
                    'name': migration['name'],
                    'description': migration['description']
                })
                
                session.commit()
                logger.info(f"Migration {version} applied successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to apply migration {version}: {e}")
            return False
    
    def rollback_migration(self, version: str) -> bool:
        """Rollback a specific migration
        
        Args:
            version: Migration version to rollback
            
        Returns:
            True if successful, False otherwise
        """
        migration = next((m for m in self.migrations if m['version'] == version), None)
        if not migration:
            logger.error(f"Migration {version} not found")
            return False
        
        try:
            logger.info(f"Rolling back migration {version}: {migration['name']}")
            
            with db_manager.get_session() as session:
                # Run the rollback
                migration['down'](session)
                
                # Remove migration record
                session.execute(text(
                    "DELETE FROM schema_migrations WHERE version = :version"
                ), {'version': version})
                
                session.commit()
                logger.info(f"Migration {version} rolled back successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to rollback migration {version}: {e}")
            return False
    
    def migrate_up(self) -> bool:
        """Apply all pending migrations
        
        Returns:
            True if all migrations successful, False otherwise
        """
        self.create_migration_table()
        applied = self.get_applied_migrations()
        
        success = True
        for migration in self.migrations:
            if migration['version'] not in applied:
                if not self.apply_migration(migration['version']):
                    success = False
                    break
        
        return success
    
    def migrate_down(self, target_version: str = None) -> bool:
        """Rollback migrations to target version
        
        Args:
            target_version: Version to rollback to. If None, rollback all.
            
        Returns:
            True if successful, False otherwise
        """
        applied = self.get_applied_migrations()
        applied.reverse()  # Rollback in reverse order
        
        success = True
        for version in applied:
            if target_version and version <= target_version:
                break
            
            if not self.rollback_migration(version):
                success = False
                break
        
        return success
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status
        
        Returns:
            Dictionary with migration status information
        """
        applied = self.get_applied_migrations()
        pending = [m for m in self.migrations if m['version'] not in applied]
        
        return {
            'applied_count': len(applied),
            'pending_count': len(pending),
            'applied_migrations': applied,
            'pending_migrations': [m['version'] for m in pending],
            'latest_version': self.migrations[-1]['version'] if self.migrations else None
        }
    
    # Migration implementations
    def _migration_001_up(self, session) -> None:
        """Initial schema creation"""
        # Create all tables using SQLAlchemy models
        Base.metadata.create_all(bind=session.bind)
        logger.info("Initial schema created")
    
    def _migration_001_down(self, session) -> None:
        """Drop initial schema"""
        Base.metadata.drop_all(bind=session.bind)
        logger.info("Initial schema dropped")
    
    def _migration_002_up(self, session) -> None:
        """Add performance indexes"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_trend_keywords_search_volume ON trend_keywords(search_volume DESC)",
            "CREATE INDEX IF NOT EXISTS idx_keyword_analyses_potential_score ON keyword_analyses(potential_score DESC)",
            "CREATE INDEX IF NOT EXISTS idx_trends_reports_created_at ON trends_reports(created_at DESC)",
        ]
        
        for index_sql in indexes:
            session.execute(text(index_sql))
        
        logger.info("Performance indexes added")
    
    def _migration_002_down(self, session) -> None:
        """Remove performance indexes"""
        indexes = [
            "DROP INDEX IF EXISTS idx_trend_keywords_search_volume",
            "DROP INDEX IF EXISTS idx_keyword_analyses_potential_score",
            "DROP INDEX IF EXISTS idx_trends_reports_created_at",
        ]
        
        for index_sql in indexes:
            session.execute(text(index_sql))
        
        logger.info("Performance indexes removed")
    
    def _migration_003_up(self, session) -> None:
        """Add data quality and metrics tracking"""
        # Tables are already created by SQLAlchemy models
        # Add any additional constraints or triggers here
        
        # Add check constraints
        constraints = [
            """ALTER TABLE trend_keywords 
               ADD CONSTRAINT chk_search_volume_positive 
               CHECK (search_volume >= 0)""",
            """ALTER TABLE keyword_analyses 
               ADD CONSTRAINT chk_potential_score_range 
               CHECK (potential_score >= 0 AND potential_score <= 100)""",
        ]
        
        for constraint_sql in constraints:
            try:
                session.execute(text(constraint_sql))
            except SQLAlchemyError:
                # Constraint might already exist
                pass
        
        logger.info("Data quality constraints added")
    
    def _migration_003_down(self, session) -> None:
        """Remove data quality constraints"""
        constraints = [
            "ALTER TABLE trend_keywords DROP CONSTRAINT IF EXISTS chk_search_volume_positive",
            "ALTER TABLE keyword_analyses DROP CONSTRAINT IF EXISTS chk_potential_score_range",
        ]
        
        for constraint_sql in constraints:
            try:
                session.execute(text(constraint_sql))
            except SQLAlchemyError:
                pass
        
        logger.info("Data quality constraints removed")


# Global migration manager instance
migration_manager = MigrationManager()


# Convenience functions
def run_migrations() -> bool:
    """Run all pending migrations"""
    return migration_manager.migrate_up()


def rollback_migrations(target_version: str = None) -> bool:
    """Rollback migrations to target version"""
    return migration_manager.migrate_down(target_version)


def get_migration_status() -> Dict[str, Any]:
    """Get migration status"""
    return migration_manager.get_migration_status()


def reset_database() -> bool:
    """Reset database (drop and recreate all tables)"""
    try:
        logger.warning("Resetting database - all data will be lost!")
        db_manager.drop_tables()
        return migration_manager.migrate_up()
    except Exception as e:
        logger.error(f"Failed to reset database: {e}")
        return False