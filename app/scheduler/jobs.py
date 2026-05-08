from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Callable

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.utils.logger import get_logger

logger = get_logger(__name__)

_scheduler: BackgroundScheduler | None = None


def _run_async_in_thread(coro):
    """Helper to run async function in thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def schedule_daily_job(job_func: Callable, hour: int = 9, minute: int = 0) -> None:
    """Schedule a job to run daily at specified time.
    
    Args:
        job_func: Async function to run
        hour: Hour in 24-hour format (0-23)
        minute: Minute (0-59)
    """
    global _scheduler
    
    if _scheduler is None:
        _scheduler = BackgroundScheduler()
    
    try:
        # Create wrapper for async function
        def wrapper():
            logger.info("Running daily job at %s", datetime.now())
            try:
                _run_async_in_thread(job_func())
            except Exception as e:
                logger.error("Daily job failed: %s", e)
        
        # Schedule using cron trigger
        trigger = CronTrigger(hour=hour, minute=minute)
        _scheduler.add_job(
            wrapper,
            trigger=trigger,
            id="daily_newsletter",
            replace_existing=True
        )
        
        logger.info("Scheduled daily job for %02d:%02d", hour, minute)
        
        if not _scheduler.running:
            _scheduler.start()
            logger.info("Scheduler started")
    
    except Exception as e:
        logger.error("Failed to schedule job: %s", e)


def stop_scheduler() -> None:
    """Stop the scheduler."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown()
        _scheduler = None
        logger.info("Scheduler stopped")


def get_scheduler() -> BackgroundScheduler | None:
    """Get the scheduler instance."""
    return _scheduler


def run_daily_job() -> None:
    """Legacy placeholder - kept for compatibility."""
    logger.info("Daily scheduler trigger - use schedule_daily_job() instead.")
