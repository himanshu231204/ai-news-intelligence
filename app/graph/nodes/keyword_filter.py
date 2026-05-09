"""Keyword filtering node for AI news articles.

This node runs BEFORE LLM processing to filter out non-AI content.
Uses local keyword matching (no LLM needed) to reduce API usage.

OPTIMIZATION: This is the FIRST filter in the pipeline - removes
non-AI articles before any expensive LLM calls are made.
"""

from __future__ import annotations

import logging
from app.graph.state import NewsState, NewsItem
from app.collectors.keyword_filter import filter_by_keywords, get_keyword_stats

logger = logging.getLogger(__name__)


def keyword_filter_node(state: NewsState) -> NewsState:
    """Filter articles using keyword matching BEFORE LLM processing.

    This runs early in the pipeline to remove non-AI content
    before any expensive LLM calls are made.

    Args:
        state: Current news state

    Returns:
        Updated state with keyword-filtered articles
    """
    # Get items to filter (use merged_news if available, otherwise raw_news)
    items_to_filter = state.merged_news or state.raw_news

    if not items_to_filter:
        logger.warning("No items to keyword filter")
        state.errors.append("No items to filter")
        return state

    # Convert to NewsItem if needed
    items = []
    for item in items_to_filter:
        if isinstance(item, NewsItem):
            items.append(item)
        elif isinstance(item, dict):
            items.append(NewsItem(**item))

    # Apply keyword filtering
    filtered_items = filter_by_keywords(items)

    # Get statistics
    stats = get_keyword_stats(items, filtered_items)

    logger.info(
        f"Keyword filter: {stats['removed_items']}/{stats['total_items']} "
        f"articles removed ({stats['filter_rate']}% filter rate)"
    )

    # Update state - add to unique_news for next stage
    state.unique_news = filtered_items

    return state
