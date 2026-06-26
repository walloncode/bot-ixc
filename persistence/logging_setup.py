"""Configuração do Loguru. Logs estruturados em arquivo + console."""
from __future__ import annotations

import sys

from loguru import logger

from config import settings


def setup_logging() -> None:
    logger.remove()
    logger.add(sys.stderr, level="INFO",
               format="<green>{time:HH:mm:ss}</green> | <level>{level: <7}</level> | {message}")
    logger.add(settings.log_path / "agent_{time:YYYY-MM-DD}.log",
               level="DEBUG", rotation="10 MB", retention="30 days", encoding="utf-8")
