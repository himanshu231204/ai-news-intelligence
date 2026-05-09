from __future__ import annotations

from typing import List
from uuid import uuid4

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from app.config.settings import get_settings
from app.graph.builder import build_graph
from app.graph.state import NewsItem, NewsState
from app.observability.langsmith import configure_langsmith
from app.utils.logger import get_logger

logger = get_logger(__name__)

COMMANDS = ["/daily", "/trending", "/opensource", "/research"]


def register_bot_handlers(application: Application) -> None:
    """Register all Telegram command handlers on the application."""
    application.add_handler(CommandHandler("start", start_cmd))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("sources", sources_cmd))
    application.add_handler(CommandHandler("developerinfo", developerinfo_cmd))
    application.add_handler(CommandHandler("daily", daily_cmd))
    application.add_handler(CommandHandler("trending", trending_cmd))
    application.add_handler(CommandHandler("opensource", opensource_cmd))
    application.add_handler(CommandHandler("research", research_cmd))


def _split_message(message: str, max_len: int = 3800) -> List[str]:
    if len(message) <= max_len:
        return [message]
    parts: List[str] = []
    start = 0
    while start < len(message):
        end = min(start + max_len, len(message))
        parts.append(message[start:end])
        start = end
    return parts


def _to_item_line(item: NewsItem, summary: str) -> str:
    title = item.title or "Untitled"
    url = item.url or ""
    source = item.source or "unknown"
    score = item.score or 0.0
    first_summary_line = (
        summary.splitlines()[1] if len(summary.splitlines()) > 1 else "Summary: n/a"
    )
    return (
        f"- {title}\n"
        f"  Source: {source} | Score: {score}\n"
        f"  {first_summary_line}\n"
        f"  Link: {url}"
    )


def _keywords_match(item: NewsItem, keywords: List[str]) -> bool:
    text = " ".join(
        [
            str(item.title or ""),
            str(item.url or ""),
            str(item.source or ""),
        ]
    ).lower()
    return any(keyword in text for keyword in keywords)


def _build_section(title: str, items: List[NewsItem], summaries: List[str]) -> str:
    if not items:
        return f"{title}\nNo matching stories found in the latest run."

    lines = [title]
    for idx, item in enumerate(items, start=1):
        summary = (
            summaries[idx - 1] if idx - 1 < len(summaries) else "Summary: unavailable"
        )
        lines.append(f"{idx}. {_to_item_line(item, summary)}")
    return "\n\n".join(lines)


async def _run_workflow_state() -> dict:
    settings = get_settings()
    configure_langsmith(settings)
    app = build_graph()
    initial_state = {
        "raw_news": [],
        "merged_news": [],
        "unique_news": [],
        "filtered_news": [],
        "ranked_news": [],
        "summaries": [],
        "newsletter": "",
        "linkedin_newsletter": "",
        "google_doc_link": "",
        "linkedin_saved": False,
        "errors": [],
        "metadata": {},
    }
    result = await app.ainvoke(
        initial_state, config={"configurable": {"thread_id": str(uuid4())}}
    )
    return result


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _ = context
    text = (
        "Welcome to AI News Agent.\n\n"
        "📰 News Generation:\n"
        "/daily - Today's AI newsletter\n\n"
        "📂 Content Filters:\n"
        "/trending - Trending discussions\n"
        "/opensource - Open source launches\n"
        "/research - Research highlights\n\n"
        "ℹ️ Info:\n"
        "/sources - List news sources\n"
        "/help - Show all commands"
    )
    await update.effective_message.reply_text(text)


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _ = context
    text = (
        "🤖 *AI News Agent - Commands*\n\n"
        "📰 *News Generation*\n"
        "/daily - Today's AI newsletter\n\n"
        "📂 *Content Filters*\n"
        "/trending - Trending discussions\n"
        "/opensource - Open source launches\n"
        "/research - Research highlights\n\n"
        "ℹ️ *Info*\n"
        "/sources - List news sources\n"
        "/developerinfo - Developer info & links\n"
        "/help - Show this help message\n\n"
        "_Use /daily to get your daily AI news brief!_"
    )
    await update.effective_message.reply_text(text, parse_mode="Markdown")


async def sources_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _ = context
    text = (
        "📡 *Configured News Sources*\n\n"
        "🔹 *RSS Feeds*\n"
        "• TechCrunch\n"
        "• Hacker News\n"
        "• OpenAI Blog\n"
        "• Anthropic Blog\n"
        "• Google AI Blog\n\n"
        "🔹 *GitHub*\n"
        "• Trending Repositories (AI/ML)\n\n"
        "🔹 *Hacker News*\n"
        "• Top AI-related stories\n\n"
        "🔹 *Reddit*\n"
        "• r/MachineLearning\n"
        "• r/ArtificialIntelligence\n\n"
        "_Sources are configured in the system. Contact admin to modify._"
    )
    await update.effective_message.reply_text(text, parse_mode="Markdown")


