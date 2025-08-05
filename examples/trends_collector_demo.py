#!/usr/bin/env python3
"""
Demo script showing how to use the TrendsCollector class
"""
import sys
import os
from datetime import datetime

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.trends_collector import TrendsCollector


def main():
    """Demo the TrendsCollector functionality"""
    print("Google Trends Collector Demo")
    print("=" * 40)
    
    # Create a trends collector instance
    collector = TrendsCollector()
    
    try:
        print("\n1. Getting trending keywords for US...")
        trending_keywords = collector.get_trending_keywords('US', 'today')
        
        if trending_keywords:
            print(f"Found {len(trending_keywords)} trending keywords:")
            for i, keyword in enumerate(trending_keywords[:5], 1):  # Show top 5
                print(f"  {i}. {keyword.keyword}")
                print(f"     Search Volume: {keyword.search_volume:,}")
                print(f"     Growth Rate: {keyword.growth_rate:.1f}%")
                print(f"     Related: {', '.join(keyword.related_keywords[:3])}")
                print()
        else:
            print("No trending keywords found (might be rate limited)")
        
        print("\n2. Getting details for a specific keyword...")
        keyword_to_analyze = "artificial intelligence"
        
        try:
            details = collector.get_keyword_details(keyword_to_analyze)
            print(f"Keyword: {details.keyword}")
            print(f"Estimated Search Volume: {details.search_volume:,}")
            print(f"Interest Over Time Points: {len(details.interest_over_time)}")
            print(f"Related Topics: {len(details.related_topics)}")
            print(f"Related Queries: {len(details.related_queries)}")
            print(f"Geographic Distribution: {len(details.geo_distribution)} regions")
            
            if details.related_topics:
                print(f"Top Related Topics: {', '.join(details.related_topics[:3])}")
            
            if details.related_queries:
                print(f"Top Related Queries: {', '.join(details.related_queries[:3])}")
                
        except Exception as e:
            print(f"Error getting keyword details: {e}")
        
        print("\n3. Getting related keywords...")
        try:
            related_keywords = collector.get_related_keywords(keyword_to_analyze)
            if related_keywords:
                print(f"Found {len(related_keywords)} related keywords:")
                for keyword in related_keywords[:10]:  # Show top 10
                    print(f"  - {keyword}")
            else:
                print("No related keywords found")
                
        except Exception as e:
            print(f"Error getting related keywords: {e}")
            
    except Exception as e:
        print(f"Demo failed with error: {e}")
        print("This might be due to rate limiting or network issues.")
        print("Try running the demo again after a few minutes.")
    
    print("\nDemo completed!")


if __name__ == "__main__":
    main()