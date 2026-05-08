from __future__ import annotations

import os
from typing import Iterable, List, Dict, Any

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.ranking.embeddings import embed_texts, embed_query
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Initialize ChromaDB client (persistent storage)
CHROMA_PATH = os.environ.get("CHROMA_PATH", "./chroma_data")


class VectorStore:
    """ChromaDB-backed vector store for deduplication."""

    def __init__(self, collection_name: str = "ai_news"):
        """Initialize ChromaDB client and collection."""
        os.makedirs(CHROMA_PATH, exist_ok=True)
        
        try:
            # Persistent ChromaDB client
            self.client = chromadb.PersistentClient(path=CHROMA_PATH)
            logger.info("Connected to ChromaDB at %s", CHROMA_PATH)
        except Exception as e:
            logger.error("Failed to initialize ChromaDB: %s. Using in-memory fallback.", e)
            self.client = chromadb.EphemeralClient()
        
        self.collection_name = collection_name
        self.collection = None
        self._init_collection()

    def _init_collection(self) -> None:
        """Initialize or get collection."""
        try:
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("Collection '%s' ready", self.collection_name)
        except Exception as e:
            logger.error("Failed to create collection: %s", e)
            raise

    def add_documents(self, documents: Dict[str, Any], metadata: Dict[str, Any] = None) -> None:
        """Add documents to vector store.
        
        Args:
            documents: Dict with 'ids', 'documents', 'embeddings', 'metadatas'
            metadata: Optional metadata to add
        """
        try:
            if not self.collection:
                logger.warning("Collection not initialized")
                return

            self.collection.add(**documents)
            logger.info("Added %s documents to ChromaDB", len(documents.get("ids", [])))
        except Exception as e:
            logger.error("Failed to add documents: %s", e)

    def search_similar(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents using semantic similarity.
        
        Args:
            query_text: Query text to search for
            n_results: Number of results to return
            
        Returns:
            List of similar documents with similarity scores
        """
        try:
            if not self.collection:
                logger.warning("Collection not initialized")
                return []

            # Embed query
            query_embedding = embed_query(query_text)
            
            # Search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted = []
            if results and results["ids"] and len(results["ids"]) > 0:
                for i, doc_id in enumerate(results["ids"][0]):
                    formatted.append({
                        "id": doc_id,
                        "document": results["documents"][0][i] if results["documents"] else "",
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results["distances"] else 0,
                        "similarity": 1 - (results["distances"][0][i] if results["distances"] else 0)
                    })
            
            return formatted
        except Exception as e:
            logger.error("Search failed: %s", e)
            return []

    def check_duplicate(self, text: str, threshold: float = 0.85) -> bool:
        """Check if similar document already exists (for deduplication).
        
        Args:
            text: Text to check
            threshold: Similarity threshold (0-1)
            
        Returns:
            True if similar document exists, False otherwise
        """
        try:
            results = self.search_similar(text, n_results=1)
            if results and results[0]["similarity"] >= threshold:
                logger.debug("Found duplicate with similarity %.2f", results[0]["similarity"])
                return True
            return False
        except Exception as e:
            logger.error("Duplicate check failed: %s", e)
            return False

    def upsert_vectors(self, documents: Dict[str, Any]) -> None:
        """Upsert documents (add or update)."""
        try:
            if not self.collection:
                logger.warning("Collection not initialized")
                return
            self.collection.upsert(**documents)
            logger.info("Upserted %s documents", len(documents.get("ids", [])))
        except Exception as e:
            logger.error("Upsert failed: %s", e)

    def delete_collection(self) -> None:
        """Delete collection (for cleanup)."""
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.info("Deleted collection '%s'", self.collection_name)
            self._init_collection()
        except Exception as e:
            logger.error("Failed to delete collection: %s", e)


# Global vectorstore instance
_vectorstore = None


def get_vectorstore() -> VectorStore:
    """Get or create global vectorstore instance."""
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = VectorStore()
    return _vectorstore


def upsert_vectors(documents: Iterable[str]) -> None:
    """Legacy wrapper for upsert_vectors - for backward compatibility."""
    try:
        vectorstore = get_vectorstore()
        docs_list = list(documents)
        
        if not docs_list:
            return
        
        # Embed all documents
        embeddings = embed_texts(docs_list)
        
        # Prepare documents for upsert
        docs_dict = {
            "ids": [f"doc_{i}" for i in range(len(docs_list))],
            "documents": docs_list,
            "embeddings": embeddings,
            "metadatas": [{"index": i} for i in range(len(docs_list))]
        }
        
        vectorstore.upsert_vectors(docs_dict)
    except Exception as e:
        logger.error("Failed to upsert vectors: %s", e)
