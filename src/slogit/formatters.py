import json
import logging

import colorama

from slogit.levels import LEVEL_MAP

# Initialize colorama
colorama.init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """A logging formatter that adds color and icons based on custom Level objects."""

    def __init__(
        self,
        **kwargs,
    ):
        """
        Initializes the formatter, passing the style to the parent class.
        """
        # Pass the style parameter to the superclass constructor
        super().__init__(**kwargs)
        self.color_map = {
            "<cyan>": "\033[36m",
            "<blue>": "\033[34m",
            "<green>": "\033[32m",
            "<yellow>": "\033[33m",
            "<red>": "\033[31m",
            "<RED>": "\033[91m",
            "<bold>": "\033[1m",
            "<white>": "\033[37m",
        }
        self.reset = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        """Applies level-specific color and icon to the log message."""
        level_info = LEVEL_MAP.get(record.levelno)
        if level_info:
            color_tag = level_info.color
            color_start = ""
            for tag, code in self.color_map.items():
                if tag in color_tag:
                    color_start += code

            log_msg = super().format(record)

            return f"{level_info.icon} {color_start}{log_msg}{self.reset}"

        return super().format(record)


class JSONFormatter(logging.Formatter):
    """Formats log records into a JSON string using a Pydantic model."""

    def __init__(self, **kwargs):
        """
        Initializes the formatter by passing all keyword arguments from the
        logging configuration directly to the parent class.
        """
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        """Provides an unambiguous string representation for developers."""
        return "JSONFormatter(schema=LogEntry)"

    def format(self, record: logging.LogRecord) -> str:
        """Formats a log record into a JSON string."""
        # Define the set of standard LogRecord attributes
        standard_attrs = {
            "args",
            "created",
            "exc_info",
            "exc_text",
            "filename",
            "funcName",
            "levelname",
            "levelno",
            "lineno",
            "message",
            "module",
            "msecs",
            "msg",
            "name",
            "pathname",
            "process",
            "processName",
            "relativeCreated",
            "stack_info",
            "thread",
            "threadName",
        }
        log_entry = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger_name": record.name,
            "function": record.funcName,
            "line": record.lineno,
        }

        extra_data = {
            key: value
            for key, value in record.__dict__.items()
            if key not in standard_attrs
        }
        if extra_data:
            log_entry["extra"] = extra_data

        # 3. Handle exception info separately
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)
