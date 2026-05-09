from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class NewsItem(BaseModel):
    """Pydantic model for news articles with validation and type safety."""

    source: str
    title: str
    url: str
    published_at: datetime | str = Field(default_factory=datetime.now)
    score: float = 0.0
    summary: str = ""
    why_it_matters: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # New fields for enhanced filtering and ranking
    company: Optional[str] = None
    category: Optional[str] = None
    importance_score: float = 0.0
    tags: List[str] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True


class NewsState(BaseModel):
    """LangGraph state for the news collection pipeline."""

    raw_news: List[NewsItem] = Field(default_factory=list)
    merged_news: List[NewsItem] = Field(default_factory=list)
    unique_news: List[NewsItem] = Field(default_factory=list)
    filtered_news: List[NewsItem] = Field(default_factory=list)
    ranked_news: List[NewsItem] = Field(default_factory=list)
    summaries: List[str] = Field(default_factory=list)
    newsletter: str = ""
    # LinkedIn newsletter fields
    linkedin_newsletter: str = ""
    google_doc_link: str = ""
    linkedin_saved: bool = False
    # Error tracking
    errors: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True
