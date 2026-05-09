"""Batch summarization for AI news articles.

This module provides BATCH summarization instead of per-article summarization.
Instead of calling LLM N times for N articles, we batch them into fewer calls.

OPTIMIZATION GOALS:
- Reduce LLM API calls drastically (from N to N/batch_size)
- Minimize token consumption
- Support free-tier rate limits
- Improve async stability

Key Features:
- Configurable batch size
- Token optimization (only title + summary sent)
- Parallel batch processing with semaphore
- Automatic fallback on failure
"""

from __future__ import annotations

import asyncio
from typing import List, Optional, Dict

from app.graph.state import NewsItem
from app.llm import providers
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Batch configuration
DEFAULT_BATCH_SIZE = 10  # Number of articles per batch
MAX_CONCURRENT_BATCHES = 2  # Limit parallel LLM requests
MAX_TOKENS_PER_BATCH = 4000  # Token limit per batch request

# System prompt for batch summarization
BATCH_SUMMARIZATION_SYSTEM = (
    "You are a technical AI news editor. Summarize multiple articles concisely. "
    "Return exactly this format for EACH article (separate with '---'):\n"
    "Title: <article title>\n"
    "Summary: <1-2 sentence summary>\n"
    "Why it matters: <1 sentence>\n"
    "Source: <source name>\n"
    "---\n"
    "(repeat for each article)"
)


