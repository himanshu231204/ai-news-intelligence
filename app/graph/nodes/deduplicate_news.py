from __future__ import annotations

from app.graph.state import NewsState
from app.ranking.deduplication import deduplicate_news


def deduplicate_news_node(state: NewsState) -> NewsState:
    state.unique_news = deduplicate_news(state.merged_news)
    return state
