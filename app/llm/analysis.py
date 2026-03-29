"""
Find engaging clips in transcript via LLM.

Splits long transcripts into overlapping chunks, calls LLM on each,
then merges and deduplicates results.
"""

import json
import math
from pathlib import Path
from typing import Any

from app.llm.backends.client import call_llm
from app.llm.modules.chunking import build_transcript_text, chunk_segments
from app.llm.modules.validation import merge_chunk_clips, validate_clips
from app.llm.prompts.system_prompt import SYSTEM_PROMPT
from app.utils import MAX_CLIPS_HARD_LIMIT, log


def _build_user_prompt(
    transcript: str,
    min_dur: int,
    max_dur: int,
    max_clips: int,
    min_score: int,
    chunk_info: str = "",
) -> str:
    header = (
        f"Analyze this transcript and extract every clip with a realistic shot at high views.\n"
        f"Duration: {min_dur}–{max_dur}s. Max {max_clips} clips. clip_score ≥ {min_score}.\n"
    )
    if chunk_info:
        header += f"{chunk_info}\n"
    return f"{header}\nTRANSKRIP:\n{transcript}"


def find_clips(
    segments: list[dict[str, Any]],
    *,
    min_duration: int = 15,
    max_duration: int = 60,
    max_clips: int = MAX_CLIPS_HARD_LIMIT,
    min_score: int = 60,
    llm_model: str | None = None,
    api_key: str | None = None,
    video_duration: float | None = None,
    chunk_duration: float = 480.0,
    chunk_overlap: float = 60.0,
    raw_clips_cache_file: str | Path | None = None,
) -> list[dict[str, Any]]:
    """
    Ask LLM to find ALL engaging clips (up to max_clips).

    Splits long transcripts into overlapping chunks for iterative processing.
    Caches raw LLM results to avoid redundant calls on re-runs.
    """
    all_raw_clips = _load_or_generate(
        segments,
        min_duration=min_duration,
        max_duration=max_duration,
        max_clips=max_clips,
        min_score=min_score,
        llm_model=llm_model,
        api_key=api_key,
        chunk_duration=chunk_duration,
        chunk_overlap=chunk_overlap,
        raw_clips_cache_file=raw_clips_cache_file,
    )

    chunks = chunk_segments(segments, chunk_duration, chunk_overlap)
    if len(chunks) > 1:
        clips = merge_chunk_clips(
            all_raw_clips, min_duration, max_duration, max_clips, min_score, video_duration
        )
    else:
        clips = validate_clips(
            all_raw_clips, min_duration, max_duration, max_clips, min_score, video_duration
        )

    if not clips:
        log("WARN", "LLM returned 0 valid clips.")
    else:
        log("OK", f"{len(clips)} valid clips after validation")
    return clips


# ── Internal: load cache or call LLM ────────────────────────────────────────
def _load_or_generate(
    segments: list[dict[str, Any]],
    *,
    min_duration: int,
    max_duration: int,
    max_clips: int,
    min_score: int,
    llm_model: str | None,
    api_key: str | None,
    chunk_duration: float,
    chunk_overlap: float,
    raw_clips_cache_file: str | Path | None,
) -> list[dict[str, Any]]:
    """Load cached raw clips, or generate via LLM chunks."""
    # Try cache
    if raw_clips_cache_file:
        cache = Path(raw_clips_cache_file)
        if cache.exists():
            log("INFO", f"Loading cached raw LLM clips from {cache}")
            return json.loads(cache.read_text())

    # Generate via LLM
    chunks = chunk_segments(segments, chunk_duration, chunk_overlap)
    system = SYSTEM_PROMPT.format(
        min_dur=min_duration,
        max_dur=max_duration,
        max_clips=max_clips,
        min_score=min_score,
    )

    all_raw: list[dict[str, Any]] = []
    n = len(chunks)

    for idx, chunk in enumerate(chunks, 1):
        per_chunk = min(max(10, math.ceil(max_clips / max(n, 1) * 1.5)), max_clips)
        transcript = build_transcript_text(chunk)

        chunk_info = ""
        if n > 1:
            chunk_info = (
                f"Ini bagian {idx}/{n} video "
                f"({chunk[0]['start']:.0f}s-{chunk[-1]['end']:.0f}s). "
                f"Ekstrak SEMUA momen menarik di bagian ini."
            )
            log("INFO", f"Chunk {idx}/{n}: {chunk[0]['start']:.0f}s → {chunk[-1]['end']:.0f}s")

        user = _build_user_prompt(
            transcript, min_duration, max_duration, per_chunk, min_score, chunk_info
        )
        raw = call_llm(system, user, api_key, llm_model)
        log("OK", f"Chunk {idx}/{n}: LLM returned {len(raw)} clips")
        all_raw.extend(raw)

    log("INFO", f"Total raw clips from {n} chunk(s): {len(all_raw)}")

    # Cache results
    if raw_clips_cache_file:
        cache = Path(raw_clips_cache_file)
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(all_raw, indent=2, ensure_ascii=False))
        log("OK", f"Cached {len(all_raw)} raw LLM clips → {cache}")

    return all_raw
