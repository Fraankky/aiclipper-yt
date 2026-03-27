"""Centralized application constants."""

from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# App metadata
# ---------------------------------------------------------------------------
APP_SLUG: str = "aiclip-app"
APP_DISPLAY_NAME: str = "AI Clip App"
APP_VERSION: str = "0.1.0"

# ---------------------------------------------------------------------------
# Environment / runtime
# ---------------------------------------------------------------------------
ENV_DEVELOPMENT: str = "development"
ENV_STAGING: str = "staging"
ENV_PRODUCTION: str = "production"

DEFAULT_ENV: str = ENV_DEVELOPMENT
DEFAULT_DEBUG: bool = True
DEFAULT_HOST: str = "127.0.0.1"
DEFAULT_PORT: int = 8000
DEFAULT_LOG_LEVEL: str = "INFO"

# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------
DEFAULT_API_PREFIX: str = "/api/v1"
HEALTH_ENDPOINT: str = "/health"
DEFAULT_CORS_ALLOW_ORIGINS: tuple[str, ...] = (
    "http://localhost:3000",
    "http://127.0.0.1:3000",
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT: Path = Path(__file__).resolve().parents[1].parent
APP_DIR: Path = PROJECT_ROOT / "app"
DATA_DIR: Path = PROJECT_ROOT / "data"
STATIC_DIR: Path = PROJECT_ROOT / "static"
ASSETS_DIR: Path = STATIC_DIR / "assets"
PROMPTS_DIR: Path = APP_DIR / "prompts"
TESTS_DIR: Path = PROJECT_ROOT / "tests"
DOCS_DIR: Path = PROJECT_ROOT / "docs"
SCRIPTS_DIR: Path = PROJECT_ROOT / "scripts"

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
DEFAULT_SQLITE_DB_FILENAME: str = "aiclip.db"
DEFAULT_DATABASE_URL: str = f"sqlite:///./data/{DEFAULT_SQLITE_DB_FILENAME}"

# ---------------------------------------------------------------------------
# AI provider (OpenRouter)
# ---------------------------------------------------------------------------
DEFAULT_OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
DEFAULT_OPENROUTER_MODEL: str = "openai/gpt-4o-mini"

# ---------------------------------------------------------------------------
# Media / pipeline
# ---------------------------------------------------------------------------
DEFAULT_FFMPEG_BIN: str = "ffmpeg"
DEFAULT_FFPROBE_BIN: str = "ffprobe"
DEFAULT_WHISPER_MODEL: str = "base"

BYTES_PER_KIB: int = 1024
BYTES_PER_MIB: int = 1024 * BYTES_PER_KIB
DEFAULT_MAX_UPLOAD_SIZE_MB: int = 1024
DEFAULT_MAX_UPLOAD_SIZE_BYTES: int = DEFAULT_MAX_UPLOAD_SIZE_MB * BYTES_PER_MIB

# ---------------------------------------------------------------------------
# Worker / jobs
# ---------------------------------------------------------------------------
DEFAULT_JOB_CONCURRENCY: int = 2
DEFAULT_JOB_POLL_INTERVAL_SECONDS: int = 2

# ---------------------------------------------------------------------------
# Security / auth placeholders
# ---------------------------------------------------------------------------
DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
MIN_SECRET_KEY_LENGTH: int = 32
MASKED_SECRET_PLACEHOLDER: str = "********"

# ---------------------------------------------------------------------------
# Time / formatting
# ---------------------------------------------------------------------------
UTC_TZ_NAME: str = "UTC"
TIMESTAMP_ISO8601_FORMAT: str = "%Y-%m-%dT%H:%M:%S.%fZ"

# ---------------------------------------------------------------------------
# Generic messages
# ---------------------------------------------------------------------------
MSG_HEALTH_OK: str = "ok"
MSG_NOT_IMPLEMENTED: str = "Not implemented yet."
