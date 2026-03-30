"""
Video downloader module — download videos from URLs via yt-dlp.

Provides helpers to detect URL inputs and download videos from platforms
like YouTube, TikTok, Instagram, etc.
"""

import re
from pathlib import Path
from typing import Any

import yt_dlp  # type: ignore[import-untyped]
from yt_dlp import DownloadError  # type: ignore[attr-defined]

from app.utils import log

# Default download cache directory
_DEFAULT_DOWNLOAD_DIR = ".cache/ai-video-clipper/downloads"


def _sanitize_filename(name: str) -> str:
    """Sanitize a string to be safe for use as a filename."""
    # Remove or replace invalid characters
    safe = re.sub(r'[<>:"/\\|?*]', "", name)
    # Collapse whitespace and replace with underscores
    safe = re.sub(r"\s+", "_", safe.strip())
    # Trim to reasonable length
    safe = safe[:100]
    # Strip trailing dots/spaces (invalid on Windows)
    safe = safe.rstrip(". ")
    return safe or "video"


def is_url(input_str: str) -> bool:
    """Return True if the input string is an HTTP(S) URL."""
    return input_str.startswith("http://") or input_str.startswith("https://")


def download_video(url: str, output_dir: str | None = None) -> str:
    """Download a video from a URL using yt-dlp.

    Args:
        url: The video URL to download.
        output_dir: Directory to save the downloaded file.
                    Defaults to ``.cache/ai-video-clipper/downloads/``.

    Returns:
        Absolute path to the downloaded .mp4 file.

    Raises:
        ValueError: If the URL is invalid or the video cannot be downloaded.
    """

    out_dir = Path(output_dir) if output_dir else Path(_DEFAULT_DOWNLOAD_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    # First pass: extract info without downloading to get the title
    info_opts: dict[str, Any] = {"quiet": True, "no_warnings": True}
    try:
        with yt_dlp.YoutubeDL(info_opts) as ydl:  # type: ignore[arg-type]
            info = ydl.extract_info(url, download=False)
            if info is None:
                raise ValueError(f"Could not extract video info from URL: {url}")
    except DownloadError as exc:
        raise ValueError(f"Invalid or unsupported URL: {url}\n  {exc}") from exc

    title: str = info.get("title") or "video"
    safe_name = _sanitize_filename(title)
    output_template = str(out_dir / f"{safe_name}.%(ext)s")

    # Check if file already exists (cache hit)
    # yt-dlp may use mkv as container; check common extensions
    for ext in ("mp4", "mkv", "webm"):
        candidate = out_dir / f"{safe_name}.{ext}"
        if candidate.exists():
            log("INFO", f"Using cached download: {candidate}")
            return str(candidate.resolve())

    # Download
    dl_opts: dict[str, Any] = {
        "format": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/"
        "bestvideo[height<=1080]+bestaudio/"
        "best[height<=1080]/best",
        "merge_output_format": "mp4",
        "outtmpl": output_template,
        "quiet": False,
        "no_warnings": False,
        # Progress hook handled by yt-dlp's built-in output
    }

    log("INFO", "Downloading video from URL...")
    try:
        with yt_dlp.YoutubeDL(dl_opts) as ydl:  # type: ignore[arg-type]
            ydl.download([url])
    except DownloadError as exc:
        # Clean up partial files on failure
        for ext in ("mp4", "mkv", "webm", "part"):
            partial = out_dir / f"{safe_name}.{ext}"
            if partial.exists():
                partial.unlink()
        raise ValueError(f"Download failed: {exc}") from exc

    # Find the downloaded file (yt-dlp may change extension)
    for ext in ("mp4", "mkv", "webm"):
        candidate = out_dir / f"{safe_name}.{ext}"
        if candidate.exists():
            log("OK", f"Download complete: {candidate}")
            return str(candidate.resolve())

    raise RuntimeError(f"Download completed but output file not found in {out_dir}")
