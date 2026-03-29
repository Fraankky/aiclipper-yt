"""
LLM client — thin facade that delegates to provider-specific modules.

Import call_llm from here (stable public API).
Provider internals live in openrouter.py, retry.py, json_parser.py.
"""

import os
import sys
from typing import Any

from app.llm.backends.openrouter import openrouter
from app.llm.config.config import API_KEY_ENV, DEFAULT_MODEL
from app.utils import log


def call_llm(
    system: str,
    user: str,
    api_key: str | None = None,
    llm_model: str | None = None,
    enable_reasoning: bool = True,
) -> list[dict[str, Any]]:
    """
    Call OpenRouter and return parsed clips.

    Args:
        api_key: API key (falls back to OPENROUTER_API_KEY env var)
        llm_model: Model override (falls back to OPENROUTER_MODEL env var, then config default)
        enable_reasoning: When True (default), request extended reasoning.
            If unsupported the call is transparently retried without reasoning.
    """
    key = api_key or os.getenv(API_KEY_ENV)
    if not key:
        log("ERROR", "No OpenRouter API key. Set OPENROUTER_API_KEY or pass --api-key.")
        sys.exit(1)

    model = llm_model or DEFAULT_MODEL
    return openrouter(system, user, key, model=model, enable_reasoning=enable_reasoning)
