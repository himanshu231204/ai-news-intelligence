"""Company and topic detection utility for AI news articles.

This module provides keyword-based detection of companies and categories
from news article titles and summaries. Used for filtering and ranking.
"""

from __future__ import annotations

import re
from typing import Optional


# Priority companies from COLLECTION_SYSTEM_PROMPT
PRIORITY_COMPANIES = [
    "OpenAI",
    "Anthropic",
    "Google DeepMind",
    "Meta AI",
    "Microsoft AI",
    "NVIDIA AI",
    "xAI",
    "Hugging Face",
    "Mistral AI",
    "Perplexity AI",
    "LangChain",
    "Cursor",
    "Windsurf",
    "Runway",
    "Midjourney",
    "Stability AI",
    "DeepMind",
    "Google",
    "Meta",
    "Microsoft",
    "Amazon",
    "Apple",
    "Tesla",
]

# Company keyword mappings (lowercase for case-insensitive matching)
COMPANY_KEYWORDS: dict[str, list[str]] = {
    "OpenAI": [
        "openai",
        "gpt",
        "chatgpt",
        "gpt-4",
        "gpt-5",
        "o1",
        "o3",
        "sora",
        "dall-e",
        "whisper",
    ],
    "Anthropic": ["anthropic", "claude", "claude ai", "opus", "sonnet", "haiku"],
    "Google DeepMind": [
        "deepmind",
        "gemini",
        "google ai",
        "bard",
        "palm",
        "alphafold",
        "alphago",
    ],
    "Meta AI": ["meta ai", "llama", "facebook ai", "meta", "mllm", "segment anything"],
    "Microsoft AI": ["microsoft ai", "copilot", "azure ai", "bing ai", "mistral"],
    "NVIDIA AI": ["nvidia", "gpu", "h100", "a100", " Blackwell", "cuda", "tensorrt"],
    "xAI": ["xai", "grok", "elon musk ai"],
    "Hugging Face": ["hugging face", "huggingface", "transformers", "hub"],
    "Mistral AI": ["mistral", "mixtral", "mistral ai"],
    "Perplexity AI": ["perplexity", "perplexity ai"],
    "LangChain": ["langchain", "langgraph", "lcg"],
    "Cursor": ["cursor", "cursor ai", "windsurf"],
    "Windsurf": ["windsurf", "codeium"],
    "Runway": ["runway", "runway ml", "gen-3"],
    "Midjourney": ["midjourney", "mj"],
    "Stability AI": ["stability ai", "stable diffusion", "sdxl"],
}

# Priority topics from COLLECTION_SYSTEM_PROMPT
PRIORITY_TOPICS = [
    "LLMs",
    "AI agents",
    "autonomous agents",
    "coding agents",
    "reasoning models",
    "AI infrastructure",
    "RAG systems",
    "multimodal AI",
    "robotics AI",
    "open-source AI",
    "inference optimization",
    "AI chips",
    "GPUs",
    "AI safety",
    "benchmark improvements",
    "enterprise AI",
    "AI startups",
    "funding rounds",
    "AI acquisitions",
    "model releases",
    "research breakthroughs",
    "developer tools",
    "AI workflows",
    "agent frameworks",
    "MCP",
    "vector databases",
]

# Topic keyword mappings
TOPIC_KEYWORDS: dict[str, list[str]] = {
    "model_release": [
        "release",
        "launch",
        "announce",
        "debut",
        "unveil",
        "introducing",
    ],
    "research": [
        "paper",
        "arxiv",
        "research",
        "study",
        "benchmark",
        "sota",
        "state of the art",
    ],
    "funding": [
        "funding",
        "raise",
        "series",
        "investment",
        "valuation",
        "seed",
        "venture",
    ],
    "acquisition": ["acquire", "acquisition", "merge", "buy", "purchase"],
    "product": ["product", "feature", "update", "beta", "launch"],
    "open_source": [
        "open source",
        "open-source",
        "github",
        "apache",
        "mit license",
        "oss",
    ],
    "infrastructure": ["infrastructure", "api", "sdk", "tool", "platform", "cloud"],
    "agents": [
        "agent",
        "autonomous",
        "agentic",
        "agentic ai",
        "ai agent",
        "coding agent",
    ],
    "reasoning": [
        "reasoning",
        "chain of thought",
        "cot",
        "o1",
        "o3",
        "thinking",
        "reasoner",
    ],
    "multimodal": ["multimodal", "vision", "image", "video", "audio", "text-to-image"],
    "safety": [
        "safety",
        "alignment",
        "jailbreak",
        "guardrail",
        "responsible ai",
        "ethics",
    ],
    "hardware": ["gpu", "chip", "npu", "tpu", "hardware", "silicon", " Blackwell"],
}

