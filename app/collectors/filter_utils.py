"""Filter utilities for AI news articles.

This module provides filtering logic based on quality, relevance,
keyword matching, and importance scoring for the news collection pipeline.

Key optimization: Keyword filtering runs BEFORE LLM calls to reduce API usage.
"""

from __future__ import annotations

from typing import List
from app.graph.state import NewsItem


# Minimum thresholds
MIN_TITLE_LENGTH = 10
MAX_TITLE_LENGTH = 300
MIN_SUMMARY_LENGTH = 20
MIN_IMPORTANCE_SCORE = 0.5


# Import keyword filter for early-stage filtering
def filter_by_keywords_early(items: List[NewsItem]) -> List[NewsItem]:
    """Apply keyword filtering before LLM processing.

    This is the FIRST filter in the pipeline - runs before quality filtering.
    Uses local keyword matching (no LLM needed) to remove non-AI content.

    Args:
        items: List of NewsItems to filter

    Returns:
        Filtered list of AI-related NewsItems
    """
    from app.collectors.keyword_filter import filter_by_keywords

    return filter_by_keywords(items)


def is_low_quality(item: NewsItem) -> bool:
    """Check if a news item is low quality and should be filtered.

    Args:
        item: NewsItem to check

    Returns:
        True if item should be filtered out
    """
    # Check title length
    title = item.title or ""
    if len(title) < MIN_TITLE_LENGTH or len(title) > MAX_TITLE_LENGTH:
        return True

    # Check summary length (if exists)
    summary = item.summary or ""
    if summary and len(summary) < MIN_SUMMARY_LENGTH:
        # Allow if there's importance score from company detection
        if item.importance_score < 1.0:
            return True

    # Check importance score threshold
    if item.importance_score < MIN_IMPORTANCE_SCORE:
        return True

    # Check for missing URL
    if not item.url or not item.url.startswith("http"):
        return True

    # Check for missing source
    if not item.source:
        return True

    return False


def filter_low_quality_items(items: List[NewsItem]) -> List[NewsItem]:
    """Filter out low-quality news items.

    Args:
        items: List of NewsItem to filter

    Returns:
        Filtered list of NewsItem
    """
    filtered = []
    for item in items:
        if not is_low_quality(item):
            filtered.append(item)

    return filtered


def calculate_filter_score(item: NewsItem) -> float:
    """Calculate a filter score for ranking within filtered items.

    Args:
        item: NewsItem to score

    Returns:
        Filter score from 0.0 to 10.0
    """
    score = 0.0

    # Importance score weight (0-5)
    score += min(item.importance_score, 5.0)

    # Company match bonus (0-2)
    if item.company:
        score += 2.0

    # Category bonus (0-1)
    if item.category:
        score += 1.0

    # Source score bonus (0-2)
    if item.score > 100:
        score += 2.0
    elif item.score > 50:
        score += 1.0

    return min(score, 10.0)


def rank_filtered_items(items: List[NewsItem]) -> List[NewsItem]:
    """Rank filtered items by filter score.

    Args:
        items: List of filtered NewsItem

    Returns:
        Sorted list of NewsItem by filter score descending
    """
    scored_items = []
    for item in items:
        item_dict = dict(item)
        item_dict["_filter_score"] = calculate_filter_score(item)
        scored_items.append(item_dict)

    scored_items.sort(key=lambda x: x.get("_filter_score", 0.0), reverse=True)

    # Remove internal score and return as NewsItem
    result = []
    for item_dict in scored_items:
        item_dict.pop("_filter_score", None)
        result.append(NewsItem(**item_dict))

    return result


def get_filter_stats(items: List[NewsItem], filtered_items: List[NewsItem]) -> dict:
    """Get statistics about filtering results.

    Args:
        items: Original list before filtering
        filtered_items: List after filtering

    Returns:
        Dictionary with filter statistics
    """
    return {
        "total_items": len(items),
        "filtered_items": len(filtered_items),
        "removed_items": len(items) - len(filtered_items),
        "filter_rate": round((len(items) - len(filtered_items)) / len(items) * 100, 1)
        if items
        else 0,
        "avg_importance_before": round(
            sum(i.importance_score for i in items) / len(items), 2
        )
        if items
        else 0,
        "avg_importance_after": round(
            sum(i.importance_score for i in filtered_items) / len(filtered_items), 2
        )
        if filtered_items
        else 0,
    }
