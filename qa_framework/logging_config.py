"""Request/response logging with credential redaction."""

from __future__ import annotations

import logging
from pathlib import Path

from .helpers import redact

LOGGER_NAME = "api_automation"
_LOG_FILE = Path("reports/api_test.log")


class RedactingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, dict):
            record.msg = redact(record.msg)
        return True


def configure_logging(log_file: Path = _LOG_FILE) -> logging.Logger:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    handler.addFilter(RedactingFilter())
    logger.addHandler(handler)
    logger.propagate = False
    return logger


logger = logging.getLogger(LOGGER_NAME)