# Negative keywords for filtering
NEGATIVE_KEYWORDS = [
    "crypto",
    "bitcoin",
    "ethereum",
    "blockchain",
    "nft",
    "web3",
    "celebrity",
    "gossip",
    "sports",
    "politics",
    "clickbait",
    "shocking",
    "you won't believe",
]


def detect_company(title: str, summary: str = "") -> Optional[str]:
    """Detect priority company from title and summary.

    Args:
        title: Article title
        summary: Article summary or description

    Returns:
        Company name if detected, None otherwise
    """
    text = f"{title} {summary}".lower()

    for company, keywords in COMPANY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text:
                return company

    return None


def detect_category(title: str, summary: str = "") -> Optional[str]:
    """Detect topic category from title and summary.

    Args:
        title: Article title
        summary: Article summary or description

    Returns:
        Category name if detected, None otherwise
    """
    text = f"{title} {summary}".lower()

    for category, keywords in TOPIC_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text:
                return category

    return None


def calculate_importance(
    company: Optional[str], category: Optional[str], title: str, score: float = 0.0
) -> float:
    """Calculate importance score based on company, category, and metadata.

    Args:
        company: Detected company name
        category: Detected category
        title: Article title (for length check)
        score: Existing score from source (e.g., HN points)

    Returns:
        Importance score from 0.0 to 10.0
    """
    importance = 0.0

    # Company boost (0-3 points)
    if company:
        importance += 3.0

    # Category boost (0-2 points)
    if category:
        category_boost = {
            "model_release": 2.0,
            "research": 1.5,
            "funding": 1.5,
            "acquisition": 1.5,
            "agents": 2.0,
            "reasoning": 2.0,
            "open_source": 1.0,
            "safety": 1.5,
        }
        importance += category_boost.get(category, 1.0)

    # Title length bonus (0-1 point)
    if 30 <= len(title) <= 200:
        importance += 1.0

    # Source score boost (0-2 points)
    if score > 100:
        importance += 2.0
    elif score > 50:
        importance += 1.0

    # Cap at 10.0
    return min(importance, 10.0)


def is_negative_content(title: str, summary: str = "") -> bool:
    """Check if content contains negative/irrelevant keywords.

    Args:
        title: Article title
        summary: Article summary

    Returns:
        True if content should be filtered out
    """
    text = f"{title} {summary}".lower()

    for keyword in NEGATIVE_KEYWORDS:
        if keyword in text:
            return True

    return False


def extract_tags(title: str, summary: str = "") -> list[str]:
    """Extract relevant tags from title and summary.

    Args:
        title: Article title
        summary: Article summary

    Returns:
        List of relevant tags
    """
    tags = []
    text = f"{title} {summary}".lower()

    # Extract company tags
    for company in COMPANY_KEYWORDS:
        for keyword in COMPANY_KEYWORDS[company]:
            if keyword in text and company not in tags:
                tags.append(company)
                break

    # Extract topic tags
    for topic in TOPIC_KEYWORDS:
        for keyword in TOPIC_KEYWORDS[topic]:
            if keyword in text and topic not in tags:
                tags.append(topic)
                break

    return tags[:10]  # Limit to 10 tags


def enrich_news_item(title: str, summary: str, score: float = 0.0) -> dict:
    """Enrich a news item with company, category, importance, and tags.

    Args:
        title: Article title
        summary: Article summary
        score: Source score (e.g., HN points)

    Returns:
        Dictionary with enriched fields
    """
    company = detect_company(title, summary)
    category = detect_category(title, summary)
    importance = calculate_importance(company, category, title, score)
    tags = extract_tags(title, summary)

    return {
        "company": company,
        "category": category,
        "importance_score": round(importance, 2),
        "tags": tags,
    }
