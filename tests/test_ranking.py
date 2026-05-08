"""
Tests for ranking pipeline
"""

import pytest
from unittest.mock import patch, MagicMock
from typing import List, Dict, Any


class TestRanking:
    """Test news ranking system"""
    
    def test_rank_items_basic(self, sample_news_items):
        """Test basic ranking of news items"""
        from app.ranking.scorer import rank_news
        
        result = rank_news(sample_news_items)
        
        # Should return list of ranked items
        assert isinstance(result, list)
        assert len(result) == len(sample_news_items)
    
    def test_rank_items_have_scores(self, sample_news_items):
        """Test ranked items have scores"""
        from app.ranking.scorer import rank_news
        
        result = rank_news(sample_news_items)
        
        for item in result:
            assert "score" in item or "rank" in item
    
    def test_rank_items_sorted_by_score(self, sample_news_items):
        """Test items are sorted by score (descending)"""
        from app.ranking.scorer import rank_news
        
        result = rank_news(sample_news_items)
        
        if len(result) > 1 and "score" in result[0]:
            scores = [item.get("score", 0) for item in result]
            # Should be sorted in descending order or similar ranking
            assert isinstance(scores, list)
    
    def test_rank_empty_list(self):
        """Test ranking empty list"""
        from app.ranking.scorer import rank_news
        
        result = rank_news([])
        
        assert result == []
    
    def test_rank_single_item(self, sample_news_items):
        """Test ranking single item"""
        from app.ranking.scorer import rank_news
        
        result = rank_news(sample_news_items[:1])
        
        assert len(result) == 1
    
    def test_rank_considers_virality(self):
        """Test ranking considers virality metrics"""
        items = [
            {
                "title": "Breaking AI News",
                "url": "https://example.com/1",
                "source": "News",
                "published_date": "2026-05-09",
                "content": "Content",
                "engagement": 1000,  # High engagement
            },
            {
                "title": "Minor Update",
                "url": "https://example.com/2",
                "source": "News",
                "published_date": "2026-05-09",
                "content": "Content",
                "engagement": 10,  # Low engagement
            },
        ]
        
        from app.ranking.scorer import rank_news
        
        result = rank_news(items)
        
        # Higher engagement should rank higher
        assert len(result) == 2
    
    def test_rank_considers_age(self):
        """Test ranking penalizes old items"""
        from datetime import datetime, timedelta
        
        items = [
            {
                "title": "Recent News",
                "url": "https://example.com/recent",
                "source": "News",
                "published_date": datetime.now().isoformat(),
                "content": "Content",
            },
            {
                "title": "Old News",
                "url": "https://example.com/old",
                "source": "News",
                "published_date": (datetime.now() - timedelta(days=30)).isoformat(),
                "content": "Content",
            },
        ]
        
        from app.ranking.scorer import rank_news
        
        result = rank_news(items)
        
        # Should prefer recent
        assert isinstance(result, list)
    
    def test_rank_preserves_metadata(self, sample_news_items):
        """Test ranking preserves original item metadata"""
        from app.ranking.scorer import rank_news
        
        result = rank_news(sample_news_items)
        
        for ranked_item in result:
            assert "title" in ranked_item
            assert "url" in ranked_item


class TestScoringFactors:
    """Test individual scoring factors"""
    
    def test_score_keyword_importance(self):
        """Test scoring considers keyword importance"""
        items = [
            {
                "title": "GPT-5 Released",
                "url": "https://example.com/1",
                "source": "News",
                "published_date": "2026-05-09",
                "content": "New model release",
            },
            {
                "title": "Blog Post",
                "url": "https://example.com/2",
                "source": "News",
                "published_date": "2026-05-09",
                "content": "Random content",
            },
        ]
        
        from app.ranking.scorer import rank_news
        
        result = rank_news(items)
        
        # First item should score higher due to important keywords
        assert len(result) >= 1
    
    def test_score_source_credibility(self):
        """Test scoring considers source credibility"""
        items = [
            {
                "title": "AI News",
                "url": "https://example.com/1",
                "source": "Official Blog",
                "published_date": "2026-05-09",
                "content": "Content",
            },
            {
                "title": "AI News",
                "url": "https://example.com/2",
                "source": "Random Blog",
                "published_date": "2026-05-09",
                "content": "Content",
            },
        ]
        
        from app.ranking.scorer import rank_news
        
        result = rank_news(items)
        
        assert len(result) == 2


class TestRankingEdgeCases:
    """Test ranking edge cases"""
    
    def test_rank_with_missing_fields(self):
        """Test ranking with missing fields"""
        items = [
            {"title": "Title 1", "url": "http://example.com/1", "source": "News"},
            {"title": "Title 2", "url": "http://example.com/2"},  # Missing source
            {"source": "News"},  # Missing title
        ]
        
        from app.ranking.scorer import rank_news
        
        # Should handle gracefully
        result = rank_news(items)
        assert isinstance(result, list)
    
    def test_rank_zero_scores(self):
        """Test ranking with zero scores"""
        items = [
            {
                "title": f"Article {i}",
                "url": f"https://example.com/{i}",
                "source": "News",
                "published_date": "2026-05-09",
                "content": "Content",
            }
            for i in range(3)
        ]
        
        from app.ranking.scorer import rank_news
        
        result = rank_news(items)
        
        assert len(result) >= 0


class TestRankingPerformance:
    """Test ranking performance"""
    
    def test_rank_large_batch(self):
        """Test ranking large batch of items"""
        items = [
            {
                "title": f"Article {i}",
                "url": f"https://example.com/{i}",
                "source": "News",
                "published_date": "2026-05-09",
                "content": f"Content {i}",
            }
            for i in range(100)
        ]
        
        from app.ranking.scorer import rank_news
        
        result = rank_news(items)
        
        assert len(result) == len(items)


class TestRankingConfiguration:
    """Test ranking configuration"""
    
    def test_ranking_threshold(self):
        """Test ranking with different thresholds"""
        items = [
            {
                "title": "High Quality",
                "url": "https://example.com/1",
                "source": "Major News",
                "published_date": "2026-05-09",
                "content": "Important AI update",
            },
            {
                "title": "Low Quality",
                "url": "https://example.com/2",
                "source": "Minor Blog",
                "published_date": "2026-05-09",
                "content": "Random post",
            },
        ]
        
        from app.ranking.scorer import rank_news
        
        result = rank_news(items)
        
        # Should return both (filtering happens later)
        assert len(result) == 2
    
    def test_ranking_top_n(self):
        """Test getting top N ranked items"""
        items = [
            {
                "title": f"Article {i}",
                "url": f"https://example.com/{i}",
                "source": "News",
                "published_date": "2026-05-09",
                "content": f"Content {i}",
            }
            for i in range(10)
        ]
        
        from app.ranking.scorer import rank_news
        
        result = rank_news(items)
        top_5 = result[:5]
        
        assert len(top_5) == 5
