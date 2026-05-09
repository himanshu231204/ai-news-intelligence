from __future__ import annotations

import logging
from typing import List
from datetime import datetime
import feedparser

from app.graph.state import NewsItem
from app.utils.company_detector import enrich_news_item, is_negative_content

logger = logging.getLogger(__name__)

# High-quality AI/tech RSS feeds
AI_RSS_FEEDS = [
    # Major AI Labs & Companies
    "https://www.deeplearning.ai/the-batch/feed/",  # DeepLearning.AI
    "https://openai.com/feed.rss",  # OpenAI
    "https://www.anthropic.com/feed",  # Anthropic
    "https://huggingface.co/feed.xml",  # HuggingFace
    "https://stability.ai/feed",  # Stability AI
    "https://www.google.ai/feed",  # Google AI
    "https://www.metai.com/feed",  # Meta AI
    "https://www.nvidia.com/ai-blog/rss",  # NVIDIA AI
    "https://www.microsoft.com/ai/blog/rss",  # Microsoft AI
    "https://www.amazon.science/feed",  # Amazon Science
    "https://www.mistral.ai/feed",  # Mistral AI
    "https://www.x.ai/feed",  # xAI
    "https://www.cohere.com/feed",  # Cohere
    "https://www.ai21.com/feed",  # AI21 Labs
    "https://www.anyscale.com/feed",  # Anyscale
    "https://www.run.ai/feed",  # Run:ai
    # AI Research & Papers
    "https://arxiv.org/rss/cs.AI",  # arXiv AI
    "https://arxiv.org/rss/cs.LG",  # arXiv Machine Learning
    "https://arxiv.org/rss/cs.CL",  # arXiv Computation & Language
    "https://arxiv.org/rss/cs.CV",  # arXiv Computer Vision
    "https://paperswithcode.com/feed",  # Papers With Code
    # Tech News - AI Section
    "https://feeds.arstechnica.com/arstechnica/ai",  # Ars Technica AI
    "https://techcrunch.com/feed/?category=artificial-intelligence&feed=rss2",  # TechCrunch AI
    "https://www.theverge.com/rss/ai/index.xml",  # The Verge AI
    "https://www.wired.com/feed/tag/ai/latest/rss",  # Wired AI
    "https://www.wired.com/feed/tag/machine-learning/latest/rss",  # Wired ML
    "https://venturebeat.com/ai/feed/",  # VentureBeat AI
    "https://www.zdnet.com/news/artificial-intelligence/feed/",  # ZDNet AI
    "https://www.forbes.com/ai/rss.xml",  # Forbes AI
    "https://www.reuters.com/technology/artificial-intelligence/feed/",  # Reuters AI
    "https://www.reuters.com/technology/tech-industry/feed/",  # Reuters Tech
    # AI Newsletters & Blogs
    "https://www.sequoiacap.com/feed/",  # Sequoia Capital
    "https://a16z.com/feed/",  # Andreessen Horowitz
    "https://www.lenny.fyi/feed.xml",  # Lenny's Newsletter
    "https://www.interconnects.ai/feed",  # Interconnects
    "https://www.latent.space/feed",  # Latent Space
    "https://www.smashingrobots.com/feed",  # Smashing Robots
    # Open Source AI
    "https://github.blog/feed/",  # GitHub Blog
    "https://blog.pytorch.org/feed.xml",  # PyTorch Blog
    "https://tensorflow.blog/feed/",  # TensorFlow Blog
    "https://mlops.space/feed/",  # MLOps.space
    # AI Podcasts & Media
    "https://lexfridman.com/feed/",  # Lex Fridman
    "https://podcast.ai/feed",  # Podcast.ai
]


from app.utils.retry import async_retry


@async_retry(max_retries=3, backoff_factor=2, initial_delay=2)
async def fetch_rss() -> List[NewsItem]:
    """Fetch AI news from RSS feeds with company detection."""
    items = []

    for feed_url in AI_RSS_FEEDS:
        try:
            logger.info(f"Fetching RSS from {feed_url}")
            feed = feedparser.parse(feed_url)

            if feed.bozo:
                logger.warning(
                    f"Feed parsing warning for {feed_url}: {feed.bozo_exception}"
                )

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

    logger.info(f"Collected {len(items)} items from RSS feeds")
    return items
