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
    parts = {
        "title": "",
        "summary": "",
        "why_it_matters": "",
        "source": ""
    }
    
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
    """Remove common footer lines that may be injected into LLM summaries.

    This strips lines containing linkedin, github, 'follow me', 'powered by',
    or similar phrases so the final newsletter contains a single footer.
    """
    if not text:
        return text

    lines = []
    for line in text.splitlines():
        low = line.lower().strip()
        if (
            'linkedin.com' in low
            or 'github.com' in low
            or 'follow me' in low
            or 'powered by' in low
            or low.startswith('follow for')
        ):
            continue
        # also drop short standalone links that look like footers
        if low.startswith('http') and ('linkedin' in low or 'github' in low):
            continue
        lines.append(line)

    return '\n'.join(lines).strip()


def _format_article(counter: int, parsed: dict, emoji: str = "") -> str:
    """Format a single article compactly with an emoji prefix.

    Output style (single-line per item):
    1. 🔥 Title — Short summary (Source)
    """
    title = parsed.get("title", "Untitled")
    summary = parsed.get("summary", "")
    source = parsed.get("source", "unknown")

    # Shorten summary to first sentence if very long
    first_sentence = summary.split(". ")[0].strip()
    if first_sentence and not first_sentence.endswith('.'):
        first_sentence = first_sentence + '.'

    line = f"{counter}. {emoji} {title} — {first_sentence} ({source})\n"
    return line


def build_newsletter(items: List[NewsItem], summaries: List[str]) -> str:
    """Build a professionally formatted newsletter matching enterprise standards."""
    
    # Format date: Saturday, May 09, 2026
    today = datetime.now()
    day_name = today.strftime("%A")
    date_str = today.strftime("%B %d, %Y")
    formatted_date = f"{day_name}, {date_str}"
    
    # Header
    header = (
        "AI INTELLIGENCE DAILY BRIEF\n"
        f"{formatted_date}\n\n"
        "Daily intelligence covering the most important developments\n"
        "in artificial intelligence, research, and technology.\n\n\n"
    )
    
    # Parse and pair summaries with items
    valid_pairs = []
    for i, summary in enumerate(summaries):
        if summary and i < len(items):
            parsed = _parse_summary(summary)
            if parsed["title"]:
                valid_pairs.append((items[i], parsed))

    # If Groq is configured, attempt to generate a full editorial newsletter
    settings = get_settings()
    if getattr(settings, "groq_api_key", None):
        try:
            # Build a concise data payload for the LLM
            article_list = []
            for idx, (item, parsed) in enumerate(valid_pairs[:30], start=1):
                article_list.append(
                    f"{idx}. Title: {parsed.get('title','')}\n"
                    f"URL: {item.get('url','')}\n"
                    f"Source: {parsed.get('source','')}\n"
                    f"Summary: {parsed.get('summary','')}\n"
                    f"Why it matters: {parsed.get('why_it_matters','')}\n"
                )

            user_content = (
                f"Current date: {formatted_date}\n\n"
                "Use the following articles to produce a single professional newsletter.\n"
                "Please follow the exact SECTION STRUCTURE and FORMAT RULES in the system instructions.\n\n"
                "Articles:\n\n"
                + "\n".join(article_list)
            )

            payload = {
                "model": settings.groq_model,
                "temperature": 0.2,
                "messages": [
                    {"role": "system", "content": NEWSLETTER_GENERATION_PROMPT},
                    {"role": "user", "content": user_content},
                ],
            }

            with httpx.Client(timeout=60) as client:
                resp = client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.groq_api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()
                generated = data["choices"][0]["message"]["content"].strip()

            # Ensure no repeated footers in generated text
            generated = _strip_footer(generated)
            # Append canonical footer
            canonical_footer = (
                "\n\n" + "━" * 80 + "\n\n"
                "Follow for more AI insights and engineering updates\n\n"
                "LinkedIn:\n"
                "linkedin.com/in/himanshu231204\n\n"
                "GitHub:\n"
                "github.com/himanshu231204\n\n"
                "━" * 80
            )
            final_generated = generated.rstrip() + canonical_footer
            return final_generated
        except Exception:
            # On any failure, fall back to programmatic formatter below
            pass
    
    # Categorize by source
    industry_news = []
    research_papers = []
    opensource_tools = []
    community_signals = []
    
    for item, parsed in valid_pairs[:20]:
        source = item.get("source", "").lower()
        
        if source == "arxiv":
            research_papers.append(parsed)
        elif source == "github trending":
            opensource_tools.append(parsed)
        elif source in ["hacker news", "reddit"]:
            community_signals.append(parsed)
        else:
            industry_news.append(parsed)
    
    # Build professional newsletter
    body = header
    
    sep = "━" * 50 + "\n"

    # Section 1: TOP INDUSTRY DEVELOPMENTS
    if industry_news:
        body += sep
        body += "TOP INDUSTRY DEVELOPMENTS\n"
        body += sep
        counter = 1
        for article in industry_news[:6]:
            body += _format_article(counter, article, emoji="🔥")
            counter += 1
        body += "\n"
    
    # Section 2: RESEARCH HIGHLIGHTS
    if research_papers:
        body += "RESEARCH HIGHLIGHTS\n"
        body += sep
        counter = len(industry_news) + 1
        for article in research_papers[:4]:
            body += _format_article(counter, article, emoji="📚")
            counter += 1
        body += "\n"
    
    # Section 3: OPEN-SOURCE & TOOLS
    if opensource_tools:
        body += "OPEN-SOURCE & TOOLS\n"
        body += sep
        counter = len(industry_news) + len(research_papers) + 1
        for article in opensource_tools[:4]:
            body += _format_article(counter, article, emoji="⭐")
            counter += 1
        body += "\n"
    
    # Section 4: COMMUNITY SIGNALS
    if community_signals:
        body += "COMMUNITY SIGNALS\n"
        body += sep
        counter = len(industry_news) + len(research_papers) + len(opensource_tools) + 1
        for article in community_signals[:4]:
            body += _format_article(counter, article, emoji="💬")
            counter += 1
        body += "\n"
    
    # Executive Insight
    body += "EXECUTIVE INSIGHT\n"
    body += "━" * 80 + "\n\n"
    body += (
        "The AI ecosystem is shifting from pure model innovation toward:\n"
        "• production infrastructure\n"
        "• orchestration systems\n"
        "• evaluation reliability\n"
        "• deployment scalability\n"
        "• autonomous AI workflows\n\n"
        "The next major advantage will come from building reliable,\n"
        "production-grade AI systems at scale.\n\n\n"
    )
    
    # Remove any footer-like lines accidentally present in the assembled body
    body = _strip_footer(body)

    # Footer block (single canonical footer)
    footer = (
        "━" * 80 + "\n\n"
        "Follow for more AI insights and engineering updates\n\n"
        "LinkedIn:\n"
        "linkedin.com/in/himanshu231204\n\n"
        "GitHub:\n"
        "github.com/himanshu231204\n\n"
        "━" * 80
    )

    # Compose final newsletter and ensure footer appears only once
    final = (body + "\n" + footer).strip()

    # Defensive: if the newsletter already contains repeated footer-like blocks,
    # locate the first occurrence of the footer header and replace the remainder
    # with a single canonical footer to avoid duplication.
    footer_header_pattern = re.compile(r"Follow for more AI insights", re.IGNORECASE)
    m = footer_header_pattern.search(final)
    if m:
        # Keep everything up to the first footer occurrence and append canonical footer
        final = final[: m.start()].rstrip() + "\n\n" + footer

    return final
