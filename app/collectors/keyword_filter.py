"""Local keyword filtering for AI news articles.

This module provides keyword-based filtering BEFORE any LLM calls.
It removes low-signal articles and non-AI content using high-signal keywords.

Key Features:
- Fast Python-based filtering (no LLM needed)
- High-signal AI keywords
- Configurable keyword lists
- Early exit before expensive LLM processing
"""

from __future__ import annotations

import re
from typing import List, Set

from app.graph.state import NewsItem
from app.utils.logger import get_logger

logger = get_logger(__name__)

# High-signal AI keywords - articles must contain at least one
HIGH_SIGNAL_KEYWORDS: Set[str] = {
    # Major AI Companies/Products
    "openai",
    "anthropic",
    "claude",
    "gpt-5",
    "gpt4",
    "gpt-4",
    "gemini",
    "deepmind",
    "google ai",
    "meta ai",
    "llama",
    "mistral",
    "deepseek",
    "qwen",
    "yi",
    "moonshot",
    # AI Categories
    "ai agent",
    "agents",
    "agentic",
    "reasoning",
    "reasoning model",
    "multimodal",
    "vision model",
    "text-to-image",
    "image generation",
    "text-to-video",
    "video generation",
    "text-to-speech",
    "voice ai",
    "rag",
    "retrieval augmented",
    "vector database",
    "embedding",
    "fine-tuning",
    "pre-training",
    "training data",
    "model distillation",
    "inference",
    "inference engine",
    "serving",
    "deployment",
    # AI Infrastructure
    "langgraph",
    "langchain",
    "autogen",
    "crewai",
    "agent framework",
    "mlops",
    "aiops",
    "model registry",
    "feature store",
    "gpu",
    "tpu",
    "nvidia",
    "cuda",
    "tensorrt",
    # Technical Terms
    "transformer",
    "attention",
    "diffusion",
    "latent space",
    "tokenizer",
    "vocabulary",
    "context window",
    "context length",
    "parameters",
    "weights",
    "neural network",
    "deep learning",
    # Research
    "arxiv",
    "paper",
    "research",
    "benchmark",
    "sota",
    "iclr",
    "neurips",
    "cvpr",
    "acl",
    "emNLP",
    # Open Source
    "open source",
    "github",
    "hugging face",
    "weights",
    "model weights",
    "apache",
    "mit license",
    "repository",
    "stars",
    "trending",
    # Business/Industry
    "funding",
    "series a",
    "series b",
    "acquisition",
    "ipo",
    "partnership",
    "enterprise",
    "api",
    "sdk",
    "developer tool",
}

# Low-signal keywords - articles containing these are filtered out
LOW_SIGNAL_KEYWORDS: Set[str] = {
    # Non-AI Tech
    "crypto",
    "bitcoin",
    "ethereum",
    "blockchain",
    "nft",
    "web3",
    "defi",
    "smart contract",
    "solidity",
    # Non-AI Hardware
    "iphone",
    "android",
    "samsung",
    "pixel",
    "galaxy",
    "macbook",
    "laptop",
    "desktop",
    "cpu",
    "ram",
    # Non-AI Software
    "excel",
    "word",
    "powerpoint",
    "notion",
    "slack",
    "zoom",
    "teams",
    "discord",
    "spotify",
    "netflix",
    # Generic/Vague
    "tech news",
    "technology",
    "innovation",
    "startup",
    "breaking",
    "latest",
    "just in",
    "announcing",
}


def is_ai_related(item: NewsItem) -> bool:
    """Check if article is related to AI using keyword matching.

    Fast local filtering - no LLM needed.

    Args:
        item: NewsItem to check

    Returns:
        True if article is AI-related, False otherwise
    """
    title = (item.title or "").lower()
    summary = (item.summary or "").lower()
    url = (item.url or "").lower()

    # Combine text for checking
    combined = f"{title} {summary} {url}"

    # Check for high-signal keywords
    has_high_signal = any(keyword in combined for keyword in HIGH_SIGNAL_KEYWORDS)

    if not has_high_signal:
        return False

    # Check for low-signal keywords
    has_low_signal = any(keyword in combined for keyword in LOW_SIGNAL_KEYWORDS)

    # If has low-signal keywords, be more strict - require strong AI signal
    if has_low_signal:
        # Count high-signal matches
        high_signal_count = sum(1 for kw in HIGH_SIGNAL_KEYWORDS if kw in combined)
        # Require at least 2 high-signal keywords if low-signal present
        return high_signal_count >= 2

    return True


def filter_by_keywords(items: List[NewsItem]) -> List[NewsItem]:
    """Filter articles using keyword matching.

    This runs BEFORE any LLM calls to reduce API usage.

    Args:
        items: List of NewsItems to filter

    Returns:
        Filtered list of AI-related NewsItems
    """
    filtered = []
    removed_count = 0

    for item in items:
        if is_ai_related(item):
            filtered.append(item)
        else:
            removed_count += 1
            logger.debug(f"Filtered out non-AI: {item.title[:50]}...")

    if removed_count > 0:
        logger.info(
            f"Keyword filter: {removed_count}/{len(items)} articles removed "
            f"({removed_count / len(items) * 100:.1f}% filtered)"
        )

    return filtered


def get_keyword_stats(items: List[NewsItem], filtered: List[NewsItem]) -> dict:
    """Get statistics about keyword filtering results.

    Args:
        items: Original list before filtering
        filtered: List after filtering

    Returns:
        Dictionary with filter statistics
    """
    return {
        "total_items": len(items),
        "filtered_items": len(filtered),
        "removed_items": len(items) - len(filtered),
        "filter_rate": round((len(items) - len(filtered)) / len(items) * 100, 1)
        if items
        else 0,
    }


def extract_ai_keywords(text: str) -> List[str]:
    """Extract AI keywords from text for debugging/logging.

    Args:
        text: Text to search for keywords

    Returns:
        List of matched keywords
    """
    text_lower = text.lower()
    matched = []

    for keyword in HIGH_SIGNAL_KEYWORDS:
        if keyword in text_lower:
            matched.append(keyword)

    return matched[:5]  # Return top 5 matches
