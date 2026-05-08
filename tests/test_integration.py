"""
Integration tests for AI News Research Agent
Tests the full workflow end-to-end
"""

import asyncio
from uuid import uuid4

import pytest

from app.graph.builder import build_graph
from app.config.settings import get_settings
from app.observability.langsmith import configure_langsmith
from app.memory.vectorstore import get_vectorstore
from app.ranking.deduplication import deduplicate_news
from app.graph.state import NewsItem
from app.ranking.embeddings import embed_texts


class TestEmbeddings:
    """Test embedding functionality"""

    def test_embed_texts(self) -> None:
        """Test text embedding generation"""
        texts = ["AI research paper", "Machine learning breakthrough"]
        embeddings = embed_texts(texts)
        
        assert len(embeddings) == 2
        assert all(len(emb) > 0 for emb in embeddings)

    def test_embed_empty_list(self) -> None:
        """Test embedding with empty list"""
        embeddings = embed_texts([])
        assert embeddings == []


class TestDeduplication:
    """Test deduplication logic"""

    def test_deduplicate_identical_urls(self) -> None:
        """Test deduplication of identical URLs"""
        items = [
            {"title": "AI News 1", "url": "https://example.com/1", "source": "news"},
            {"title": "AI News 1", "url": "https://example.com/1", "source": "news"},
        ]
        unique = deduplicate_news(items)
        assert len(unique) == 1

    def test_deduplicate_empty_list(self) -> None:
        """Test deduplication with empty list"""
        unique = deduplicate_news([])
        assert unique == []

    def test_preserve_different_items(self) -> None:
        """Test that different items are preserved"""
        items = [
            {"title": "AI News 1", "url": "https://example.com/1", "source": "news"},
            {"title": "AI News 2", "url": "https://example.com/2", "source": "news"},
            {"title": "AI News 3", "url": "https://example.com/3", "source": "news"},
        ]
        unique = deduplicate_news(items)
        assert len(unique) == 3


class TestVectorStore:
    """Test ChromaDB vectorstore"""

    def test_vectorstore_initialization(self) -> None:
        """Test vectorstore can be initialized"""
        vectorstore = get_vectorstore()
        assert vectorstore is not None
        assert vectorstore.collection is not None

    def test_vectorstore_singleton(self) -> None:
        """Test vectorstore singleton pattern"""
        vs1 = get_vectorstore()
        vs2 = get_vectorstore()
        assert vs1 is vs2

    def test_search_similar(self) -> None:
        """Test semantic search"""
        vectorstore = get_vectorstore()
        # This will use fallback embeddings if OpenAI is not available
        results = vectorstore.search_similar("AI research paper", n_results=5)
        assert isinstance(results, list)

    def test_check_duplicate(self) -> None:
        """Test duplicate checking"""
        vectorstore = get_vectorstore()
        # This should not crash even with fallback embeddings
        is_dup = vectorstore.check_duplicate("AI research", threshold=0.85)
        assert isinstance(is_dup, bool)


class TestWorkflow:
    """Test LangGraph workflow"""

    @pytest.mark.asyncio
    async def test_workflow_initialization(self) -> None:
        """Test workflow can be initialized"""
        app = build_graph()
        assert app is not None

    @pytest.mark.asyncio
    async def test_workflow_execution(self) -> None:
        """Test full workflow execution"""
        settings = get_settings()
        configure_langsmith(settings)
        
        app = build_graph()
        initial_state = {
            "raw_news": [],
            "merged_news": [],
            "unique_news": [],
            "filtered_news": [],
            "ranked_news": [],
            "summaries": [],
            "newsletter": "",
            "errors": [],
            "metadata": {},
        }
        
        result = await app.ainvoke(
            initial_state,
            config={"configurable": {"thread_id": str(uuid4())}},
        )
        
        # Verify result structure
        assert "newsletter" in result
        assert "errors" in result
        assert isinstance(result["newsletter"], str)
        assert isinstance(result["errors"], list)

    @pytest.mark.asyncio
    async def test_workflow_with_sample_data(self) -> None:
        """Test workflow with sample news data"""
        settings = get_settings()
        configure_langsmith(settings)
        
        app = build_graph()
        initial_state = {
            "raw_news": [
                {
                    "title": "New AI Model Released",
                    "url": "https://example.com/1",
                    "source": "test",
                    "published_at": "2024-05-09",
                }
            ],
            "merged_news": [],
            "unique_news": [],
            "filtered_news": [],
            "ranked_news": [],
            "summaries": [],
            "newsletter": "",
            "errors": [],
            "metadata": {},
        }
        
        result = await app.ainvoke(
            initial_state,
            config={"configurable": {"thread_id": str(uuid4())}},
        )
        
        # Verify workflow processed the data
        assert "newsletter" in result


class TestConfiguration:
    """Test configuration"""

    def test_settings_loading(self) -> None:
        """Test settings can be loaded"""
        settings = get_settings()
        assert settings is not None
        assert isinstance(settings.groq_model, str)

    def test_settings_caching(self) -> None:
        """Test settings are cached"""
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2


# Pytest fixtures
@pytest.fixture
def news_items() -> list[NewsItem]:
    """Fixture with sample news items"""
    return [
        {
            "title": "OpenAI Releases GPT-5",
            "url": "https://openai.com/news/1",
            "source": "openai",
            "published_at": "2024-05-09",
        },
        {
            "title": "Google AI Breakthrough",
            "url": "https://google.com/news/1",
            "source": "google",
            "published_at": "2024-05-09",
        },
    ]


def test_with_sample_data(news_items: list[NewsItem]) -> None:
    """Test with sample news items"""
    assert len(news_items) == 2
    assert news_items[0]["title"] == "OpenAI Releases GPT-5"


# Run all tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
