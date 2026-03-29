"""
Score computation and normalization for clips.

Handles:
- Parsing score values (0–100 clamping)
- Normalizing legacy → new field names
- Weighted clip_score formula
- Low-value content detection (intros, outros, disclaimers)
"""

import re
from typing import Any

# ── Low-value content patterns ───────────────────────────────────────────────
# Q&A / tanya jawab is NOT excluded — often contains great insights.

_LOW_VALUE_PATTERNS = re.compile(
    r"(?i)"
    r"(?:selamat datang|pembuka|opening|penutup|closing|terima kasih|"
    r"thank you|perkenalan|introduction|polling|vote|subscribe|"
    r"topik yang akan|webinar akan|rekaman|pendekatan materi|"
    r"ajak partisipasi|sapa penonton|ucapan|disclaimer|house\s*keeping)"
)


def is_low_value_clip(c: dict[str, Any]) -> bool:
    """True if clip title/topic matches intro/outro/disclaimer patterns."""
    combined = f"{c.get('title', '') or ''} {c.get('topic', '') or ''}".strip()
    return bool(_LOW_VALUE_PATTERNS.search(combined))


# ── Score helpers ────────────────────────────────────────────────────────────


def to_score(value: Any) -> int:
    """Parse any value into a bounded int [0, 100]."""
    try:
        return max(0, min(100, int(round(float(value)))))
    except (TypeError, ValueError):
        return 0


def normalize_score_fields(c: dict[str, Any]) -> dict[str, int]:
    """
    Return the 5 canonical score fields, falling back to legacy names.
    """
    hook = to_score(c.get("score_hook"))
    insight = to_score(c.get("score_insight_density"))
    retention = to_score(c.get("score_retention"))
    emotional = to_score(c.get("score_emotional_payoff"))
    clarity = to_score(c.get("score_clarity"))

    # Legacy fallback
    if hook + insight + retention + emotional + clarity == 0:
        hook = to_score(c.get("score_newsworthy", c.get("score_shareability", 0)))
        insight = to_score(c.get("score_informative", c.get("score_educational", 0)))
        retention = to_score(c.get("score_energy", 0))
        emotional = to_score(c.get("score_entertainment", 0))
        clarity = to_score(c.get("score_easy", 0))

    return {
        "score_hook": hook,
        "score_insight_density": insight,
        "score_retention": retention,
        "score_emotional_payoff": emotional,
        "score_clarity": clarity,
    }


def compute_clip_score(c: dict[str, Any]) -> float:
    """
    Weighted clip_score.  Preserves original if legacy clip has no new fields.

    Formula: hook×0.30 + insight×0.25 + retention×0.20 + emotional×0.15 + clarity×0.10
    """
    scores = normalize_score_fields(c)
    hook = scores["score_hook"]
    insight = scores["score_insight_density"]
    retention = scores["score_retention"]
    emotional = scores["score_emotional_payoff"]
    clarity = scores["score_clarity"]

    # Legacy clip with existing valid score — preserve it
    has_original = "clip_score" in c and isinstance(c.get("clip_score"), (int, float))
    has_new = any(c.get(f) is not None for f in scores)
    if has_original and not has_new and c["clip_score"] > 0:
        return float(c["clip_score"])

    total = hook + insight + retention + emotional + clarity
    if total > 0:
        return round(
            hook * 0.30 + insight * 0.25 + retention * 0.20 + emotional * 0.15 + clarity * 0.10,
            1,
        )

    # No scores — LLM chose this clip, assign default passing score
    return 70.0
