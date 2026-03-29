"""
Robust JSON extraction from LLM responses.

Three-stage parsing:
  1. Direct json.loads (fast path)
  2. Balanced bracket scan (handles markdown fences, extra text)
  3. Partial array salvage (recovers truncated outputs)
"""

import json
import re
from typing import Any

from app.utils import log


def parse_llm_json(raw: str) -> tuple[list[dict[str, Any]], bool]:
    """
    Extract a JSON array from raw LLM text.

    Returns (parsed_data, success).
    """
    # Strip thinking blocks and markdown fences
    cleaned = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL)
    cleaned = re.sub(r"```(?:json)?", "", cleaned).strip().rstrip("`").strip()

    # 1) Direct parse
    try:
        data = json.loads(cleaned)
        if isinstance(data, list):
            return data, True
        # Wrapped in object — find first array value
        for v in data.values():
            if isinstance(v, list):
                return v, True
        return [], False
    except json.JSONDecodeError:
        pass

    # 2) Balanced bracket scan
    block = _extract_balanced_array(cleaned)
    if block:
        try:
            data = json.loads(block)
            if isinstance(data, list):
                return data, True
        except json.JSONDecodeError:
            pass

    # 3) Partial array salvage
    partial = _parse_partial_array(cleaned)
    if partial:
        log("WARN", f"Recovered {len(partial)} clip(s) from truncated output")
        return partial, True

    return [], False


def retry_on_json_failure(
    api_call_fn,
    system: str,
    user: str,
    max_attempts: int = 2,
) -> list[dict[str, Any]]:
    """
    Retry LLM call with modified prompt if JSON parsing fails.

    Returns parsed clips or [].
    """
    retry_suffixes = [
        "",
        "\n\n[RETRY: Respond with ONLY a valid JSON array, no other text.]",
        '\n\n[RETRY 2: Output ONLY JSON array. Example: [{"start": 0, "end": 10, ...}].]',
    ]

    raw = ""
    for attempt in range(min(max_attempts, len(retry_suffixes))):
        raw = api_call_fn(system, user + retry_suffixes[attempt])
        clips, ok = parse_llm_json(raw)
        if ok:
            return clips
        if attempt < max_attempts - 1:
            log("WARN", f"JSON parse failed (attempt {attempt + 1}), retrying…")

    log("ERROR", "Could not parse JSON after retries")
    return []


# ── Internal helpers ─────────────────────────────────────────────────────────


def _extract_balanced_array(text: str) -> str | None:
    """Return first syntactically balanced ``[...]`` substring, or None."""
    start = text.find("[")
    if start < 0:
        return None

    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


def _parse_partial_array(text: str) -> list[dict[str, Any]]:
    """Salvage leading valid objects from a possibly truncated JSON array."""
    arr = text.strip()
    if not arr.startswith("["):
        return []

    body = arr[1:]
    decoder = json.JSONDecoder()
    idx = 0
    out: list[dict[str, Any]] = []

    while idx < len(body):
        while idx < len(body) and body[idx] in " \t\r\n,":
            idx += 1
        if idx >= len(body) or body[idx] == "]":
            break
        try:
            item, idx = decoder.raw_decode(body, idx)
        except json.JSONDecodeError:
            break
        if isinstance(item, dict):
            out.append(item)

    return out
