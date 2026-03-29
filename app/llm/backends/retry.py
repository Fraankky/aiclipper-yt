"""
Retry logic for LLM API calls.

Handles rate limits (429), transient provider errors (502/503/504),
and empty responses with exponential backoff.
"""

import json
import time
from collections.abc import Callable

from app.utils import log


def retry_on_rate_limit(
    api_call_fn: Callable[[], str],
    max_retries: int = 5,
    initial_wait: float = 2.0,
) -> str:
    """
    Retry API call on rate limits, transient errors, or empty responses.

    Non-retriable errors are raised immediately.
    Persistent retriable failures return "" (caller decides what to do).
    """
    for attempt in range(max_retries):
        try:
            response = api_call_fn()
            if response:
                return response

            # Empty response — retry
            if attempt < max_retries - 1:
                wait = initial_wait * (2**attempt)
                log("WARN", f"Empty response. Retry {attempt + 1}/{max_retries} in {wait:.1f}s…")
                time.sleep(wait)
            else:
                log("ERROR", f"Empty response after {max_retries} retries")
                return ""

        except Exception as e:
            err = str(e).lower()
            err_type = type(e).__name__

            is_rate_limit = "429" in str(e) or "RateLimitError" in err_type or "rate limit" in err
            is_transient = isinstance(e, json.JSONDecodeError) or any(
                m in err
                for m in (
                    "expecting value",
                    "line 1 column 1",
                    "bad gateway",
                    "service unavailable",
                    "gateway timeout",
                    "502",
                    "503",
                    "504",
                    "api connection error",
                    "connection reset",
                    "timed out",
                )
            )

            if not (is_rate_limit or is_transient):
                raise  # non-retriable — propagate

            if attempt < max_retries - 1:
                wait = initial_wait * (2**attempt)
                reason = "Rate limited (429)" if is_rate_limit else "Transient API error"
                log("WARN", f"{reason}. Retry {attempt + 1}/{max_retries} in {wait:.1f}s…")
                time.sleep(wait)
            else:
                reason = "Rate limit" if is_rate_limit else "Transient API error"
                log("ERROR", f"{reason} persisted after {max_retries} retries")
                return ""
    return ""
