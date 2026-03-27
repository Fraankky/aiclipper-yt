from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="AI Clip App", alias="APP_NAME")
    app_env: Literal["development", "staging", "production", "test"] = Field(
        default="development",
        alias="APP_ENV",
    )
    app_debug: bool = Field(default=True, alias="APP_DEBUG")
    app_host: str = Field(default="127.0.0.1", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    app_log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        alias="APP_LOG_LEVEL",
    )

    # API
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")
    cors_allow_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        alias="CORS_ALLOW_ORIGINS",
    )

    # Database
    database_url: str = Field(default="sqlite:///./data/aiclip.db", alias="DATABASE_URL")

    # Storage
    data_dir: str = Field(default="./data", alias="DATA_DIR")
    static_dir: str = Field(default="./static", alias="STATIC_DIR")
    assets_dir: str = Field(default="./static/assets", alias="ASSETS_DIR")

    # AI Provider
    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        alias="OPENROUTER_BASE_URL",
    )
    openrouter_model: str = Field(default="openai/gpt-4o-mini", alias="OPENROUTER_MODEL")

    # Pipeline / Processing
    ffmpeg_bin: str = Field(default="ffmpeg", alias="FFMPEG_BIN")
    ffprobe_bin: str = Field(default="ffprobe", alias="FFPROBE_BIN")
    whisper_model: str = Field(default="base", alias="WHISPER_MODEL")
    max_upload_size_mb: int = Field(default=1024, alias="MAX_UPLOAD_SIZE_MB")

    # Worker / Jobs
    job_concurrency: int = Field(default=2, alias="JOB_CONCURRENCY")
    job_poll_interval_seconds: int = Field(default=2, alias="JOB_POLL_INTERVAL_SECONDS")

    # Security
    secret_key: str = Field(default="change-this-in-production", alias="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()


settings = get_settings()
