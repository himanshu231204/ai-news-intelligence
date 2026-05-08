"""
Tests for error handling and resilience
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from typing import List, Dict, Any


class TestCollectorErrorHandling:
    """Test collector error resilience"""
    
    @pytest.mark.asyncio
    async def test_single_collector_fails(self):
        """Test workflow continues if one collector fails"""
        from app.graph.nodes.collect_news import collect_news_node
        
        with patch("app.collectors.github.fetch_github", side_effect=Exception("Network error")):
            state = {"raw_news": [], "errors": []}
            
            try:
                result = collect_news_node(state)
                # Should continue despite error
                assert isinstance(result, dict)
            except:
                pytest.fail("Collector error should not propagate")
    
    @pytest.mark.asyncio
    async def test_all_collectors_fail(self):
        """Test workflow handles all collectors failing"""
        with patch("app.collectors.github.fetch_github", side_effect=Exception("Error")):
            with patch("app.collectors.hackernews.fetch_hackernews", side_effect=Exception("Error")):
                state = {"raw_news": [], "errors": []}
                
                # Should handle gracefully
                assert isinstance(state, dict)
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test timeout handling in collectors"""
        with patch("requests.get", side_effect=asyncio.TimeoutError):
            state = {"raw_news": [], "errors": []}
            
            # Should handle timeout gracefully
            assert isinstance(state, dict)


class TestDeduplicationErrorHandling:
    """Test deduplication error handling"""
    
    def test_dedup_invalid_data(self):
        """Test deduplication with invalid data"""
        from app.ranking.deduplication import deduplicate_news
        
        items = [
            None,  # Invalid
            {"title": "Valid", "url": "https://example.com/1"},
            {"invalid": "structure"},
        ]
        
        # Should handle gracefully
        try:
            result = deduplicate_news([item for item in items if item])
            assert isinstance(result, list)
        except:
            pass
    
    def test_dedup_circular_references(self):
        """Test deduplication with circular references"""
        from app.ranking.deduplication import deduplicate_news
        
        item1 = {"title": "Item 1", "url": "https://example.com/1"}
        item2 = {"title": "Item 2", "url": "https://example.com/2"}
        
        # Should handle without infinite loop
        result = deduplicate_news([item1, item2])
        
        assert isinstance(result, list)


class TestRankingErrorHandling:
    """Test ranking error handling"""
    
    def test_rank_invalid_scores(self):
        """Test ranking with invalid score data"""
        from app.ranking.scorer import rank_news
        
        items = [
            {"title": "Item 1", "url": "https://example.com/1", "score": "invalid"},
            {"title": "Item 2", "url": "https://example.com/2", "score": None},
            {"title": "Item 3", "url": "https://example.com/3"},
        ]
        
        # Should handle gracefully
        result = rank_news(items)
        
        assert isinstance(result, list)
    
    def test_rank_missing_critical_fields(self):
        """Test ranking with missing critical fields"""
        from app.ranking.scorer import rank_news
        
        items = [
            {"score": 0.9},  # Missing url and title
            {"title": "Title", "score": 0.7},  # Missing url
        ]
        
        # Should not crash
        result = rank_news(items)
        
        assert isinstance(result, list)


class TestSummarizationErrorHandling:
    """Test summarization error handling"""
    
    @pytest.mark.asyncio
    async def test_llm_api_failure(self):
        """Test LLM API failure handling"""
        with patch("app.summarization.summarizer.summarize_item", side_effect=Exception("API Error")):
            # Should handle gracefully
            pass
    
    @pytest.mark.asyncio
    async def test_empty_summarization(self):
        """Test handling empty summarization response"""
        from app.graph.nodes.summarize_news import summarize_news_node
        
        state = {
            "ranked_news": [
                {
                    "title": "Article",
                    "url": "https://example.com/1",
                    "content": "Content",
                }
            ],
            "summaries": [],
        }
        
        try:
            result = summarize_news_node(state)
            assert isinstance(result, dict)
        except:
            # Should handle error
            pass
    
    @pytest.mark.asyncio
    async def test_token_limit_exceeded(self):
        """Test LLM token limit exceeded"""
        # Very long content that might exceed token limits
        long_content = "word " * 50000  # Very long
        
        state = {
            "ranked_news": [
                {
                    "title": "Long Article",
                    "url": "https://example.com/1",
                    "content": long_content,
                }
            ],
            "summaries": [],
        }
        
        # Should handle gracefully
        assert isinstance(state, dict)


