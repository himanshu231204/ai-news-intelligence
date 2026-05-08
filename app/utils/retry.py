from __future__ import annotations

import asyncio
import functools
from typing import Callable, TypeVar, Any

from app.utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


def async_retry(max_retries: int = 3, backoff_factor: float = 2.0, initial_delay: float = 1.0):
    """Decorator for retrying async functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Exponential backoff multiplier (e.g., 2.0 = double delay each retry)
        initial_delay: Initial delay in seconds before first retry
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            "Attempt %d/%d failed for %s: %s. Retrying in %.1fs...",
                            attempt + 1,
                            max_retries + 1,
                            func.__name__,
                            e,
                            delay
                        )
                        await asyncio.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(
                            "All %d attempts failed for %s: %s",
                            max_retries + 1,
                            func.__name__,
                            e
                        )
            
            raise last_exception
        
        return wrapper
    return decorator


def sync_retry(max_retries: int = 3, backoff_factor: float = 2.0, initial_delay: float = 1.0):
    """Decorator for retrying sync functions with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            import time
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            "Attempt %d/%d failed for %s: %s. Retrying in %.1fs...",
                            attempt + 1,
                            max_retries + 1,
                            func.__name__,
                            e,
                            delay
                        )
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(
                            "All %d attempts failed for %s: %s",
                            max_retries + 1,
                            func.__name__,
                            e
                        )
            
            raise last_exception
        
        return wrapper
    return decorator
