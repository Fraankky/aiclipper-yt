"""
Segment chunking, transcript text building, and gap detection.

Used by find_clips to split long transcripts for iterative LLM processing,
and to find uncovered time ranges for a second-pass extraction.
"""

from typing import Any

from app.utils import log


def build_transcript_text(segments: list[dict[str, Any]]) -> str:
    """Compact transcript: [start-end]text — saves tokens."""
    lines: list[str] = []
    for s in segments:
        st = f"{s['start']:.0f}" if s["start"] == int(s["start"]) else f"{s['start']:.1f}"
        en = f"{s['end']:.0f}" if s["end"] == int(s["end"]) else f"{s['end']:.1f}"
        lines.append(f"[{st}-{en}]{s['text']}")
    return "\n".join(lines)


def chunk_segments(
    segments: list[dict[str, Any]],
    chunk_duration: float = 480.0,
    overlap_duration: float = 60.0,
) -> list[list[dict[str, Any]]]:
    """
    Split segments into time-based chunks with overlap.

    If total duration ≤ 1.3 × chunk_duration, returns a single chunk (no split).
    """
    if not segments:
        return []

    total_dur = segments[-1]["end"] - segments[0]["start"]
    if total_dur <= chunk_duration * 1.3:
        return [segments]

    chunks: list[list[dict[str, Any]]] = []
    window_start = segments[0]["start"]
    total_end = segments[-1]["end"]

    while window_start < total_end:
        window_end = window_start + chunk_duration
        chunk = [
            s
            for s in segments
            if s["end"] > window_start and s["start"] < window_end + overlap_duration
        ]
        if chunk:
            chunks.append(chunk)
        window_start += chunk_duration

    log(
        "INFO",
        f"Split {total_dur:.0f}s transcript into {len(chunks)} chunks "
        f"(~{chunk_duration:.0f}s each, {overlap_duration:.0f}s overlap)",
    )
    return chunks


def find_gaps(
    clips: list[dict[str, Any]],
    segments: list[dict[str, Any]],
    min_gap: float = 30.0,
) -> list[tuple[float, float]]:
    """Find time ranges not covered by any clip (≥ min_gap seconds)."""
    if not segments:
        return []

    total_start = segments[0]["start"]
    total_end = segments[-1]["end"]
    sorted_clips = sorted(clips, key=lambda c: float(c.get("start", 0)))

    gaps: list[tuple[float, float]] = []
    cursor = total_start

    for c in sorted_clips:
        cs, ce = float(c["start"]), float(c["end"])
        if cs > cursor + min_gap:
            gaps.append((cursor, cs))
        cursor = max(cursor, ce)

    if total_end > cursor + min_gap:
        gaps.append((cursor, total_end))

    return gaps


def segments_in_range(
    segments: list[dict[str, Any]],
    start: float,
    end: float,
) -> list[dict[str, Any]]:
    """Return segments overlapping [start, end]."""
    return [s for s in segments if s["end"] > start and s["start"] < end]
