from __future__ import annotations

from textwrap import wrap

import requests

from app.config.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def send_newsletter(message: str) -> None:
    """Send newsletter message to configured Telegram chat.

    Defensive: collapse repeated footer blocks to avoid spamming the footer
    across multiple chunks if the newsletter text already contains duplicates.
    """
    def _collapse_footer(msg: str) -> str:
        key = "Follow for more AI insights"
        first = msg.find(key)
        if first == -1:
            return msg
        # Keep everything up to the first footer occurrence, then append a single footer block
        head = msg[:first]
        tail = msg[first:]
        # Find canonical footer end marker (the last rule '━' sequence)
        # Trim any subsequent repeated occurrences by keeping only the first footer block
        # Split tail by the footer key and take the first chunk
        parts = tail.split(key)
        if not parts:
            return msg
        # Rebuild single footer: key + remainder of the first occurrence
        single_footer = key + parts[1]
        return head + single_footer

    # Collapse duplicated footer blocks defensively
    message = _collapse_footer(message)

    settings = get_settings()
    if not settings.telegram_bot_token:
        logger.warning("TELEGRAM_BOT_TOKEN not configured. Skipping send.")
        return

    if not settings.telegram_chat_id:
        logger.warning("TELEGRAM_CHAT_ID not configured. Skipping send.")
        return

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    chunks = wrap(message, 3800, break_long_words=False, replace_whitespace=False) or [message]

    for index, chunk in enumerate(chunks, start=1):
        response = requests.post(
            url,
            json={
                "chat_id": settings.telegram_chat_id,
                "text": chunk,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True,
            },
            timeout=30,
        )
        if not response.ok:
            logger.error("Telegram send failed on chunk %s/%s: %s", index, len(chunks), response.text)
            response.raise_for_status()

    logger.info("Newsletter sent to Telegram in %s chunk(s). chars=%s", len(chunks), len(message))