async def developerinfo_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _ = context
    text = (
        "👨‍💻 *Developer Info*\n\n"
        "Built with ❤️ by Himanshu\n\n"
        "🔗 *Connect*\n"
        "• [LinkedIn](https://linkedin.com/in/himanshu231204)\n"
        "• [GitHub](https://github.com/himanshu231204)\n\n"
        "🛠 *Tech Stack*\n"
        "• LangGraph + LangChain\n"
        "• Groq + Gemini LLMs\n"
        "• FastAPI + PostgreSQL\n"
        "• Telegram Bot API\n\n"
        "_Thanks for using AI News Agent!_"
    )
    await update.effective_message.reply_text(text, parse_mode="Markdown")


async def daily_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _ = context
    # Send progress messages
    msg = await update.effective_message.reply_text(
        "🧠 Collecting AI news from sources..."
    )
    try:
        result = await _run_workflow_state()
    except Exception as exc:  # noqa: BLE001
        logger.exception("Daily workflow failed: %s", exc)
        await update.effective_message.reply_text(
            "Daily generation failed. Check logs and try again."
        )
        return

    # Update to processing message
    await msg.edit_text("✍️ Generating newsletter...")

    newsletter = result.get("newsletter", "") or "No newsletter generated."

    # Delete the processing message
    await msg.delete()

    for part in _split_message(newsletter):
        await update.effective_message.reply_text(part)


async def trending_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _ = context
    # Send progress message
    msg = await update.effective_message.reply_text("🔍 Collecting trending AI news...")
    try:
        result = await _run_workflow_state()
    except Exception as exc:  # noqa: BLE001
        logger.exception("Trending workflow failed: %s", exc)
        await update.effective_message.reply_text(
            "Trending digest failed. Check logs and try again."
        )
        return

    # Update to processing message
    await msg.edit_text("📊 Building trending digest...")

    ranked = result.get("ranked_news", [])[:5]
    summaries = result.get("summaries", [])[:5]
    message = _build_section("Trending Discussions", ranked, summaries)

    # Delete processing message
    await msg.delete()

    for part in _split_message(message):
        await update.effective_message.reply_text(part)


async def opensource_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _ = context
    # Send progress message
    msg = await update.effective_message.reply_text(
        "🛠️ Collecting open-source projects..."
    )
    try:
        result = await _run_workflow_state()
    except Exception as exc:  # noqa: BLE001
        logger.exception("Open-source workflow failed: %s", exc)
        await update.effective_message.reply_text(
            "Open-source digest failed. Check logs and try again."
        )
        return

    # Update to processing message
    await msg.edit_text("📦 Building open-source watchlist...")

    keywords = ["open-source", "opensource", "github", "repo", "oss", "release"]
    ranked = result.get("ranked_news", [])
    matched = [item for item in ranked if _keywords_match(item, keywords)][:5]
    summaries = result.get("summaries", [])[: len(matched)]
    message = _build_section("Open Source Launches", matched, summaries)

    # Delete processing message
    await msg.delete()

    for part in _split_message(message):
        await update.effective_message.reply_text(part)


async def research_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _ = context
    # Send progress message
    msg = await update.effective_message.reply_text("📚 Collecting research papers...")
    try:
        result = await _run_workflow_state()
    except Exception as exc:  # noqa: BLE001
        logger.exception("Research workflow failed: %s", exc)
        await update.effective_message.reply_text(
            "Research digest failed. Check logs and try again."
        )
        return

    # Update to processing message
    await msg.edit_text("🔬 Building research highlights...")

    keywords = ["research", "paper", "arxiv", "benchmark", "study", "preprint"]
    ranked = result.get("ranked_news", [])
    matched = [item for item in ranked if _keywords_match(item, keywords)][:5]
    summaries = result.get("summaries", [])[: len(matched)]
    message = _build_section("Research Highlights", matched, summaries)

    # Delete processing message
    await msg.delete()

    for part in _split_message(message):
        await update.effective_message.reply_text(part)


def run_telegram_bot() -> None:
    settings = get_settings()
    if not settings.telegram_bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN is required to run bot mode.")

    application = Application.builder().token(settings.telegram_bot_token).build()
    register_bot_handlers(application)
    logger.info("Starting Telegram bot polling mode.")
    application.run_polling(drop_pending_updates=True)
