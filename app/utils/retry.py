"""Retry and exponential backoff helper."""

import functools
import time
from typing import Any, Callable, TypeVar
from app.logging_config import logger

T = TypeVar("T")


def retry_with_backoff(
    retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 30.0,
    exceptions: tuple = (Exception,),
) -> Callable:
    """Decorator to retry a function with exponential backoff and jitter."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            delay = initial_delay
            last_exception = None

            for attempt in range(1, retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == retries:
                        logger.error(
                            f"Operation '{func.__name__}' failed on final attempt {attempt}/{retries}: {e}"
                        )
                        raise
                    logger.warning(
                        f"Operation '{func.__name__}' attempt {attempt}/{retries} failed: {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )
                    time.sleep(delay)
                    delay = min(delay * backoff_factor, max_delay)

            if last_exception:
                raise last_exception
            raise RuntimeError(f"Unexpected retry failure for {func.__name__}")

        return wrapper

    return decorator
