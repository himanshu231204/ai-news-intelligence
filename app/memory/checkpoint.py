from __future__ import annotations

import os
from typing import Optional

from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres import PostgresSaver

from app.config.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def get_checkpointer():
    """Get checkpointer (PostgreSQL if configured, otherwise in-memory)."""
    settings = get_settings()
    
    # Try PostgreSQL if connection string is available
    if settings.postgres_url:
        try:
            logger.info("Initializing PostgreSQL checkpointer")
            checkpointer = PostgresSaver.from_conn_string(settings.postgres_url)
            logger.info("PostgreSQL checkpointer initialized")
            return checkpointer
        except Exception as e:
            logger.warning("Failed to initialize PostgreSQL checkpointer: %s. Using in-memory.", e)
    
    logger.info("Using in-memory checkpointer")
    return MemorySaver()
