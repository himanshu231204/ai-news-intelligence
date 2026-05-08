from __future__ import annotations

from typing import List
from app.graph.state import NewsItem


# Priority companies for ranking boost
PRIORITY_COMPANIES = {
    "OpenAI": 3.0,
    "Anthropic": 3.0,
    "Google DeepMind": 2.5,
    "Meta AI": 2.0,
    "Microsoft AI": 2.0,
    "NVIDIA AI": 2.5,
    "xAI": 2.0,
    "Hugging Face": 2.0,
    "Mistral AI": 1.5,
    "Perplexity AI": 1.5,
    "LangChain": 1.5,
}

# Category weights for ranking
CATEGORY_WEIGHTS = {
    "model_release": 2.5,
    "research": 2.0,
    "funding": 1.5,
    "acquisition": 1.5,
    "agents": 2.0,
    "reasoning": 2.0,
    "open_source": 1.5,
    "safety": 1.5,
    "infrastructure": 1.0,
    "product": 1.0,
    "hardware": 1.5,
    "multimodal": 1.5,
}


def score_item(item: NewsItem) -> float:
    """Calculate ranking score for a news item.

    Uses multiple factors:
    - Importance score from collector
    - Company priority boost
    - Category weight
    - Source score (e.g., HN points, GitHub stars)
    - Title length quality

    Args:
        item: NewsItem to score

    Returns:
        Score from 0.0 to 10.0
    """
    score = 0.0

    # Base importance from collector (0-5)
    score += min(item.importance_score, 5.0)

    # Company priority boost (0-3)
    if item.company:
        score += PRIORITY_COMPANIES.get(item.company, 1.0)

    # Category weight (0-2.5)
    if item.category:
        score += CATEGORY_WEIGHTS.get(item.category, 1.0)

    # Source score boost (0-2)
    if item.score > 100:
        score += 2.0
    elif item.score > 50:
        score += 1.0
    elif item.score > 20:
        score += 0.5

    # Title quality bonus (0-1)
    title = item.title or ""
    if 30 <= len(title) <= 150:
        score += 0.5

    # Tag bonus (0-1)
    if item.tags and len(item.tags) >= 3:
        score += 0.5

    return round(min(score, 10.0), 3)


def rank_news(items: List[NewsItem]) -> List[NewsItem]:
    """Rank news items by composite score.

    Args:
        items: List of NewsItem to rank

    Returns:
        Sorted list of NewsItem by score descending
    """
    scored: List[NewsItem] = []
    for item in items:
        # Create new item with updated score
        item_dict = dict(item)
        item_dict["score"] = score_item(item)
        scored.append(NewsItem(**item_dict))

    return sorted(scored, key=lambda x: x.score, reverse=True)
