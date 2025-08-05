"""
SQLAlchemy database models for Google Trends Website Builder
"""
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, Boolean,
    ForeignKey, JSON, Index, UniqueConstraint
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()


class TrendKeywordModel(Base):
    """Database model for trending keywords"""
    __tablename__ = 'trend_keywords'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    keyword = Column(String(100), nullable=False, index=True)
    search_volume = Column(Integer, nullable=False, default=0)
    growth_rate = Column(Float, nullable=False, default=0.0)
    region = Column(String(2), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    related_keywords = Column(JSON, nullable=True)
    
    # Relationships
    analyses = relationship("KeywordAnalysisModel", back_populates="keyword_ref")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_keyword_region_timestamp', 'keyword', 'region', 'timestamp'),
        Index('idx_category_timestamp', 'category', 'timestamp'),
        UniqueConstraint('keyword', 'region', 'timestamp', name='uq_keyword_region_time'),
    )
    
    def __repr__(self):
        return f"<TrendKeyword(keyword='{self.keyword}', region='{self.region}', volume={self.search_volume})>"


class KeywordDetailsModel(Base):
    """Database model for detailed keyword information"""
    __tablename__ = 'keyword_details'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    keyword = Column(String(100), nullable=False, index=True)
    search_volume = Column(Integer, nullable=False, default=0)
    interest_over_time = Column(JSON, nullable=True)
    related_topics = Column(JSON, nullable=True)
    related_queries = Column(JSON, nullable=True)
    geo_distribution = Column(JSON, nullable=True)
    timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    
    __table_args__ = (
        Index('idx_keyword_details_timestamp', 'keyword', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<KeywordDetails(keyword='{self.keyword}', volume={self.search_volume})>"


class DomainInfoModel(Base):
    """Database model for domain information"""
    __tablename__ = 'domain_info'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    domain = Column(String(255), nullable=False, unique=True, index=True)
    available = Column(Boolean, nullable=False, default=False)
    price = Column(Float, nullable=True)
    registrar = Column(String(100), nullable=True)
    alternatives = Column(JSON, nullable=True)
    last_checked = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    
    def __repr__(self):
        return f"<DomainInfo(domain='{self.domain}', available={self.available})>"


class KeywordAnalysisModel(Base):
    """Database model for keyword analysis results"""
    __tablename__ = 'keyword_analyses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    keyword = Column(String(100), nullable=False, index=True)
    potential_score = Column(Float, nullable=False, default=0.0)
    competition_level = Column(String(20), nullable=False, index=True)
    domain_suggestions = Column(JSON, nullable=True)
    content_ideas = Column(JSON, nullable=True)
    estimated_traffic = Column(Integer, nullable=False, default=0)
    analysis_timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    
    # Foreign key to trend keyword
    trend_keyword_id = Column(Integer, ForeignKey('trend_keywords.id'), nullable=True)
    keyword_ref = relationship("TrendKeywordModel", back_populates="analyses")
    
    # Relationships
    reports = relationship("TrendsReportModel", back_populates="analysis")
    
    __table_args__ = (
        Index('idx_keyword_analysis_timestamp', 'keyword', 'analysis_timestamp'),
        Index('idx_competition_score', 'competition_level', 'potential_score'),
    )
    
    def __repr__(self):
        return f"<KeywordAnalysis(keyword='{self.keyword}', score={self.potential_score})>"


class TrendsReportModel(Base):
    """Database model for trends reports"""
    __tablename__ = 'trends_reports'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    keyword = Column(String(100), nullable=False, index=True)
    analysis_date = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    recommendations = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Foreign key to analysis
    analysis_id = Column(Integer, ForeignKey('keyword_analyses.id'), nullable=False)
    analysis = relationship("KeywordAnalysisModel", back_populates="reports")
    
    __table_args__ = (
        Index('idx_report_keyword_date', 'keyword', 'analysis_date'),
    )
    
    def __repr__(self):
        return f"<TrendsReport(id='{self.id}', keyword='{self.keyword}')>"


class DataQualityLog(Base):
    """Database model for tracking data quality issues"""
    __tablename__ = 'data_quality_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    table_name = Column(String(100), nullable=False, index=True)
    record_id = Column(String(100), nullable=False)
    issue_type = Column(String(50), nullable=False, index=True)
    issue_description = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False, default='medium', index=True)
    resolved = Column(Boolean, nullable=False, default=False, index=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    resolved_at = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index('idx_quality_table_severity', 'table_name', 'severity', 'resolved'),
    )
    
    def __repr__(self):
        return f"<DataQualityLog(table='{self.table_name}', issue='{self.issue_type}')>"


class SystemMetrics(Base):
    """Database model for system performance metrics"""
    __tablename__ = 'system_metrics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(20), nullable=True)
    tags = Column(JSON, nullable=True)
    timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    
    __table_args__ = (
        Index('idx_metrics_name_timestamp', 'metric_name', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<SystemMetrics(name='{self.metric_name}', value={self.metric_value})>"