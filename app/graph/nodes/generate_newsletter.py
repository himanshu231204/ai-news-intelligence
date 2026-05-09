from __future__ import annotations

from app.graph.state import NewsState
from app.newsletter.generator import build_newsletter


async def generate_newsletter_node(state: NewsState) -> NewsState:
    """Generate the newsletter using Gemini with template fallback."""
    newsletter = await build_newsletter(state.ranked_news, state.summaries)
    state.newsletter = newsletter
    return state
