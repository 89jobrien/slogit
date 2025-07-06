import logging
from datetime import datetime, timezone

import colorama

from slogit.models import LogEntry

# Initialize colorama
colorama.init(autoreset=True)

LEVEL_COLORS = {
    logging.DEBUG: colorama.Fore.CYAN,
    logging.INFO: colorama.Fore.GREEN,
    logging.WARNING: colorama.Fore.YELLOW,
    logging.ERROR: colorama.Fore.RED,
    logging.CRITICAL: colorama.Fore.MAGENTA,
}


class ColoredFormatter(logging.Formatter):
    """A logging formatter that adds color to log messages based on their level."""

    def __init__(self, fmt: str | None = None, datefmt: str | None = None, **kwargs):
        super().__init__(fmt=fmt, datefmt=datefmt)

    def __repr__(self) -> str:
        """Provides an unambiguous string representation for developers."""
        return f"ColoredFormatter(fmt='{self._fmt}', datefmt='{self.datefmt}')"

    def format(self, record: logging.LogRecord) -> str:
        """Applies level-specific color to the entire log message."""
        color = LEVEL_COLORS.get(record.levelno, colorama.Fore.WHITE)
        if record.levelname == "WARNING":
            record.levelname = "WARN"  # Alias for brevity
        message = super().format(record)
        return f"{color}{message}{colorama.Style.RESET_ALL}"


class JSONFormatter(logging.Formatter):
    """Formats log records into a JSON string using a Pydantic model."""

    def __repr__(self) -> str:
        """Provides an unambiguous string representation for developers."""
        return "JSONFormatter(schema=LogEntry)"

    def format(self, record: logging.LogRecord) -> str:
        """Formats a log record into a JSON string."""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger_name": record.name,
            "pathname": record.pathname,
            "line": record.lineno,
            "function": record.funcName,
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        if record.stack_info:
            log_data["stack_info"] = self.formatStack(record.stack_info)

        standard_attrs = set(vars(logging.LogRecord("", 0, "", 0, "", (), None, None)))
        extra_data = {
            key: value
            for key, value in vars(record).items()
            if key not in standard_attrs
        }
        if extra_data:
            log_data["extra"] = extra_data

        log_entry = LogEntry(**log_data)
        return log_entry.model_dump_json()
