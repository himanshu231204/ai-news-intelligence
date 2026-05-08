from __future__ import annotations

from typing import Any, Dict, List, TypedDict


class NewsItem(TypedDict, total=False):
    source: str
    title: str
    url: str
    published_at: str
    score: float
    summary: str
    why_it_matters: str
    metadata: Dict[str, Any]


class NewsState(TypedDict):
    raw_news: List[NewsItem]
    merged_news: List[NewsItem]
    unique_news: List[NewsItem]
    filtered_news: List[NewsItem]
    ranked_news: List[NewsItem]
    summaries: List[str]
    newsletter: str
    errors: List[str]
    metadata: Dict[str, Any]
