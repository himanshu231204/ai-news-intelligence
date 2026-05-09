"""
LinkedIn Newsletter Generator

Generates long-form professional AI newsletter for LinkedIn publishing.
Uses Gemini → OpenRouter → error fallback (no template).
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from app.config.settings import get_settings
from app.graph.state import NewsItem
from app.newsletter.linkedin_prompts import LINKEDIN_NEWSLETTER_SYSTEM
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _parse_summary(summary: str) -> dict:
    """Parse summary into components."""
    parts = {"title": "", "summary": "", "why_it_matters": "", "source": ""}

    for line in summary.split("\n"):
        if line.startswith("Title:"):
            parts["title"] = line.replace("Title:", "").strip()
        elif line.startswith("Summary:"):
            parts["summary"] = line.replace("Summary:", "").strip()
        elif line.startswith("Why it matters:"):
            parts["why_it_matters"] = line.replace("Why it matters:", "").strip()
        elif line.startswith("Source:"):
            parts["source"] = line.replace("Source:", "").strip()

    return parts


async def build_linkedin_newsletter(
    items: List[NewsItem],
    summaries: List[str],
) -> str:
    """Build a long-form LinkedIn newsletter.

    Uses Gemini → OpenRouter → error fallback (no template).

    Args:
        items: List of ranked news items
        summaries: List of summaries from LLM

    Returns:
        Long-form LinkedIn newsletter string
    """
    # Format date: May 9, 2026
    today = datetime.now()
    formatted_date = today.strftime("%B %d, %Y")

    # Parse and pair summaries with items
    valid_pairs = []
    for i, summary in enumerate(summaries):
        if summary and i < len(items):
            parsed = _parse_summary(summary)
            if parsed["title"]:
                valid_pairs.append((items[i], parsed))

    settings = get_settings()

    # Try Gemini first
    if settings.gemini_api_key:
        try:
            newsletter = await _generate_with_gemini(valid_pairs, formatted_date)
            if newsletter:
                logger.info("LinkedIn newsletter generated via Gemini")
                return newsletter
        except Exception as e:
            logger.warning(f"Gemini LinkedIn newsletter generation failed: {e}")

    # Fallback to OpenRouter
    if settings.openrouter_api_key:
        try:
            newsletter = await _generate_with_openrouter(valid_pairs, formatted_date)
            if newsletter:
                logger.info("LinkedIn newsletter generated via OpenRouter")
                return newsletter
        except Exception as e:
            logger.warning(f"OpenRouter LinkedIn newsletter generation failed: {e}")

    # If both fail, return error message
    logger.error("All LLM providers failed for LinkedIn newsletter")
    return (
        "⚠️ LinkedIn newsletter generation failed.\n\n"
        "Error: All LLM providers are currently unavailable. "
        "Please try again later."
    )


async def _generate_with_gemini(
    valid_pairs: List[tuple],
    formatted_date: str,
) -> Optional[str]:
    """Generate LinkedIn newsletter using Gemini API."""
    from app.llm import providers

    # Build article list (limited to 25 for token optimization)
    article_list = []
    for idx, (item, parsed) in enumerate(valid_pairs[:25], start=1):
        article_list.append(
            f"Article {idx}:\n"
            f"Title: {parsed.get('title', '')}\n"
            f"Source: {parsed.get('source', '')}\n"
            f"Summary: {parsed.get('summary', '')}\n"
            f"Why it matters: {parsed.get('why_it_matters', '')}\n"
        )

    system_prompt = LINKEDIN_NEWSLETTER_SYSTEM.format(current_date=formatted_date)

    user_content = (
        f"Date: {formatted_date}\n\n"
        "Write a detailed, professional AI newsletter for LinkedIn publishing.\n"
        "Follow the structure in the system prompt exactly.\n"
        "Write in paragraphs, not bullet points (except Key Takeaways).\n"
        "Make it sound human-written and editorial quality.\n\n"
        "Articles to cover:\n\n" + "\n".join(article_list)
    )

    result = await providers.call_gemini(
        prompt=user_content,
        system=system_prompt,
        model="gemini-2.5-flash",
        temperature=0.3,
    )

    if result:
        # Ensure proper footer
        if "About the Author" not in result and "👤" not in result:
            result += (
                "\n\n---\n\n"
                "👤 About the Author\n\n"
                "Himanshu is an AI engineer and technical creator building "
                "with large language models, AI agents, and modern ML infrastructure. "
                "He shares insights on AI developments, engineering practices, "
                "and the future of AI technology."
            )
        return result.rstrip()

    return None


async def _generate_with_openrouter(
    valid_pairs: List[tuple],
    formatted_date: str,
) -> Optional[str]:
    """Generate LinkedIn newsletter using OpenRouter API."""
    from app.llm import providers

    # Build article list (limited to 25 for token optimization)
    article_list = []
    for idx, (item, parsed) in enumerate(valid_pairs[:25], start=1):
        article_list.append(
            f"Article {idx}:\n"
            f"Title: {parsed.get('title', '')}\n"
            f"Source: {parsed.get('source', '')}\n"
            f"Summary: {parsed.get('summary', '')}\n"
            f"Why it matters: {parsed.get('why_it_matters', '')}\n"
        )

    system_prompt = LINKEDIN_NEWSLETTER_SYSTEM.format(current_date=formatted_date)

    user_content = (
        f"Date: {formatted_date}\n\n"
        "Write a detailed, professional AI newsletter for LinkedIn publishing.\n"
        "Follow the structure in the system prompt exactly.\n"
        "Write in paragraphs, not bullet points (except Key Takeaways).\n"
        "Make it sound human-written and editorial quality.\n\n"
        "Articles to cover:\n\n" + "\n".join(article_list)
    )

    settings = get_settings()
    result = await providers.call_openrouter(
        prompt=user_content,
        system=system_prompt,
        model=settings.openrouter_model,
        temperature=0.3,
    )

    if result:
        # Ensure proper footer
        if "About the Author" not in result and "👤" not in result:
            result += (
                "\n\n---\n\n"
                "👤 About the Author\n\n"
                "Himanshu is an AI engineer and technical creator building "
                "with large language models, AI agents, and modern ML infrastructure. "
                "He shares insights on AI developments, engineering practices, "
                "and the future of AI technology."
            )
        return result.rstrip()

    return None
