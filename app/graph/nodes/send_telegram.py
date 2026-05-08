from __future__ import annotations

from app.graph.state import NewsState
from app.telegram.bot import send_newsletter


def send_telegram_node(state: NewsState) -> NewsState:
    send_newsletter(state.newsletter)
    return state
