"""LLM Router with automatic fallback handling.

OPTIMIZATIONS:
- Batch summarization (reduces API calls drastically)
- Token optimization (only title + summary sent)
- Gemini ONLY for final newsletter formatting
- Multiple fallback models for OpenRouter
- Improved retry with exponential backoff

This module provides:
- LLMRouter class with provider fallback chains
- Batch summarization: Groq → OpenRouter (batched)
- Newsletter: Gemini ONLY (no other providers for formatting)

Key Features:
- Automatic provider switching on failure
- Rate limit handling
- Error logging
- Token optimization (minimal content sent)
"""

from __future__ import annotations

import asyncio
from typing import List, Optional

from app.config.settings import get_settings
from app.graph.state import NewsItem
from app.llm import providers
from app.llm.batch_summarizer import get_batch_summarizer
from app.utils.logger import get_logger

logger = get_logger(__name__)

# System prompts for different tasks
SUMMARIZATION_SYSTEM = (
    "You are a technical AI news editor focused on factual, concise summaries. "
    "Return exactly this format with concise text and no markdown:\n"
    "Title:\nSummary:\nWhy it matters:\nSource:"
)

NEWSLETTER_SYSTEM = """You are an expert AI news editor creating a premium daily AI newsletter.

Generate a professional newsletter in this structure:

🧠 AI DAILY BRIEF — {current_date}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚨 BREAKING NEWS
[Only if there's a major announcement - model releases, funding >$100M, major partnerships]
• [Title] - [1-line summary]

🤖 MODEL RELEASES
[New AI models, updates, benchmarks]
• [Model Name] by [Company] - [What it does]
• [Model Name] by [Company] - [What it does]

💻 AI AGENTS & CODING
[Agent frameworks, coding tools, developer tools]
• [Tool/Project] - [What it does]
• [Tool/Project] - [What it does]

📄 RESEARCH PAPERS
[arXiv papers, research breakthroughs]
• [Paper Name] - [Key insight]
• [Paper Name] - [Key insight]

🛠 OPEN SOURCE
[New GitHub repos, open-source projects]
• [Repo/Project] - [What it does]
• [Repo/Project] - [What it does]

💰 FUNDING & M&A
[Investments, acquisitions, partnerships]
• [Company] - [Amount/Deal] - [Investors]
• [Company] - [Amount/Deal] - [Investors]

🎯 PRODUCTS & DEMOS
[Product launches, demos, tools]
• [Product] - [What it is]
• [Product] - [What it is]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔗 CONNECT WITH ME
• [LinkedIn](https://linkedin.com/in/himanshu231204)
• [GitHub](https://github.com/himanshu231204)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 Stay ahead of AI! See you tomorrow! 🚀
"""


