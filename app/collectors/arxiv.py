from __future__ import annotations

import logging
import asyncio
from typing import List
from datetime import datetime
import httpx
import xml.etree.ElementTree as ET

from app.graph.state import NewsItem

logger = logging.getLogger(__name__)

# ArXiv search URL
ARXIV_API_URL = "https://export.arxiv.org/api/query"

# AI/ML categories
ARXIV_CATEGORIES = [
    "cat:cs.AI",  # Artificial Intelligence
    "cat:cs.LG",  # Machine Learning
    "cat:cs.CL",  # Computation and Language (NLP)
]


async def fetch_arxiv_papers() -> List[NewsItem]:
    """Fetch latest AI/ML research papers from ArXiv."""
    items = []

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            for category in ARXIV_CATEGORIES:
                try:
                    logger.info(f"Fetching ArXiv papers from {category}")

                    # Simpler query to avoid rate limits - just get recent papers
                    query = category
                    response = await client.get(
                        ARXIV_API_URL,
                        params={
                            "search_query": query,
                            "start": 0,
                            "max_results": 5,
                            "sortBy": "submittedDate",
                            "sortOrder": "descending",
                        }
                    )
                    response.raise_for_status()

                    # Parse XML response
                    root = ET.fromstring(response.text)
                    namespace = {"atom": "http://www.w3.org/2005/Atom"}

                    entries = root.findall("atom:entry", namespace)
                    for entry in entries[:3]:  # Top 3 papers per category
                        try:
                            title_elem = entry.find("atom:title", namespace)
                            id_elem = entry.find("atom:id", namespace)
                            summary_elem = entry.find("atom:summary", namespace)
                            published_elem = entry.find("atom:published", namespace)
                            authors_elem = entry.findall("atom:author/atom:name", namespace)

                            if title_elem is None or id_elem is None:
                                continue

                            title = title_elem.text.strip().replace("\n", " ")
                            arxiv_id = id_elem.text.split("/abs/")[-1]
                            summary = summary_elem.text.strip() if summary_elem is not None else ""
                            published = published_elem.text if published_elem is not None else ""
                            authors = [a.text for a in authors_elem]

                            item = NewsItem(
                                title=f"📄 {title}",
                                url=f"https://arxiv.org/abs/{arxiv_id}",
                                source="ArXiv",
                                summary=summary[:400],
                                published_at=datetime.fromisoformat(published.replace("Z", "+00:00")),
                                raw_text=f"Authors: {', '.join(authors[:3])}. {summary[:200]}",
                                metadata={
                                    "arxiv_id": arxiv_id,
                                    "category": category,
                                    "authors": authors,
                                }
                            )
                            items.append(item)
                        except Exception as e:
                            logger.warning(f"Error parsing ArXiv entry: {e}")
                            continue
                    
                    # Add small delay to avoid rate limiting
                    await asyncio.sleep(0.5)

                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429:
                        logger.warning("ArXiv rate limit hit - backing off")
                        break
                    logger.error(f"ArXiv API error for {category}: {e}")
                except httpx.RequestError as e:
                    logger.error(f"ArXiv API error for {category}: {e}")

    except Exception as e:
        logger.error(f"Error fetching ArXiv papers: {e}")

    logger.info(f"Collected {len(items)} papers from ArXiv")
    return items
