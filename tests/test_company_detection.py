"""Tests for company detection and importance scoring."""

import pytest
from app.utils.company_detector import (
    detect_company,
    detect_category,
    calculate_importance,
    is_negative_content,
    extract_tags,
    enrich_news_item,
    PRIORITY_COMPANIES,
    PRIORITY_TOPICS,
)


class TestCompanyDetection:
    """Test company detection from titles and summaries."""

    def test_detect_openai(self):
        assert (
            detect_company("OpenAI releases GPT-5", "New model from OpenAI") == "OpenAI"
        )
        assert (
            detect_company("ChatGPT gets new features", "OpenAI announces update")
            == "OpenAI"
        )

    def test_detect_anthropic(self):
        assert (
            detect_company("Claude 3.5 released", "Anthropic announces new model")
            == "Anthropic"
        )

    def test_detect_google_deepmind(self):
        assert (
            detect_company("Gemini 2.0 launched", "Google DeepMind announces")
            == "Google DeepMind"
        )

    def test_detect_meta(self):
        assert (
            detect_company("Llama 4 released", "Meta AI announces new model")
            == "Meta AI"
        )

    def test_detect_nvidia(self):
        assert (
            detect_company("New NVIDIA GPU announced", "Blackwell architecture")
            == "NVIDIA AI"
        )

    def test_detect_langchain(self):
        assert (
            detect_company("LangGraph 0.2 released", "New agent framework")
            == "LangChain"
        )

    def test_no_company_detected(self):
        assert detect_company("Random tech news", "Some random article") is None


class TestCategoryDetection:
    """Test topic category detection."""

    def test_detect_model_release(self):
        assert (
            detect_category("GPT-5 released", "New model launched") == "model_release"
        )

    def test_detect_research(self):
        assert (
            detect_category("New paper on transformers", "ArXiv research") == "research"
        )

    def test_detect_funding(self):
        assert (
            detect_category("AI startup raises $100M", "Series B funding") == "funding"
        )

    def test_detect_agents(self):
        assert detect_category("Agentic AI trends", "Autonomous systems") == "agents"

    def test_detect_reasoning(self):
        assert (
            detect_category("Reasoning model improvements", "Chain of thought")
            == "reasoning"
        )


class TestImportanceScoring:
    """Test importance score calculation."""

    def test_high_importance_with_company(self):
        score = calculate_importance(
            "OpenAI", "model_release", "OpenAI releases GPT-5", 100
        )
        assert score >= 6.0

    def test_medium_importance_with_category(self):
        score = calculate_importance(None, "research", "New AI research paper", 50)
        assert 1.0 <= score <= 5.0

    def test_low_importance_no_match(self):
        score = calculate_importance(None, None, "Random article", 10)
        assert score < 3.0

    def test_score_cap_at_10(self):
        score = calculate_importance("OpenAI", "model_release", "OpenAI GPT-5", 500)
        assert score <= 10.0


class TestNegativeContentFiltering:
    """Test negative content filtering."""

    def test_filter_crypto(self):
        assert is_negative_content("Bitcoin price surges", "Crypto news") is True

    def test_filter_non_ai(self):
        assert is_negative_content("Sports results", "Game scores") is True

    def test_allow_ai_content(self):
        assert is_negative_content("OpenAI releases GPT-5", "New AI model") is False


class TestTagExtraction:
    """Test tag extraction from content."""

    def test_extract_company_tags(self):
        tags = extract_tags("OpenAI releases GPT-5", "OpenAI and Anthropic")
        assert "OpenAI" in tags
        assert "Anthropic" in tags

    def test_tag_limit(self):
        long_text = " ".join([f"keyword{i}" for i in range(20)])
        tags = extract_tags(long_text, long_text)
        assert len(tags) <= 10


class TestEnrichNewsItem:
    """Test full news item enrichment."""

    def test_enrich_with_all_fields(self):
        result = enrich_news_item("OpenAI releases GPT-5", "New model from OpenAI", 100)
        assert result["company"] == "OpenAI"
        assert result["category"] == "model_release"
        assert result["importance_score"] >= 5.0

    def test_enrich_minimal_content(self):
        result = enrich_news_item("Random article", "Some text", 10)
        assert result["company"] is None
        assert result["importance_score"] < 3.0


class TestPriorityConstants:
    """Test priority constants are defined."""

    def test_priority_companies_defined(self):
        assert len(PRIORITY_COMPANIES) > 0
        assert "OpenAI" in PRIORITY_COMPANIES

    def test_priority_topics_defined(self):
        assert len(PRIORITY_TOPICS) > 0
        assert "LLMs" in PRIORITY_TOPICS
