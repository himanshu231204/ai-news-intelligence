from __future__ import annotations

import logging
from typing import List
from datetime import datetime
import httpx

from app.graph.state import NewsItem
from app.config.settings import get_settings

logger = logging.getLogger(__name__)

# AI-related search queries for Twitter
TWITTER_SEARCH_QUERIES = [
    "#AI",
    "#MachineLearning",
    "#LLM",
    "#GPT",
    "#OpenAI",
    "#Anthropic",
    "#LangChain",
    "artificial intelligence",
]


from app.utils.retry import async_retry

@async_retry(max_retries=3, backoff_factor=2, initial_delay=2)
async def fetch_twitter() -> List[NewsItem]:
    """Fetch AI news from Twitter using search.
    
    Note: Requires Twitter API v2 Bearer Token.
    Get one from: https://developer.twitter.com/en/portal/dashboard
    """
    items = []
    settings = get_settings()
    
    # Check if Twitter API token is configured
    if not settings.twitter_bearer_token:
        logger.warning("Twitter Bearer token not configured. Skipping Twitter collection.")
        return items
    
    headers = {"Authorization": f"Bearer {settings.twitter_bearer_token}"}
    
    try:
        async with httpx.AsyncClient(timeout=15, headers=headers) as client:
            for query in TWITTER_SEARCH_QUERIES[:3]:  # Search top 3 queries
                try:
                    logger.info(f"Searching Twitter for: {query}")
                    
                    response = await client.get(
                        "https://api.twitter.com/2/tweets/search/recent",
                        params={
                            "query": f"{query} -is:retweet -is:reply lang:en",
                            "max_results": 10,
                            "tweet.fields": "created_at,public_metrics",
                            "expansions": "author_id",
                            "user.fields": "username",
                        }
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    tweets = data.get("data", [])
                    includes = data.get("includes", {})
                    users = {user["id"]: user["username"] for user in includes.get("users", [])}
                    
                    for tweet in tweets[:3]:
                        author_id = tweet.get("author_id")
                        username = users.get(author_id, "Unknown")
                        metrics = tweet.get("public_metrics", {})
                        
                        item = NewsItem(
                            title=tweet.get("text", "")[:200],
                            url=f"https://twitter.com/{username}/status/{tweet.get('id', '')}",
                            source=f"Twitter (@{username})",
                            summary=f"❤️ {metrics.get('like_count', 0)} | 🔄 {metrics.get('retweet_count', 0)} | 💬 {metrics.get('reply_count', 0)}",
                            published_at=datetime.fromisoformat(tweet.get("created_at", datetime.now().isoformat()).replace("Z", "+00:00")),
                            raw_text=tweet.get("text", ""),
                        )
                        items.append(item)
                        
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429:
                        logger.warning("Twitter API rate limit reached")
                        break
                    logger.error(f"Twitter API error for query '{query}': {e}")
                except Exception as e:
                    logger.warning(f"Error processing Twitter query '{query}': {e}")
        
        logger.info(f"Collected {len(items)} items from Twitter")
        
    except Exception as e:
        logger.error(f"Error fetching from Twitter: {e}")
    
    return items
