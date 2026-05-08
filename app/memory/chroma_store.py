from __future__ import annotations

import uuid
from typing import Iterable, List

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config.settings import get_settings

# Optional: you can use any LangChain embedding class here. For now we provide a placeholder
# that simply stores raw documents without embeddings when embeddings are disabled.


def _get_client():
    """Create a persistent Chroma client based on the configured path."""
    settings = get_settings()
    client = chromadb.PersistentClient(path=settings.chroma_path)
    return client


def init_collection():
    """Initialize (or get) the collection for news embeddings.

    Returns:
        chromadb.Collection: The Chroma collection instance.
    """
    client = _get_client()
    # Use a fixed collection name; creates if not exists.
    collection = client.get_or_create_collection(name="news_embeddings")
    return collection


def upsert_vectors(documents: Iterable[str]) -> None:
    """Upsert raw documents into the Chroma collection.

    If embeddings are disabled via the `use_embeddings` flag, this function becomes a no‑op.
    Otherwise, it computes embeddings using the configured LLM provider and stores them.
    """
    settings = get_settings()

    if not settings.use_embeddings:
        # Feature disabled – skip any work.
        return

    # Lazy import to avoid unnecessary heavy dependencies when embeddings are off.
    # Prefer Groq embeddings if GROQ_API_KEY is set, otherwise fall back to OpenAI.
    if settings.groq_api_key:
        from langchain_community.embeddings import GroqEmbeddings
        embedder = GroqEmbeddings(api_key=settings.groq_api_key, model="nomic-ai/nomic-embed-text-v1.5-Groq")
    elif settings.openai_api_key:
        from langchain_openai import OpenAIEmbeddings
        embedder = OpenAIEmbeddings(openai_api_key=settings.openai_api_key)
    else:
        raise RuntimeError("No embedding provider configured (neither GROQ nor OpenAI API key set).")

    docs = list(documents)
    if not docs:
        return

    # Compute embeddings – this may be an async operation in some providers, but we use sync for simplicity.
    embeddings: List[List[float]] = embedder.embed_documents(docs)

    collection = init_collection()

    # Generate stable ids for each document – using uuid4.
    ids = [str(uuid.uuid4()) for _ in docs]

    # Add or update entries in the collection.
    collection.add(ids=ids, documents=docs, embeddings=embeddings)
