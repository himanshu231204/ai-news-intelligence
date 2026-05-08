from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class NewsletterRun:
    created_at: datetime
    article_count: int
    newsletter_text: str
