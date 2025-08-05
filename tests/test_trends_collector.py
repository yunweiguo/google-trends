"""
Unit tests for TrendsCollector class
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import pandas as pd

from src.services.trends_collector import TrendsCollector
from src.models.core import TrendKeyword, KeywordDetails, TrendCategory
from pytrends.exceptions import ResponseError, TooManyRequestsError


class TestTrendsCollector:
    """Test cases for TrendsCollector"""
    
    @pytest.fixture
    def trends_collector(self):
        """Create a TrendsCollector instance for testing"""
        return TrendsCollector(hl='en-US', tz=360, timeout=10)
    
    @pytest.fixture
    def mock_pytrends(self):
        """Create a mock pytrends client"""
        mock = Mock()
        mock.trending_searches.return_value = pd.DataFrame(['test keyword', 'another keyword'])
        mock.build_payload = Mock()
        mock.interest_over_time.return_value = pd.DataFrame()
        mock.related_topics.return_value = {}
        mock.related_queries.return_value = {}
        mock.interest_by_region.return_value = pd.DataFrame()
        return mock
    
    def test_init(self):
        """Test TrendsCollector initialization"""
        collector = TrendsCollector(hl='en-GB', tz=0, timeout=20)
        
        assert collector.hl == 'en-GB'
        assert collector.tz == 0
        assert collector.timeout == 20
        assert collector._pytrends is None
        assert collector._min_request_interval == 1.0
    
    @patch('src.services.trends_collector.TrendReq')
    def test_get_pytrends_client(self, mock_trends_req, trends_collector):
        """Test pytrends client creation"""
        mock_client = Mock()
        mock_trends_req.return_value = mock_client
        
        client = trends_collector._get_pytrends_client()
        
        assert client == mock_client
        assert trends_collector._pytrends == mock_client
        mock_trends_req.assert_called_once_with(
            hl='en-US',
            tz=360,
            timeout=10,
            retries=2,
            backoff_factor=0.1
        )
    
    @patch('src.services.trends_collector.time.sleep')
    @patch('src.services.trends_collector.time.time')
    def test_rate_limit(self, mock_time, mock_sleep, trends_collector):
        """Test rate limiting functionality"""
        # Simulate time progression: current time at start, final time after sleep
        mock_time.side_effect = [0.5, 1.5]  # current_time, final time
        
        trends_collector._last_request_time = 0  # Last request was at time 0
        trends_collector._rate_limit()
        
        # time_since_last = 0.5 - 0 = 0.5
        # sleep_time = 1.0 - 0.5 = 0.5
        mock_sleep.assert_called_once_with(0.5)
        assert trends_collector._last_request_time == 1.5
    
    def test_handle_request_error_too_many_requests(self, trends_collector):
        """Test handling of TooManyRequestsError"""
        mock_response = Mock()
        error = TooManyRequestsError("Rate limit exceeded", mock_response)
        
        with patch('src.services.trends_collector.time.sleep') as mock_sleep:
            with pytest.raises(TooManyRequestsError):
                trends_collector._handle_request_error(error, "test_operation")
            
            mock_sleep.assert_called_once_with(60)
    
    def test_handle_request_error_response_error(self, trends_collector):
        """Test handling of ResponseError"""
        mock_response = Mock()
        error = ResponseError("Invalid response", mock_response)
        
        with pytest.raises(ResponseError):
            trends_collector._handle_request_error(error, "test_operation")
    
    def test_handle_request_error_generic(self, trends_collector):
        """Test handling of generic errors"""
        error = Exception("Generic error")
        
        with pytest.raises(Exception):
            trends_collector._handle_request_error(error, "test_operation")
    
    @patch('src.services.trends_collector.TrendsCollector._get_pytrends_client')
    @patch('src.services.trends_collector.TrendsCollector._rate_limit')
    def test_get_trending_keywords_success(self, mock_rate_limit, mock_get_client, trends_collector):
        """Test successful retrieval of trending keywords"""
        # Setup mock data
        mock_client = Mock()
        trending_df = pd.DataFrame(['artificial intelligence', 'climate change'])
        mock_client.trending_searches.return_value = trending_df
        mock_get_client.return_value = mock_client
        
        # Mock the internal methods
        with patch.object(trends_collector, '_get_keyword_interest') as mock_interest:
            with patch.object(trends_collector, '_calculate_growth_rate') as mock_growth:
                with patch.object(trends_collector, '_estimate_search_volume') as mock_volume:
                    with patch.object(trends_collector, '_get_related_keywords_simple') as mock_related:
                        
                        mock_interest.return_value = [{'date': '2023-01-01', 'value': 50}]
                        mock_growth.return_value = 15.5
                        mock_volume.return_value = 10000
                        mock_related.return_value = ['AI', 'machine learning']
                        
                        result = trends_collector.get_trending_keywords('US', 'today')
                        
                        assert len(result) == 2
                        assert all(isinstance(kw, TrendKeyword) for kw in result)
                        assert result[0].keyword == 'artificial intelligence'
                        assert result[0].region == 'US'
                        assert result[0].growth_rate == 15.5
                        assert result[0].search_volume == 10000
    
    @patch('src.services.trends_collector.TrendsCollector._get_pytrends_client')
    @patch('src.services.trends_collector.TrendsCollector._rate_limit')
    def test_get_trending_keywords_empty_result(self, mock_rate_limit, mock_get_client, trends_collector):
        """Test handling of empty trending searches result"""
        mock_client = Mock()
        mock_client.trending_searches.return_value = pd.DataFrame()  # Empty DataFrame
        mock_get_client.return_value = mock_client
        
        result = trends_collector.get_trending_keywords('US', 'today')
        
        assert result == []
    
    @patch('src.services.trends_collector.TrendsCollector._get_pytrends_client')
    @patch('src.services.trends_collector.TrendsCollector._rate_limit')
    def test_get_trending_keywords_none_result(self, mock_rate_limit, mock_get_client, trends_collector):
        """Test handling of None result from trending searches"""
        mock_client = Mock()
        mock_client.trending_searches.return_value = None
        mock_get_client.return_value = mock_client
        
        result = trends_collector.get_trending_keywords('US', 'today')
        
        assert result == []
    
    @patch('src.services.trends_collector.TrendsCollector._get_pytrends_client')
    @patch('src.services.trends_collector.TrendsCollector._rate_limit')
    def test_get_keyword_details_success(self, mock_rate_limit, mock_get_client, trends_collector):
        """Test successful retrieval of keyword details"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        # Mock interest over time data
        interest_df = pd.DataFrame({
            'test keyword': [50, 60, 70, 80],
            'isPartial': [False, False, False, True]
        }, index=pd.date_range('2023-01-01', periods=4, freq='W'))
        mock_client.interest_over_time.return_value = interest_df
        
        # Mock related topics
        topics_df = pd.DataFrame({
            'topic_title': ['Topic 1', 'Topic 2'],
            'value': [100, 80]
        })
        mock_client.related_topics.return_value = {'test keyword': {'top': topics_df}}
        
        # Mock related queries
        queries_df = pd.DataFrame({
            'query': ['related query 1', 'related query 2'],
            'value': [100, 90]
        })
        mock_client.related_queries.return_value = {'test keyword': {'top': queries_df}}
        
        # Mock geographical data
        geo_df = pd.DataFrame({
            'test keyword': [100, 80, 60]
        }, index=['United States', 'Canada', 'United Kingdom'])
        mock_client.interest_by_region.return_value = geo_df
        
        result = trends_collector.get_keyword_details('test keyword')
        
        assert isinstance(result, KeywordDetails)
        assert result.keyword == 'test keyword'
        assert len(result.interest_over_time) == 4
        assert len(result.related_topics) == 2
        assert len(result.related_queries) == 2
        assert 'United States' in result.geo_distribution
    
    @patch('src.services.trends_collector.TrendsCollector._get_pytrends_client')
    @patch('src.services.trends_collector.TrendsCollector._rate_limit')
    def test_get_related_keywords_success(self, mock_rate_limit, mock_get_client, trends_collector):
        """Test successful retrieval of related keywords"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        # Mock related queries data
        top_queries_df = pd.DataFrame({
            'query': ['related 1', 'related 2', 'test keyword'],  # Include original keyword
            'value': [100, 90, 85]
        })
        rising_queries_df = pd.DataFrame({
            'query': ['rising 1', 'rising 2'],
            'value': [200, 150]
        })
        
        mock_client.related_queries.return_value = {
            'test keyword': {
                'top': top_queries_df,
                'rising': rising_queries_df
            }
        }
        
        result = trends_collector.get_related_keywords('test keyword')
        
        assert isinstance(result, list)
        assert len(result) == 4  # Should exclude the original keyword
        assert 'related 1' in result
        assert 'related 2' in result
        assert 'rising 1' in result
        assert 'rising 2' in result
        assert 'test keyword' not in result  # Original keyword should be removed
    
    def test_calculate_growth_rate_normal(self, trends_collector):
        """Test growth rate calculation with normal data"""
        interest_data = [
            {'date': '2023-01-01', 'value': 40},
            {'date': '2023-01-08', 'value': 45},
            {'date': '2023-01-15', 'value': 50},
            {'date': '2023-01-22', 'value': 55},
            {'date': '2023-01-29', 'value': 60},
            {'date': '2023-02-05', 'value': 65},
            {'date': '2023-02-12', 'value': 70},
            {'date': '2023-02-19', 'value': 75}
        ]
        
        growth_rate = trends_collector._calculate_growth_rate(interest_data)
        
        # Recent average (last 4): (60+65+70+75)/4 = 67.5
        # Previous average (4 before): (40+45+50+55)/4 = 47.5
        # Growth: ((67.5-47.5)/47.5)*100 = 42.11%
        assert abs(growth_rate - 42.11) < 0.1
    
    def test_calculate_growth_rate_insufficient_data(self, trends_collector):
        """Test growth rate calculation with insufficient data"""
        interest_data = [{'date': '2023-01-01', 'value': 50}]
        
        growth_rate = trends_collector._calculate_growth_rate(interest_data)
        
        assert growth_rate == 0.0
    
    def test_calculate_growth_rate_zero_previous(self, trends_collector):
        """Test growth rate calculation when previous average is zero"""
        interest_data = [
            {'date': '2023-01-01', 'value': 0},
            {'date': '2023-01-08', 'value': 0},
            {'date': '2023-01-15', 'value': 0},
            {'date': '2023-01-22', 'value': 0},
            {'date': '2023-01-29', 'value': 50},
            {'date': '2023-02-05', 'value': 60},
            {'date': '2023-02-12', 'value': 70},
            {'date': '2023-02-19', 'value': 80}
        ]
        
        growth_rate = trends_collector._calculate_growth_rate(interest_data)
        
        assert growth_rate == 100.0
    
    def test_estimate_search_volume_normal(self, trends_collector):
        """Test search volume estimation with normal data"""
        interest_data = [
            {'date': '2023-01-01', 'value': 50},
            {'date': '2023-01-08', 'value': 60},
            {'date': '2023-01-15', 'value': 70}
        ]
        
        volume = trends_collector._estimate_search_volume(interest_data)
        
        # Average interest: (50+60+70)/3 = 60
        # Estimated volume: 60 * 10000 = 600000
        assert volume == 600000
    
    def test_estimate_search_volume_empty_data(self, trends_collector):
        """Test search volume estimation with empty data"""
        interest_data = []
        
        volume = trends_collector._estimate_search_volume(interest_data)
        
        assert volume == 0
    
    def test_estimate_search_volume_zero_values(self, trends_collector):
        """Test search volume estimation with all zero values"""
        interest_data = [
            {'date': '2023-01-01', 'value': 0},
            {'date': '2023-01-08', 'value': 0}
        ]
        
        volume = trends_collector._estimate_search_volume(interest_data)
        
        assert volume == 0
    
    def test_estimate_search_volume_minimum(self, trends_collector):
        """Test search volume estimation returns minimum value"""
        interest_data = [
            {'date': '2023-01-01', 'value': 1}  # Very low interest
        ]
        
        volume = trends_collector._estimate_search_volume(interest_data)
        
        # Should return at least 100 (minimum)
        assert volume >= 100
    
    @patch('src.services.trends_collector.TrendsCollector._get_pytrends_client')
    @patch('src.services.trends_collector.TrendsCollector._rate_limit')
    def test_error_handling_in_get_trending_keywords(self, mock_rate_limit, mock_get_client, trends_collector):
        """Test error handling in get_trending_keywords"""
        mock_client = Mock()
        mock_response = Mock()
        mock_client.trending_searches.side_effect = ResponseError("API Error", mock_response)
        mock_get_client.return_value = mock_client
        
        # The method should return empty list when error handling catches the exception
        result = trends_collector.get_trending_keywords('US', 'today')
        assert result == []
    
    @patch('src.services.trends_collector.TrendsCollector._get_pytrends_client')
    @patch('src.services.trends_collector.TrendsCollector._rate_limit')
    def test_error_handling_in_get_keyword_details(self, mock_rate_limit, mock_get_client, trends_collector):
        """Test error handling in get_keyword_details"""
        mock_client = Mock()
        mock_response = Mock()
        mock_client.build_payload.side_effect = ResponseError("API Error", mock_response)
        mock_get_client.return_value = mock_client
        
        with patch.object(trends_collector, '_handle_request_error') as mock_handle_error:
            mock_response = Mock()
            mock_handle_error.side_effect = ResponseError("API Error", mock_response)
            
            with pytest.raises(ResponseError):
                trends_collector.get_keyword_details('test keyword')
            
            mock_handle_error.assert_called_once()
    
    @patch('src.services.trends_collector.TrendsCollector._get_pytrends_client')
    @patch('src.services.trends_collector.TrendsCollector._rate_limit')
    def test_error_handling_in_get_related_keywords(self, mock_rate_limit, mock_get_client, trends_collector):
        """Test error handling in get_related_keywords"""
        mock_client = Mock()
        mock_response = Mock()
        mock_client.build_payload.side_effect = TooManyRequestsError("Rate limit", mock_response)
        mock_get_client.return_value = mock_client
        
        # The method should return empty list when error handling catches the exception
        result = trends_collector.get_related_keywords('test keyword')
        assert result == []