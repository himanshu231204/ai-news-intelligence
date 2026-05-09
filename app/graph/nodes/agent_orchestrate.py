"""AgentRouter orchestration node for LangGraph workflow.

This node integrates AgentRouter multi-agent orchestration with the
existing LangGraph workflow. It handles the ENTIRE pipeline as primary:
- Collection coordination (receives from collect_news)
- Merging results
- Deduplication
- Filtering
- Ranking
- Summarization
- Newsletter generation
"""

from __future__ import annotations

from typing import Dict, Any, List

from app.graph.state import NewsState, NewsItem
from app.agents.orchestrator import get_orchestrator, initialize_orchestrator
from app.utils.logger import get_logger

logger = get_logger(__name__)


def is_agentrouter_available() -> bool:
    """Check if AgentRouter is configured and available."""
    from app.config.settings import get_settings

    settings = get_settings()
    return bool(settings.agentrouter_api_key)


async def agent_full_workflow_node(state: NewsState) -> Dict[str, Any]:
    """AgentRouter node for the entire workflow (primary path).

    This node uses AgentRouter as the PRIMARY path for the entire pipeline:
    1. Receives raw news from collect_news
    2. Merges, deduplicates, filters, ranks
    3. Summarizes articles
    4. Generates newsletter

    Falls back to LLM-based nodes if AgentRouter is not available.

    Args:
        state: Current workflow state with raw_news

    Returns:
        Updated state with all processed data (merged, unique, filtered, ranked, summaries, newsletter)
    """
    logger.info("Running AgentRouter full workflow node (PRIMARY)")

    # Check if AgentRouter is available
    if not is_agentrouter_available():
        logger.info("AgentRouter not configured. Using LLM fallback workflow.")
        return {"metadata": {"workflow_method": "llm_fallback"}}

    # Initialize orchestrator
    orchestrator = get_orchestrator()
    await orchestrator.initialize()

    if not orchestrator._initialized:
        logger.warning("AgentRouter initialization failed. Using LLM fallback.")
        return {"metadata": {"workflow_method": "llm_fallback"}}

    try:
        # Convert raw news items to dicts for agent processing
        news_items = []
        for item in state.raw_news:
            news_items.append(
                {
                    "title": item.title,
                    "source": item.source,
                    "url": item.url,
                    "published_at": str(item.published_at) if item.published_at else "",
                    "score": item.score,
                    "company": item.company,
                    "category": item.category,
                }
            )

        if not news_items:
            logger.warning("No raw news items to process")
            return {
                "errors": state.errors + ["No raw news items for AgentRouter"],
                "metadata": {"workflow_method": "error"},
            }

        logger.info(
            f"Processing {len(news_items)} items with AgentRouter full workflow"
        )

        # Run agent workflow - this handles the entire pipeline
        result = await orchestrator.run_workflow(news_items)

        # Extract results from AgentRouter
        ranked_items = result.get("ranked_items", [])
        summaries = result.get("summaries", [])
        newsletter = result.get("newsletter", "")

        logger.info(
            f"AgentRouter completed: ranked_items={len(ranked_items)}, "
            f"summaries={len(summaries)}, newsletter_length={len(newsletter)}"
        )

        # Convert ranked items back to NewsItem objects
        processed_items = []
        for item_data in ranked_items:
            processed_items.append(
                NewsItem(
                    title=item_data.get("title", "Untitled"),
                    source=item_data.get("source", "unknown"),
                    url=item_data.get("url", ""),
                    score=item_data.get("score", 0.0),
                    company=item_data.get("company"),
                    category=item_data.get("category"),
                )
            )

        # If AgentRouter produced results, use them
        if processed_items or summaries or newsletter:
            return {
                "merged_news": processed_items,
                "unique_news": processed_items,
                "filtered_news": processed_items,
                "ranked_news": processed_items,
                "summaries": summaries,
                "newsletter": newsletter,
                "metadata": {
                    "workflow_method": "agentrouter",
                    "agent_used": True,
                },
            }
        else:
            # AgentRouter didn't produce expected output
            logger.warning("AgentRouter didn't produce expected output")
            return {"metadata": {"workflow_method": "llm_fallback"}}

    except Exception as e:
        logger.error(f"AgentRouter full workflow failed: {e}. Using LLM fallback.")
        return {
            "errors": state.errors + [f"AgentRouter error: {str(e)}"],
            "metadata": {"workflow_method": "llm_fallback"},
        }


async def agent_summarize_and_generate_node(state: NewsState) -> Dict[str, Any]:
    """AgentRouter node for summarization and newsletter generation only.

    This is used when AgentRouter is only used for summarization/generation
    (not the full pipeline). Kept for potential partial usage.

    Args:
        state: Current workflow state with ranked_news

    Returns:
        Updated state with summaries and newsletter
    """
    logger.info("Running AgentRouter summarization node (partial)")

    if not is_agentrouter_available():
        return {"metadata": {"summarization_method": "llm_fallback"}}

    orchestrator = get_orchestrator()
    await orchestrator.initialize()

    if not orchestrator._initialized:
        return {"metadata": {"summarization_method": "llm_fallback"}}

    try:
        news_items = []
        for item in state.ranked_news:
            news_items.append(
                {
                    "title": item.title,
                    "source": item.source,
                    "url": item.url,
                    "score": item.score,
                    "company": item.company,
                    "category": item.category,
                }
            )

        if not news_items:
            return {"errors": state.errors + ["No ranked news items"]}

        result = await orchestrator.run_workflow(news_items)

        summaries = result.get("summaries", [])
        newsletter = result.get("newsletter", "")

        if newsletter:
            return {
                "summaries": summaries,
                "newsletter": newsletter,
                "metadata": {
                    "summarization_method": "agentrouter",
                    "agent_used": True,
                },
            }

        return {"metadata": {"summarization_method": "llm_fallback"}}

    except Exception as e:
        logger.error(f"AgentRouter summarization failed: {e}")
        return {"metadata": {"summarization_method": "llm_fallback"}}
