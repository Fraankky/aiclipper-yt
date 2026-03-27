"""Application logging configuration utilities."""

from __future__ import annotations

import logging
import sys

_DEFAULT_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(filename)s:%(lineno)d | %(message)s"
_DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    level: str = "INFO",
    *,
    logger_name: str | None = None,
    fmt: str = _DEFAULT_FORMAT,
    datefmt: str = _DEFAULT_DATE_FORMAT,
) -> logging.Logger:
    """
    Configure and return an application logger.

    This function is safe to call multiple times. It clears existing handlers
    on the target logger to avoid duplicate log lines during reload or tests.
    """
    normalized_level = level.upper().strip()
    numeric_level = getattr(logging, normalized_level, logging.INFO)

    logger = logging.getLogger(logger_name) if logger_name else logging.getLogger()
    logger.setLevel(numeric_level)

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setLevel(numeric_level)
    handler.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))

    # Prevent duplicate handlers if setup is called repeatedly.
    logger.handlers.clear()
    logger.addHandler(handler)

    # If this is a named logger, avoid propagating to root and double output.
    if logger_name:
        logger.propagate = False

    # Also set root level to keep third-party logs consistent.
    logging.getLogger().setLevel(numeric_level)

    logger.debug("Logging initialized", extra={"configured_level": normalized_level})
    return logger
