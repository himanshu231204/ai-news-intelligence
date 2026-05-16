from __future__ import annotations

from app.graph.state import NewsState
from app.ranking.deduplication import deduplicate_news


def deduplicate_news_node(state: NewsState) -> NewsState:
    # Use keyword-filtered items when available; otherwise fall back to merged input.
    # This preserves the intended early keyword filter optimization.
    items_to_dedup = state.unique_news or state.merged_news
    state.unique_news = deduplicate_news(items_to_dedup)
    return state
