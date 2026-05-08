from __future__ import annotations

from app.graph.state import NewsState


def merge_results_node(state: NewsState) -> NewsState:
    """Normalize merge for downstream steps."""
    new_state = dict(state)
    new_state["merged_news"] = list(state["raw_news"])
    return new_state
