"""
Summary Cache Module

Provides caching for LLM summaries to avoid redundant API calls.
Uses SQLite for persistent storage.
"""

import hashlib
import json
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Optional

from app.utils.logger import get_logger

logger = get_logger(__name__)

# Cache file path
CACHE_DB_PATH = "summary_cache.db"


class SummaryCache:
    """SQLite-based cache for LLM summaries."""

    def __init__(self, db_path: str = CACHE_DB_PATH, ttl_days: int = 7):
        """Initialize the summary cache.

        Args:
            db_path: Path to SQLite database
            ttl_days: Time-to-live for cache entries in days
        """
        self.db_path = db_path
        self.ttl_days = ttl_days
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the database and table."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS summary_cache (
                    key TEXT PRIMARY KEY,
                    summary TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            conn.close()
            logger.info(f"Summary cache initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize summary cache: {e}")

    def _generate_key(self, title: str, source: str) -> str:
        """Generate a unique cache key from title and source."""
        # Normalize the key by lowercasing and removing special chars
        normalized = f"{title.lower().strip()}_{source.lower().strip()}"
        return hashlib.sha256(normalized.encode()).hexdigest()

    def get(self, title: str, source: str) -> Optional[str]:
        """Get a cached summary if it exists and is not expired.

        Args:
            title: Article title
            source: Article source

        Returns:
            Cached summary or None if not found/expired
        """
        try:
            key = self._generate_key(title, source)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check if key exists and is not expired
            cursor.execute(
                """
                SELECT summary, created_at FROM summary_cache
                WHERE key = ?
                """,
                (key,),
            )
            row = cursor.fetchone()
            conn.close()

            if row:
                summary, created_at = row
                # Check if expired
                created = datetime.fromisoformat(created_at)
                if datetime.now() - created < timedelta(days=self.ttl_days):
                    logger.info(f"Cache hit for: {title[:30]}...")
                    return summary
                else:
                    # Clean up expired entry
                    self._delete(key)
                    logger.info(f"Cache expired for: {title[:30]}...")

            return None

        except Exception as e:
            logger.warning(f"Cache get error: {e}")
            return None

    def set(self, title: str, source: str, summary: str) -> None:
        """Store a summary in the cache.

        Args:
            title: Article title
            source: Article source
            summary: Summary text to cache
        """
        try:
            key = self._generate_key(title, source)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO summary_cache (key, summary, created_at)
                VALUES (?, ?, ?)
                """,
                (key, summary, datetime.now().isoformat()),
            )
            conn.commit()
            conn.close()
            logger.info(f"Cached summary for: {title[:30]}...")

        except Exception as e:
            logger.warning(f"Cache set error: {e}")

    def _delete(self, key: str) -> None:
        """Delete a cache entry by key."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM summary_cache WHERE key = ?", (key,))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"Cache delete error: {e}")

    def cleanup(self) -> int:
        """Remove all expired entries from the cache.

        Returns:
            Number of entries removed
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Delete entries older than TTL
            cutoff = (datetime.now() - timedelta(days=self.ttl_days)).isoformat()
            cursor.execute("DELETE FROM summary_cache WHERE created_at < ?", (cutoff,))
            deleted = cursor.rowcount
            conn.commit()
            conn.close()

            if deleted > 0:
                logger.info(f"Cleaned up {deleted} expired cache entries")

            return deleted

        except Exception as e:
            logger.warning(f"Cache cleanup error: {e}")
            return 0

    def clear(self) -> None:
        """Clear all cache entries."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM summary_cache")
            conn.commit()
            conn.close()
            logger.info("Summary cache cleared")
        except Exception as e:
            logger.warning(f"Cache clear error: {e}")


# Global cache instance
_cache: Optional[SummaryCache] = None


def get_summary_cache() -> SummaryCache:
    """Get or create the global summary cache instance."""
    global _cache
    if _cache is None:
        _cache = SummaryCache()
    return _cache
