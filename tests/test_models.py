"""
Unit tests for core data models
"""
import pytest
from datetime import datetime
from src.models.core import (
    TrendKeyword, KeywordDetails, DomainInfo, KeywordAnalysis, TrendsReport,
    CompetitionLevel, TrendCategory,
    validate_keyword, validate_region, validate_search_volume,
    validate_growth_rate, validate_potential_score
)


class TestValidationFunctions:
    """Test validation utility functions"""
    
    def test_validate_keyword_valid(self):
        """Test valid keyword validation"""
        assert validate_keyword("python programming") == "python programming"
        assert validate_keyword("  AI  ") == "AI"
        assert validate_keyword("machine-learning") == "machine-learning"
    
    def test_validate_keyword_invalid(self):
        """Test invalid keyword validation"""
        with pytest.raises(ValueError, match="Keyword must be a non-empty string"):
            validate_keyword("")
        
        with pytest.raises(ValueError, match="Keyword cannot be empty"):
            validate_keyword("   ")
        
        with pytest.raises(ValueError, match="Keyword cannot exceed 100 characters"):
            validate_keyword("a" * 101)
        
        with pytest.raises(ValueError, match="Keyword contains invalid characters"):
            validate_keyword("test<script>")
    
    def test_validate_region_valid(self):
        """Test valid region validation"""
        assert validate_region("us") == "US"
        assert validate_region("CN") == "CN"
        assert validate_region("  gb  ") == "GB"
    
    def test_validate_region_invalid(self):
        """Test invalid region validation"""
        with pytest.raises(ValueError, match="Region must be a non-empty string"):
            validate_region("")
        
        with pytest.raises(ValueError, match="Region must be a valid 2-letter country code"):
            validate_region("USA")
        
        with pytest.raises(ValueError, match="Region must be a valid 2-letter country code"):
            validate_region("1A")
    
    def test_validate_search_volume_valid(self):
        """Test valid search volume validation"""
        assert validate_search_volume(0) == 0
        assert validate_search_volume(1000) == 1000
        assert validate_search_volume(1000000) == 1000000
    
    def test_validate_search_volume_invalid(self):
        """Test invalid search volume validation"""
        with pytest.raises(ValueError, match="Search volume must be an integer"):
            validate_search_volume("1000")
        
        with pytest.raises(ValueError, match="Search volume cannot be negative"):
            validate_search_volume(-1)
        
        with pytest.raises(ValueError, match="Search volume exceeds maximum allowed value"):
            validate_search_volume(2000000000)
    
    def test_validate_growth_rate_valid(self):
        """Test valid growth rate validation"""
        assert validate_growth_rate(0) == 0.0
        assert validate_growth_rate(50.5) == 50.5
        assert validate_growth_rate(-50) == -50.0
    
    def test_validate_growth_rate_invalid(self):
        """Test invalid growth rate validation"""
        with pytest.raises(ValueError, match="Growth rate must be a number"):
            validate_growth_rate("50%")
        
        with pytest.raises(ValueError, match="Growth rate cannot be less than -100%"):
            validate_growth_rate(-150)
        
        with pytest.raises(ValueError, match="Growth rate exceeds maximum allowed value"):
            validate_growth_rate(20000)
    
    def test_validate_potential_score_valid(self):
        """Test valid potential score validation"""
        assert validate_potential_score(0) == 0.0
        assert validate_potential_score(50.5) == 50.5
        assert validate_potential_score(100) == 100.0
    
    def test_validate_potential_score_invalid(self):
        """Test invalid potential score validation"""
        with pytest.raises(ValueError, match="Potential score must be a number"):
            validate_potential_score("50")
        
        with pytest.raises(ValueError, match="Potential score must be between 0 and 100"):
            validate_potential_score(-1)
        
        with pytest.raises(ValueError, match="Potential score must be between 0 and 100"):
            validate_potential_score(101)


