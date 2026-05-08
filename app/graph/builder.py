from __future__ import annotations

from app.graph.workflow import build_workflow
from app.memory.checkpoint import get_checkpointer


def build_graph():
    """Compile workflow with checkpoint support."""
    workflow = build_workflow()
    checkpointer = get_checkpointer()
    return workflow.compile(checkpointer=checkpointer)
