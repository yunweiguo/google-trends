"""
Unit tests for database models and connection management
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import (
    Base, TrendKeywordModel, KeywordDetailsModel, DomainInfoModel,
    KeywordAnalysisModel, TrendsReportModel, DataQualityLog, SystemMetrics
)
from src.database.connection import DatabaseManager
from src.database.migrations import MigrationManager


@pytest.fixture
def in_memory_db():
    """Create in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    return engine, SessionLocal


class TestDatabaseModels:
    """Test database models"""
    
    def test_trend_keyword_model(self, in_memory_db):
        """Test TrendKeywordModel creation and relationships"""
        engine, SessionLocal = in_memory_db
        
        with SessionLocal() as session:
            keyword = TrendKeywordModel(
                keyword="python programming",
                search_volume=10000,
                growth_rate=25.5,
                region="US",
                category="science_tech",
                timestamp=datetime.now(),
                related_keywords=["python", "programming", "coding"]
            )
            
            session.add(keyword)
            session.commit()
            
            # Test retrieval
            retrieved = session.query(TrendKeywordModel).filter_by(keyword="python programming").first()
            assert retrieved is not None
            assert retrieved.search_volume == 10000
            assert retrieved.growth_rate == 25.5
            assert retrieved.region == "US"
            assert retrieved.category == "science_tech"
            assert len(retrieved.related_keywords) == 3
    
    def test_keyword_details_model(self, in_memory_db):
        """Test KeywordDetailsModel creation"""
        engine, SessionLocal = in_memory_db
        
        with SessionLocal() as session:
            details = KeywordDetailsModel(
                keyword="python",
                search_volume=50000,
                interest_over_time=[
                    {"date": "2023-01-01", "value": 80},
                    {"date": "2023-01-02", "value": 85}
                ],
                related_topics=["programming", "coding"],
                related_queries=["python tutorial", "python course"],
                geo_distribution={"US": 40, "IN": 30, "GB": 15},
                timestamp=datetime.now()
            )
            
            session.add(details)
            session.commit()
            
            # Test retrieval
            retrieved = session.query(KeywordDetailsModel).filter_by(keyword="python").first()
            assert retrieved is not None
            assert retrieved.search_volume == 50000
            assert len(retrieved.interest_over_time) == 2
            assert len(retrieved.related_topics) == 2
            assert len(retrieved.related_queries) == 2
            assert "US" in retrieved.geo_distribution
    
    def test_domain_info_model(self, in_memory_db):
        """Test DomainInfoModel creation"""
        engine, SessionLocal = in_memory_db
        
        with SessionLocal() as session:
            domain = DomainInfoModel(
                domain="example.com",
                available=True,
                price=12.99,
                registrar="GoDaddy",
                alternatives=["example.net", "example.org"],
                last_checked=datetime.now()
            )
            
            session.add(domain)
            session.commit()
            
            # Test retrieval
            retrieved = session.query(DomainInfoModel).filter_by(domain="example.com").first()
            assert retrieved is not None
            assert retrieved.available is True
            assert retrieved.price == 12.99
            assert retrieved.registrar == "GoDaddy"
            assert len(retrieved.alternatives) == 2
    
    def test_keyword_analysis_model(self, in_memory_db):
        """Test KeywordAnalysisModel creation"""
        engine, SessionLocal = in_memory_db
        
        with SessionLocal() as session:
            analysis = KeywordAnalysisModel(
                keyword="python programming",
                potential_score=85.5,
                competition_level="medium",
                domain_suggestions=["python-programming.com", "learn-python.net"],
                content_ideas=["Python tutorial", "Python best practices"],
                estimated_traffic=15000,
                analysis_timestamp=datetime.now()
            )
            
            session.add(analysis)
            session.commit()
            
            # Test retrieval
            retrieved = session.query(KeywordAnalysisModel).filter_by(keyword="python programming").first()
            assert retrieved is not None
            assert retrieved.potential_score == 85.5
            assert retrieved.competition_level == "medium"
            assert len(retrieved.domain_suggestions) == 2
            assert len(retrieved.content_ideas) == 2
            assert retrieved.estimated_traffic == 15000
    
    def test_trends_report_model(self, in_memory_db):
        """Test TrendsReportModel creation and relationships"""
        engine, SessionLocal = in_memory_db
        
        with SessionLocal() as session:
            # Create analysis first
            analysis = KeywordAnalysisModel(
                keyword="python",
                potential_score=80.0,
                competition_level="medium",
                domain_suggestions=["python-guide.com"],
                content_ideas=["Python tutorial"],
                estimated_traffic=12000,
                analysis_timestamp=datetime.now()
            )
            session.add(analysis)
            session.flush()  # Get the ID
            
            # Create report
            report = TrendsReportModel(
                keyword="python",
                analysis_date=datetime.now(),
                recommendations=["Focus on tutorial content", "Target beginners"],
                analysis_id=analysis.id
            )
            
            session.add(report)
            session.commit()
            
            # Test retrieval and relationships
            retrieved = session.query(TrendsReportModel).filter_by(keyword="python").first()
            assert retrieved is not None
            assert retrieved.keyword == "python"
            assert len(retrieved.recommendations) == 2
            assert retrieved.analysis is not None
            assert retrieved.analysis.keyword == "python"
    
    def test_data_quality_log_model(self, in_memory_db):
        """Test DataQualityLog model"""
        engine, SessionLocal = in_memory_db
        
        with SessionLocal() as session:
            log = DataQualityLog(
                table_name="trend_keywords",
                record_id="123",
                issue_type="validation_error",
                issue_description="Invalid search volume",
                severity="high",
                resolved=False,
                created_at=datetime.now()
            )
            
            session.add(log)
            session.commit()
            
            # Test retrieval
            retrieved = session.query(DataQualityLog).filter_by(table_name="trend_keywords").first()
            assert retrieved is not None
            assert retrieved.issue_type == "validation_error"
            assert retrieved.severity == "high"
            assert retrieved.resolved is False
    
    def test_system_metrics_model(self, in_memory_db):
        """Test SystemMetrics model"""
        engine, SessionLocal = in_memory_db
        
        with SessionLocal() as session:
            metric = SystemMetrics(
                metric_name="api_response_time",
                metric_value=0.25,
                metric_unit="seconds",
                tags={"endpoint": "/api/trends", "method": "GET"},
                timestamp=datetime.now()
            )
            
            session.add(metric)
            session.commit()
            
            # Test retrieval
            retrieved = session.query(SystemMetrics).filter_by(metric_name="api_response_time").first()
            assert retrieved is not None
            assert retrieved.metric_value == 0.25
            assert retrieved.metric_unit == "seconds"
            assert "endpoint" in retrieved.tags


