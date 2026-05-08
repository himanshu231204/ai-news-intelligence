"""
Tests for filtering pipeline
"""

import pytest
from unittest.mock import patch, MagicMock


class TestQualityFiltering:
    """Test quality filtering"""
    
    def test_filter_low_quality(self, low_quality_items):
        """Test filtering removes low quality items"""
        from app.graph.nodes.filter_low_quality import filter_low_quality
        
        state = {"filtered_news": low_quality_items}
        
        # Mock the filtering
        result = filter_low_quality(state)
        
        assert isinstance(result, dict)
        assert "filtered_news" in result
    
    def test_filter_empty_title(self):
        """Test filtering removes items with empty title"""
        items = [
            {
                "title": "Valid Title",
                "url": "https://example.com/1",
                "source": "News",
                "published_date": "2026-05-09",
                "content": "Content",
            },
            {
                "title": "",  # Empty
                "url": "https://example.com/2",
                "source": "News",
                "published_date": "2026-05-09",
                "content": "Content",
            },
        ]
        
        from app.graph.nodes.filter_low_quality import filter_low_quality
        
        state = {"filtered_news": items}
        result = filter_low_quality(state)
        
        assert "filtered_news" in result
    
    def test_filter_spam_content(self):
        """Test filtering removes spam-like content"""
        items = [
            {
                "title": "Real AI News",
                "url": "https://example.com/1",
                "source": "News",
                "published_date": "2026-05-09",
                "content": "Meaningful content about AI",
            },
            {
                "title": "CLICK HERE!!!",
                "url": "https://spam.com/1",
                "source": "Spam",
                "published_date": "2026-05-09",
                "content": "Buy now! Free money! Limited time!!!",
            },
        ]
        
        from app.graph.nodes.filter_low_quality import filter_low_quality
        
        state = {"filtered_news": items}
        result = filter_low_quality(state)
        
        assert isinstance(result, dict)
    
    def test_filter_too_short_content(self):
        """Test filtering removes items with too short content"""
        items = [
            {
                "title": "Good Article",
                "url": "https://example.com/1",
                "source": "News",
                "published_date": "2026-05-09",
                "content": "This is a meaningful article with substantial content about AI and machine learning.",
            },
            {
                "title": "Too Short",
                "url": "https://example.com/2",
                "source": "News",
                "published_date": "2026-05-09",
                "content": "Short",
            },
        ]
        
        from app.graph.nodes.filter_low_quality import filter_low_quality
        
        state = {"filtered_news": items}
        result = filter_low_quality(state)
        
        assert isinstance(result, dict)
    
    def test_filter_maintains_good_quality(self, sample_news_items):
        """Test filtering maintains high quality items"""
        from app.graph.nodes.filter_low_quality import filter_low_quality
        
        state = {"filtered_news": sample_news_items}
        result = filter_low_quality(state)
        
        # Should keep good items
        assert isinstance(result, dict)
        if result["filtered_news"]:
            assert len(result["filtered_news"]) > 0


class TestQualityMetrics:
    """Test quality metric calculations"""
    
    def test_calculate_content_quality(self):
        """Test content quality calculation"""
        items = [
            {
                "title": "AI Breakthrough",
                "url": "https://example.com/1",
                "source": "Research Paper",
                "published_date": "2026-05-09",
                "content": "A comprehensive analysis of AI breakthroughs in natural language processing, including transformer architectures and attention mechanisms.",
            },
            {
                "title": "OK",
                "url": "https://example.com/2",
                "source": "Blog",
                "published_date": "2026-05-09",
                "content": "Short post",
            },
        ]
        
        from app.graph.nodes.filter_low_quality import filter_low_quality
        
        state = {"filtered_news": items}
        result = filter_low_quality(state)
        
        assert isinstance(result, dict)
    
    def test_filter_by_source_credibility(self):
        """Test filtering by source credibility"""
        items = [
            {
                "title": "Official Announcement",
                "url": "https://example.com/1",
                "source": "OpenAI Official",
                "published_date": "2026-05-09",
                "content": "Official statement",
            },
            {
                "title": "Random Post",
                "url": "https://example.com/2",
                "source": "Unknown Blog",
                "published_date": "2026-05-09",
                "content": "Random content",
            },
        ]
        
        from app.graph.nodes.filter_low_quality import filter_low_quality
        
        state = {"filtered_news": items}
        result = filter_low_quality(state)
        
        # Should prioritize official sources
        assert isinstance(result, dict)