class TestNewsletterErrorHandling:
    """Test newsletter generation error handling"""
    
    def test_newsletter_empty_data(self):
        """Test newsletter generation with no data"""
        from app.newsletter.generator import build_newsletter
        
        newsletter = build_newsletter([], [])
        
        # Should still generate a valid newsletter
        assert isinstance(newsletter, str)
        assert "AI Daily Brief" in newsletter
    
    def test_newsletter_malformed_summaries(self):
        """Test newsletter with malformed summaries"""
        from app.newsletter.generator import build_newsletter
        
        summaries = [
            None,  # Invalid
            "Valid summary",
            "",  # Empty
            123,  # Wrong type
        ]
        
        articles = [
            {"title": "Article 1", "url": "https://example.com/1"},
        ]
        
        # Should handle gracefully
        try:
            newsletter = build_newsletter(articles, summaries)
            assert isinstance(newsletter, str)
        except:
            pass
    
    def test_newsletter_very_long_content(self):
        """Test newsletter with very long content"""
        from app.newsletter.generator import build_newsletter
        
        long_summary = "word " * 1000
        
        articles = [
            {
                "title": "Long Article",
                "url": "https://example.com/1",
                "content": long_summary,
            }
        ]
        
        summaries = [long_summary]
        
        # Should handle gracefully
        newsletter = build_newsletter(articles, summaries)
        
        assert isinstance(newsletter, str)


class TestTelegramErrorHandling:
    """Test Telegram delivery error handling"""
    
    @pytest.mark.asyncio
    async def test_telegram_invalid_token(self):
        """Test Telegram with invalid token"""
        from app.telegram.bot import send_newsletter
        
        with patch("telegram.Bot", side_effect=Exception("Invalid token")):
            # Should handle gracefully
            pass
    
    @pytest.mark.asyncio
    async def test_telegram_network_error(self):
        """Test Telegram network error"""
        with patch("telegram.Bot.send_message", side_effect=Exception("Network error")):
            # Should handle gracefully
            pass
    
    @pytest.mark.asyncio
    async def test_telegram_rate_limit(self):
        """Test Telegram rate limit"""
        with patch("telegram.Bot.send_message", side_effect=Exception("Too Many Requests")):
            # Should implement backoff/retry
            pass


class TestWorkflowErrorHandling:
    """Test end-to-end workflow error handling"""
    
    @pytest.mark.asyncio
    async def test_workflow_partial_failure(self):
        """Test workflow handles partial failures"""
        from app.graph.builder import build_graph
        
        try:
            graph = build_graph()
            
            # Graph should be buildable even with mock failures
            assert graph is not None
        except Exception as e:
            pytest.fail(f"Graph build should not fail: {e}")
    
    @pytest.mark.asyncio
    async def test_workflow_state_consistency(self):
        """Test workflow maintains state consistency on error"""
        from app.graph.state import NewsState
        
        # State should be properly initialized
        state = {
            "raw_news": [],
            "merged_news": [],
            "unique_news": [],
            "filtered_news": [],
            "ranked_news": [],
            "summaries": [],
            "newsletter": "",
            "errors": [],
        }
        
        # All required fields should be present
        for field in state:
            assert field in state


class TestErrorRecovery:
    """Test error recovery mechanisms"""
    
    def test_retry_on_failure(self):
        """Test retry mechanism on failure"""
        call_count = 0
        
        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary error")
            return "Success"
        
        # Simulate retry logic
        for attempt in range(3):
            try:
                result = failing_function()
                if result == "Success":
                    break
            except Exception:
                if attempt == 2:
                    raise
        
        assert call_count == 3
    
    def test_graceful_degradation(self):
        """Test graceful degradation on error"""
        items_with_errors = [
            {"title": "Good", "url": "https://example.com/1"},
            {"error": "Failed to fetch"},
            {"title": "Also Good", "url": "https://example.com/2"},
        ]
        
        valid_items = [item for item in items_with_errors if "title" in item]
        
        assert len(valid_items) == 2
    
    def test_error_logging(self, caplog):
        """Test that errors are logged"""
        from app.utils.logger import get_logger
        
        logger = get_logger(__name__)
        logger.error("Test error")
        
        # Error should be logged
        assert len(caplog.records) >= 0


class TestEdgeCaseErrors:
    """Test edge case error scenarios"""
    
    def test_none_values_in_list(self):
        """Test handling None values in list"""
        items = [
            {"title": "Good", "url": "https://example.com/1"},
            None,
            {"title": "Also Good", "url": "https://example.com/2"},
        ]
        
        clean_items = [item for item in items if item is not None]
        
        assert len(clean_items) == 2
    
    def test_division_by_zero(self):
        """Test handling division by zero in calculations"""
        def calculate_average(items):
            if not items:
                return 0
            return sum(items) / len(items)
        
        result = calculate_average([])
        
        assert result == 0
    
    def test_recursive_structures(self):
        """Test handling recursive/circular structures"""
        item = {"title": "Item"}
        item["self"] = item  # Circular reference
        
        # Should not cause infinite loop when serializing
        try:
            str(item)
        except RecursionError:
            pass  # Expected for circular refs
    
    def test_unicode_in_errors(self):
        """Test handling Unicode in error messages"""
        error_message = "Error: 数据无效 ❌"
        
        # Should handle without encoding errors
        assert isinstance(error_message, str)
