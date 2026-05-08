from __future__ import annotations

from typing import List

from app.graph.state import NewsItem
from app.memory.vectorstore import get_vectorstore
from app.utils.logger import get_logger

logger = get_logger(__name__)


def deduplicate_news(items: List[NewsItem]) -> List[NewsItem]:
    """Deduplicate news using semantic similarity with ChromaDB.
    
    Falls back to URL/title matching if semantic deduplication fails.
    """
    if not items:
        return []
    
    vectorstore = get_vectorstore()
    unique: List[NewsItem] = []
    seen_urls = set()
    
    for item in items:
        # Check URL/title first (fast path)
        url = item.get("url")
        title = item.get("title", "")
        
        if url and url in seen_urls:
            logger.debug("Skipped duplicate URL: %s", url)
            continue
        
        if url:
            seen_urls.add(url)
        
        # Semantic similarity check using embeddings
        try:
            # Use title + summary for semantic search
            search_text = f"{title} {item.get('summary', '')}"
            
            # Check if similar document already exists
            if vectorstore.check_duplicate(search_text, threshold=0.85):
                logger.debug("Skipped semantic duplicate: %s", title[:50])
                continue
            
        except Exception as e:
            logger.warning("Semantic deduplication failed for '%s': %s", title[:50], e)
            # Continue with URL-based deduplication if semantic check fails
        
        unique.append(item)
    
    logger.info("Deduplicated %d items -> %d unique", len(items), len(unique))
    return unique
