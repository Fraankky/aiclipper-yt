"""
OpenRouter backend — single-model, OpenAI-compatible API.

Handles reasoning toggle with automatic fallback when the model
doesn't support extended thinking.
"""

import sys
from typing import Any

from app.llm.backends.json_parser import parse_llm_json, retry_on_json_failure
from app.llm.backends.retry import retry_on_rate_limit
from app.llm.config.config import (
    DEFAULT_MODEL,
    EXTRA_HEADERS,
    MAX_TOKENS,
    MAX_TOKENS_REASONING,
    OPENROUTER_BASE_URL,
    TEMPERATURE,
    TEMPERATURE_REASONING,
)
from app.utils import BOLD, RESET, log


def _is_reasoning_unsupported(error: Exception) -> bool:
    """Check if API error means the model doesn't support reasoning."""
    msg = str(error).lower()
    return any(
        m in msg
        for m in (
            "reasoning",
            "unsupported parameter",
            "invalid parameter",
            "not supported",
            "unknown field",
            "extra inputs are not permitted",
            "400",
        )
    )


def openrouter(
    system: str,
    user: str,
    api_key: str,
    model: str = DEFAULT_MODEL,
    base_url: str = OPENROUTER_BASE_URL,
    enable_reasoning: bool = True,
) -> list[dict[str, Any]]:
    """
    Call OpenRouter and return parsed clips.

    Tries reasoning first; falls back to plain call if unsupported.
    """
    try:
        from openai import OpenAI
    except ImportError:
        log("ERROR", "openai SDK not installed.  pip install openai")
        sys.exit(1)

    log("LLM", f"OpenRouter → {BOLD}{model}{RESET}")
    client = OpenAI(api_key=api_key, base_url=base_url)

    def _call_once(sys_prompt: str, user_prompt: str, reasoning: bool) -> str:
        """Single API call with or without reasoning."""

        def api_call() -> str:
            kwargs: dict[str, Any] = {
                "model": model,
                "max_tokens": MAX_TOKENS_REASONING if reasoning else MAX_TOKENS,
                "temperature": TEMPERATURE_REASONING if reasoning else TEMPERATURE,
                "messages": [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "extra_headers": EXTRA_HEADERS,
            }
            if reasoning:
                kwargs["extra_body"] = {"reasoning": {"effort": "high"}}

            resp = client.chat.completions.create(**kwargs)
            message = resp.choices[0].message

            reasoning_text = getattr(message, "reasoning", None) or ""
            content = message.content or ""

            if reasoning_text:
                log("DEBUG", f"Reasoning trace ({len(reasoning_text)} chars)")

            _, content_ok = parse_llm_json(content) if content else ([], False)
            if content_ok:
                return content

            if reasoning_text:
                _, reasoning_ok = parse_llm_json(reasoning_text)
                if reasoning_ok:
                    log("DEBUG", "Using JSON from reasoning field")
                    return reasoning_text

            return content or ""

        return retry_on_rate_limit(api_call, max_retries=5, initial_wait=2.0)

    def _call_with_reasoning(sys_prompt: str, user_prompt: str) -> str:
        if not enable_reasoning:
            return _call_once(sys_prompt, user_prompt, reasoning=False)
        try:
            return _call_once(sys_prompt, user_prompt, reasoning=True)
        except Exception as e:
            if _is_reasoning_unsupported(e):
                log("WARN", "Model doesn't support reasoning; retrying without.")
                return _call_once(sys_prompt, user_prompt, reasoning=False)
            raise

    def _call_without_reasoning(sys_prompt: str, user_prompt: str) -> str:
        return _call_once(sys_prompt, user_prompt, reasoning=False)

    clips = retry_on_json_failure(_call_with_reasoning, system, user, max_attempts=2)

    if not clips and enable_reasoning:
        log("WARN", "Reasoning yielded nothing — retrying without reasoning.")
        clips = retry_on_json_failure(_call_without_reasoning, system, user, max_attempts=2)

    if clips:
        log("OK", f"OpenRouter returned {len(clips)} clips")
    else:
        log("WARN", "OpenRouter returned 0 clips")
    return clips
