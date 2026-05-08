from __future__ import annotations

from app.graph.state import NewsState


def merge_results_node(state: NewsState) -> NewsState:
    """Normalize merge for downstream steps."""
    state.merged_news = list(state.raw_news)
    return state
