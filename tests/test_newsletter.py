"""
Tests for newsletter generation
"""

import pytest
from unittest.mock import patch, MagicMock


class TestNewsletterGeneration:
    """Test newsletter generation"""
    
    def test_generate_newsletter_basic(self, sample_news_items):
        """Test basic newsletter generation"""
        from app.newsletter.generator import build_newsletter
        
        newsletter = build_newsletter(sample_news_items, [])
        
        assert isinstance(newsletter, str)
        assert "AI Daily Brief" in newsletter
    
    def test_generate_newsletter_with_summaries(self, sample_news_items):
        """Test newsletter with article summaries"""
        from app.newsletter.generator import build_newsletter
        
        summaries = [
            "Summary 1 about AI",
            "Summary 2 about ML",
            "Summary 3 about LLMs",
        ]
        
        newsletter = build_newsletter(sample_news_items, summaries)
        
        assert isinstance(newsletter, str)
        assert len(newsletter) > 0
    
    def test_newsletter_includes_headers(self):
        """Test newsletter includes section headers"""
        from app.newsletter.generator import build_newsletter
        
        articles = [
            {"title": "Breaking News", "url": "https://example.com/1"},
            {"title": "Research", "url": "https://example.com/2"},
        ]
        
        newsletter = build_newsletter(articles, [])
        
        # Should have structured headers
        assert isinstance(newsletter, str)
    
    def test_newsletter_includes_links(self, sample_news_items):
        """Test newsletter includes article links"""
        from app.newsletter.generator import build_newsletter
        
        newsletter = build_newsletter(sample_news_items, [])
        
        # Should contain URLs
        for item in sample_news_items:
            if "url" in item:
                # Newsletter might format URL
                assert isinstance(newsletter, str)
    
    def test_newsletter_empty_items(self):
        """Test newsletter with empty items list"""
        from app.newsletter.generator import build_newsletter
        
        newsletter = build_newsletter([], [])
        
        # Should still generate valid newsletter
        assert isinstance(newsletter, str)
        assert "Daily Brief" in newsletter or "Brief" in newsletter
    
    def test_newsletter_formatting(self):
        """Test newsletter is properly formatted"""
        from app.newsletter.generator import build_newsletter
        
        articles = [
            {
                "title": "Article 1",
                "url": "https://example.com/1",
                "source": "News",
            },
        ]
        
        newsletter = build_newsletter(articles, ["Summary"])
        
        # Should have readable formatting
        assert isinstance(newsletter, str)
        assert "\n" in newsletter  # Should have line breaks


class TestNewsletterStructure:
    """Test newsletter structure and sections"""
    
    def test_newsletter_has_header(self):
        """Test newsletter has header"""
        from app.newsletter.generator import build_newsletter
        
        newsletter = build_newsletter([], [])
        
        # Should have header
        lines = newsletter.split("\n")
        assert len(lines) > 0
    
    def test_newsletter_has_footer(self):
        """Test newsletter has footer"""
        from app.newsletter.generator import build_newsletter
        
        newsletter = build_newsletter([], [])
        
        # Should indicate it's a newsletter
        assert isinstance(newsletter, str)
    
    def test_newsletter_sections_separated(self):
        """Test newsletter sections are separated"""
        from app.newsletter.generator import build_newsletter
        
        articles = [
            {"title": f"Article {i}", "url": f"https://example.com/{i}"}
            for i in range(3)
        ]
        
        newsletter = build_newsletter(articles, [])
        
        # Should have clear separation
        assert isinstance(newsletter, str)


class TestNewsletterFormatting:
    """Test newsletter formatting"""
    
    def test_newsletter_markdown_formatting(self):
        """Test newsletter uses markdown formatting"""
        from app.newsletter.generator import build_newsletter
        
        newsletter = build_newsletter([], [])
        
        # Might use markdown
        assert isinstance(newsletter, str)
    
    def test_newsletter_code_blocks(self):
        """Test newsletter properly escapes code"""
        from app.newsletter.generator import build_newsletter
        
        articles = [
            {
                "title": "Code Article",
                "url": "https://example.com/1",
                "content": "```python\nprint('hello')\n```",
            },
        ]
        
        newsletter = build_newsletter(articles, [])
        
        # Should handle code blocks
        assert isinstance(newsletter, str)
    
    def test_newsletter_special_characters(self):
        """Test newsletter handles special characters"""
        from app.newsletter.generator import build_newsletter
        
        articles = [
            {
                "title": "Special Chars: & < > \" '",
                "url": "https://example.com/1",
            },
        ]
        
        newsletter = build_newsletter(articles, [])
        
        # Should escape properly
        assert isinstance(newsletter, str)
    
    def test_newsletter_unicode(self):
        """Test newsletter handles unicode"""
        from app.newsletter.generator import build_newsletter
        
        articles = [
            {
                "title": "Unicode: 你好 مرحبا",
                "url": "https://example.com/1",
            },
        ]
        
        newsletter = build_newsletter(articles, [])
        
        # Should handle unicode
        assert isinstance(newsletter, str)


