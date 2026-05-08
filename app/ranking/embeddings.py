from __future__ import annotations

import os
from typing import Iterable, List

from langchain_huggingface import HuggingFaceEmbeddings

from app.config.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def get_embeddings_model():
    """Get embeddings model using free HuggingFace (no API key required)."""
    try:
        settings = get_settings()
        logger.info("Loading HuggingFace embeddings (free, no API key needed)")
        # Using a small, fast local model by default.
        embeddings = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
            model_kwargs={"trust_remote_code": True}
        )
        logger.info("HuggingFace embeddings ready")
        return embeddings
    except Exception as e:
        logger.error("Failed to load HuggingFace embeddings: %s", e)
        raise


def embed_texts(texts: Iterable[str]) -> List[List[float]]:
    """Embed texts using free HuggingFace embeddings."""
    try:
        model = get_embeddings_model()
        text_list = list(texts)
        if not text_list:
            return []
        embeddings = model.embed_documents(text_list)
        return embeddings
    except Exception as e:
        logger.error("Embedding failed: %s. Using zero vectors as fallback.", e)
        # Fallback: return zero vectors (384 dimensions for all-MiniLM-L6-v2)
        return [[0.0] * 384 for _ in text_list]


def embed_query(query: str) -> List[float]:
    """Embed a single query text."""
    try:
        model = get_embeddings_model()
        embedding = model.embed_query(query)
        return embedding
    except Exception as e:
        logger.error("Query embedding failed: %s. Using zero vector as fallback.", e)
        return [0.0] * 384
