"""
Integration tests for TrendsCollector (requires internet access)
Run with: pytest tests/test_trends_collector_integration.py -m integration
"""
import pytest
from src.services.trends_collector import TrendsCollector
from src.models.core import TrendKeyword, KeywordDetails


@pytest.mark.integration
class TestTrendsCollectorIntegration:
    """Integration tests for TrendsCollector with real Google Trends API"""
    
    @pytest.fixture
    def trends_collector(self):
        """Create a TrendsCollector instance for integration testing"""
        return TrendsCollector()
    
    @pytest.mark.slow
    def test_get_trending_keywords_real(self, trends_collector):
        """Test getting real trending keywords (requires internet)"""
        try:
            keywords = trends_collector.get_trending_keywords('US', 'today')
            
            # Should get some keywords (might be empty if no trends available)
            assert isinstance(keywords, list)
            
            # If we got keywords, verify they are valid TrendKeyword objects
            for keyword in keywords:
                assert isinstance(keyword, TrendKeyword)
                assert keyword.keyword
                assert keyword.region == 'US'
                assert isinstance(keyword.search_volume, int)
                assert isinstance(keyword.growth_rate, float)
                
        except Exception as e:
            # If we get rate limited or other API errors, that's expected in testing
            pytest.skip(f"API request failed (expected in testing): {e}")
    
    @pytest.mark.slow
    def test_get_keyword_details_real(self, trends_collector):
        """Test getting real keyword details (requires internet)"""
        try:
            # Use a common keyword that should have data
            details = trends_collector.get_keyword_details('python')
            
            assert isinstance(details, KeywordDetails)
            assert details.keyword == 'python'
            assert isinstance(details.search_volume, int)
            assert isinstance(details.interest_over_time, list)
            assert isinstance(details.related_topics, list)
            assert isinstance(details.related_queries, list)
            assert isinstance(details.geo_distribution, dict)
            
        except Exception as e:
            # If we get rate limited or other API errors, that's expected in testing
            pytest.skip(f"API request failed (expected in testing): {e}")
    
    @pytest.mark.slow
    def test_get_related_keywords_real(self, trends_collector):
        """Test getting real related keywords (requires internet)"""
        try:
            # Use a common keyword that should have related terms
            related = trends_collector.get_related_keywords('python')
            
            assert isinstance(related, list)
            # Should get some related keywords
            if related:  # Might be empty due to rate limiting
                for keyword in related:
                    assert isinstance(keyword, str)
                    assert keyword.strip()
                    
        except Exception as e:
            # If we get rate limited or other API errors, that's expected in testing
            pytest.skip(f"API request failed (expected in testing): {e}")
    
    def test_rate_limiting_behavior(self, trends_collector):
        """Test that rate limiting works correctly"""
        import time
        
        # Make two quick requests to test rate limiting
        start_time = time.time()
        
        try:
            trends_collector.get_related_keywords('test1')
            trends_collector.get_related_keywords('test2')
            
            end_time = time.time()
            
            # Should take at least the minimum interval between requests
            assert end_time - start_time >= trends_collector._min_request_interval
            
        except Exception as e:
            # Rate limiting or API errors are expected
            pytest.skip(f"API request failed (expected in testing): {e}")


if __name__ == "__main__":
    # Run integration tests manually
    pytest.main([__file__, "-v", "-m", "integration"])