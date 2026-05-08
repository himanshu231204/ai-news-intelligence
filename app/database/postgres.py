from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from app.config.settings import get_settings
from app.graph.state import NewsState
from app.utils.logger import get_logger

logger = get_logger(__name__)


def save_newsletter_run(state: NewsState) -> None:
    """Persist the newsletter run to a local SQLite store."""
    settings = get_settings()
    db_path = Path(settings.sqlite_db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Defensive: aggressively remove any existing footer lines (linkedin/github/follow/powered by)
    import re

    raw_text = state.newsletter or ""
    # Remove exact canonical footer occurrences
    canonical_footer = (
        "━" * 80 + "\n\n"
        "Follow for more AI insights and engineering updates\n\n"
        "LinkedIn:\n"
        "linkedin.com/in/himanshu231204\n\n"
        "GitHub:\n"
        "github.com/himanshu231204\n\n"
        "━" * 80
    )

    cleaned = raw_text.replace(canonical_footer, "")

    # Strip any stray lines that mention linkedin, github, follow, or powered by
    cleaned = re.sub(
        r"(?im)^.*(linkedin\.com|github\.com|follow for more|follow me|powered by).*$\n?",
        "",
        cleaned,
    )

    sanitized = cleaned.strip() + "\n\n" + canonical_footer

    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "article_count": len(state.ranked_news),
        "newsletter_text": sanitized,
        "errors": json.dumps(state.errors),
        "metadata": json.dumps(state.metadata),
    }

    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS newsletter_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                article_count INTEGER NOT NULL,
                newsletter_text TEXT NOT NULL,
                errors TEXT NOT NULL,
                metadata TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            INSERT INTO newsletter_runs (created_at, article_count, newsletter_text, errors, metadata)
            VALUES (:created_at, :article_count, :newsletter_text, :errors, :metadata)
            """,
            payload,
        )
        connection.commit()

    logger.info(
        "Persisted newsletter run to %s with %s ranked items",
        db_path,
        payload["article_count"],
    )
