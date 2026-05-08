from __future__ import annotations

from app.graph.state import NewsState
from app.summarization.summarizer import summarize_batch


async def summarize_news_node(state: NewsState) -> NewsState:
    summaries = await summarize_batch(state["ranked_news"])
    new_state = dict(state)
    new_state["summaries"] = summaries
    return new_state
