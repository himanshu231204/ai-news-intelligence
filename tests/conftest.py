"""
Pytest fixtures and test configuration
"""

import pytest
import asyncio
from typing import List, Dict, Any
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime


@pytest.fixture
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_news_items() -> List[Dict[str, Any]]:
    """Sample news items for testing"""
    return [
        {
            "title": "OpenAI Releases GPT-5",
            "summary": "OpenAI announces GPT-5 with improved reasoning",
            "url": "https://example.com/gpt5",
            "source": "OpenAI Blog",
            "published_date": datetime.now().isoformat(),
            "content": "OpenAI has announced GPT-5...",
            "image_url": "https://example.com/gpt5.jpg",
        },
        {
            "title": "Anthropic Launches Claude 4",
            "summary": "Anthropic introduces Claude 4 with enhanced capabilities",
            "url": "https://example.com/claude4",
            "source": "Anthropic Blog",
            "published_date": datetime.now().isoformat(),
            "content": "Anthropic has launched Claude 4...",
            "image_url": "https://example.com/claude4.jpg",
        },
        {
            "title": "Google Releases Gemini Ultra",
            "summary": "Google unveils Gemini Ultra model",
            "url": "https://example.com/gemini",
            "source": "Google Blog",
            "published_date": datetime.now().isoformat(),
            "content": "Google has released Gemini Ultra...",
            "image_url": "https://example.com/gemini.jpg",
        },
    ]


@pytest.fixture
def duplicate_news_items() -> List[Dict[str, Any]]:
    """Duplicate news items for deduplication testing"""
    return [
        {
            "title": "OpenAI Releases GPT-5",
            "summary": "OpenAI announces GPT-5",
            "url": "https://example.com/gpt5",
            "source": "OpenAI Blog",
            "published_date": datetime.now().isoformat(),
            "content": "OpenAI GPT-5 release",
        },
        {
            "title": "OpenAI Releases GPT-5",  # Exact duplicate
            "summary": "OpenAI announces GPT-5",
            "url": "https://example.com/gpt5",
            "source": "OpenAI Official",
            "published_date": datetime.now().isoformat(),
            "content": "OpenAI GPT-5 release",
        },
        {
            "title": "GPT-5 Released by OpenAI",  # Semantic duplicate
            "summary": "OpenAI's new GPT-5 model",
            "url": "https://example.com/gpt5-mirror",
            "source": "Tech News",
            "published_date": datetime.now().isoformat(),
            "content": "OpenAI has released their latest model GPT-5",
        },
    ]


@pytest.fixture
def low_quality_items() -> List[Dict[str, Any]]:
    """Low quality news items for filtering"""
    return [
        {
            "title": "Random text",
            "summary": "asdf qwer",
            "url": "https://spam.com/1",
            "source": "Spam Source",
            "published_date": datetime.now().isoformat(),
            "content": "xyz abc",
        },
        {
            "title": "",  # Empty title
            "summary": "No content",
            "url": "https://empty.com/1",
            "source": "Bad Source",
            "published_date": datetime.now().isoformat(),
            "content": "",
        },
        {
            "title": "!!!!!!",  # Suspicious
            "summary": "Click here!!!",
            "url": "https://clickbait.com/1",
            "source": "Clickbait",
            "published_date": datetime.now().isoformat(),
            "content": "Buy now! Free money!",
        },
    ]


@pytest.fixture
def mock_telegram_bot():
    """Mock Telegram bot for testing"""
    bot = AsyncMock()
    bot.send_message = AsyncMock(return_value=MagicMock(message_id=123))
    bot.send_photo = AsyncMock(return_value=MagicMock(message_id=124))
    return bot


@pytest.fixture
def mock_groq_client():
    """Mock Groq LLM client"""
    client = MagicMock()
    client.chat.completions.create = MagicMock(
        return_value=MagicMock(
            choices=[MagicMock(message=MagicMock(content="This is a test summary."))]
        )
    )
    return client


@pytest.fixture
def mock_chromadb_collection():
    """Mock ChromaDB collection"""
    collection = MagicMock()
    collection.query = MagicMock(
        return_value={
            "ids": [["doc1", "doc2"]],
            "distances": [[0.1, 0.5]],
            "documents": [["Document 1", "Document 2"]],
        }
    )
    collection.add = MagicMock()
    return collection


@pytest.fixture
def mock_embeddings():
    """Mock embeddings function"""
    def embed(texts):
        return [[0.1 * i for _ in range(384)] for i in range(len(texts))]
    return embed


@pytest.fixture
def settings_mock(monkeypatch):
    """Mock settings for testing"""
    mock_settings = {
        "groq_api_key": "test_key",
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
        "telegram_bot_token": "test_token",
        "telegram_chat_id": "123456",
        "postgres_url": "",
        "use_postgres_checkpoint": False,
        "similarity_threshold": 0.85,
        "max_items_per_source": 10,
        "newsletter_hour": 9,
        "newsletter_minute": 0,
    }
    return mock_settings


# Parametrize test data for different scenarios
QUALITY_SCORES = [
    (0.95, True),   # High quality
    (0.5, False),   # Medium quality (below threshold)
    (0.2, False),   # Low quality
    (0.0, False),   # No quality
    (1.0, True),    # Perfect quality
]

RANKING_SCORES = [
    ("breaking-news", 0.95),
    ("research", 0.75),
    ("tutorial", 0.5),
    ("promotional", 0.2),
]

ERROR_SCENARIOS = [
    ("network_error", Exception("Network error")),
    ("timeout", TimeoutError("Request timeout")),
    ("invalid_data", ValueError("Invalid data format")),
    ("api_error", RuntimeError("API Error")),
]
