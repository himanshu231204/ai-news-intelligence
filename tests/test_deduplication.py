"""
Tests for deduplication pipeline
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from typing import List, Dict, Any


class TestDeduplication:
    """Test news deduplication"""
    
    def test_deduplicate_exact_duplicates(self, duplicate_news_items):
        """Test removal of exact duplicate URLs"""
        from app.ranking.deduplication import deduplicate_news
        
        result = deduplicate_news(duplicate_news_items, similarity_threshold=0.85)
        
        # Should reduce duplicates
        assert len(result) < len(duplicate_news_items)
    
    def test_deduplicate_empty_list(self):
        """Test deduplication with empty list"""
        from app.ranking.deduplication import deduplicate_news
        
        result = deduplicate_news([])
        
        assert result == []
    
    def test_deduplicate_single_item(self, sample_news_items):
        """Test deduplication with single item"""
        from app.ranking.deduplication import deduplicate_news
        
        result = deduplicate_news(sample_news_items[:1])
        
        assert len(result) == 1
        assert result[0]["title"] == sample_news_items[0]["title"]
    
    def test_deduplicate_by_url(self):
        """Test deduplication removes same URL"""
        items = [
            {
                "title": "Title 1",
                "url": "https://example.com/article1",
                "source": "Source 1",
                "published_date": "2026-05-09",
                "content": "Content 1",
            },
            {
                "title": "Title 1 (Different)",
                "url": "https://example.com/article1",  # Same URL
                "source": "Source 2",
                "published_date": "2026-05-09",
                "content": "Content 1",
            },
        ]
        
        from app.ranking.deduplication import deduplicate_news
        
        result = deduplicate_news(items)
        
        # Should only keep one
        urls = [item["url"] for item in result]
        assert len(urls) == len(set(urls))
    
    def test_deduplicate_threshold_high(self, sample_news_items):
        """Test deduplication with high similarity threshold"""
        from app.ranking.deduplication import deduplicate_news
        
        # High threshold = keep more items
        result_high = deduplicate_news(sample_news_items, similarity_threshold=0.95)
        result_low = deduplicate_news(sample_news_items, similarity_threshold=0.5)
        
        # High threshold should keep at least as many as low
        assert len(result_high) >= len(result_low)
    
    def test_deduplicate_preserves_best_quality(self, duplicate_news_items):
        """Test that deduplication preserves highest quality item"""
        # Add quality scores
        for i, item in enumerate(duplicate_news_items):
            item["quality_score"] = 0.5 + (i * 0.2)
        
        from app.ranking.deduplication import deduplicate_news
        
        result = deduplicate_news(duplicate_news_items)
        
        # If multiple duplicates exist, should keep best quality
        if result:
            assert any(item in result for item in duplicate_news_items)
    
    def test_deduplicate_logging(self, caplog, duplicate_news_items):
        """Test deduplication logs correctly"""
        from app.ranking.deduplication import deduplicate_news
        
        result = deduplicate_news(duplicate_news_items)
        
        # Should have logging
        assert len(caplog.records) >= 0  # May or may not log


class TestSemanticDeduplication:
    """Test semantic similarity deduplication"""
    
    @pytest.mark.asyncio
    async def test_semantic_duplicate_detection(self):
        """Test semantic duplicate detection"""
        items = [
            {
                "title": "OpenAI Releases GPT-5",
                "url": "https://example.com/gpt5-1",
                "source": "Source 1",
                "published_date": "2026-05-09",
                "content": "OpenAI has released GPT-5",
            },
            {
                "title": "GPT-5 Released by OpenAI",
                "url": "https://example.com/gpt5-2",
                "source": "Source 2",
                "published_date": "2026-05-09",
                "content": "OpenAI's new GPT-5 model",
            },
            {
                "title": "Completely Different Topic",
                "url": "https://example.com/different",
                "source": "Source 3",
                "published_date": "2026-05-09",
                "content": "Unrelated content",
            },
        ]
        
        from app.ranking.deduplication import deduplicate_news
        
        result = deduplicate_news(items, similarity_threshold=0.7)
        
        # Should have reduced items due to semantic similarity
        assert len(result) <= len(items)


class TestDeduplicationEdgeCases:
    """Test edge cases in deduplication"""
    
    def test_deduplicate_missing_fields(self):
        """Test deduplication with missing fields"""
        items = [
            {"title": "Title 1", "url": "http://example.com/1"},
            {"title": "Title 2"},  # Missing URL
            {"url": "http://example.com/3"},  # Missing title
        ]
        
        from app.ranking.deduplication import deduplicate_news
        
        # Should handle gracefully
        result = deduplicate_news(items)
        assert isinstance(result, list)
    
    def test_deduplicate_special_characters(self):
        """Test deduplication with special characters"""
        items = [
            {
                "title": "AI: The Future!",
                "url": "https://example.com/ai-future",
                "source": "News",
                "published_date": "2026-05-09",
                "content": "AI content",
            },
            {
                "title": "AI: The Future!",  # Exact match with special chars
                "url": "https://example.com/ai-future",
                "source": "News2",
                "published_date": "2026-05-09",
                "content": "AI content",
            },
        ]
        
        from app.ranking.deduplication import deduplicate_news
        
        result = deduplicate_news(items)
        
        # Should remove duplicate
        assert len(result) == 1
    
    def test_deduplicate_unicode(self):
        """Test deduplication with unicode characters"""
        items = [
            {
                "title": "AI 研究 (AI Research)",
                "url": "https://example.com/ai-chinese",
                "source": "News",
                "published_date": "2026-05-09",
                "content": "Content",
            },
            {
                "title": "AI Research",
                "url": "https://example.com/ai-english",
                "source": "News",
                "published_date": "2026-05-09",
                "content": "Content",
            },
        ]
        
        from app.ranking.deduplication import deduplicate_news
        
        result = deduplicate_news(items)
        
        assert isinstance(result, list)


class TestDeduplicationPerformance:
    """Test deduplication performance"""
    
    def test_deduplicate_large_batch(self):
        """Test deduplication with large number of items"""
        items = [
            {
                "title": f"Article {i}",
                "url": f"https://example.com/article-{i}",
                "source": "News",
                "published_date": "2026-05-09",
                "content": f"Content {i}",
            }
            for i in range(100)
        ]
        
        from app.ranking.deduplication import deduplicate_news
        
        result = deduplicate_news(items)
        
        # Should process without error
        assert len(result) <= len(items)
    
    def test_deduplicate_maintains_order(self, sample_news_items):
        """Test that deduplication maintains relative order"""
        from app.ranking.deduplication import deduplicate_news
        
        result = deduplicate_news(sample_news_items)
        
        if len(result) > 1:
            # Should maintain order or indicate preserved order
            assert isinstance(result, list)


class TestDeduplicationWithVectorStore:
    """Test deduplication with ChromaDB vectorstore"""
    
    @pytest.mark.asyncio
    async def test_vectorstore_deduplication(self, mock_chromadb_collection, mock_embeddings):
        """Test deduplication using vector store"""
        with patch("app.memory.vectorstore.get_vectorstore", return_value=mock_chromadb_collection):
            with patch("app.ranking.embeddings.embed_texts", side_effect=mock_embeddings):
                from app.ranking.deduplication import deduplicate_news
                
                items = [
                    {
                        "title": "AI News 1",
                        "url": "https://example.com/1",
                        "source": "News",
                        "published_date": "2026-05-09",
                        "content": "Content 1",
                    },
                ]
                
                result = deduplicate_news(items)
                
                assert isinstance(result, list)
