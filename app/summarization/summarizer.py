from __future__ import annotations

import asyncio
import json
from typing import List

import httpx

from app.config.settings import get_settings
from app.graph.state import NewsItem
from app.utils.logger import get_logger
from app.utils.retry import async_retry

logger = get_logger(__name__)


def _generate_fallback_summary(item: NewsItem) -> str:
    """Generate a deterministic fallback summary from available data."""
    title = item.title or "Untitled"
    source = item.source or "unknown"
    url = item.url or ""

    # Try to extract useful info from available fields
    summary_parts = []

    # Extract repo name from GitHub URLs
    if "github.com" in url:
        parts = url.rstrip("/").split("/")
        if len(parts) >= 2:
            repo = f"{parts[-2]}/{parts[-1]}"
            summary_parts.append(f"GitHub repository: {repo}")

    # Use score if available (e.g., GitHub stars, HN points)
    if item.score and item.score > 0:
        summary_parts.append(f"Popularity score: {item.score}")

    # Use category if detected
    if item.category:
        summary_parts.append(f"Category: {item.category}")

    # Use company if detected
    if item.company:
        summary_parts.append(f"Company: {item.company}")

    summary_text = (
        "; ".join(summary_parts)
        if summary_parts
        else "Trending repository in AI/ML space"
    )

    return (
        f"Title: {title}\n"
        f"Summary: {summary_text}\n"
        "Why it matters: Tracks AI momentum and community direction.\n"
        f"Source: {source}"
    )


async def _summarize_with_openrouter(
    item: NewsItem, api_key: str, model: str, max_retries: int = 3
) -> str:
    """Summarize using OpenRouter API with retry logic."""
    title = item.title or "Untitled"
    source = item.source or "unknown"
    url = item.url or ""
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

    delay = 1.0
    last_exception = None

    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://github.com/himanshu231204/ai-news-agent",
                        "X-Title": "AI News Agent",
                    },
                    content=json.dumps(payload),
                )
                response.raise_for_status()
                data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            last_exception = e
            if attempt < max_retries - 1:
                logger.warning(
                    "OpenRouter attempt %d/%d failed for '%s': %s. Retrying in %.1fs...",
                    attempt + 1,
                    max_retries,
                    title,
                    e,
                    delay,
                )
                await asyncio.sleep(delay)
                delay *= 2

    raise last_exception


async def _summarize_with_groq(
    item: NewsItem, api_key: str, model: str, max_retries: int = 3
) -> str:
    """Summarize using Groq API with retry logic."""
    title = item.title or "Untitled"
    source = item.source or "unknown"
    url = item.url or ""
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

    delay = 1.0
    last_exception = None

    for attempt in range(max_retries):
        try:
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
        except Exception as e:
            last_exception = e
            if attempt < max_retries - 1:
                logger.warning(
                    "Groq attempt %d/%d failed for '%s': %s. Retrying in %.1fs...",
                    attempt + 1,
                    max_retries,
                    title,
                    e,
                    delay,
                )
                await asyncio.sleep(delay)
                delay *= 2

    raise last_exception


@async_retry(max_retries=1, backoff_factor=2, initial_delay=2)
async def summarize_batch(items: List[NewsItem]) -> List[str]:
    """Summarize news with OpenRouter (primary) or Groq (fallback)."""
    settings = get_settings()

    # Determine which API to use
    use_openrouter = bool(settings.openrouter_api_key)
    use_groq = bool(settings.groq_api_key)

    if not use_openrouter and not use_groq:
        logger.warning("No LLM API configured. Using fallback summaries.")
        return [_generate_fallback_summary(item) for item in items]

    summaries = []
    for item in items:
        summary = None

        # Try OpenRouter first
        if use_openrouter:
            try:
                summary = await _summarize_with_openrouter(
                    item, settings.openrouter_api_key, settings.openrouter_model
                )
            except Exception as e:
                logger.warning(
                    "OpenRouter failed for '%s': %s", item.title or "Untitled", e
                )

        # Fall back to Groq if OpenRouter failed
        if not summary and use_groq:
            try:
                summary = await _summarize_with_groq(
                    item, settings.groq_api_key, settings.groq_model
                )
            except Exception as e:
                logger.warning("Groq failed for '%s': %s", item.title or "Untitled", e)

        # Final fallback to deterministic summary
        if not summary:
            logger.warning(
                "All LLM APIs failed. Using fallback for '%s'.",
                item.title or "Untitled",
            )
            summary = _generate_fallback_summary(item)

        # Small delay between requests
        await asyncio.sleep(0.3)
        summaries.append(summary)

    return summaries
