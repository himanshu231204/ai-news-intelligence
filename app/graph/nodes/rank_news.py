from __future__ import annotations

from app.graph.state import NewsState
from app.ranking.scorer import rank_news


def rank_news_node(state: NewsState) -> NewsState:
    new_state = dict(state)
    new_state["ranked_news"] = rank_news(state["filtered_news"])
    return new_state
