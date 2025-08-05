"""
Database package for Google Trends Website Builder

This package provides database models, connection management, and migration utilities.
"""

from .models import (
    Base,
    TrendKeywordModel,
    KeywordDetailsModel,
    DomainInfoModel,
    KeywordAnalysisModel,
    TrendsReportModel,
    DataQualityLog,
    SystemMetrics
)

from .connection import (
    DatabaseManager,
    db_manager,
    get_db_session,
    init_database,
    check_database_health,
    get_database_dependency
)

from .migrations import (
    MigrationManager,
    migration_manager,
    run_migrations,
    rollback_migrations,
    get_migration_status,
    reset_database
)

__all__ = [
    # Models
    'Base',
    'TrendKeywordModel',
    'KeywordDetailsModel', 
    'DomainInfoModel',
    'KeywordAnalysisModel',
    'TrendsReportModel',
    'DataQualityLog',
    'SystemMetrics',
    
    # Connection management
    'DatabaseManager',
    'db_manager',
    'get_db_session',
    'init_database',
    'check_database_health',
    'get_database_dependency',
    
    # Migrations
    'MigrationManager',
    'migration_manager',
    'run_migrations',
    'rollback_migrations',
    'get_migration_status',
    'reset_database'
]