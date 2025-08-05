"""
Google Trends data collection service using pytrends library
"""
import logging
import time
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from dataclasses import asdict

import pandas as pd
from pytrends.request import TrendReq
from pytrends.exceptions import ResponseError, TooManyRequestsError

from ..models.core import TrendKeyword, KeywordDetails, TrendCategory
from .interfaces import ITrendsDataService


logger = logging.getLogger(__name__)


class TrendsCollector(ITrendsDataService):
    """
    Google Trends data collector using pytrends library
    """
    
    def __init__(self, hl: str = 'en-US', tz: int = 360, timeout: int = 10):
        """
        Initialize trends collector
        
        Args:
            hl: Language code (default: 'en-US')
            tz: Timezone offset in minutes (default: 360 for US Central)
            timeout: Request timeout in seconds
        """
        self.hl = hl
        self.tz = tz
        self.timeout = timeout
        self._pytrends = None
        self._last_request_time = 0
        self._min_request_interval = 1.0  # Minimum seconds between requests
        
        logger.info(f"TrendsCollector initialized with hl={hl}, tz={tz}, timeout={timeout}")
    
    def _get_pytrends_client(self) -> TrendReq:
        """Get or create pytrends client instance"""
        if self._pytrends is None:
            try:
                self._pytrends = TrendReq(
                    hl=self.hl, 
                    tz=self.tz, 
                    timeout=self.timeout,
                    retries=2,
                    backoff_factor=0.1
                )
                logger.debug("Created new pytrends client")
            except Exception as e:
                logger.error(f"Failed to create pytrends client: {e}")
                raise
        
        return self._pytrends
    
    def _rate_limit(self) -> None:
        """Apply rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self._min_request_interval:
            sleep_time = self._min_request_interval - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self._last_request_time = time.time()
    
    def _handle_request_error(self, error: Exception, operation: str) -> None:
        """Handle and log request errors"""
        if isinstance(error, TooManyRequestsError):
            logger.warning(f"Rate limit exceeded during {operation}, backing off")
            time.sleep(60)  # Wait 1 minute on rate limit
            raise error
        elif isinstance(error, ResponseError):
            logger.error(f"Response error during {operation}: {error}")
            raise error
        else:
            logger.error(f"Unexpected error during {operation}: {error}")
            raise error
    
    def get_trending_keywords(
        self, 
        region: str = 'US', 
        timeframe: str = 'today'
    ) -> List[TrendKeyword]:
        """
        Get current trending keywords from Google Trends
        
        Args:
            region: Country code (e.g., 'US', 'GB', 'DE')
            timeframe: Time period ('today', 'today 5-y', 'today 12-m', etc.)
            
        Returns:
            List of TrendKeyword objects
        """
        logger.info(f"Getting trending keywords for region={region}, timeframe={timeframe}")
        
        try:
            self._rate_limit()
            pytrends = self._get_pytrends_client()
            
            # Get trending searches
            trending_searches = pytrends.trending_searches(pn=region)
            
            if trending_searches is None or trending_searches.empty:
                logger.warning(f"No trending searches found for region {region}")
                return []
            
            keywords = []
            current_time = datetime.now()
            
            # Convert trending searches to TrendKeyword objects
            for idx, keyword_row in trending_searches.head(20).iterrows():  # Limit to top 20
                keyword_text = str(keyword_row[0]).strip()
                
                if not keyword_text:
                    continue
                
                try:
                    # Get basic interest data for the keyword
                    interest_data = self._get_keyword_interest(keyword_text, timeframe)
                    
                    # Calculate growth rate from interest data
                    growth_rate = self._calculate_growth_rate(interest_data)
                    
                    # Estimate search volume (pytrends doesn't provide absolute numbers)
                    search_volume = self._estimate_search_volume(interest_data)
                    
                    # Get related keywords
                    related_keywords = self._get_related_keywords_simple(keyword_text)
                    
                    trend_keyword = TrendKeyword(
                        keyword=keyword_text,
                        search_volume=search_volume,
                        growth_rate=growth_rate,
                        region=region.upper(),
                        category=TrendCategory.ALL.value,
                        timestamp=current_time,
                        related_keywords=related_keywords
                    )
                    
                    keywords.append(trend_keyword)
                    logger.debug(f"Added trending keyword: {keyword_text}")
                    
                except Exception as e:
                    logger.warning(f"Failed to process keyword '{keyword_text}': {e}")
                    continue
            
            logger.info(f"Successfully retrieved {len(keywords)} trending keywords")
            return keywords
            
        except Exception as e:
            try:
                self._handle_request_error(e, "get_trending_keywords")
            except Exception:
                pass  # Error was logged, continue with empty result
            return []
    
    def get_keyword_details(self, keyword: str) -> KeywordDetails:
        """
        Get detailed information about a specific keyword
        
        Args:
            keyword: The keyword to analyze
            
        Returns:
            KeywordDetails object with comprehensive keyword data
        """
        logger.info(f"Getting detailed information for keyword: {keyword}")
        
        try:
            self._rate_limit()
            pytrends = self._get_pytrends_client()
            
            # Build payload for the keyword
            pytrends.build_payload([keyword], cat=0, timeframe='today 12-m', geo='', gprop='')
            
            # Get interest over time
            interest_over_time_df = pytrends.interest_over_time()
            interest_over_time = []
            
            if not interest_over_time_df.empty and keyword in interest_over_time_df.columns:
                for date, row in interest_over_time_df.iterrows():
                    interest_over_time.append({
                        'date': date.isoformat(),
                        'value': int(row[keyword]) if not pd.isna(row[keyword]) else 0
                    })
            
            # Get related topics
            related_topics_dict = pytrends.related_topics()
            related_topics = []
            if keyword in related_topics_dict and related_topics_dict[keyword]['top'] is not None:
                topics_df = related_topics_dict[keyword]['top']
                related_topics = topics_df['topic_title'].head(10).tolist()
            
            # Get related queries
            related_queries_dict = pytrends.related_queries()
            related_queries = []
            if keyword in related_queries_dict and related_queries_dict[keyword]['top'] is not None:
                queries_df = related_queries_dict[keyword]['top']
                related_queries = queries_df['query'].head(10).tolist()
            
            # Get geographical distribution
            geo_df = pytrends.interest_by_region(resolution='COUNTRY', inc_low_vol=True, inc_geo_code=False)
            geo_distribution = {}
            if not geo_df.empty and keyword in geo_df.columns:
                # Get top 10 countries
                top_geo = geo_df[keyword].sort_values(ascending=False).head(10)
                geo_distribution = {country: int(value) for country, value in top_geo.items() if value > 0}
            
            # Estimate search volume
            search_volume = self._estimate_search_volume(interest_over_time)
            
            keyword_details = KeywordDetails(
                keyword=keyword,
                search_volume=search_volume,
                interest_over_time=interest_over_time,
                related_topics=related_topics,
                related_queries=related_queries,
                geo_distribution=geo_distribution,
                timestamp=datetime.now()
            )
            
            logger.info(f"Successfully retrieved details for keyword: {keyword}")
            return keyword_details
            
        except Exception as e:
            self._handle_request_error(e, f"get_keyword_details for '{keyword}'")
            raise
    
    def get_related_keywords(self, keyword: str) -> List[str]:
        """
        Get keywords related to the given keyword
        
        Args:
            keyword: The base keyword
            
        Returns:
            List of related keyword strings
        """
        logger.info(f"Getting related keywords for: {keyword}")
        
        try:
            self._rate_limit()
            pytrends = self._get_pytrends_client()
            
            # Build payload for the keyword
            pytrends.build_payload([keyword], cat=0, timeframe='today 12-m', geo='', gprop='')
            
            # Get related queries
            related_queries_dict = pytrends.related_queries()
            related_keywords = []
            
            if keyword in related_queries_dict:
                # Get top related queries
                if related_queries_dict[keyword]['top'] is not None:
                    top_queries = related_queries_dict[keyword]['top']['query'].head(15).tolist()
                    related_keywords.extend(top_queries)
                
                # Get rising related queries
                if related_queries_dict[keyword]['rising'] is not None:
                    rising_queries = related_queries_dict[keyword]['rising']['query'].head(10).tolist()
                    related_keywords.extend(rising_queries)
            
            # Remove duplicates and the original keyword
            related_keywords = list(set(related_keywords))
            if keyword in related_keywords:
                related_keywords.remove(keyword)
            
            # Limit to top 20 related keywords
            related_keywords = related_keywords[:20]
            
            logger.info(f"Found {len(related_keywords)} related keywords for: {keyword}")
            return related_keywords
            
        except Exception as e:
            try:
                self._handle_request_error(e, f"get_related_keywords for '{keyword}'")
            except Exception:
                pass  # Error was logged, continue with empty result
            return []
    
    def _get_keyword_interest(self, keyword: str, timeframe: str = 'today 12-m') -> List[Dict[str, Any]]:
        """Get interest over time data for a keyword"""
        try:
            pytrends = self._get_pytrends_client()
            pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo='', gprop='')
            
            interest_df = pytrends.interest_over_time()
            interest_data = []
            
            if not interest_df.empty and keyword in interest_df.columns:
                for date, row in interest_df.iterrows():
                    interest_data.append({
                        'date': date.isoformat(),
                        'value': int(row[keyword]) if not pd.isna(row[keyword]) else 0
                    })
            
            return interest_data
            
        except Exception as e:
            logger.warning(f"Failed to get interest data for '{keyword}': {e}")
            return []
    
    def _calculate_growth_rate(self, interest_data: List[Dict[str, Any]]) -> float:
        """Calculate growth rate from interest over time data"""
        if len(interest_data) < 2:
            return 0.0
        
        try:
            # Compare last month average with previous month average
            recent_values = [item['value'] for item in interest_data[-4:]]  # Last 4 data points
            previous_values = [item['value'] for item in interest_data[-8:-4]]  # Previous 4 data points
            
            if not recent_values or not previous_values:
                return 0.0
            
            recent_avg = sum(recent_values) / len(recent_values)
            previous_avg = sum(previous_values) / len(previous_values)
            
            if previous_avg == 0:
                return 100.0 if recent_avg > 0 else 0.0
            
            growth_rate = ((recent_avg - previous_avg) / previous_avg) * 100
            return round(growth_rate, 2)
            
        except Exception as e:
            logger.warning(f"Failed to calculate growth rate: {e}")
            return 0.0
    
    def _estimate_search_volume(self, interest_data: List[Dict[str, Any]]) -> int:
        """Estimate search volume based on interest data"""
        if not interest_data:
            return 0
        
        try:
            # Get average interest value
            values = [item['value'] for item in interest_data if item['value'] > 0]
            if not values:
                return 0
            
            avg_interest = sum(values) / len(values)
            
            # Rough estimation: interest value of 100 = ~1M searches per month
            # This is a very rough approximation since Google doesn't provide absolute numbers
            estimated_monthly = int(avg_interest * 10000)  # Scale factor
            
            return max(estimated_monthly, 100)  # Minimum 100 searches
            
        except Exception as e:
            logger.warning(f"Failed to estimate search volume: {e}")
            return 1000  # Default estimate
    
    def _get_related_keywords_simple(self, keyword: str) -> List[str]:
        """Get a simple list of related keywords (used internally)"""
        try:
            # This is a simplified version to avoid too many API calls
            # In a production system, you might want to cache these results
            return []  # Return empty for now to avoid rate limiting
            
        except Exception as e:
            logger.warning(f"Failed to get simple related keywords for '{keyword}': {e}")
            return []