class LLMRouter:
    """Multi-provider LLM router with automatic fallback.

    Provider Chain:
    - Summarization: Groq (primary) → OpenRouter (fallback) → deterministic (final)
    - Newsletter: Gemini (primary) → template (fallback)

    Features:
    - Automatic provider switching on API failure
    - Rate limit handling with exponential backoff
    - Token optimization (minimal content sent)
    - Comprehensive error logging
    """

    def __init__(self):
        self.settings = get_settings()
        logger.info("LLMRouter initialized")

    async def summarize(self, item: NewsItem) -> str:
        """Summarize a news item with fallback chain.

        Flow: Cache → Groq → OpenRouter → deterministic fallback

        Args:
            item: NewsItem to summarize

        Returns:
            Formatted summary string
        """
        # Build minimal prompt (token optimization)
        title = item.title or "Untitled"
        source = item.source or "unknown"
        url = item.url or ""

        # Check cache first
        from app.utils.summary_cache import get_summary_cache

        cache = get_summary_cache()
        cached = cache.get(title, source)
        if cached:
            return cached

        prompt = f"Article title: {title}\nSource: {source}\nURL: {url}\n"

        # Try Groq first (primary - better rate limits on free tier)
        if self.settings.groq_api_key:
            try:
                result = await providers.call_groq(
                    prompt=prompt,
                    system=SUMMARIZATION_SYSTEM,
                    model=self.settings.groq_model,
                )
                if result:
                    logger.info(f"Summarized via Groq: {title[:50]}...")
                    # Cache the result
                    cache.set(title, source, result)
                    return result
            except Exception as e:
                logger.warning(f"Groq failed for '{title}': {e}")

        # Fallback to OpenRouter
        if self.settings.openrouter_api_key:
            try:
                result = await providers.call_openrouter(
                    prompt=prompt,
                    system=SUMMARIZATION_SYSTEM,
                    model=self.settings.openrouter_model,
                )
                if result:
                    logger.info(
                        f"Summarized via OpenRouter (fallback): {title[:50]}..."
                    )
                    # Cache the result
                    cache.set(title, source, result)
                    return result
            except Exception as e:
                logger.warning(f"OpenRouter failed for '{title}': {e}")

        # Final fallback: deterministic summary
        logger.warning(
            f"All LLM providers failed. Using deterministic fallback for: {title}"
        )
        return self._generate_fallback_summary(item)

    async def summarize_batch(self, items: List[NewsItem]) -> List[str]:
        """Summarize multiple news items using BATCH processing.

        OPTIMIZATION: Uses batch summarization instead of per-article calls.
        This reduces API calls from N to N/batch_size.

        Args:
            items: List of NewsItems to summarize

        Returns:
            List of formatted summary strings
        """
        if not items:
            return []

        logger.info(f"Using batch summarization for {len(items)} items")

        # Use batch summarizer (reduces API calls drastically)
        batch_summarizer = get_batch_summarizer()
        summaries = await batch_summarizer.summarize_batch(items)

        return summaries

    async def generate_newsletter(
        self,
        items: List[NewsItem],
        summaries: List[str],
        formatted_date: str,
    ) -> str:
        """Generate newsletter with Gemini ONLY for final formatting.

        OPTIMIZATION: Gemini is used ONLY for final newsletter formatting.
        Not used for: filtering, ranking, per-article summaries.

        Flow: Gemini (primary) → OpenRouter (fallback) → template (final)

        Args:
            items: List of ranked news items
            summaries: List of summaries from LLM
            formatted_date: Formatted date string for header

        Returns:
            Formatted newsletter string
        """
        # Import here to avoid circular dependency
        from app.newsletter.generator import _build_fallback_newsletter, _parse_summary

        # Build article list for LLM (token optimized - only essential fields)
        valid_pairs = []
        for i, summary in enumerate(summaries):
            if summary and i < len(items):
                parsed = _parse_summary(summary)
                if parsed["title"]:
                    valid_pairs.append((items[i], parsed))

        # Try Gemini first (ONLY used for final formatting)
        if self.settings.gemini_api_key:
            try:
                newsletter = await self._generate_with_gemini(
                    valid_pairs, formatted_date
                )
                if newsletter:
                    logger.info("Newsletter generated via Gemini (final formatting)")
                    return newsletter
            except Exception as e:
                logger.warning(f"Gemini newsletter generation failed: {e}")

        # Fallback to OpenRouter
        if self.settings.openrouter_api_key:
            try:
                newsletter = await self._generate_with_openrouter(
                    valid_pairs, formatted_date
                )
                if newsletter:
                    logger.info("Newsletter generated via OpenRouter (fallback)")
                    return newsletter
            except Exception as e:
                logger.warning(f"OpenRouter newsletter generation failed: {e}")

        # Final fallback: template-based newsletter
        logger.warning("All LLM providers failed. Using template fallback")
        return _build_fallback_newsletter(valid_pairs, formatted_date)

    async def _generate_with_gemini(
        self,
        valid_pairs: List[tuple],
        formatted_date: str,
    ) -> Optional[str]:
        """Generate newsletter using Gemini API.

        Args:
            valid_pairs: List of (item, parsed_summary) tuples
            formatted_date: Date string for header

        Returns:
            Generated newsletter or None
        """
        # Build article list (limited to 30 for token optimization)
        article_list = []
        for idx, (item, parsed) in enumerate(valid_pairs[:30], start=1):
            article_list.append(
                f"{idx}. Title: {parsed.get('title', '')}\n"
                f"URL: {item.url or ''}\n"
                f"Source: {parsed.get('source', '')}\n"
                f"Summary: {parsed.get('summary', '')}\n"
                f"Why it matters: {parsed.get('why_it_matters', '')}\n"
            )

        # Get current quarter
        from datetime import datetime

        month = datetime.now().month
        quarter = f"Q{(month - 1) // 3 + 1}"

        # Format system prompt
        system_prompt = NEWSLETTER_SYSTEM.format(
            current_date=formatted_date,
            quarter=quarter,
        )

        user_content = (
            f"Current date: {formatted_date}\n\n"
            "Use the following articles to produce a single professional newsletter.\n"
            "Please follow the exact FORMAT in the system instructions.\n\n"
            "Articles:\n\n" + "\n".join(article_list)
        )

        result = await providers.call_gemini(
            prompt=user_content,
            system=system_prompt,
            model=self.settings.gemini_model,
            temperature=0.2,
        )

        if result:
            # Clean up any footer artifacts
            from app.newsletter.generator import _strip_footer

            result = _strip_footer(result)

            # Ensure proper footer with links is present
            has_linkedin = "linkedin.com/in/himanshu231204" in result
            has_github = "github.com/himanshu231204" in result

            if not has_linkedin or not has_github:
                # Remove any incomplete footer and add proper one
                lines = result.split("\n")
                cutoff = len(lines)
                for i, line in enumerate(lines):
                    if "CONNECT" in line.upper() or "STAY AHEAD" in line.upper():
                        cutoff = i
                        break

                result = "\n".join(lines[:cutoff])

                result += (
                    "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "🔗 CONNECT WITH ME\n"
                    "• LinkedIn: https://linkedin.com/in/himanshu231204\n"
                    "• GitHub: https://github.com/himanshu231204\n\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "💡 Stay ahead of AI! See you tomorrow! 🚀"
                )

            return result.rstrip()

        return None

    async def _generate_with_openrouter(
        self,
        valid_pairs: List[tuple],
        formatted_date: str,
    ) -> Optional[str]:
        """Generate newsletter using OpenRouter API.

        Args:
            valid_pairs: List of (item, parsed_summary) tuples
            formatted_date: Date string for header

        Returns:
            Generated newsletter or None
        """
        # Build article list (limited to 30 for token optimization)
        article_list = []
        for idx, (item, parsed) in enumerate(valid_pairs[:30], start=1):
            article_list.append(
                f"{idx}. Title: {parsed.get('title', '')}\n"
                f"URL: {item.url or ''}\n"
                f"Source: {parsed.get('source', '')}\n"
                f"Summary: {parsed.get('summary', '')}\n"
                f"Why it matters: {parsed.get('why_it_matters', '')}\n"
            )

        # Format system prompt
        system_prompt = NEWSLETTER_SYSTEM.format(
            current_date=formatted_date,
        )

        user_content = (
            f"Current date: {formatted_date}\n\n"
            "Use the following articles to produce a single professional newsletter.\n"
            "Please follow the exact FORMAT in the system instructions.\n\n"
            "Articles:\n\n" + "\n".join(article_list)
        )

        result = await providers.call_openrouter(
            prompt=user_content,
            system=system_prompt,
            model=self.settings.openrouter_model,
            temperature=0.2,
        )

        if result:
            # Clean up any footer artifacts
            from app.newsletter.generator import _strip_footer

            result = _strip_footer(result)

            # Ensure proper footer with links is present
            has_linkedin = "linkedin.com/in/himanshu231204" in result
            has_github = "github.com/himanshu231204" in result

            if not has_linkedin or not has_github:
                lines = result.split("\n")
                cutoff = len(lines)
                for i, line in enumerate(lines):
                    if "CONNECT" in line.upper() or "STAY AHEAD" in line.upper():
                        cutoff = i
                        break

                result = "\n".join(lines[:cutoff])

                result += (
                    "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "🔗 CONNECT WITH ME\n"
                    "• LinkedIn: https://linkedin.com/in/himanshu231204\n"
                    "• GitHub: https://github.com/himanshu231204\n\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "💡 Stay ahead of AI! See you tomorrow! 🚀"
                )

            return result.rstrip()

        return None

    def _generate_fallback_summary(self, item: NewsItem) -> str:
        """Generate deterministic fallback summary from available data.

        Args:
            item: NewsItem to summarize

        Returns:
            Formatted summary string
        """
        title = item.title or "Untitled"
        source = item.source or "unknown"
        url = item.url or ""

        summary_parts = []

        # Extract repo name from GitHub URLs
        if "github.com" in url:
            parts = url.rstrip("/").split("/")
            if len(parts) >= 2:
                repo = f"{parts[-2]}/{parts[-1]}"
                summary_parts.append(f"GitHub repository: {repo}")

        # Use score if available
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


# Module-level router instance for convenience
_router: Optional[LLMRouter] = None


def get_router() -> LLMRouter:
    """Get or create the global LLM router instance.

    Returns:
        LLMRouter instance
    """
    global _router
    if _router is None:
        _router = LLMRouter()
    return _router


async def summarize_with_fallback(item: NewsItem) -> str:
    """Convenience function for single-item summarization.

    Args:
        item: NewsItem to summarize

    Returns:
        Formatted summary string
    """
    router = get_router()
    return await router.summarize(item)


async def summarize_batch_with_fallback(items: List[NewsItem]) -> List[str]:
    """Convenience function for batch summarization.

    Args:
        items: List of NewsItems to summarize

    Returns:
        List of formatted summary strings
    """
    router = get_router()
    return await router.summarize_batch(items)


async def generate_newsletter_with_fallback(
    items: List[NewsItem],
    summaries: List[str],
    formatted_date: str,
) -> str:
    """Convenience function for newsletter generation.

    Args:
        items: List of ranked news items
        summaries: List of summaries
        formatted_date: Formatted date string

    Returns:
        Formatted newsletter string
    """
    router = get_router()
    return await router.generate_newsletter(items, summaries, formatted_date)
