from __future__ import annotations

import json
from typing import List

import httpx

from app.config.settings import get_settings
from app.graph.state import NewsItem
from app.utils.logger import get_logger
from app.utils.retry import async_retry

logger = get_logger(__name__)


def _fallback_summary(item: NewsItem) -> str:
    title = item.get("title", "Untitled")
    source = item.get("source", "unknown")
    return (
        f"Title: {title}\n"
        "Summary: Placeholder summary due to unavailable model response.\n"
        "Why it matters: Tracks AI momentum and community direction.\n"
        f"Source: {source}"
    )


async def _summarize_with_groq(item: NewsItem, api_key: str, model: str) -> str:
    title = item.get("title", "Untitled")
    source = item.get("source", "unknown")
    url = item.get("url", "")
    prompt = (
        "Return exactly this format with concise text and no markdown:\n"
        "Title:\nSummary:\nWhy it matters:\nSource:\n\n"
        f"Article title: {title}\n"
        f"Source: {source}\n"
        f"URL: {url}\n"
    )

    payload = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {
                "role": "system",
                "content": "You are a technical AI news editor focused on factual, concise summaries.",
            },
            {"role": "user", "content": prompt},
        ],
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            content=json.dumps(payload),
        )
        response.raise_for_status()
        data = response.json()

    return data["choices"][0]["message"]["content"].strip()


@async_retry(max_retries=3, backoff_factor=2, initial_delay=2)
async def summarize_batch(items: List[NewsItem]) -> List[str]:
    """Summarize news with Groq. Falls back to deterministic placeholders."""
    settings = get_settings()

    if not settings.groq_api_key:
        logger.warning("GROQ_API_KEY is not configured. Using fallback summaries.")
        return [_fallback_summary(item) for item in items]

    summaries = []
    for item in items:
        try:
            summary = await _summarize_with_groq(item, settings.groq_api_key, settings.groq_model)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Groq summarization failed for '%s': %s", item.get("title", "Untitled"), exc)
            summary = _fallback_summary(item)
        summaries.append(summary)

    return summaries