class BatchSummarizer:
    """Batch summarizer with parallel processing and rate limiting.

    Optimizations:
    - Batches articles to reduce API calls
    - Uses semaphore to limit concurrent requests
    - Token-optimized prompts (only title + summary)
    - Automatic fallback on failure
    """

    def __init__(
        self,
        batch_size: int = DEFAULT_BATCH_SIZE,
        max_concurrent: int = MAX_CONCURRENT_BATCHES,
    ):
        """Initialize batch summarizer.

        Args:
            batch_size: Number of articles per batch
            max_concurrent: Maximum concurrent LLM requests
        """
        self.batch_size = batch_size
        self.semaphore = asyncio.Semaphore(max_concurrent)
        logger.info(
            f"BatchSummarizer initialized: batch_size={batch_size}, "
            f"max_concurrent={max_concurrent}"
        )

    def _prepare_article_for_llm(self, item: NewsItem) -> str:
        """Prepare article for LLM with token optimization.

        Only sends: title + short summary + source
        Does NOT send full content.

        Args:
            item: NewsItem to prepare

        Returns:
            Optimized string for LLM
        """
        title = item.title or "Untitled"
        source = item.source or "unknown"

        # Use existing summary if available, otherwise truncate content
        summary = item.summary or ""
        if len(summary) > 200:
            summary = summary[:200] + "..."

        return f"Title: {title}\nSource: {source}\nSummary: {summary}"

    def _create_batch_prompt(self, items: List[NewsItem]) -> str:
        """Create a single prompt for a batch of articles.

        Token optimized - only includes essential fields.

        Args:
            items: List of NewsItems to batch

        Returns:
            Combined prompt string
        """
        article_parts = []
        for idx, item in enumerate(items, start=1):
            article_text = self._prepare_article_for_llm(item)
            article_parts.append(f"{idx}. {article_text}")

        return "\n".join(article_parts)

    async def _summarize_batch(
        self,
        items: List[NewsItem],
        batch_num: int,
    ) -> List[Optional[str]]:
        """Summarize a single batch of articles.

        Uses semaphore to limit concurrent requests.

        Args:
            items: List of NewsItems in this batch
            batch_num: Batch number for logging

        Returns:
            List of summaries (None for failed items)
        """
        async with self.semaphore:
            logger.info(f"Processing batch {batch_num}: {len(items)} articles")

            # Check cache first for each item
            from app.utils.summary_cache import get_summary_cache

            cache = get_summary_cache()

            cached_summaries = []
            uncached_items = []
            uncached_indices = []

            for idx, item in enumerate(items):
                cached = cache.get(item.title or "", item.source or "")
                if cached:
                    cached_summaries.append((idx, cached))
                else:
                    uncached_items.append(item)
                    uncached_indices.append(idx)

            # Log cache hits
            if cached_summaries:
                logger.info(f"Batch {batch_num}: {len(cached_summaries)} cache hits")

            # If all cached, return early
            if not uncached_items:
                results = [None] * len(items)
                for idx, summary in cached_summaries:
                    results[idx] = summary
                return results

            # Create batch prompt for uncached items
            prompt = self._create_batch_prompt(uncached_items)

            # Try Groq first (primary)
            result = None
            from app.config.settings import get_settings

            settings = get_settings()

            if settings.groq_api_key:
                try:
                    result = await providers.call_groq(
                        prompt=prompt,
                        system=BATCH_SUMMARIZATION_SYSTEM,
                        model=settings.groq_model,
                    )
                except Exception as e:
                    logger.warning(f"Groq batch failed: {e}")

            # Fallback to OpenRouter
            if not result and settings.openrouter_api_key:
                try:
                    result = await providers.call_openrouter(
                        prompt=prompt,
                        system=BATCH_SUMMARIZATION_SYSTEM,
                        model=settings.openrouter_model,
                    )
                except Exception as e:
                    logger.warning(f"OpenRouter batch failed: {e}")

            # Parse results
            summaries = self._parse_batch_result(result, len(uncached_items))

            # Fill in results
            results = [None] * len(items)

            # Add cached results
            for idx, summary in cached_summaries:
                results[idx] = summary

            # Add new results
            for i, idx in enumerate(uncached_indices):
                if i < len(summaries) and summaries[i]:
                    results[idx] = summaries[i]
                    # Cache the result
                    if uncached_items[i].title and uncached_items[i].source:
                        cache.set(
                            uncached_items[i].title,
                            uncached_items[i].source,
                            summaries[i],
                        )

            return results

    def _parse_batch_result(
        self,
        result: Optional[str],
        expected_count: int,
    ) -> List[Optional[str]]:
        """Parse batch LLM response into individual summaries.

        Args:
            result: Raw LLM response
            expected_count: Number of articles expected

        Returns:
            List of parsed summaries
        """
        if not result:
            return [None] * expected_count

        summaries = []

        # Split by "---" delimiter
        parts = result.split("---")

        for part in parts:
            part = part.strip()
            if not part:
                continue

            # Extract fields
            title = ""
            summary = ""
            why_matters = ""
            source = ""

            for line in part.split("\n"):
                line = line.strip()
                if line.startswith("Title:"):
                    title = line[6:].strip()
                elif line.startswith("Summary:"):
                    summary = line[8:].strip()
                elif line.startswith("Why it matters:"):
                    why_matters = line[15:].strip()
                elif line.startswith("Source:"):
                    source = line[7:].strip()

            if title:
                summaries.append(
                    f"Title: {title}\n"
                    f"Summary: {summary}\n"
                    f"Why it matters: {why_matters}\n"
                    f"Source: {source}"
                )

        # Pad if needed
        while len(summaries) < expected_count:
            summaries.append(None)

        return summaries[:expected_count]

    async def summarize_batch(
        self,
        items: List[NewsItem],
    ) -> List[str]:
        """Summarize multiple articles using batch processing.

        Optimizations:
        - Batches articles to reduce API calls
        - Uses semaphore to limit concurrent requests
        - Caches results to avoid repeated calls

        Args:
            items: List of NewsItems to summarize

        Returns:
            List of formatted summary strings
        """
        if not items:
            return []

        logger.info(f"Batch summarizing {len(items)} articles")

        # Create batches
        batches = []
        for i in range(0, len(items), self.batch_size):
            batch = items[i : i + self.batch_size]
            batches.append((batch, i // self.batch_size + 1))

        logger.info(f"Created {len(batches)} batches")

        # Process batches in parallel (limited by semaphore)
        tasks = [
            self._summarize_batch(items, batch_num) for items, batch_num in batches
        ]

        batch_results = await asyncio.gather(*tasks)

        # Flatten results
        all_summaries = []
        for batch_result in batch_results:
            all_summaries.extend(batch_result)

        # Replace None with fallback
        final_summaries = []
        for i, summary in enumerate(all_summaries):
            if summary:
                final_summaries.append(summary)
            else:
                # Generate fallback summary
                final_summaries.append(self._generate_fallback(items[i]))

        logger.info(f"Batch summarization complete: {len(final_summaries)} summaries")
        return final_summaries

    def _generate_fallback(self, item: NewsItem) -> str:
        """Generate deterministic fallback summary.

        Args:
            item: NewsItem to summarize

        Returns:
            Formatted summary string
        """
        title = item.title or "Untitled"
        source = item.source or "unknown"

        return (
            f"Title: {title}\n"
            f"Summary: {item.summary[:150] if item.summary else 'No summary available'}\n"
            f"Why it matters: Tracks AI development progress\n"
            f"Source: {source}"
        )


# Global instance
_summarizer: Optional[BatchSummarizer] = None


def get_batch_summarizer() -> BatchSummarizer:
    """Get or create the global batch summarizer.

    Returns:
        BatchSummarizer instance
    """
    global _summarizer
    if _summarizer is None:
        _summarizer = BatchSummarizer()
    return _summarizer


async def summarize_batch_optimized(items: List[NewsItem]) -> List[str]:
    """Convenience function for batch summarization.

    Args:
        items: List of NewsItems to summarize

    Returns:
        List of formatted summary strings
    """
    summarizer = get_batch_summarizer()
    return await summarizer.summarize_batch(items)
