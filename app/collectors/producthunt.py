from __future__ import annotations

import logging
from typing import List
from datetime import datetime
import httpx
import xml.etree.ElementTree as ET

from app.graph.state import NewsItem

logger = logging.getLogger(__name__)

# ProductHunt RSS feed (unofficial but reliable)
PRODUCTHUNT_RSS_URL = "https://www.producthunt.com/feed?category=artificial-intelligence"


from app.utils.retry import async_retry

@async_retry(max_retries=3, backoff_factor=2, initial_delay=2)
async def fetch_producthunt_tools() -> List[NewsItem]:
    """Fetch new AI tools from ProductHunt."""
    items = []

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            try:
                logger.info("Fetching ProductHunt AI tools")

                # Try to fetch with timeout and follow redirects
                response = await client.get(
                    PRODUCTHUNT_RSS_URL,
                    follow_redirects=True,
                    timeout=20
                )
                response.raise_for_status()

                # Parse RSS feed
                try:
                    root = ET.fromstring(response.text)
                except ET.ParseError as e:
                    logger.warning(f"ProductHunt RSS parse error (trying alternative): {e}")
                    # Try removing XML declaration if it's causing issues
                    clean_text = response.text.replace('<?xml version="1.0" encoding="UTF-8"?>', '')
                    root = ET.fromstring(clean_text)

                # Handle both standard RSS and custom ProductHunt format
                items_elem = root.findall(".//item")
                
                if not items_elem:
                    logger.warning("No items found in ProductHunt RSS feed")
                    return items

                for item_elem in items_elem[:5]:  # Top 5 products
                    try:
                        title_elem = item_elem.find("title")
                        link_elem = item_elem.find("link")
                        description_elem = item_elem.find("description")
                        pub_date_elem = item_elem.find("pubDate")
                        creator_elem = item_elem.find("{http://purl.org/dc/elements/1.1/}creator")

                        if title_elem is None or link_elem is None:
                            continue

                        title = title_elem.text.strip() if title_elem.text else "No title"
                        link = link_elem.text.strip() if link_elem.text else ""
                        description = description_elem.text.strip()[:400] if description_elem is not None else ""
                        creator = creator_elem.text if creator_elem is not None else "ProductHunt"

                        # Parse pub date
                        pub_date_str = pub_date_elem.text if pub_date_elem is not None else datetime.now().isoformat()
                        try:
                            # ProductHunt uses RFC 2822 format, try to parse
                            published_at = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %z")
                        except:
                            published_at = datetime.now()

                        item = NewsItem(
                            title=f"🚀 {title}",
                            url=link,
                            source="ProductHunt",
                            summary=description,
                            published_at=published_at,
                            raw_text=description,
                            metadata={
                                "creator": creator,
                                "category": "AI Tools",
                            }
                        )
                        items.append(item)
                    except Exception as e:
                        logger.warning(f"Error parsing ProductHunt item: {e}")
                        continue

            except (httpx.RequestError, ET.ParseError) as e:
                logger.error(f"ProductHunt RSS fetch error: {e}")

    except Exception as e:
        logger.error(f"Error fetching ProductHunt tools: {e}")

    logger.info(f"Collected {len(items)} tools from ProductHunt")
    return items
