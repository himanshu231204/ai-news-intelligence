from __future__ import annotations

from datetime import date, datetime
import re
from typing import List

from app.graph.state import NewsItem
import httpx

from app.config.settings import get_settings
from app.newsletter.prompts import NEWSLETTER_GENERATION_PROMPT


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


def build_newsletter(items: List[NewsItem], summaries: List[str]) -> str:
    """Build a professionally formatted newsletter matching enterprise standards."""

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

    # Try LLM-based generation first (OpenRouter or Groq)
    settings = get_settings()
    openrouter_key = getattr(settings, "openrouter_api_key", None)
    groq_key = getattr(settings, "groq_api_key", None)

    if openrouter_key or groq_key:
        try:
            # Build article list for LLM
            article_list = []
            for idx, (item, parsed) in enumerate(valid_pairs[:30], start=1):
                article_list.append(
                    f"{idx}. Title: {parsed.get('title', '')}\n"
                    f"URL: {item.url or ''}\n"
                    f"Source: {parsed.get('source', '')}\n"
                    f"Summary: {parsed.get('summary', '')}\n"
                    f"Why it matters: {parsed.get('why_it_matters', '')}\n"
                )

            user_content = (
                f"Current date: {formatted_date}\n\n"
                "Use the following articles to produce a single professional newsletter.\n"
                "Please follow the exact FORMAT in the system instructions.\n\n"
                "Articles:\n\n" + "\n".join(article_list)
            )

            # Try OpenRouter first, then Groq
            api_key = None
            api_url = None
            model = None

            if openrouter_key:
                api_key = openrouter_key
                api_url = "https://openrouter.ai/api/v1/chat/completions"
                model = getattr(
                    settings, "openrouter_model", "anthropic/claude-3.5-sonnet"
                )
            elif groq_key:
                api_key = groq_key
                api_url = "https://api.groq.com/openai/v1/chat/completions"
                model = settings.groq_model

            if api_key:
                payload = {
                    "model": model,
                    "temperature": 0.2,
                    "messages": [
                        {
                            "role": "system",
                            "content": NEWSLETTER_GENERATION_PROMPT.format(
                                current_date=formatted_date
                            ),
                        },
                        {"role": "user", "content": user_content},
                    ],
                }

                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                }

                if "openrouter" in api_url:
                    headers["HTTP-Referer"] = (
                        "https://github.com/himanshu231204/ai-news-agent"
                    )
                    headers["X-Title"] = "AI News Agent"

                with httpx.Client(timeout=60) as client:
                    resp = client.post(api_url, headers=headers, json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    generated = data["choices"][0]["message"]["content"].strip()

                # Ensure proper footer
                generated = _strip_footer(generated)
                final = generated.rstrip()
                if not final.endswith("CONNECT & BUILD"):
                    final += (
                        "\n\n"
                        + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n🔗 CONNECT & BUILD\n\nLinkedIn: linkedin.com/in/himanshu231204\nGitHub: github.com/himanshu231204\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                    )
                return final

        except Exception:
            pass

    # Fallback: Programmatic template matching the premium design
    return _build_fallback_newsletter(valid_pairs, formatted_date)


def _build_fallback_newsletter(valid_pairs: List, formatted_date: str) -> str:
    """Build newsletter using the premium template format."""

    # Categorize items
    industry_news = []
    research_papers = []
    opensource_tools = []
    community_signals = []

    for item, parsed in valid_pairs[:20]:
        source = (item.source or "").lower()

        if source == "arxiv":
            research_papers.append(parsed)
        elif source == "github trending":
            opensource_tools.append(parsed)
        elif source in ["hacker news", "reddit"]:
            community_signals.append(parsed)
        else:
            industry_news.append(parsed)

    # Build the premium template
    lines = []

    # Header
    lines.append(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    lines.append('💎 The Premium "Intelligence" Template')
    lines.append("🧠 AI INTELLIGENCE DAILY BRIEF")
    lines.append(formatted_date)
    lines.append("")
    lines.append("The essential update for AI Engineers and Tech Leaders.")
    lines.append("")
    lines.append(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    lines.append("")

    # TOP DEVELOPMENTS
    if industry_news:
        lines.append("🔴 TOP DEVELOPMENTS")
        lines.append("")
        counter = 1
        for article in industry_news[:6]:
            title = article.get("title", "Untitled")
            summary = article.get("summary", "")
            source = article.get("source", "unknown")
            why = article.get("why_it_matters", "")

            lines.append(f"{counter}. {title}")
            lines.append(summary[:200] if summary else "No summary available.")
            if why:
                lines.append(f"The Shift: {why}")
            lines.append(f"Source: {source}")
            lines.append("")
            counter += 1

        lines.append(
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        lines.append("")

    # RESEARCH HIGHLIGHTS
    if research_papers:
        lines.append("🔬 RESEARCH HIGHLIGHTS")
        lines.append("")
        for article in research_papers[:4]:
            title = article.get("title", "Untitled")
            summary = article.get("summary", "")
            source = article.get("source", "unknown")

            lines.append(title)
            lines.append(summary[:200] if summary else "No summary available.")
            lines.append(f"Source: {source}")
            lines.append("")
        lines.append("")

    # OPEN-SOURCE & TOOLS
    if opensource_tools:
        lines.append("🛠 OPEN-SOURCE & TOOLS")
        lines.append("")
        for article in opensource_tools[:4]:
            title = article.get("title", "Untitled")
            summary = article.get("summary", "")
            source = article.get("source", "unknown")

            lines.append(title)
            lines.append(summary[:200] if summary else "No summary available.")
            lines.append(f"Source: {source}")
            lines.append("")
        lines.append("")

    # EXECUTIVE SUMMARY
    lines.append(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    lines.append("")
    lines.append("📊 EXECUTIVE SUMMARY")
    lines.append("")
    lines.append(
        "The industry is pivoting from Conversational UI → Autonomous Systems."
    )
    lines.append("")
    lines.append("Priority Focus for Q2:")
    lines.append("• High-fidelity Reasoning")
    lines.append("• Infrastructure Reliability")
    lines.append("• Agent Orchestration")
    lines.append("")
    lines.append(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    lines.append("")
    lines.append("🔗 CONNECT & BUILD")
    lines.append("")
    lines.append("LinkedIn: linkedin.com/in/himanshu231204")
    lines.append("GitHub: github.com/himanshu231204")
    lines.append("")
    lines.append(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

    return "\n".join(lines)