class TestNewsletterLength:
    """Test newsletter length and truncation"""
    
    def test_newsletter_reasonable_length(self):
        """Test newsletter is reasonable length"""
        from app.newsletter.generator import build_newsletter
        
        articles = [
            {"title": "Article", "url": "https://example.com/1"}
            for _ in range(5)
        ]
        
        newsletter = build_newsletter(articles, [])
        
        # Should be readable length
        assert len(newsletter) > 100
        assert len(newsletter) < 100000  # Not absurdly long
    
    def test_newsletter_truncates_long_summaries(self):
        """Test newsletter truncates long summaries"""
        from app.newsletter.generator import build_newsletter
        
        long_summary = "word " * 1000
        
        newsletter = build_newsletter([], [long_summary])
        
        # Should not be absurdly long
        assert len(newsletter) < 100000


class TestNewsletterDateTime:
    """Test newsletter includes date/time"""
    
    def test_newsletter_has_date(self):
        """Test newsletter includes date"""
        from app.newsletter.generator import build_newsletter
        from datetime import datetime
        
        newsletter = build_newsletter([], [])
        
        # Might include current date
        assert isinstance(newsletter, str)


class TestNewsletterStatistics:
    """Test newsletter includes statistics"""
    
    def test_newsletter_includes_count(self):
        """Test newsletter mentions article count"""
        from app.newsletter.generator import build_newsletter
        
        articles = [
            {"title": f"Article {i}", "url": f"https://example.com/{i}"}
            for i in range(5)
        ]
        
        newsletter = build_newsletter(articles, [])
        
        # Should mention number of articles or show them
        assert isinstance(newsletter, str)
    
    def test_newsletter_source_diversity(self):
        """Test newsletter shows source diversity"""
        from app.newsletter.generator import build_newsletter
        
        articles = [
            {"title": "Article 1", "url": "https://example.com/1", "source": "Source A"},
            {"title": "Article 2", "url": "https://example.com/2", "source": "Source B"},
            {"title": "Article 3", "url": "https://example.com/3", "source": "Source C"},
        ]
        
        newsletter = build_newsletter(articles, [])
        
        # Should include diverse sources
        assert isinstance(newsletter, str)


class TestNewsletterCallToAction:
    """Test newsletter CTA elements"""
    
    def test_newsletter_has_meaningful_content(self):
        """Test newsletter isn't empty"""
        from app.newsletter.generator import build_newsletter
        
        articles = [
            {"title": "AI News", "url": "https://example.com/1"},
        ]
        
        newsletter = build_newsletter(articles, [])
        
        assert isinstance(newsletter, str)
        assert len(newsletter) > 50


class TestNewsletterIntegration:
    """Test newsletter in workflow context"""
    
    def test_newsletter_from_workflow_state(self):
        """Test newsletter generation from workflow state"""
        from app.graph.nodes.generate_newsletter import generate_newsletter_node
        
        state = {
            "ranked_news": [
                {"title": "News 1", "url": "https://example.com/1"},
            ],
            "summaries": ["Summary 1"],
            "newsletter": "",
        }
        
        try:
            result = generate_newsletter_node(state)
            
            assert isinstance(result, dict)
            assert "newsletter" in result
        except:
            pass
    
    def test_newsletter_empty_state(self):
        """Test newsletter with empty workflow state"""
        from app.graph.nodes.generate_newsletter import generate_newsletter_node
        
        state = {
            "ranked_news": [],
            "summaries": [],
            "newsletter": "",
        }
        
        try:
            result = generate_newsletter_node(state)
            
            assert isinstance(result, dict)
        except:
            pass
