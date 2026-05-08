from __future__ import annotations

import logging
from app.graph.state import NewsState, NewsItem
from app.collectors.filter_utils import (
    filter_low_quality_items,
    rank_filtered_items,
    get_filter_stats,
)

logger = logging.getLogger(__name__)


def filter_low_quality_node(state: NewsState) -> NewsState:
    """Filter low-quality news items and rank by importance.

    Uses company detection, category, and importance score to filter
    and rank items. Provides detailed logging of filter statistics.
    """
    # Convert state dict to list of NewsItem if needed
    unique_items = []
    for item in state.unique_news:
        if isinstance(item, NewsItem):
            unique_items.append(item)
        elif isinstance(item, dict):
            unique_items.append(NewsItem(**item))

    # Filter low quality items
    filtered_items = filter_low_quality_items(unique_items)

    # Rank filtered items by filter score
    ranked_items = rank_filtered_items(filtered_items)

    # Get filter statistics
    stats = get_filter_stats(unique_items, ranked_items)

    logger.info(
        f"Filter stats: {stats['removed_items']}/{stats['total_items']} "
        f"removed ({stats['filter_rate']}% filter rate). "
        f"Avg importance: {stats['avg_importance_before']} -> {stats['avg_importance_after']}"
    )

    # Update state
    state.filtered_news = ranked_items
    return state
