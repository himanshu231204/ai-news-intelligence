from __future__ import annotations

from datetime import date, datetime
import re
from typing import List

from app.graph.state import NewsItem
import httpx

from app.config.settings import get_settings
from app.newsletter.prompts import NEWSLETTER_GENERATION_PROMPT
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

    # Remove any footer-like lines that may be present in summaries
    parts["title"] = _strip_footer(parts["title"])
    parts["summary"] = _strip_footer(parts["summary"])
    parts["why_it_matters"] = _strip_footer(parts["why_it_matters"])
    parts["source"] = _strip_footer(parts["source"])

    return parts


def _strip_footer(text: str) -> str:
    """Remove common footer lines that may be injected into LLM summaries."""
    if not text:
        return text

    lines = []
    for line in text.splitlines():
        low = line.lower().strip()
        if (
            "linkedin.com" in low
            or "github.com" in low
            or "follow me" in low
            or "powered by" in low
            or low.startswith("follow for")
        ):
            continue
        if low.startswith("http") and ("linkedin" in low or "github" in low):
            continue
        lines.append(line)

    return "\n".join(lines).strip()


def _format_article_compact(counter: int, parsed: dict, emoji: str = "") -> str:
    """Format article in compact style."""
    title = parsed.get("title", "Untitled")
    summary = parsed.get("summary", "")
    source = parsed.get("source", "unknown")

    # Shorten summary to first sentence if very long
    first_sentence = summary.split(". ")[0].strip()
    if first_sentence and not first_sentence.endswith("."):
        first_sentence = first_sentence + "."

    return f"{counter}. {emoji} {title} — {first_sentence} ({source})\n"


def _format_article_detailed(counter: int, parsed: dict, emoji: str = "") -> str:
    """Format article in detailed style matching the premium template."""
    title = parsed.get("title", "Untitled")
    summary = parsed.get("summary", "")
    why_it_matters = parsed.get("why_it_matters", "")
    source = parsed.get("source", "unknown")

    lines = [
        f"{counter}. {emoji} {title}",
        summary,
    ]

    if why_it_matters:
        lines.append(f"The Shift: {why_it_matters}")

    lines.append(f"Source: {source}")
    lines.append("")

    return "\n".join(lines)


async def build_newsletter(items: List[NewsItem], summaries: List[str]) -> str:
    """Build a professionally formatted newsletter matching enterprise standards.

    Uses Gemini for LLM-based generation with template fallback.

    Args:
        items: List of ranked news items
        summaries: List of summaries from LLM

    Returns:
        Formatted newsletter string
    """

    # Format date: Saturday, May 09, 2026
    today = datetime.now()
    day_name = today.strftime("%A")
    date_str = today.strftime("%B %d, %Y")
    formatted_date = f"{day_name}, {date_str}"

    # Parse and pair summaries with items
    valid_pairs = []
    for i, summary in enumerate(summaries):
        if summary and i < len(items):
            parsed = _parse_summary(summary)
            if parsed["title"]:
                valid_pairs.append((items[i], parsed))

    # Try Gemini-based generation first (primary provider for newsletter)
    settings = get_settings()

    if settings.gemini_api_key:
        try:
            # Use the LLM router for Gemini generation
            from app.llm.router import get_router

            router = get_router()

            newsletter = await router.generate_newsletter(
                items, summaries, formatted_date
            )

            if newsletter:
                logger.info("Newsletter generated via Gemini")
                return newsletter

        except Exception as e:
            logger.warning(f"Gemini newsletter generation failed: {e}")

    # Fallback: Programmatic template matching the premium design
    logger.info("Using template fallback for newsletter")
    return _build_fallback_newsletter(valid_pairs, formatted_date)


