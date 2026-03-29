"""
Clip validation, merging, and deduplication.

Applied after LLM returns raw clips — ensures quality gates:
- Duration within bounds
- Score ≥ minimum threshold
- No overlapping duplicates
- Required fields present
"""

from typing import Any

from app.llm.modules.scoring import compute_clip_score, is_low_value_clip, normalize_score_fields
from app.utils import log


def validate_clips(
    clips: list[dict[str, Any]],
    min_dur: int,
    max_dur: int,
    max_clips: int,
    min_score: int,
    video_duration: float | None = None,
) -> list[dict[str, Any]]:
    """Sanitize, deduplicate, score-sort, and cap the clip list."""
    seen_ranges: list[tuple[float, float]] = []

    # Score and sort
    scored: list[dict[str, Any]] = []
    for c in clips:
        try:
            s, e = float(c["start"]), float(c["end"])
        except (KeyError, ValueError, TypeError):
            continue
        score = compute_clip_score(c)
        if is_low_value_clip(c):
            score = max(0, score - 25)
        c["_score"] = score
        scored.append(c)
    scored.sort(key=lambda x: (-x["_score"], -int(x.get("score_hook", 0) or 0)))

    valid: list[dict[str, Any]] = []
    for c in scored:
        s, e = float(c["start"]), float(c["end"])
        dur = e - s
        title = c.get("title", "?")

        if dur < min_dur or dur > max_dur:
            log("DEBUG", f"Skip '{title}' [{s:.0f}-{e:.0f}]: duration {dur:.0f}s")
            continue
        if video_duration and e > video_duration + 2:
            log("DEBUG", f"Skip '{title}' [{s:.0f}-{e:.0f}]: exceeds video duration")
            continue
        if c["_score"] < min_score:
            log("DEBUG", f"Skip '{title}' [{s:.0f}-{e:.0f}]: score {c['_score']:.1f} < {min_score}")
            continue

        if any(_overlap_ratio(s, e, rs, re) > 0.5 for rs, re in seen_ranges):
            continue

        seen_ranges.append((s, e))
        _fill_defaults(c, len(valid) + 1, normalize_score_fields(c))
        c["clip_score"] = c.pop("_score")
        c.pop("engagement_score", None)
        for legacy in (
            "score_shareability",
            "score_educational",
            "score_entertainment",
            "score_easy",
            "score_informative",
            "score_energy",
            "score_newsworthy",
        ):
            c.pop(legacy, None)

        valid.append(c)
        if len(valid) >= max_clips:
            break

    valid.sort(key=lambda x: (-x.get("clip_score", 0), -int(x.get("score_hook", 0) or 0)))
    for i, c in enumerate(valid, 1):
        c["rank"] = i

    return valid


def merge_chunk_clips(
    all_clips: list[dict[str, Any]],
    min_dur: int,
    max_dur: int,
    max_clips: int,
    min_score: int,
    video_duration: float | None = None,
) -> list[dict[str, Any]]:
    """
    Merge clips from multiple chunks, removing near-duplicates (>70% overlap).
    Then validate the merged list.
    """
    all_clips.sort(key=lambda c: (float(c.get("start", 0)), -compute_clip_score(c)))

    deduped: list[dict[str, Any]] = []
    for clip in all_clips:
        try:
            s, e = float(clip["start"]), float(clip["end"])
        except (KeyError, ValueError, TypeError):
            continue

        is_dup = False
        for i, existing in enumerate(deduped):
            es, ee = float(existing["start"]), float(existing["end"])
            overlap = max(0, min(e, ee) - max(s, es))
            shorter = min(e - s, ee - es)
            if shorter > 0 and overlap / shorter > 0.7:
                if compute_clip_score(clip) > compute_clip_score(existing):
                    deduped[i] = clip
                is_dup = True
                break
        if not is_dup:
            deduped.append(clip)

    log("INFO", f"Merged {len(all_clips)} raw clips → {len(deduped)} after dedup")
    return validate_clips(deduped, min_dur, max_dur, max_clips, min_score, video_duration)


# ── Internal helpers ─────────────────────────────────────────────────────────


def _overlap_ratio(s1: float, e1: float, s2: float, e2: float) -> float:
    overlap = max(0, min(e1, e2) - max(s1, s2))
    shorter = min(e1 - s1, e2 - s2)
    return overlap / shorter if shorter > 0 else 0


def _fill_defaults(c: dict[str, Any], rank: int, normalized: dict[str, int]) -> None:
    c.setdefault("rank", rank)
    c.setdefault("title", f"Clip {rank}")
    c.setdefault("topic", "")
    c.setdefault("caption", "")
    c.setdefault("reason", "")
    c.setdefault("hook", "")
    c.update(normalized)
