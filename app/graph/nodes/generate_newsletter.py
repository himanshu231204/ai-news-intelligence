from __future__ import annotations

from app.graph.state import NewsState
from app.newsletter.generator import build_newsletter


def generate_newsletter_node(state: NewsState) -> NewsState:
    newsletter = build_newsletter(state["ranked_news"], state["summaries"])
    new_state = dict(state)
    new_state["newsletter"] = newsletter
    return new_state
