from __future__ import annotations

import os

from app.config.settings import Settings


def configure_langsmith(settings: Settings) -> None:
    if settings.langchain_api_key:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ.setdefault("LANGCHAIN_API_KEY", settings.langchain_api_key)
    else:
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
