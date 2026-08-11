# backend/utils/retry.py
import asyncio
from typing import Awaitable, Callable, TypeVar

from core.constants import (
    MAX_RETRIES,
    BACKOFF_BASE_SECONDS,
    RETRYABLE_STATUS_CODES,
)
from utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class RetryExhaustedError(Exception):
    """Raised when all retry attempts fail."""

    def __init__(self, message: str, last_status_code: int | None = None):
        self.message = message
        self.last_status_code = last_status_code
        super().__init__(message)


async def call_with_retry(
    func: Callable[[], Awaitable],
    get_status_code: Callable[[object], int],
    max_retries: int = MAX_RETRIES,
) -> object:
    """
    Generic retry wrapper. `func` is a zero-arg async callable that
    returns a response-like object. `get_status_code` extracts the
    HTTP status code from that response so this stays transport-agnostic.

    Retries only on RETRYABLE_STATUS_CODES (408, 429, 500, 502, 503, 504).
    Uses exponential backoff: BACKOFF_BASE_SECONDS ** attempt.
    """
    last_response = None

    for attempt in range(max_retries + 1):
        response = await func()
        status_code = get_status_code(response)

        if status_code not in RETRYABLE_STATUS_CODES:
            return response

        last_response = response

        if attempt < max_retries:
            wait_time = BACKOFF_BASE_SECONDS ** attempt
            logger.info(
                f"Retryable status {status_code} received. "
                f"Attempt {attempt + 1}/{max_retries}. "
                f"Retrying in {wait_time:.1f}s..."
            )
            await asyncio.sleep(wait_time)

    logger.error(f"Retry attempts exhausted after {max_retries} retries.")
    raise RetryExhaustedError(
        "Max retries exceeded while calling downstream service.",
        last_status_code=get_status_code(last_response) if last_response else None,
    )