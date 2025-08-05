"""
Core data models for Google Trends Website Builder
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
import re
import uuid


class CompetitionLevel(Enum):
    """Competition level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TrendCategory(Enum):
    """Trend category enumeration"""
    ALL = "all"
    BUSINESS = "business"
    ENTERTAINMENT = "entertainment"
    HEALTH = "health"
    SCIENCE_TECH = "science_tech"
    SPORTS = "sports"
    TOP_STORIES = "top_stories"


def validate_keyword(keyword: str) -> str:
    """Validate and clean keyword input"""
    if not keyword or not isinstance(keyword, str):
        raise ValueError("Keyword must be a non-empty string")
    
    cleaned = keyword.strip()
    if not cleaned:
        raise ValueError("Keyword cannot be empty or whitespace only")
    
    if len(cleaned) > 100:
        raise ValueError("Keyword cannot exceed 100 characters")
    
    # Check for invalid characters
    if re.search(r'[<>"\']', cleaned):
        raise ValueError("Keyword contains invalid characters")
    
    return cleaned


def validate_region(region: str) -> str:
    """Validate region code"""
    if not region or not isinstance(region, str):
        raise ValueError("Region must be a non-empty string")
    
    region = region.upper().strip()
    if not re.match(r'^[A-Z]{2}$', region):
        raise ValueError("Region must be a valid 2-letter country code")
    
    return region


def validate_search_volume(volume: int) -> int:
    """Validate search volume"""
    if not isinstance(volume, int):
        raise ValueError("Search volume must be an integer")
    
    if volume < 0:
        raise ValueError("Search volume cannot be negative")
    
    if volume > 1000000000:  # 1 billion max
        raise ValueError("Search volume exceeds maximum allowed value")
    
    return volume


def validate_growth_rate(rate: float) -> float:
    """Validate growth rate percentage"""
    if not isinstance(rate, (int, float)):
        raise ValueError("Growth rate must be a number")
    
    if rate < -100:
        raise ValueError("Growth rate cannot be less than -100%")
    
    if rate > 10000:  # 10000% max growth
        raise ValueError("Growth rate exceeds maximum allowed value")
    
    return float(rate)


def validate_potential_score(score: float) -> float:
    """Validate potential score (0-100)"""
    if not isinstance(score, (int, float)):
        raise ValueError("Potential score must be a number")
    
    if not 0 <= score <= 100:
        raise ValueError("Potential score must be between 0 and 100")
    
    return float(score)


@dataclass
class TrendKeyword:
    """Represents a trending keyword with its metadata"""
    keyword: str
    search_volume: int
    growth_rate: float
    region: str
    category: str
    timestamp: datetime
    related_keywords: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate data after initialization"""
        self.keyword = validate_keyword(self.keyword)
        self.search_volume = validate_search_volume(self.search_volume)
        self.growth_rate = validate_growth_rate(self.growth_rate)
        self.region = validate_region(self.region)
        
        # Validate category
        if self.category not in [cat.value for cat in TrendCategory]:
            raise ValueError(f"Invalid category: {self.category}")
        
        # Validate timestamp
        if not isinstance(self.timestamp, datetime):
            raise ValueError("Timestamp must be a datetime object")
        
        # Validate related keywords
        if not isinstance(self.related_keywords, list):
            raise ValueError("Related keywords must be a list")
        
        # Clean and validate each related keyword
        validated_keywords = []
        for kw in self.related_keywords:
            try:
                validated_keywords.append(validate_keyword(kw))
            except ValueError:
                continue  # Skip invalid keywords
        self.related_keywords = validated_keywords
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'keyword': self.keyword,
            'search_volume': self.search_volume,
            'growth_rate': self.growth_rate,
            'region': self.region,
            'category': self.category,
            'timestamp': self.timestamp.isoformat(),
            'related_keywords': self.related_keywords
        }


@dataclass
class KeywordDetails:
    """Detailed information about a specific keyword"""
    keyword: str
    search_volume: int
    interest_over_time: List[Dict[str, Any]]
    related_topics: List[str]
    related_queries: List[str]
    geo_distribution: Dict[str, Any]
    timestamp: datetime
    
    def __post_init__(self):
        """Validate keyword details data"""
        self.keyword = validate_keyword(self.keyword)
        self.search_volume = validate_search_volume(self.search_volume)
        
        # Validate timestamp
        if not isinstance(self.timestamp, datetime):
            raise ValueError("Timestamp must be a datetime object")
        
        # Validate interest over time data
        if not isinstance(self.interest_over_time, list):
            raise ValueError("Interest over time must be a list")
        
        for item in self.interest_over_time:
            if not isinstance(item, dict):
                raise ValueError("Interest over time items must be dictionaries")
            if 'date' not in item or 'value' not in item:
                raise ValueError("Interest over time items must have 'date' and 'value' keys")
        
        # Validate related topics and queries
        if not isinstance(self.related_topics, list):
            raise ValueError("Related topics must be a list")
        if not isinstance(self.related_queries, list):
            raise ValueError("Related queries must be a list")
        if not isinstance(self.geo_distribution, dict):
            raise ValueError("Geo distribution must be a dictionary")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'keyword': self.keyword,
            'search_volume': self.search_volume,
            'interest_over_time': self.interest_over_time,
            'related_topics': self.related_topics,
            'related_queries': self.related_queries,
            'geo_distribution': self.geo_distribution,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class DomainInfo:
    """Information about domain availability and suggestions"""
    domain: str
    available: bool
    price: Optional[float] = None
    registrar: Optional[str] = None
    alternatives: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate domain information"""
        if not self.domain or not isinstance(self.domain, str):
            raise ValueError("Domain must be a non-empty string")
        
        # Basic domain validation
        domain_pattern = r'^[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.[a-zA-Z]{2,}$'
        if not re.match(domain_pattern, self.domain.strip()):
            raise ValueError("Invalid domain format")
        
        self.domain = self.domain.strip().lower()
        
        if not isinstance(self.available, bool):
            raise ValueError("Available must be a boolean")
        
        if self.price is not None:
            if not isinstance(self.price, (int, float)) or self.price < 0:
                raise ValueError("Price must be a non-negative number")
        
        if not isinstance(self.alternatives, list):
            raise ValueError("Alternatives must be a list")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'domain': self.domain,
            'available': self.available,
            'price': self.price,
            'registrar': self.registrar,
            'alternatives': self.alternatives
        }


