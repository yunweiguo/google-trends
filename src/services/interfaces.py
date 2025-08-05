"""
Core service interfaces defining system boundaries
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from ..models.core import (
    TrendKeyword, 
    KeywordDetails, 
    KeywordAnalysis, 
    DomainInfo,
    TrendsReport
)


class ITrendsDataService(ABC):
    """Interface for trends data collection service"""
    
    @abstractmethod
    def get_trending_keywords(
        self, 
        region: str = 'US', 
        timeframe: str = 'today'
    ) -> List[TrendKeyword]:
        """Get current trending keywords"""
        pass
    
    @abstractmethod
    def get_keyword_details(self, keyword: str) -> KeywordDetails:
        """Get detailed information about a specific keyword"""
        pass
    
    @abstractmethod
    def get_related_keywords(self, keyword: str) -> List[str]:
        """Get keywords related to the given keyword"""
        pass


class IAnalysisService(ABC):
    """Interface for keyword analysis service"""
    
    @abstractmethod
    def analyze_keyword_potential(self, keyword: str) -> KeywordAnalysis:
        """Analyze the commercial potential of a keyword"""
        pass
    
    @abstractmethod
    def check_domain_availability(self, keyword: str) -> List[DomainInfo]:
        """Check domain availability for keyword-based domains"""
        pass
    
    @abstractmethod
    def calculate_competition_score(self, keyword: str) -> float:
        """Calculate competition score for a keyword"""
        pass


class IDataRepository(ABC):
    """Interface for data storage operations"""
    
    @abstractmethod
    def save_trend_keyword(self, keyword: TrendKeyword) -> bool:
        """Save a trend keyword to storage"""
        pass
    
    @abstractmethod
    def get_trend_keywords(
        self, 
        region: Optional[str] = None,
        limit: int = 100
    ) -> List[TrendKeyword]:
        """Retrieve trend keywords from storage"""
        pass
    
    @abstractmethod
    def save_analysis_result(self, analysis: KeywordAnalysis) -> bool:
        """Save analysis results to storage"""
        pass
    
    @abstractmethod
    def get_analysis_result(self, keyword: str) -> Optional[KeywordAnalysis]:
        """Get analysis results for a keyword"""
        pass


class ICacheService(ABC):
    """Interface for caching service"""
    
    @abstractmethod
    def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: str, ttl: int = 3600) -> bool:
        """Set value in cache with TTL"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        pass


class IRateLimiter(ABC):
    """Interface for rate limiting service"""
    
    @abstractmethod
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed for identifier"""
        pass
    
    @abstractmethod
    def record_request(self, identifier: str) -> None:
        """Record a request for rate limiting"""
        pass
    
    @abstractmethod
    def get_remaining_requests(self, identifier: str) -> int:
        """Get remaining requests for identifier"""
        pass