class TestTrendKeyword:
    """Test TrendKeyword data model"""
    
    def test_valid_trend_keyword(self):
        """Test creating a valid TrendKeyword"""
        keyword = TrendKeyword(
            keyword="python programming",
            search_volume=10000,
            growth_rate=25.5,
            region="US",
            category="science_tech",
            timestamp=datetime.now(),
            related_keywords=["python", "programming", "coding"]
        )
        
        assert keyword.keyword == "python programming"
        assert keyword.search_volume == 10000
        assert keyword.growth_rate == 25.5
        assert keyword.region == "US"
        assert keyword.category == "science_tech"
        assert len(keyword.related_keywords) == 3
    
    def test_trend_keyword_validation(self):
        """Test TrendKeyword validation"""
        with pytest.raises(ValueError, match="Keyword must be a non-empty string"):
            TrendKeyword(
                keyword="",
                search_volume=1000,
                growth_rate=10.0,
                region="US",
                category="all",
                timestamp=datetime.now()
            )
        
        with pytest.raises(ValueError, match="Search volume cannot be negative"):
            TrendKeyword(
                keyword="test",
                search_volume=-1,
                growth_rate=10.0,
                region="US",
                category="all",
                timestamp=datetime.now()
            )
        
        with pytest.raises(ValueError, match="Invalid category"):
            TrendKeyword(
                keyword="test",
                search_volume=1000,
                growth_rate=10.0,
                region="US",
                category="invalid_category",
                timestamp=datetime.now()
            )
    
    def test_trend_keyword_to_dict(self):
        """Test TrendKeyword serialization"""
        timestamp = datetime.now()
        keyword = TrendKeyword(
            keyword="test",
            search_volume=1000,
            growth_rate=10.0,
            region="US",
            category="all",
            timestamp=timestamp,
            related_keywords=["related1", "related2"]
        )
        
        result = keyword.to_dict()
        assert result['keyword'] == "test"
        assert result['search_volume'] == 1000
        assert result['growth_rate'] == 10.0
        assert result['region'] == "US"
        assert result['category'] == "all"
        assert result['timestamp'] == timestamp.isoformat()
        assert result['related_keywords'] == ["related1", "related2"]


