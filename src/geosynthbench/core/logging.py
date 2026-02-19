from __future__ import annotations

import sys

from loguru import logger

sys.stdout.reconfigure(encoding="utf-8")  # type: ignore


def setup_logging() -> None:
    """
    Configure global logger.
    Call this once at program entrypoints.
    """

    logger.remove()

    logger.add(
        sys.stdout,
        level="INFO",
        format=(
            "<green>{time:HH:mm:ss}</green> | "
            "<level>{level}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> "
            "- {message}"
        ),
        colorize=True,
    )


def get_logger():
    return logger
