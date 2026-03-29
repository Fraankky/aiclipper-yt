"""
LLM configuration — centralized settings for model, API, and generation.

All model/provider knobs live here so backends.py stays focused on API logic.
Override defaults via environment variables (OPENROUTER_API_KEY, OPENROUTER_MODEL).
"""

import os

# ── OpenRouter ───────────────────────────────────────────────────────────────
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemma-2-9b-it:free")
API_KEY_ENV = "OPENROUTER_API_KEY"
MODEL_ENV = "OPENROUTER_MODEL"

# ── Generation defaults ─────────────────────────────────────────────────────
MAX_TOKENS = 8192
MAX_TOKENS_REASONING = 16000
TEMPERATURE = 0.3
TEMPERATURE_REASONING = 1.0

# ── Request metadata (shown in OpenRouter dashboard) ─────────────────────────
EXTRA_HEADERS = {
    "HTTP-Referer": "https://github.com/ai-video-clipper",
    "X-Title": "AI Video Clipper",
}