class TestDatabaseManager:
    """Test DatabaseManager class"""
    
    @patch('src.database.connection.create_engine')
    @patch('src.database.connection.sessionmaker')
    @patch('src.database.connection.event')
    def test_database_manager_initialization(self, mock_event, mock_sessionmaker, mock_create_engine):
        """Test DatabaseManager initialization"""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        mock_session_factory = Mock()
        mock_sessionmaker.return_value = mock_session_factory
        
        db_manager = DatabaseManager("postgresql://test:test@localhost/test")
        db_manager.initialize()
        
        assert db_manager._initialized is True
        assert db_manager.engine == mock_engine
        assert db_manager.SessionLocal == mock_session_factory
        
        # Verify engine was created with correct parameters
        mock_create_engine.assert_called_once()
        args, kwargs = mock_create_engine.call_args
        assert args[0] == "postgresql://test:test@localhost/test"
        assert 'poolclass' in kwargs
        assert 'pool_size' in kwargs
        
        # Verify event listeners were set up
        assert mock_event.listens_for.call_count >= 3  # connect, checkout, checkin
    
    def test_database_manager_health_check(self):
        """Test database health check"""
        # Test with in-memory database
        db_manager = DatabaseManager("sqlite:///:memory:")
        db_manager.initialize()
        db_manager.create_tables()
        
        # Health check should pass
        assert db_manager.health_check() is True
        
        # Test connection info
        info = db_manager.get_connection_info()
        assert info['status'] == 'connected'
    
    def test_database_manager_session_context(self):
        """Test database session context manager"""
        db_manager = DatabaseManager("sqlite:///:memory:")
        db_manager.initialize()
        db_manager.create_tables()
        
        # Test successful session
        with db_manager.get_session() as session:
            keyword = TrendKeywordModel(
                keyword="test",
                search_volume=1000,
                growth_rate=10.0,
                region="US",
                category="all",
                timestamp=datetime.now()
            )
            session.add(keyword)
        
        # Verify data was committed
        with db_manager.get_session() as session:
            retrieved = session.query(TrendKeywordModel).filter_by(keyword="test").first()
            assert retrieved is not None
    
    def test_database_manager_session_rollback(self):
        """Test database session rollback on error"""
        db_manager = DatabaseManager("sqlite:///:memory:")
        db_manager.initialize()
        db_manager.create_tables()
        
        # Test session rollback on exception
        with pytest.raises(Exception):
            with db_manager.get_session() as session:
                keyword = TrendKeywordModel(
                    keyword="test",
                    search_volume=1000,
                    growth_rate=10.0,
                    region="US",
                    category="all",
                    timestamp=datetime.now()
                )
                session.add(keyword)
                raise Exception("Test exception")
        
        # Verify data was not committed
        with db_manager.get_session() as session:
            retrieved = session.query(TrendKeywordModel).filter_by(keyword="test").first()
            assert retrieved is None


class TestMigrationManager:
    """Test MigrationManager class"""
    
    def test_migration_manager_initialization(self):
        """Test MigrationManager initialization"""
        manager = MigrationManager()
        
        assert len(manager.migrations) > 0
        assert all('version' in m for m in manager.migrations)
        assert all('name' in m for m in manager.migrations)
        assert all('up' in m for m in manager.migrations)
        assert all('down' in m for m in manager.migrations)
    
    def test_migration_status(self):
        """Test migration status tracking"""
        manager = MigrationManager()
        status = manager.get_migration_status()
        
        assert 'applied_count' in status
        assert 'pending_count' in status
        assert 'applied_migrations' in status
        assert 'pending_migrations' in status
        assert 'latest_version' in status
        
        # Initially, no migrations should be applied
        assert isinstance(status['applied_count'], int)
        assert isinstance(status['pending_count'], int)