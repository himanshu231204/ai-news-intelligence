from __future__ import annotations

from app.graph.state import NewsState
from app.ranking.deduplication import deduplicate_news


def deduplicate_news_node(state: NewsState) -> NewsState:
    new_state = dict(state)
    new_state["unique_news"] = deduplicate_news(state["merged_news"])
    return new_state