class TestKeywordDetails:
    """Test KeywordDetails data model"""
    
    def test_valid_keyword_details(self):
        """Test creating valid KeywordDetails"""
        details = KeywordDetails(
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
        
        assert details.keyword == "python"
        assert details.search_volume == 50000
        assert len(details.interest_over_time) == 2
        assert len(details.related_topics) == 2
        assert len(details.related_queries) == 2
    
    def test_keyword_details_validation(self):
        """Test KeywordDetails validation"""
        with pytest.raises(ValueError, match="Interest over time must be a list"):
            KeywordDetails(
                keyword="test",
                search_volume=1000,
                interest_over_time="invalid",
                related_topics=[],
                related_queries=[],
                geo_distribution={},
                timestamp=datetime.now()
            )
        
        with pytest.raises(ValueError, match="Interest over time items must have 'date' and 'value' keys"):
            KeywordDetails(
                keyword="test",
                search_volume=1000,
                interest_over_time=[{"invalid": "data"}],
                related_topics=[],
                related_queries=[],
                geo_distribution={},
                timestamp=datetime.now()
            )


class TestDomainInfo:
    """Test DomainInfo data model"""
    
    def test_valid_domain_info(self):
        """Test creating valid DomainInfo"""
        domain = DomainInfo(
            domain="example.com",
            available=True,
            price=12.99,
            registrar="GoDaddy",
            alternatives=["example.net", "example.org"]
        )
        
        assert domain.domain == "example.com"
        assert domain.available is True
        assert domain.price == 12.99
        assert domain.registrar == "GoDaddy"
        assert len(domain.alternatives) == 2
    
    def test_domain_info_validation(self):
        """Test DomainInfo validation"""
        with pytest.raises(ValueError, match="Domain must be a non-empty string"):
            DomainInfo(domain="", available=True)
        
        with pytest.raises(ValueError, match="Invalid domain format"):
            DomainInfo(domain="invalid-domain", available=True)
        
        with pytest.raises(ValueError, match="Price must be a non-negative number"):
            DomainInfo(domain="example.com", available=True, price=-10)


class TestKeywordAnalysis:
    """Test KeywordAnalysis data model"""
    
    def test_valid_keyword_analysis(self):
        """Test creating valid KeywordAnalysis"""
        analysis = KeywordAnalysis(
            keyword="python programming",
            potential_score=85.5,
            competition_level=CompetitionLevel.MEDIUM,
            domain_suggestions=["python-programming.com", "learn-python.net"],
            content_ideas=["Python tutorial", "Python best practices"],
            estimated_traffic=15000,
            analysis_timestamp=datetime.now()
        )
        
        assert analysis.keyword == "python programming"
        assert analysis.potential_score == 85.5
        assert analysis.competition_level == CompetitionLevel.MEDIUM
        assert len(analysis.domain_suggestions) == 2
        assert len(analysis.content_ideas) == 2
        assert analysis.estimated_traffic == 15000
    
    def test_keyword_analysis_validation(self):
        """Test KeywordAnalysis validation"""
        with pytest.raises(ValueError, match="Potential score must be between 0 and 100"):
            KeywordAnalysis(
                keyword="test",
                potential_score=150,
                competition_level=CompetitionLevel.LOW,
                domain_suggestions=[],
                content_ideas=[],
                estimated_traffic=1000,
                analysis_timestamp=datetime.now()
            )
        
        with pytest.raises(ValueError, match="Estimated traffic must be a non-negative integer"):
            KeywordAnalysis(
                keyword="test",
                potential_score=50,
                competition_level=CompetitionLevel.LOW,
                domain_suggestions=[],
                content_ideas=[],
                estimated_traffic=-100,
                analysis_timestamp=datetime.now()
            )
    
    def test_keyword_analysis_competition_level_string(self):
        """Test KeywordAnalysis with string competition level"""
        analysis = KeywordAnalysis(
            keyword="test",
            potential_score=50,
            competition_level="high",  # String instead of enum
            domain_suggestions=[],
            content_ideas=[],
            estimated_traffic=1000,
            analysis_timestamp=datetime.now()
        )
        
        assert analysis.competition_level == CompetitionLevel.HIGH


class TestTrendsReport:
    """Test TrendsReport data model"""
    
    def test_valid_trends_report(self):
        """Test creating valid TrendsReport"""
        trend_data = [
            TrendKeyword(
                keyword="python",
                search_volume=10000,
                growth_rate=15.0,
                region="US",
                category="science_tech",
                timestamp=datetime.now()
            )
        ]
        
        analysis = KeywordAnalysis(
            keyword="python",
            potential_score=80.0,
            competition_level=CompetitionLevel.MEDIUM,
            domain_suggestions=["python-guide.com"],
            content_ideas=["Python tutorial"],
            estimated_traffic=12000,
            analysis_timestamp=datetime.now()
        )
        
        report = TrendsReport(
            id="test-report-123",
            keyword="python",
            analysis_date=datetime.now(),
            trend_data=trend_data,
            analysis_results=analysis,
            recommendations=["Focus on tutorial content", "Target beginners"]
        )
        
        assert report.id == "test-report-123"
        assert report.keyword == "python"
        assert len(report.trend_data) == 1
        assert isinstance(report.analysis_results, KeywordAnalysis)
        assert len(report.recommendations) == 2
    
    def test_trends_report_auto_id(self):
        """Test TrendsReport with auto-generated ID"""
        trend_data = [
            TrendKeyword(
                keyword="test",
                search_volume=1000,
                growth_rate=10.0,
                region="US",
                category="all",
                timestamp=datetime.now()
            )
        ]
        
        analysis = KeywordAnalysis(
            keyword="test",
            potential_score=50.0,
            competition_level=CompetitionLevel.LOW,
            domain_suggestions=[],
            content_ideas=[],
            estimated_traffic=1000,
            analysis_timestamp=datetime.now()
        )
        
        report = TrendsReport(
            id="",  # Empty ID should be auto-generated
            keyword="test",
            analysis_date=datetime.now(),
            trend_data=trend_data,
            analysis_results=analysis
        )
        
        assert report.id  # Should have auto-generated ID
        assert len(report.id) > 0
    
    def test_trends_report_keyword_consistency(self):
        """Test TrendsReport keyword consistency validation"""
        trend_data = [
            TrendKeyword(
                keyword="python",
                search_volume=1000,
                growth_rate=10.0,
                region="US",
                category="all",
                timestamp=datetime.now()
            )
        ]
        
        analysis = KeywordAnalysis(
            keyword="java",  # Different keyword
            potential_score=50.0,
            competition_level=CompetitionLevel.LOW,
            domain_suggestions=[],
            content_ideas=[],
            estimated_traffic=1000,
            analysis_timestamp=datetime.now()
        )
        
        with pytest.raises(ValueError, match="Report keyword must match analysis results keyword"):
            TrendsReport(
                id="test",
                keyword="python",
                analysis_date=datetime.now(),
                trend_data=trend_data,
                analysis_results=analysis
            )
    
    def test_add_recommendation(self):
        """Test adding recommendations to report"""
        trend_data = [
            TrendKeyword(
                keyword="test",
                search_volume=1000,
                growth_rate=10.0,
                region="US",
                category="all",
                timestamp=datetime.now()
            )
        ]
        
        analysis = KeywordAnalysis(
            keyword="test",
            potential_score=50.0,
            competition_level=CompetitionLevel.LOW,
            domain_suggestions=[],
            content_ideas=[],
            estimated_traffic=1000,
            analysis_timestamp=datetime.now()
        )
        
        report = TrendsReport(
            id="test",
            keyword="test",
            analysis_date=datetime.now(),
            trend_data=trend_data,
            analysis_results=analysis
        )
        
        report.add_recommendation("Test recommendation")
        assert len(report.recommendations) == 1
        assert "Test recommendation" in report.recommendations
        
        # Adding duplicate should not increase count
        report.add_recommendation("Test recommendation")
        assert len(report.recommendations) == 1
        
        # Adding empty recommendation should raise error
        with pytest.raises(ValueError, match="Recommendation must be a non-empty string"):
            report.add_recommendation("")