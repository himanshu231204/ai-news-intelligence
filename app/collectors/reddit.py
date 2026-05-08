from __future__ import annotations

import logging
from typing import List
from datetime import datetime
import praw

from app.graph.state import NewsItem
from app.config.settings import get_settings

logger = logging.getLogger(__name__)

# AI-focused subreddits
AI_SUBREDDITS = [
    "MachineLearning",
    "LanguageModels",
    "OpenAI",
    "LocalLLaMA",
    "Artificial",
    "deeplearning",
]


async def fetch_reddit() -> List[NewsItem]:
    """Fetch AI news from Reddit subreddits."""
    items = []
    settings = get_settings()
    
    try:
        # Check if Reddit credentials are configured
        if not settings.reddit_client_id or not settings.reddit_client_secret:
            logger.warning("Reddit credentials not configured. Skipping Reddit collection.")
            return items
        
        reddit = praw.Reddit(
            client_id=settings.reddit_client_id,
            client_secret=settings.reddit_client_secret,
            user_agent="AINewsAgent/1.0",
        )
        
        for subreddit_name in AI_SUBREDDITS:
            try:
                logger.info(f"Fetching posts from r/{subreddit_name}")
                subreddit = reddit.subreddit(subreddit_name)
                
                # Get top posts from past day
                for post in subreddit.top(time_filter="day", limit=5):
                    item = NewsItem(
                        title=post.title,
                        url=post.url if post.url.startswith("http") else f"https://reddit.com{post.permalink}",
                        source=f"Reddit (r/{subreddit_name})",
                        summary=post.selftext[:500] if post.selftext else f"↑ {post.ups} | Comments: {post.num_comments}",
                        published_at=datetime.fromtimestamp(post.created_utc),
                        raw_text=post.title,
                    )
                    items.append(item)
                    
            except Exception as e:
                logger.error(f"Error fetching r/{subreddit_name}: {e}")
        
        logger.info(f"Collected {len(items)} items from Reddit")
        
    except Exception as e:
        logger.error(f"Error initializing Reddit API: {e}")
    
    return items
