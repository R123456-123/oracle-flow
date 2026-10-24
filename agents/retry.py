from __future__ import annotations

import asyncio
import functools
import logging
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def _is_transient_error(exception: Exception) -> bool:
	message = str(exception).lower()
	status_code = getattr(exception, "status_code", None) or getattr(exception, "code", None)

	if status_code in {429, 500, 502, 503, 504}:
		return True

	transient_signals = (
		"rate limit",
		"too many requests",
		"timeout",
		"timed out",
		"service unavailable",
		"temporary",
		"connection reset",
		"connection aborted",
		"network error",
	)
	return any(signal in message for signal in transient_signals)


def retry_with_backoff(
	max_retries: int = 3,
	initial_backoff: float = 1.0,
	max_backoff: float = 8.0,
	exponential_base: float = 2.0,
):
	"""Retry async agent calls on transient failures only."""

	def decorator(func: F) -> F:
		@functools.wraps(func)
		async def wrapper(*args, **kwargs):
			backoff = initial_backoff

			for attempt in range(1, max_retries + 1):
				try:
					return await func(*args, **kwargs)
				except Exception as exception:
					if not _is_transient_error(exception) or attempt >= max_retries:
						raise

					wait_seconds = min(backoff, max_backoff)
					logger.warning(
						"Transient error in %s (attempt %s/%s): %s. Retrying in %.1fs",
						func.__name__,
						attempt,
						max_retries,
						type(exception).__name__,
						wait_seconds,
					)
					await asyncio.sleep(wait_seconds)
					backoff *= exponential_base

			raise RuntimeError("Retry loop exited unexpectedly")

		return wrapper  # type: ignore[return-value]

	return decorator
