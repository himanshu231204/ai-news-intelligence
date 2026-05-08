from __future__ import annotations

from typing import List

from app.graph.state import NewsItem


def score_item(item: NewsItem) -> float:
    title = item.get("title", "")
    source = item.get("source", "")
    base = float(len(title)) / 100.0
    source_boost = 0.2 if source in {"rss", "github", "hackernews"} else 0.0
    return round(base + source_boost, 3)


def rank_news(items: List[NewsItem]) -> List[NewsItem]:
    scored: List[NewsItem] = []
    for item in items:
        enriched = dict(item)
        enriched["score"] = score_item(item)
        scored.append(enriched)
    return sorted(scored, key=lambda x: x.get("score", 0.0), reverse=True)
