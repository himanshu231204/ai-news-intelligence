from __future__ import annotations

from app.graph.state import NewsState
from app.newsletter.generator import build_newsletter


def generate_newsletter_node(state: NewsState) -> NewsState:
    newsletter = build_newsletter(state.ranked_news, state.summaries)
    state.newsletter = newsletter
    return state
