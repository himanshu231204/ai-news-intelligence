"""News summarization with multi-provider LLM fallback.

This module provides:
- Batch summarization using LLMRouter
- Automatic fallback: Groq → OpenRouter → deterministic
- Token optimization (minimal content sent)
- Rate limiting between requests
"""

from __future__ import annotations

from typing import List

from app.graph.state import NewsItem
from app.llm.router import get_router
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def summarize_batch(items: List[NewsItem]) -> List[str]:
    """Summarize news items with automatic provider fallback.

    Flow: Groq (primary) → OpenRouter (fallback) → deterministic (final)

    Args:
        items: List of NewsItems to summarize

    Returns:
        List of formatted summary strings
    """
    if not items:
        logger.warning("No items to summarize")
        return []

    logger.info(f"Summarizing {len(items)} news items")

    router = get_router()
    summaries = await router.summarize_batch(items)

    logger.info(f"Completed summarization: {len(summaries)} summaries generated")
    return summaries


async def summarize_single(item: NewsItem) -> str:
    """Summarize a single news item.

    Args:
        item: NewsItem to summarize

    Returns:
        Formatted summary string
    """
    router = get_router()
    return await router.summarize(item)