@dataclass
class KeywordAnalysis:
    """Analysis results for a keyword"""
    keyword: str
    potential_score: float
    competition_level: CompetitionLevel
    domain_suggestions: List[str]
    content_ideas: List[str]
    estimated_traffic: int
    analysis_timestamp: datetime
    
    def __post_init__(self):
        """Validate analysis data"""
        self.keyword = validate_keyword(self.keyword)
        self.potential_score = validate_potential_score(self.potential_score)
        
        # Validate competition level
        if not isinstance(self.competition_level, CompetitionLevel):
            if isinstance(self.competition_level, str):
                try:
                    self.competition_level = CompetitionLevel(self.competition_level.lower())
                except ValueError:
                    raise ValueError(f"Invalid competition level: {self.competition_level}")
            else:
                raise ValueError("Competition level must be a CompetitionLevel enum")
        
        # Validate estimated traffic
        if not isinstance(self.estimated_traffic, int) or self.estimated_traffic < 0:
            raise ValueError("Estimated traffic must be a non-negative integer")
        
        # Validate timestamp
        if not isinstance(self.analysis_timestamp, datetime):
            raise ValueError("Analysis timestamp must be a datetime object")
        
        # Validate lists
        if not isinstance(self.domain_suggestions, list):
            raise ValueError("Domain suggestions must be a list")
        if not isinstance(self.content_ideas, list):
            raise ValueError("Content ideas must be a list")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'keyword': self.keyword,
            'potential_score': self.potential_score,
            'competition_level': self.competition_level.value,
            'domain_suggestions': self.domain_suggestions,
            'content_ideas': self.content_ideas,
            'estimated_traffic': self.estimated_traffic,
            'analysis_timestamp': self.analysis_timestamp.isoformat()
        }


@dataclass
class TrendsReport:
    """Complete trends analysis report"""
    id: str
    keyword: str
    analysis_date: datetime
    trend_data: List[TrendKeyword]
    analysis_results: KeywordAnalysis
    recommendations: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate report data"""
        # Generate ID if not provided
        if not self.id:
            self.id = str(uuid.uuid4())
        elif not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("Report ID must be a non-empty string")
        
        self.keyword = validate_keyword(self.keyword)
        
        # Validate analysis date
        if not isinstance(self.analysis_date, datetime):
            raise ValueError("Analysis date must be a datetime object")
        
        # Validate trend data
        if not isinstance(self.trend_data, list):
            raise ValueError("Trend data must be a list")
        
        for trend in self.trend_data:
            if not isinstance(trend, TrendKeyword):
                raise ValueError("All trend data items must be TrendKeyword instances")
        
        # Validate analysis results
        if not isinstance(self.analysis_results, KeywordAnalysis):
            raise ValueError("Analysis results must be a KeywordAnalysis instance")
        
        # Validate recommendations
        if not isinstance(self.recommendations, list):
            raise ValueError("Recommendations must be a list")
        
        # Ensure keyword consistency
        if self.keyword != self.analysis_results.keyword:
            raise ValueError("Report keyword must match analysis results keyword")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'keyword': self.keyword,
            'analysis_date': self.analysis_date.isoformat(),
            'trend_data': [trend.to_dict() for trend in self.trend_data],
            'analysis_results': self.analysis_results.to_dict(),
            'recommendations': self.recommendations
        }
    
    def add_recommendation(self, recommendation: str) -> None:
        """Add a recommendation to the report"""
        if not recommendation or not isinstance(recommendation, str):
            raise ValueError("Recommendation must be a non-empty string")
        
        recommendation = recommendation.strip()
        if recommendation and recommendation not in self.recommendations:
            self.recommendations.append(recommendation)