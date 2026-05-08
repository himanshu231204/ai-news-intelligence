from __future__ import annotations

import logging
from typing import List
from datetime import datetime
import httpx

from app.graph.state import NewsItem
from app.utils.company_detector import enrich_news_item, is_negative_content

logger = logging.getLogger(__name__)

# DEV.to API
DEVTO_API_URL = "https://dev.to/api/articles"

# AI-related tags
DEVTO_TAGS = ["ai", "machinelearning", "llm"]


from app.utils.retry import async_retry


@async_retry(max_retries=3, backoff_factor=2, initial_delay=2)
async def fetch_devto_articles() -> List[NewsItem]:
    """Fetch AI/ML articles from DEV.to community with company detection."""
    items = []

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            for tag in DEVTO_TAGS:
                try:
                    logger.info(f"Fetching DEV.to articles with tag: {tag}")

                    response = await client.get(
                        DEVTO_API_URL,
                        params={
                            "tag": tag,
                            "per_page": 5,
                            "state": "fresh",  # Recent articles
                        },
                    )
                    response.raise_for_status()
                    articles = response.json()

                    for article in articles[:3]:  # Top 3 per tag
                        try:
                            title = article.get("title", "No title")
                            summary = article.get("description", "")[:400]

                            # Skip negative content
                            if is_negative_content(title, summary):
                                continue

                            # Get source score for importance calculation
                            source_score = float(article.get("reactions_count", 0))

                            # Enrich with company detection
                            enrichment = enrich_news_item(title, summary, source_score)

                            item = NewsItem(
                                title=title,
                                url=article.get("url", ""),
                                source=f"DEV.to ({tag})",
                                summary=summary,
                                published_at=datetime.fromisoformat(
                                    article.get(
                                        "published_at", datetime.now().isoformat()
                                    ).replace("Z", "+00:00")
                                ),
                                raw_text=article.get("description", ""),
                                score=source_score,
                                metadata={
                                    "author": article.get("user", {}).get(
                                        "name", "Unknown"
                                    ),
                                    "tags": article.get("tag_list", []),
                                    "reactions": article.get("reactions_count", 0),
                                    "comments": article.get("comments_count", 0),
                                },
                                # New fields
                                company=enrichment["company"],
                                category=enrichment["category"],
                                importance_score=enrichment["importance_score"],
                                tags=enrichment["tags"],
                            )
                            items.append(item)
                        except Exception as e:
                            logger.warning(f"Error parsing DEV.to article: {e}")
                            continue

                except httpx.RequestError as e:
                    logger.error(f"DEV.to API error for tag '{tag}': {e}")

    except Exception as e:
        logger.error(f"Error fetching DEV.to articles: {e}")

    logger.info(f"Collected {len(items)} articles from DEV.to")
    return items
