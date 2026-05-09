from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # LLM Configuration
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    openrouter_api_key: str = ""
    openrouter_model: str = "liquid/lfm-2.5-1.2b-thinking:free"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # LangChain/LangSmith
    langchain_api_key: str = ""
    langchain_tracing_v2: bool = True

    # Telegram
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # Database
    postgres_url: str = ""
    sqlite_db_path: str = "newsletter.db"

    # Vector Store
    chroma_path: str = "./chroma_data"

    # Reddit API credentials (optional)
    reddit_client_id: str = ""
    reddit_client_secret: str = ""

    # Twitter API credentials (optional)
    twitter_bearer_token: str = ""

    # Scheduler configuration
    newsletter_hour: int = 9
    newsletter_minute: int = 0

    # Newsletter settings
    min_news_items: int = 5
    max_news_items: int = 20
    similarity_threshold: float = 0.85

    # Logging
    log_level: str = "INFO"

    # Feature flags
    use_embeddings: bool = True
    use_postgres_checkpoint: bool = False

    # Google Drive Integration
    google_service_account_json: str = ""
    google_drive_folder_id: str = ""
    enable_google_drive: bool = False

    # AgentRouter Configuration
    agentrouter_api_key: str = ""
    agentrouter_model: str = "usf-mini"

    # Run mode detection
    is_scheduled_run: bool = False

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
