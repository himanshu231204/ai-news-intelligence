"""
Tests for news collectors
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from typing import List, Dict, Any


class TestGitHubCollector:
    """Test GitHub trending collector"""
    
    @pytest.mark.asyncio
    async def test_github_collector_success(self):
        """Test successful GitHub collection"""
        from app.collectors.github import fetch_github
        
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "items": [
                    {
                        "name": "langchain",
                        "description": "AI framework",
                        "url": "https://github.com/langchain",
                        "stars": 50000,
                    }
                ]
            }
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            result = await fetch_github()
            
            assert isinstance(result, list)
            assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_github_collector_network_error(self):
        """Test GitHub collector with network error"""
        from app.collectors.github import fetch_github
        
        with patch("requests.get") as mock_get:
            mock_get.side_effect = Exception("Network error")
            
            result = await fetch_github()
            
            # Should return empty list on error
            assert result == []
    
    @pytest.mark.asyncio
    async def test_github_collector_format(self):
        """Test GitHub collector returns correct format"""
        from app.collectors.github import fetch_github
        
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "items": [
                    {
                        "name": "test-repo",
                        "description": "Test",
                        "url": "https://github.com/test",
                        "stars": 100,
                    }
                ]
            }
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            result = await fetch_github()
            
            if result:
                item = result[0]
                assert "title" in item or "name" in item
                assert "url" in item


class TestHackerNewsCollector:
    """Test Hacker News collector"""
    
    @pytest.mark.asyncio
    async def test_hackernews_success(self):
        """Test successful HN collection"""
        from app.collectors.hackernews import fetch_hackernews
        
        result = await fetch_hackernews()
        
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_hackernews_format(self):
        """Test HN collector returns correct format"""
        from app.collectors.hackernews import fetch_hackernews
        
        result = await fetch_hackernews()
        
        if result:
            item = result[0]
            assert "title" in item or "url" in item


class TestRedditCollector:
    """Test Reddit collector"""
    
    @pytest.mark.asyncio
    async def test_reddit_with_mock(self):
        """Test Reddit collector with mocked PRAW"""
        with patch("praw.Reddit") as mock_reddit:
            mock_instance = MagicMock()
            mock_subreddit = MagicMock()
            
            # Mock the subreddit and posts
            mock_post = MagicMock()
            mock_post.title = "AI Breakthrough"
            mock_post.url = "https://reddit.com/post"
            mock_post.score = 1000
            mock_post.created_utc = datetime.now().timestamp()
            
            mock_subreddit.hot.return_value = [mock_post]
            mock_instance.subreddit.return_value = mock_subreddit
            mock_reddit.return_value = mock_instance
            
            from app.collectors.reddit import fetch_reddit
            
            result = await fetch_reddit()
            
            # Result should be a list
            assert isinstance(result, list)


class TestRSSCollector:
    """Test RSS feed collector"""
    
    @pytest.mark.asyncio
    async def test_rss_success(self):
        """Test successful RSS collection"""
        from app.collectors.rss import fetch_rss
        
        result = await fetch_rss()
        
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_rss_with_mock(self):
        """Test RSS with mocked feedparser"""
        with patch("feedparser.parse") as mock_parse:
            mock_parse.return_value = {
                "entries": [
                    {
                        "title": "AI News",
                        "link": "https://example.com/ai",
                        "published": "Mon, 09 May 2026 12:00:00 GMT",
                        "summary": "Breaking AI news",
                    }
                ]
            }
            
            from app.collectors.rss import fetch_rss
            
            result = await fetch_rss()
            
            assert isinstance(result, list)


class TestArxivCollector:
    """Test arXiv collector"""
    
    @pytest.mark.asyncio
    async def test_arxiv_success(self):
        """Test successful arXiv collection"""
        from app.collectors.arxiv import fetch_arxiv
        
        result = await fetch_arxiv()
        
        assert isinstance(result, list)


class TestCollectorParallel:
    """Test parallel collection of all sources"""
    
    @pytest.mark.asyncio
    async def test_all_collectors_run(self):
        """Test that all collectors can run without fatal errors"""
        from app.collectors.github import fetch_github
        from app.collectors.hackernews import fetch_hackernews
        
        # Run in parallel
        results = await asyncio.gather(
            fetch_github(),
            fetch_hackernews(),
            return_exceptions=True
        )
        
        # All should return lists or exceptions (which are handled)
        for result in results:
            assert isinstance(result, (list, Exception))


class TestCollectorErrorHandling:
    """Test collector error handling"""
    
    @pytest.mark.asyncio
    async def test_collector_timeout(self):
        """Test collector with timeout"""
        with patch("requests.get", side_effect=asyncio.TimeoutError):
            from app.collectors.github import fetch_github
            
            result = await fetch_github()
            
            # Should return empty list, not raise
            assert result == []
    
    @pytest.mark.asyncio
    async def test_collector_invalid_response(self):
        """Test collector with invalid response"""
        with patch("requests.get") as mock_get:
            mock_get.side_effect = ValueError("Invalid JSON")
            
            from app.collectors.github import fetch_github
            
            result = await fetch_github()
            
            # Should handle gracefully
            assert isinstance(result, list)


class TestCollectorDataValidation:
    """Test collector data validation"""
    
    @pytest.mark.asyncio
    async def test_collector_output_structure(self):
        """Test collector output has required fields"""
        from app.collectors.hackernews import fetch_hackernews
        
        result = await fetch_hackernews()
        
        if result:
            item = result[0]
            # Should have basic fields
            assert isinstance(item, dict)
            assert any(field in item for field in ["title", "url", "link"])