def _build_fallback_newsletter(valid_pairs: List, formatted_date: str) -> str:
    """Build newsletter using the enhanced template format."""

    # Categorize items by detected company/category
    breaking_news = []
    model_releases = []
    ai_agents = []
    research_papers = []
    opensource = []
    funding = []
    products = []
    other_news = []

    # Company keywords for categorization
    company_keywords = {
        "openai": "OpenAI",
        "anthropic": "Anthropic",
        "google": "Google",
        "deepmind": "DeepMind",
        "meta": "Meta",
        "microsoft": "Microsoft",
        "nvidia": "NVIDIA",
        "x.ai": "xAI",
        "mistral": "Mistral",
        "hugging face": "HuggingFace",
        "stability": "Stability AI",
        "cohere": "Cohere",
        "amazon": "Amazon",
    }

    for item, parsed in valid_pairs[:25]:
        title = (parsed.get("title", "") or "").lower()
        summary = (parsed.get("summary", "") or "").lower()
        source = (item.source or "").lower()
        company = (item.company or "").lower()

        # Check for funding keywords
        if any(
            kw in title or kw in summary
            for kw in [
                "funding",
                "raises",
                "series",
                "acquired",
                "investment",
                "million",
                "billion",
            ]
        ):
            funding.append(parsed)
            continue

        # Check for model release keywords
        if any(
            kw in title
            for kw in [
                "model",
                "gpt",
                "claude",
                "gemini",
                "llama",
                "release",
                "launch",
                "announce",
            ]
        ):
            model_releases.append(parsed)
            continue

        # Check for research (arxiv)
        if source == "arxiv" or "arxiv" in source:
            research_papers.append(parsed)
            continue

        # Check for open source / GitHub
        if source == "github" or "github" in source or "huggingface" in source:
            opensource.append(parsed)
            continue

        # Check for agent/coding keywords
        if any(
            kw in title
            for kw in ["agent", "coding", "dev", "tool", "framework", "sdk", "api"]
        ):
            ai_agents.append(parsed)
            continue

        # Check for product/demo keywords
        if any(
            kw in title
            for kw in ["demo", "product", "launch", "release", "beta", "preview"]
        ):
            products.append(parsed)
            continue

        # Default to other news
        other_news.append(parsed)

    # Build the enhanced template
    lines = []

    # Header
    lines.append(f"🧠 AI DAILY BRIEF — {formatted_date}")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")

    # BREAKING NEWS (if any major announcements)
    if breaking_news:
        lines.append("🚨 BREAKING NEWS")
        lines.append("")
        for article in breaking_news[:2]:
            title = article.get("title", "Untitled")
            summary = article.get("summary", "")[:100]
            lines.append(f"• {title} - {summary}")
        lines.append("")

    # MODEL RELEASES
    if model_releases:
        lines.append("🤖 MODEL RELEASES")
        lines.append("")
        for article in model_releases[:4]:
            title = article.get("title", "Untitled")[:70]
            why = article.get("why_it_matters", "")[:80]
            lines.append(f"• {title}")
            if why:
                lines.append(f"  → {why}")
        lines.append("")

    # AI AGENTS & CODING
    if ai_agents:
        lines.append("💻 AI AGENTS & CODING")
        lines.append("")
        for article in ai_agents[:4]:
            title = article.get("title", "Untitled")[:70]
            lines.append(f"• {title}")
        lines.append("")

    # RESEARCH PAPERS
    if research_papers:
        lines.append("📄 RESEARCH PAPERS")
        lines.append("")
        for article in research_papers[:4]:
            title = article.get("title", "Untitled")[:65]
            lines.append(f"• {title}")
        lines.append("")

    # OPEN SOURCE
    if opensource:
        lines.append("🛠 OPEN SOURCE")
        lines.append("")
        for article in opensource[:4]:
            title = article.get("title", "Untitled")[:65]
            lines.append(f"• {title}")
        lines.append("")

    # FUNDING
    if funding:
        lines.append("💰 FUNDING & M&A")
        lines.append("")
        for article in funding[:4]:
            title = article.get("title", "Untitled")[:65]
            lines.append(f"• {title}")
        lines.append("")

    # PRODUCTS & DEMOS
    if products:
        lines.append("🎯 PRODUCTS & DEMOS")
        lines.append("")
        for article in products[:4]:
            title = article.get("title", "Untitled")[:65]
            lines.append(f"• {title}")
        lines.append("")

    # Fallback: other news if nothing categorized
    if (
        not any(
            [model_releases, ai_agents, research_papers, opensource, funding, products]
        )
        and other_news
    ):
        lines.append("📰 TOP NEWS")
        lines.append("")
        for article in other_news[:5]:
            title = article.get("title", "Untitled")[:65]
            lines.append(f"• {title}")
        lines.append("")

    # Footer
    lines.append("━━━━━━━━━")
    lines.append("")
    lines.append("🔗 CONNECT WITH ME")
    lines.append("• [LinkedIn](https://linkedin.com/in/himanshu231204)")
    lines.append("• [GitHub](https://github.com/himanshu231204)")
    lines.append("")
    lines.append("━━━━━━━━━━━")
    lines.append("💡 Stay ahead of AI! See you tomorrow! 🚀")

    return "\n".join(lines)
