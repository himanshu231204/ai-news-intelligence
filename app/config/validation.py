from __future__ import annotations

from app.config.settings import Settings, get_settings


def validate_settings(settings: Settings | None = None) -> None:
    """Validate that the required configuration secrets are present.

    Raises:
        RuntimeError: If any required secret is missing.
    """
    if settings is None:
        settings = get_settings()

    missing = []
    if not settings.groq_api_key:
        missing.append("GROQ_API_KEY")
    if not settings.telegram_bot_token:
        missing.append("TELEGRAM_BOT_TOKEN")
    if not settings.telegram_chat_id:
        missing.append("TELEGRAM_CHAT_ID")
    if settings.use_postgres_checkpoint and not settings.postgres_url:
        missing.append("POSTGRES_URL (required only when Postgres checkpoints are enabled)")

    if missing:
        raise RuntimeError(
            f"Missing required configuration values: {', '.join(missing)}. "
            "Set them in the .env file or environment before running."
        )
