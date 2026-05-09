"""LLM module for multi-provider AI inference.

This module provides:
- Direct provider calls (Groq, OpenRouter, Gemini)
- Fallback routing with automatic provider switching
- Retry logic with exponential backoff
- Error handling and logging

Usage:
    from app.llm import LLMRouter

    router = LLMRouter()
    summary = await router.summarize(news_item)
    newsletter = await router.generate_newsletter(articles, date)
"""

from app.llm.router import LLMRouter

__all__ = ["LLMRouter"]
