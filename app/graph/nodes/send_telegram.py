from __future__ import annotations

from app.graph.state import NewsState
from app.telegram.bot import send_newsletter
from app.utils.logger import get_logger

logger = get_logger(__name__)


def send_telegram_node(state: NewsState) -> NewsState:
    try:
        send_newsletter(state.newsletter)
    except Exception as e:
        logger.error("Failed to send Telegram message: %s", e)
        # Don't raise - allow workflow to continue
    return state
