from __future__ import annotations

import argparse
import asyncio
import signal
import sys
from uuid import uuid4

from app.graph.builder import build_graph
from app.config.settings import get_settings
from app.observability.langsmith import configure_langsmith
from app.telegram.handlers import run_telegram_bot
from app.telegram.bot import send_newsletter
from app.scheduler.jobs import schedule_daily_job, stop_scheduler
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def run_newsletter() -> None:
    """Run the daily AI news workflow."""
    settings = get_settings()
    from app.config.validation import validate_settings
    validate_settings(settings)
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
        "errors": [],
        "metadata": {},
    }
    
    logger.info("Starting newsletter workflow...")
    try:
        result = await app.ainvoke(
            initial_state,
            config={"configurable": {"thread_id": str(uuid4())}},
        )
        newsletter = result.get("newsletter", "")
        errors = result.get("errors", [])
        
        if errors:
            logger.warning("Workflow completed with %d errors: %s", len(errors), errors)
        else:
            logger.info("Workflow completed successfully")
        
        logger.info("Newsletter generated. Length=%s", len(newsletter))
        
        # Send to Telegram if configured
        if settings.telegram_bot_token and settings.telegram_chat_id:
            send_newsletter(newsletter)
        
        return result
    
    except Exception as e:
        logger.error("Newsletter workflow failed: %s", e, exc_info=True)
        raise


def run_workflow_once() -> None:
    """Run workflow once and exit."""
    try:
        asyncio.run(run_newsletter())
    except Exception as e:
        logger.error("Workflow failed: %s", e)
        sys.exit(1)


def run_scheduled() -> None:
    """Run workflow on schedule (24-hour cycle)."""
    settings = get_settings()
    
    # Schedule daily job at specified time (default 9:00 AM)
    schedule_daily_job(
        run_newsletter,
        hour=settings.newsletter_hour if hasattr(settings, "newsletter_hour") else 9,
        minute=settings.newsletter_minute if hasattr(settings, "newsletter_minute") else 0
    )
    
    logger.info("Scheduler running. Press Ctrl+C to exit.")
    
    # Handle graceful shutdown
    def signal_handler(sig, frame):
        logger.info("Received interrupt signal. Shutting down...")
        stop_scheduler()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Keep the scheduler running
    try:
        while True:
            asyncio.run(asyncio.sleep(1))
    except KeyboardInterrupt:
        stop_scheduler()


def run_telegram_bot_mode() -> None:
    """Run Telegram bot in polling mode."""
    logger.info("Starting Telegram bot...")
    try:
        run_telegram_bot()
    except KeyboardInterrupt:
        logger.info("Telegram bot stopped")
    except Exception as e:
        logger.error("Telegram bot failed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI News Agent runner")
    parser.add_argument(
        "--mode",
        choices=["workflow", "bot", "scheduler"],
        default="workflow",
        help="workflow: run one newsletter cycle, bot: start Telegram command bot, scheduler: run on 24-hour cycle",
    )
    args = parser.parse_args()

    if args.mode == "bot":
        run_telegram_bot_mode()
    elif args.mode == "scheduler":
        run_scheduled()
    else:
        run_workflow_once()
