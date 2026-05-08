from __future__ import annotations

from app.graph.state import NewsState


def filter_low_quality_node(state: NewsState) -> NewsState:
    """Remove items missing required fields."""
    filtered = [
        item
        for item in state["unique_news"]
        if item.get("title") and item.get("url") and item.get("source")
    ]
    new_state = dict(state)
    new_state["filtered_news"] = filtered
    return new_state
