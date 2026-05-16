from __future__ import annotations

from langgraph.graph import END, StateGraph

from app.graph.state import NewsState
from app.graph.nodes.collect_news import collect_news_node
from app.graph.nodes.merge_results import merge_results_node
from app.graph.nodes.keyword_filter import keyword_filter_node
from app.graph.nodes.deduplicate_news import deduplicate_news_node
from app.graph.nodes.filter_low_quality import filter_low_quality_node
from app.graph.nodes.rank_news import rank_news_node
from app.graph.nodes.summarize_news import summarize_news_node
from app.graph.nodes.generate_newsletter import generate_newsletter_node
from app.graph.nodes.generate_linkedin import generate_linkedin_node
from app.graph.nodes.save_linkedin import save_linkedin_node
from app.graph.nodes.store_results import store_results_node
from app.graph.nodes.send_telegram import send_telegram_node
from app.graph.nodes.agent_orchestrate import (
    agent_full_workflow_node,
    is_agentrouter_available,
)
from app.config.settings import get_settings


def _should_generate_linkedin(state: NewsState) -> str:
    """Determine if LinkedIn newsletter should be generated.

    Only generates LinkedIn newsletter for scheduled runs.
    """
    settings = get_settings()
    if settings.is_scheduled_run:
        return "generate_linkedin"
    return "skip_linkedin"


def _should_use_agentrouter(state: NewsState) -> str:
    """Determine if AgentRouter should be used.

    Uses AgentRouter if API key is configured.
    """
    if is_agentrouter_available():
        return "agent_workflow"
    return "llm_workflow"


def _agentrouter_succeeded(state: NewsState) -> str:
    """Check if AgentRouter produced valid output.

    Returns 'llm_fallback' if AgentRouter failed or didn't produce output.
    """
    metadata = state.metadata or {}
    workflow_method = metadata.get("workflow_method", "")

    # If AgentRouter succeeded and produced newsletter, route based on schedule mode.
    if workflow_method == "agentrouter" and state.newsletter:
        settings = get_settings()
        if settings.is_scheduled_run:
            return "continue_with_linkedin"
        return "continue_without_linkedin"

    # Otherwise, use LLM fallback
    return "llm_fallback"


def build_workflow() -> StateGraph:
    """Create and wire the LangGraph workflow.

    OPTIMIZED PIPELINE:
    1. collect_news - Collect from all sources
    2. merge_results - Merge all collected news
    3. keyword_filter - Filter by keywords (BEFORE LLM - reduces API calls)
    4. deduplicate_news - Remove duplicates
    5. filter_low_quality - Quality filtering
    6. rank_news - Rank by importance
    7. summarize_news - Batch summarization (reduces API calls)
    8. generate_newsletter - Generate Telegram newsletter
    9. generate_linkedin - Generate LinkedIn newsletter
    10. save_linkedin - Save to Google Drive
    11. store_results - Store in database
    12. send_telegram - Send to Telegram
    """
    graph = StateGraph(NewsState)

    # Add all nodes
    # LLM-based nodes (fallback path)
    graph.add_node("collect_news", collect_news_node)
    graph.add_node("merge_results", merge_results_node)
    graph.add_node("keyword_filter", keyword_filter_node)  # NEW: Keyword filtering
    graph.add_node("deduplicate_news", deduplicate_news_node)
    graph.add_node("filter_low_quality", filter_low_quality_node)
    graph.add_node("rank_news", rank_news_node)
    graph.add_node("summarize_news", summarize_news_node)
    graph.add_node("generate_newsletter", generate_newsletter_node)
    # AgentRouter node (primary)
    graph.add_node("agent_workflow", agent_full_workflow_node)
    # LinkedIn nodes
    graph.add_node("generate_linkedin", generate_linkedin_node)
    graph.add_node("save_linkedin", save_linkedin_node)
    graph.add_node("store_results", store_results_node)
    graph.add_node("send_telegram", send_telegram_node)

    # Set entry point
    graph.set_entry_point("collect_news")

    # ==========================================================================
    # CONDITIONAL ROUTING: AgentRouter (primary) vs LLM (fallback)
    # ==========================================================================

    graph.add_conditional_edges(
        "collect_news",
        _should_use_agentrouter,
        {
            "agent_workflow": "agent_workflow",  # AgentRouter path
            "llm_workflow": "merge_results",  # LLM path
        },
    )

    # ==========================================================================
    # AGENTROUTER PATH
    # ==========================================================================
    # After agent_workflow, check if it produced valid output
    # If not, fall back to LLM path
    graph.add_conditional_edges(
        "agent_workflow",
        _agentrouter_succeeded,
        {
            "continue_with_linkedin": "generate_linkedin",  # scheduled run
            "continue_without_linkedin": "store_results",  # non-scheduled run
            "llm_fallback": "merge_results",  # AgentRouter failed, use LLM
        },
    )

    # ==========================================================================
    # LLM PATH (FALLBACK) - OPTIMIZED
    # ==========================================================================
    # NEW: Added keyword_filter BEFORE deduplication
    # This removes non-AI content BEFORE expensive LLM processing
    graph.add_edge("merge_results", "keyword_filter")
    graph.add_edge("keyword_filter", "deduplicate_news")
    graph.add_edge("deduplicate_news", "filter_low_quality")
    graph.add_edge("filter_low_quality", "rank_news")
    graph.add_edge("rank_news", "summarize_news")
    graph.add_edge("summarize_news", "generate_newsletter")

    # ==========================================================================
    # LINKEDIN GENERATION (common for both paths)
    # ==========================================================================
    graph.add_conditional_edges(
        "generate_newsletter",
        _should_generate_linkedin,
        {
            "generate_linkedin": "generate_linkedin",
            "skip_linkedin": "store_results",
        },
    )

    # LinkedIn workflow (only runs in scheduled mode)
    graph.add_edge("generate_linkedin", "save_linkedin")
    graph.add_edge("save_linkedin", "store_results")

    # Final edges
    graph.add_edge("store_results", "send_telegram")
    graph.add_edge("send_telegram", END)

    return graph
