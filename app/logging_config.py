"""Structured logging configuration with automatic secrets redaction."""

import logging
import re
import sys
from app.config import settings

# Regex patterns to detect and mask secrets in log messages
SECRET_PATTERNS = [
    re.compile(r"(access_token=)[^&\s'\"]+", re.IGNORECASE),
    re.compile(r"(Bearer\s+)[a-zA-Z0-9_\-\.]+", re.IGNORECASE),
    re.compile(r"(AIza[0-9A-Za-z-_]{35})", re.IGNORECASE),
    re.compile(r"(api[-_]?key['\":\s=]+)[a-zA-Z0-9_\-]+", re.IGNORECASE),
    re.compile(r"(secret['\":\s=]+)[a-zA-Z0-9_\-]+", re.IGNORECASE),
]


class SecretRedactingFormatter(logging.Formatter):
    """Custom formatter that automatically scrubs sensitive credentials from logs."""

    def format(self, record: logging.LogRecord) -> str:
        original = super().format(record)
        redacted = original
        for pattern in SECRET_PATTERNS:
            redacted = pattern.sub(r"\1[REDACTED]", redacted)
        return redacted


def setup_logging() -> logging.Logger:
    """Configure root and application loggers."""
    log_file = settings.log_file_path
    log_file.parent.mkdir(parents=True, exist_ok=True)

    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Format: [2026-09-15 12:00:00] [INFO] [app.module]: Message
    log_format = "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    formatter = SecretRedactingFormatter(fmt=log_format, datefmt=date_format)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Avoid duplicate handlers if setup_logging is called multiple times
    if not root_logger.handlers:
        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        # File Handler (append mode)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    logger = logging.getLogger("studynotes")
    logger.setLevel(level)
    return logger


logger = setup_logging()