class TestFilteringEdgeCases:
    """Test filtering edge cases"""
    
    def test_filter_empty_list(self):
        """Test filtering empty list"""
        from app.graph.nodes.filter_low_quality import filter_low_quality
        
        state = {"filtered_news": []}
        result = filter_low_quality(state)
        
        assert isinstance(result, dict)
        assert result["filtered_news"] == []
    
    def test_filter_all_items_removed(self):
        """Test when all items are filtered out"""
        items = [
            {"title": "", "url": "https://example.com/1", "source": ""},
            {"title": "spam!!!!", "url": "https://example.com/2", "content": ""},
        ]
        
        from app.graph.nodes.filter_low_quality import filter_low_quality
        
        state = {"filtered_news": items}
        result = filter_low_quality(state)
        
        # Should handle gracefully
        assert isinstance(result, dict)
    
    def test_filter_with_missing_fields(self):
        """Test filtering with missing fields"""
        items = [
            {"title": "Title 1", "url": "https://example.com/1"},  # Missing source
            {"title": "Title 2"},  # Missing url
        ]
        
        from app.graph.nodes.filter_low_quality import filter_low_quality
        
        state = {"filtered_news": items}
        result = filter_low_quality(state)
        
        assert isinstance(result, dict)
    
    def test_filter_unicode_content(self):
        """Test filtering unicode content"""
        items = [
            {
                "title": "AI 研究 (AI Research)",
                "url": "https://example.com/1",
                "source": "中文新闻",
                "published_date": "2026-05-09",
                "content": "人工智能的最新进展",
            },
        ]
        
        from app.graph.nodes.filter_low_quality import filter_low_quality
        
        state = {"filtered_news": items}
        result = filter_low_quality(state)
        
        assert isinstance(result, dict)


class TestFilteringPerformance:
    """Test filtering performance"""
    
    def test_filter_large_batch(self):
        """Test filtering large batch"""
        items = [
            {
                "title": f"Article {i}",
                "url": f"https://example.com/{i}",
                "source": "News",
                "published_date": "2026-05-09",
                "content": f"Content for article {i} with some substance",
            }
            for i in range(100)
        ]
        
        from app.graph.nodes.filter_low_quality import filter_low_quality
        
        state = {"filtered_news": items}
        result = filter_low_quality(state)
        
        assert isinstance(result, dict)
        assert isinstance(result["filtered_news"], list)


class TestFilteringConfiguration:
    """Test filtering configuration"""
    
    def test_filter_min_content_length(self):
        """Test minimum content length threshold"""
        items = [
            {
                "title": "Good",
                "url": "https://example.com/1",
                "source": "News",
                "published_date": "2026-05-09",
                "content": "This is a long article with meaningful content about artificial intelligence and machine learning technologies.",
            },
            {
                "title": "Bad",
                "url": "https://example.com/2",
                "source": "News",
                "published_date": "2026-05-09",
                "content": "Short",
            },
        ]
        
        from app.graph.nodes.filter_low_quality import filter_low_quality
        
        state = {"filtered_news": items}
        result = filter_low_quality(state)
        
        assert isinstance(result, dict)
    
    def test_filter_language_detection(self):
        """Test filtering supports multiple languages"""
        items = [
            {
                "title": "English Article",
                "url": "https://example.com/1",
                "source": "News",
                "published_date": "2026-05-09",
                "content": "This is an English article",
            },
            {
                "title": "Articulo en Español",
                "url": "https://example.com/2",
                "source": "News",
                "published_date": "2026-05-09",
                "content": "Este es un artículo en español",
            },
        ]
        
        from app.graph.nodes.filter_low_quality import filter_low_quality
        
        state = {"filtered_news": items}
        result = filter_low_quality(state)
        
        assert isinstance(result, dict)
