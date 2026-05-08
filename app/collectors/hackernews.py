from __future__ import annotations

import logging
from typing import List
from datetime import datetime
import httpx

from app.graph.state import NewsItem
from app.utils.company_detector import enrich_news_item, is_negative_content

logger = logging.getLogger(__name__)

# HN Search API for AI-related stories
HN_SEARCH_URL = "https://hn.algolia.com/api/v1/search"
KEYWORDS = [
    "AI",
    "machine learning",
    "LLM",
    "GPT",
    "neural",
    "transformer",
    "deep learning",
]


from app.utils.retry import async_retry


@async_retry(max_retries=3, backoff_factor=2, initial_delay=2)
async def fetch_hackernews() -> List[NewsItem]:
    """Fetch top AI news from Hacker News with company detection."""
    items = []

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            for keyword in KEYWORDS[:3]:  # Search top 3 keywords
                try:
                    response = await client.get(
                        HN_SEARCH_URL,
                        params={
                            "query": keyword,
                            "tags": "story",
                            "numericFilters": f"points>50",
                            "hitsPerPage": 5,
                        },
                    )
                    response.raise_for_status()
                    data = response.json()

                    for hit in data.get("hits", [])[:3]:
                        if hit.get("url"):
                            title = hit.get("title", "No title")
                            summary = f"Points: {hit.get('points', 0)} | Comments: {hit.get('num_comments', 0)}"

                            # Skip negative content
                            if is_negative_content(title, summary):
                                continue

                            # Get source score for importance calculation
                            source_score = float(hit.get("points", 0))

                            # Enrich with company detection
                            enrichment = enrich_news_item(title, summary, source_score)

                            item = NewsItem(
                                title=title,
                                url=hit.get("url", ""),
                                source=f"Hacker News ({keyword})",
                                summary=summary,
                                published_at=datetime.now(),
                                raw_text=hit.get("title", ""),
                                score=source_score,
                                # New fields
                                company=enrichment["company"],
                                category=enrichment["category"],
                                importance_score=enrichment["importance_score"],
                                tags=enrichment["tags"],
                            )
                            items.append(item)

                except httpx.RequestError as e:
                    logger.error(f"HN API error for keyword '{keyword}': {e}")

    except Exception as e:
        logger.error(f"Error fetching Hacker News: {e}")

    logger.info(f"Collected {len(items)} items from Hacker News")
    return items
