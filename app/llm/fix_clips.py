"""
Fix and improve clips: translate to Indonesian, fix caption-topic mismatches, deduplicate.

Pipeline (runs AFTER find_clips, BEFORE subtitle generation):
  1. Translate fields to Indonesian (skip if already Indonesian)
  2. Fix mismatched caption/topic pairs
  3. Improve content and deduplicate overlapping topics
"""

import json
from typing import Any

from app.llm.backends.client import call_llm
from app.llm.modules._llm_helpers import merge_llm_result
from app.llm.prompts.prompts import get_prompt
from app.utils import log

_FIELDS = ["title", "topic", "caption", "hook"]


# ── Public API ───────────────────────────────────────────────────────────────


def generate_single_clip_metadata(
    clip: dict[str, Any],
    segments: list[dict[str, Any]],
    llm_model: str | None = None,
    api_key: str | None = None,
) -> dict[str, Any]:
    """Generate title/topic/caption/reason/hook for a full-video clip from transcript."""
    transcript = _build_transcript(segments)
    if not transcript:
        raise RuntimeError("Cannot generate metadata without transcript text")

    prompt = _read_prompt("Generate Single Clip Metadata")
    user_msg = f"{prompt}\n\nTranscript:\n{transcript}\n\nClip:\n{json.dumps([clip], ensure_ascii=False, indent=2)}"
    system_msg = (
        "You are an expert short-form video strategist. "
        "Generate accurate, compelling metadata from the transcript."
    )

    result = call_llm(system_msg, user_msg, api_key, llm_model)
    if not result or not isinstance(result, list) or not isinstance(result[0], dict):
        raise RuntimeError(f"Metadata generation failed: {result!r}")

    updated = clip.copy()
    for field in ["title", "topic", "caption", "reason", "hook"]:
        value = str(result[0].get(field, "") or "").strip()
        if not value:
            raise RuntimeError(f"Metadata missing required field: {field}")
        updated[field] = value
    return updated


def fix_and_improve_clips(
    clips: list[dict[str, Any]],
    llm_model: str | None = None,
    api_key: str | None = None,
    detected_language: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """
    3-step pipeline: translate → fix caption/topic → improve & dedup.
    """
    if not clips:
        return clips

    log("INFO", f"Fixing pipeline: {len(clips)} clips")

    clips = _translate(clips, llm_model, api_key, detected_language)
    log("OK", f"After translate: {len(clips)} clips")

    clips = _fix_caption_topic(clips, llm_model, api_key)
    log("OK", f"After fix: {len(clips)} clips")

    clips = _improve_and_dedup(clips, llm_model, api_key)
    log("OK", f"After improve: {len(clips)} clips")

    # Re-rank
    clips.sort(key=lambda x: (-x.get("clip_score", 0), x.get("rank", 999)))
    for i, c in enumerate(clips, 1):
        c["rank"] = i

    return clips


def translate_subtitle_words(
    words: list[dict],
    llm_model: str | None = None,
    api_key: str | None = None,
    max_words_per_group: int = 5,
) -> list[dict]:
    """
    Translate word-level subtitle entries to Indonesian.

    Groups words into short phrases, translates via LLM, redistributes
    timestamps proportionally across translated words.
    """
    if not words:
        return []

    # Group words
    groups: list[list[dict]] = []
    current: list[dict] = []
    for w in words:
        current.append(w)
        if len(current) >= max_words_per_group:
            groups.append(current)
            current = []
    if current:
        groups.append(current)

    # Build phrase list
    phrases = [
        {
            "id": i,
            "text": " ".join(w["word"] for w in grp),
            "start": grp[0]["start"],
            "end": grp[-1]["end"],
        }
        for i, grp in enumerate(groups)
    ]

    prompt = _read_prompt("Translate Subtitle Phrases")
    user_msg = (
        f"{prompt}\n\nPhrases to translate:\n{json.dumps(phrases, ensure_ascii=False, indent=2)}"
    )
    system_msg = (
        "You are a professional subtitle translator. "
        "Translate spoken Indonesian-language content accurately and naturally."
    )

    result = call_llm(system_msg, user_msg, api_key, llm_model)
    if not result or not isinstance(result, list):
        raise RuntimeError(f"Subtitle translation failed: {result!r}")

    # Build id → translated text map
    id_to_text = {
        int(p["id"]): p["text"].strip() for p in result if "id" in p and p.get("text", "").strip()
    }

    # Redistribute timestamps
    translated: list[dict] = []
    for i, grp in enumerate(groups):
        t = id_to_text.get(i)
        if not t:
            raise RuntimeError(f"Subtitle translation missing phrase id={i}")
        tw = t.split()
        dur = (grp[-1]["end"] - grp[0]["start"]) / len(tw)
        for j, word in enumerate(tw):
            translated.append(
                {
                    "word": word,
                    "start": grp[0]["start"] + j * dur,
                    "end": grp[0]["start"] + (j + 1) * dur,
                }
            )

    log("OK", f"Subtitles: {len(words)} → {len(translated)} translated words")
    return translated


# ── Pipeline steps ───────────────────────────────────────────────────────────


def _translate(
    clips: list[dict[str, Any]],
    llm_model: str | None,
    api_key: str | None,
    detected_language: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Translate clip fields to Indonesian. Skips if already Indonesian."""
    if not clips:
        return clips
    if detected_language:
        lang = detected_language.get("language", "").lower()
        prob = detected_language.get("language_probability", 0.0)
        if lang == "id" and prob > 0.6:
            log("OK", f"Already Indonesian (p={prob:.0%}), skipping translation")
            return clips

    system = "You are a helpful assistant that translates content to Indonesian while preserving meaning and tone."
    return merge_llm_result("Translate to Indonesian", system, clips, _FIELDS, llm_model, api_key)


def _fix_caption_topic(
    clips: list[dict[str, Any]],
    llm_model: str | None,
    api_key: str | None,
) -> list[dict[str, Any]]:
    """Fix mismatched caption/topic pairs."""
    if not clips:
        return clips
    system = "You are an expert content strategist ensuring social media content consistency."
    return merge_llm_result(
        "Fix Mismatched Caption/Topic", system, clips, ["caption", "topic"], llm_model, api_key
    )


def _improve_and_dedup(
    clips: list[dict[str, Any]],
    llm_model: str | None,
    api_key: str | None,
) -> list[dict[str, Any]]:
    """Improve content and deduplicate. LLM may drop clips or add new ones."""
    if not clips:
        return clips
    system = (
        "You are an expert social media strategist optimizing video clips for viral engagement."
    )
    result = merge_llm_result(
        "Improve and Deduplicate Clips",
        system,
        clips,
        _FIELDS,
        llm_model,
        api_key,
        append_unmatched=True,
    )
    for i, c in enumerate(result, 1):
        c["rank"] = i
    return result


# ── Utilities ────────────────────────────────────────────────────────────────


def _read_prompt(name: str) -> str:
    prompt = get_prompt(name)
    if not prompt:
        log("ERROR", f"Prompt '{name}' not found")
    return prompt


def _build_transcript(segments: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for seg in segments:
        text = str(seg.get("text", "") or "").strip()
        if not text:
            continue
        lines.append(f"[{float(seg.get('start', 0)):.0f}-{float(seg.get('end', 0)):.0f}] {text}")
    return "\n".join(lines)
