from __future__ import annotations

from app.database.postgres import save_newsletter_run
from app.graph.state import NewsState


def store_results_node(state: NewsState) -> NewsState:
    save_newsletter_run(state)
    return state
