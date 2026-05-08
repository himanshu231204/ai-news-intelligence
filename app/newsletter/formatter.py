from __future__ import annotations

from typing import List
from app.graph.state import NewsItem


def section(emoji: str, title: str, items: List[str]) -> str:
    """Format a newsletter section with emoji header and items."""
    if not items:
        return ""
    
    header = f"\n{emoji} {title}\n" + "━" * 50 + "\n"
    body = "\n".join(items)
    return header + body + "\n"


def format_news_item(item: str, index: int = None) -> str:
    """Format a single news item with index."""
    prefix = f"{index}. " if index else ""
    return f"{prefix}{item}"


def divider() -> str:
    """Return a section divider."""
    return "\n" + "─" * 50 + "\n"
