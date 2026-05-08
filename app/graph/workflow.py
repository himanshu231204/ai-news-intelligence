from __future__ import annotations

from langgraph.graph import END, StateGraph

from app.graph.state import NewsState
from app.graph.nodes.collect_news import collect_news_node
from app.graph.nodes.merge_results import merge_results_node
from app.graph.nodes.deduplicate_news import deduplicate_news_node
from app.graph.nodes.filter_low_quality import filter_low_quality_node
from app.graph.nodes.rank_news import rank_news_node
from app.graph.nodes.summarize_news import summarize_news_node
from app.graph.nodes.generate_newsletter import generate_newsletter_node
from app.graph.nodes.store_results import store_results_node
from app.graph.nodes.send_telegram import send_telegram_node


def build_workflow() -> StateGraph:
    """Create and wire the LangGraph workflow."""
    graph = StateGraph(NewsState)

    graph.add_node("collect_news", collect_news_node)
    graph.add_node("merge_results", merge_results_node)
    graph.add_node("deduplicate_news", deduplicate_news_node)
    graph.add_node("filter_low_quality", filter_low_quality_node)
    graph.add_node("rank_news", rank_news_node)
    graph.add_node("summarize_news", summarize_news_node)
    graph.add_node("generate_newsletter", generate_newsletter_node)
    graph.add_node("store_results", store_results_node)
    graph.add_node("send_telegram", send_telegram_node)

    graph.set_entry_point("collect_news")
    graph.add_edge("collect_news", "merge_results")
    graph.add_edge("merge_results", "deduplicate_news")
    graph.add_edge("deduplicate_news", "filter_low_quality")
    graph.add_edge("filter_low_quality", "rank_news")
    graph.add_edge("rank_news", "summarize_news")
    graph.add_edge("summarize_news", "generate_newsletter")
    graph.add_edge("generate_newsletter", "store_results")
    graph.add_edge("store_results", "send_telegram")
    graph.add_edge("send_telegram", END)

    return graph
