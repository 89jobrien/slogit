import gzip
import json
import logging
import logging.config
import os
import shutil
import sys
from pathlib import Path

from slogit.config import LogConfig
from slogit.constants import DEFAULT_LOG_FORMAT
from slogit.formatters import ColoredFormatter, JSONFormatter


class StructuredLogger:
    """
    An object-oriented wrapper for the standard logging module that simplifies
    configuration and provides utility methods for log management.
    """

    def __init__(self, name: str = __name__, config: LogConfig | None = None):
        """
        Initializes and configures a logger instance.

        Args:
            name: The name of the logger, typically __name__.
            config: A LogConfig object. If None, a default config is used.
        """
        self.name = name
        self.config = config or LogConfig()
        self.logger = logging.getLogger(self.name)
        self._setup_logger()

    def __repr__(self) -> str:
        """Provides an unambiguous string representation for developers."""
        return f"StructuredLogger(name='{self.name}', level='{self.config.level}')"

    def __str__(self) -> str:
        """Provides a user-friendly string representation."""
        return f"StructuredLogger for '{self.name}' writing to {len(self.logger.handlers)} handlers."

    def __getattr__(self, name: str):
        """
        Delegates attribute access to the underlying logger instance.
        This allows calling methods like .info(), .debug(), etc., directly
        on the StructuredLogger instance.

        Example:
            slog = StructuredLogger()
            slog.info("This works!")
            slog.debug("So does this!")
        """
        return getattr(self.logger, name)

    def __call__(self, msg: object, *args, **kwargs):
        """
        Allows the StructuredLogger instance to be called directly as a shortcut
        for logging at the INFO level.

        Example:
            slog = StructuredLogger()
            slog("This is an info message.")
        """
        self.logger.info(msg, *args, **kwargs)

    def _setup_logger(self):
        """Configures the logger using logging.config.dictConfig."""
        # Clear existing handlers from this specific logger to avoid duplication
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        handlers = {}
        formatters = {
            "json": {"()": JSONFormatter},
            "color": {"()": ColoredFormatter, "fmt": DEFAULT_LOG_FORMAT},
            "text": {"()": logging.Formatter, "fmt": DEFAULT_LOG_FORMAT},
        }

        if self.config.console.enabled:
            handlers["console"] = {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": self.config.console.format,
                "level": self.config.console.level.upper(),
            }

        if self.config.file.enabled:
            self.config.file.path.parent.mkdir(parents=True, exist_ok=True)
            handlers["file"] = {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": self.config.file.path,
                "maxBytes": self.config.file.max_bytes,
                "backupCount": self.config.file.backup_count,
                "formatter": self.config.file.format,
                "level": self.config.file.level.upper(),
            }

        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": formatters,
            "handlers": handlers,
            "loggers": {
                self.name: {
                    "level": self.config.level.upper(),
                    "handlers": list(handlers.keys()),
                    "propagate": False,  # Prevents logs from going to the root logger
                }
            },
        }
        logging.config.dictConfig(logging_config)

    def get_logger(self) -> logging.Logger:
        """Returns the underlying standard library logger instance."""
        return self.logger

    def archive_log_file(self):
        """
        Compresses the logger's configured log file with gzip and removes the original.
        """
        log_path = self.config.file.path
        if not self.config.file.enabled or not log_path.exists():
            self.logger.warning(
                f"File logging is disabled or log file not found: {log_path}"
            )
            return

        archive_path = log_path.with_suffix(f"{log_path.suffix}.gz")
        try:
            with open(log_path, "rb") as f_in, gzip.open(archive_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
            os.remove(log_path)
            self.logger.info(f"Archived log file to: {archive_path}")
        except Exception as e:
            self.logger.error(
                f"Failed to archive log file {log_path}: {e}", exc_info=True
            )

    def convert_log_to_json(self, output_path: str | Path):
        """
        Converts the logger's configured JSONL file to a standard JSON array file.
        """
        jsonl_path = self.config.file.path
        if not self.config.file.enabled or self.config.file.format != "json":
            self.logger.warning(
                "File logging must be enabled and in 'json' format to convert."
            )
            return

        if not jsonl_path.exists():
            self.logger.error(f"Source JSONL file not found: {jsonl_path}")
            return

        try:
            records = []
            with open(jsonl_path, "r") as f:
                for line in f:
                    if line.strip():
                        records.append(json.loads(line))

            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(records, f, indent=4)
            self.logger.info(f"Converted {jsonl_path} to {output_path}")
        except Exception as e:
            self.logger.error(f"Failed to convert JSONL file: {e}", exc_info=True)
