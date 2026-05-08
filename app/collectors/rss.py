from __future__ import annotations

import logging
from typing import List
from datetime import datetime
import feedparser

from app.graph.state import NewsItem

logger = logging.getLogger(__name__)

# High-quality AI/tech RSS feeds
AI_RSS_FEEDS = [
    "https://www.deeplearning.ai/the-batch/feed/",  # DeepLearning.AI
    "https://feeds.arstechnica.com/arstechnica/ai",  # Ars Technica AI
    "https://openai.com/feed.rss",  # OpenAI
    "https://www.anthropic.com/feed",  # Anthropic
    "https://huggingface.co/feed.xml",  # HuggingFace
    "https://stability.ai/feed",  # Stability AI
    "https://techcrunch.com/feed/?category=artificial-intelligence&feed=rss2",  # TechCrunch AI
]


async def fetch_rss() -> List[NewsItem]:
    """Fetch AI news from RSS feeds."""
    items = []
    
    for feed_url in AI_RSS_FEEDS:
        try:
            logger.info(f"Fetching RSS from {feed_url}")
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                logger.warning(f"Feed parsing warning for {feed_url}: {feed.bozo_exception}")
            
            for entry in feed.entries[:5]:  # Get top 5 from each feed
                item = NewsItem(
                    title=entry.get("title", "No title"),
                    url=entry.get("link", ""),
                    source=feed.feed.get("title", "RSS Feed"),
                    summary=entry.get("summary", "")[:500],
                    published_at=datetime.now(),
                    raw_text=entry.get("summary", ""),
                )
                items.append(item)
                
        except Exception as e:
            logger.error(f"Error fetching RSS feed {feed_url}: {e}")
    
    logger.info(f"Collected {len(items)} items from RSS feeds")
    return items
