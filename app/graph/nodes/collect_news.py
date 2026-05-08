from __future__ import annotations

import asyncio

from app.collectors.github import fetch_github_trending
from app.collectors.hackernews import fetch_hackernews
from app.collectors.reddit import fetch_reddit
from app.collectors.rss import fetch_rss
from app.collectors.twitter import fetch_twitter
from app.collectors.arxiv import fetch_arxiv_papers
from app.collectors.devto import fetch_devto_articles
from app.collectors.producthunt import fetch_producthunt_tools
from app.graph.state import NewsState


async def collect_news_node(state: NewsState) -> NewsState:
    """Collect from all sources in parallel."""
    (
        rss_news,
        github_news,
        hn_news,
        reddit_news,
        twitter_news,
        arxiv_news,
        devto_news,
        ph_news,
    ) = await asyncio.gather(
        fetch_rss(),
        fetch_github_trending(),
        fetch_hackernews(),
        fetch_reddit(),
        fetch_twitter(),
        fetch_arxiv_papers(),
        fetch_devto_articles(),
        fetch_producthunt_tools(),
        return_exceptions=True,
    )

    collected = []
    errors = list(state.errors)
    for result in (
        rss_news,
        github_news,
        hn_news,
        reddit_news,
        twitter_news,
        arxiv_news,
        devto_news,
        ph_news,
    ):
        if isinstance(result, Exception):
            errors.append(str(result))
            continue
        collected.extend(result)

    # Return updated state
    state.raw_news = collected
    state.errors = errors
    return state
