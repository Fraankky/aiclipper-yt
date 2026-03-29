"""
Shared helper for LLM call → result merge pattern.

Used by fix_clips.py for translate, fix-caption, and improve-deduplicate flows.
"""

import json
from typing import Any

from app.llm.backends.client import call_llm
from app.llm.prompts.prompts import get_prompt
from app.utils import log


def merge_llm_result(
    prompt_name: str,
    system_message: str,
    clips: list[dict[str, Any]],
    fields: list[str],
    llm_model: str | None = None,
    api_key: str | None = None,
    *,
    append_unmatched: bool = False,
) -> list[dict[str, Any]]:
    """
    Generic pattern: call LLM with prompt, merge result fields back into clips.

    Args:
        prompt_name: Key in prompts.py (e.g. "Translate to Indonesian")
        system_message: System prompt for the LLM
        clips: Original clips to process
        fields: Field names to merge from LLM result (e.g. ["title", "topic", "caption", "hook"])
        append_unmatched: If True, LLM results not matching any original are appended as-is
    """
    prompt_text = get_prompt(prompt_name)
    if not prompt_text:
        log("ERROR", f"Prompt '{prompt_name}' not found")
        return clips

    user_message = f"{prompt_text}\n\nClips:\n{json.dumps(clips, ensure_ascii=False, indent=2)}"
    result = call_llm(system_message, user_message, api_key, llm_model)

    if not result or not isinstance(result, list) or not all(isinstance(c, dict) for c in result):
        log("WARN", f"'{prompt_name}': LLM returned no valid results")
        return clips

    orig_map = {(round(c.get("start", 0), 2), round(c.get("end", 0), 2)): c for c in clips}

    merged: list[dict[str, Any]] = []
    matched = 0
    for llm_clip in result:
        key = (round(llm_clip.get("start", 0), 2), round(llm_clip.get("end", 0), 2))
        if key in orig_map:
            out = orig_map[key].copy()
            for field in fields:
                if field in llm_clip:
                    out[field] = llm_clip[field]
            merged.append(out)
            matched += 1
        elif append_unmatched:
            merged.append(llm_clip)

    log("OK", f"'{prompt_name}': matched {matched}/{len(clips)} clips")
    return merged
