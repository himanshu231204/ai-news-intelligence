from __future__ import annotations

import logging
from typing import List
from datetime import datetime
import feedparser

from app.graph.state import NewsItem
from app.utils.company_detector import enrich_news_item, is_negative_content

logger = logging.getLogger(__name__)

# High-quality AI/tech RSS feeds - verified working feeds
AI_RSS_FEEDS = [
    # Major AI Labs & Companies
    "https://www.deeplearning.ai/the-batch/feed/",  # DeepLearning.AI
    "https://openai.com/feed.rss",  # OpenAI
    "https://www.anthropic.com/feed",  # Anthropic
    "https://huggingface.co/feed.xml",  # HuggingFace
    "https://stability.ai/feed",  # Stability AI
    "https://www.google.ai/feed",  # Google AI
    "https://www.nvidia.com/ai-blog/rss",  # NVIDIA AI
    "https://www.microsoft.com/ai/blog/rss",  # Microsoft AI
    # AI Research & Papers
    "https://arxiv.org/rss/cs.AI",  # arXiv AI
    "https://arxiv.org/rss/cs.LG",  # arXiv Machine Learning
    "https://arxiv.org/rss/cs.CL",  # arXiv Computation & Language
    "https://arxiv.org/rss/cs.CV",  # arXiv Computer Vision
    # Tech News - AI Section
    "https://feeds.arstechnica.com/arstechnica/ai",  # Ars Technica AI
    "https://techcrunch.com/feed/?category=artificial-intelligence&feed=rss2",  # TechCrunch AI
    "https://www.theverge.com/rss/ai/index.xml",  # The Verge AI
    "https://www.wired.com/feed/tag/ai/latest/rss",  # Wired AI
    "https://www.zdnet.com/news/artificial-intelligence/feed/",  # ZDNet AI
    "https://www.forbes.com/ai/rss.xml",  # Forbes AI
    "https://www.reuters.com/technology/artificial-intelligence/feed/",  # Reuters AI
    # AI Newsletters & Blogs
    "https://www.sequoiacap.com/feed/",  # Sequoia Capital
    "https://a16z.com/feed/",  # Andreessen Horowitz
    "https://www.interconnects.ai/feed",  # Interconnects
    "https://www.latent.space/feed",  # Latent Space
    # Open Source AI
    "https://github.blog/feed/",  # GitHub Blog
    "https://tensorflow.blog/feed/",  # TensorFlow Blog
    # AI Podcasts & Media
    "https://lexfridman.com/feed/",  # Lex Fridman
]

# Problematic feeds - removed due to malformed content
# "https://www.amazon.science/feed",  # Returns malformed HTML
# "https://www.mistral.ai/feed",  # Returns malformed content
# "https://www.x.ai/feed",  # Returns malformed HTML
# "https://www.cohere.com/feed",  # Returns HTML instead of XML
# "https://www.ai21.com/feed",  # Returns malformed content
# "https://www.anyscale.com/feed",  # Returns malformed content
# "https://www.run.ai/feed",  # Returns malformed content
# "https://paperswithcode.com/feed",  # Returns malformed content
# "https://venturebeat.com/ai/feed/",  # Returns HTML instead of XML
# "https://www.reuters.com/technology/tech-industry/feed/",  # Returns HTML
# "https://www.lenny.fyi/feed.xml",  # Returns malformed content
# "https://www.smashingrobots.com/feed",  # Returns HTML instead of XML
# "https://blog.pytorch.org/feed.xml",  # DNS resolution failed
# "https://www.metai.com/feed",  # SSL error
# "https://www.wired.com/feed/tag/machine-learning/latest/rss",  # Malformed
# "https://podcast.ai/feed",  # DNS resolution failed
# "https://mlops.space/feed/",  # Returns HTML instead of XML


from app.utils.retry import async_retry


def _is_valid_feed(feed, feed_url: str) -> bool:
    """Check if feed is valid XML/RSS."""
    if feed.bozo:
        exception = str(feed.bozo_exception)
        # Check for common issues that indicate non-RSS content
        if "not well-formed" in exception:
            logger.warning(f"Skipping malformed feed: {feed_url}")
            return False
        if "not an XML media type" in exception:
            logger.warning(f"Skipping HTML feed (not RSS): {feed_url}")
            return False
        if "syntax error" in exception:
            logger.warning(f"Skipping feed with syntax error: {feed_url}")
            return False
        if "junk after document element" in exception:
            logger.warning(f"Skipping malformed feed: {feed_url}")
            return False
        if "mismatched tag" in exception:
            logger.warning(f"Skipping malformed feed: {feed_url}")
            return False
    return True


@async_retry(max_retries=3, backoff_factor=2, initial_delay=2)
async def fetch_rss() -> List[NewsItem]:
    """Fetch AI news from RSS feeds with company detection."""
    items = []
    valid_count = 0
    skipped_count = 0

    for feed_url in AI_RSS_FEEDS:
        try:
            logger.info(f"Fetching RSS from {feed_url}")
            feed = feedparser.parse(feed_url)

            # Validate feed before processing
            if not _is_valid_feed(feed, feed_url):
                skipped_count += 1
                continue

            valid_count += 1

            for entry in feed.entries[:5]:  # Get top 5 from each feed
                title = entry.get("title", "No title")
                summary = entry.get("summary", "")[:500]

                # Skip negative content
                if is_negative_content(title, summary):
                    continue

                # Enrich with company detection
                enrichment = enrich_news_item(title, summary)

                item = NewsItem(
                    title=title,
                    url=entry.get("link", ""),
                    source=feed.feed.get("title", "RSS Feed"),
                    summary=summary,
                    published_at=datetime.now(),
                    raw_text=entry.get("summary", ""),
                    # New fields
                    company=enrichment["company"],
                    category=enrichment["category"],
                    importance_score=enrichment["importance_score"],
                    tags=enrichment["tags"],
                )
                items.append(item)

        except Exception as e:
            logger.error(f"Error fetching RSS feed {feed_url}: {e}")
            skipped_count += 1

    logger.info(
        f"RSS Feed stats: {valid_count} valid, {skipped_count} skipped, {len(items)} items collected"
    )
    return items
