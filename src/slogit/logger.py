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

    def __init__(self, name: str, config: LogConfig | None = None):
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


# class StructuredLogger:
#     def __init__(
#         self, name: str, config: LogConfig | None = None, config_path: str | None = None
#     ):
#         if config_path:
#             config = self.load_config_from_json(config_path)
#         if config is None:
#             config = LogConfig()

#         self.logger = logging.getLogger(name)
#         self.logger.setLevel(self._get_log_level(config.level))

#         if not self.logger.handlers:
#             if config.use_color:
#                 colorama.init(autoreset=True)

#             log_format = DEFAULT_FORMAT

#             console_handler = logging.StreamHandler()
#             console_handler.setLevel(self._get_log_level(config.level))
#             if config.use_json:
#                 console_handler.setFormatter(JSONFormatter())
#             elif config.use_color:
#                 console_handler.setFormatter(ColoredFormatter(log_format))
#             else:
#                 console_handler.setFormatter(logging.Formatter(log_format))
#             self.logger.addHandler(console_handler)

#             file_handler = RotatingFileHandler(
#                 config.log_file, maxBytes=10 * 1024 * 1024, backupCount=5
#             )
#             file_handler.setLevel(self._get_log_level(config.level))
#             if config.use_json:
#                 file_handler.setFormatter(JSONFormatter())
#             else:
#                 file_handler.setFormatter(logging.Formatter(DEFAULT_FORMAT))
#             self.logger.addHandler(file_handler)

#     def __repr__(self):
#         return f"StructuredLogger(name={self.logger.name}, level={self.logger.level}, handlers={self.logger.handlers}, formatters={self.logger.handlers[0].formatter if self.logger.handlers else 'None'})"

#     def __str__(self):
#         return f"A structured logger named '{self.logger.name}' with level '{self.logger.level}' and {len(self.logger.handlers)} handlers."

#     def __enter__(self):
#         if not self.logger.handlers:
#             self.__init__(self.logger.name, LogConfig())
#         return self

#     def __exit__(self, exc_type, exc_value, traceback):
#         for handler in self.logger.handlers:
#             handler.flush()
#             handler.close()
#         logging.shutdown()

#     def __eq__(self, other):
#         if not isinstance(other, StructuredLogger):
#             return NotImplemented
#         return (
#             self.logger.name == other.logger.name
#             and self.logger.level == other.logger.level
#             and len(self.logger.handlers) == len(other.logger.handlers)
#         )

#     def _get_log_level(self, level: str | int) -> int:
#         """Converts a string log level to a logging module log level."""
#         if isinstance(level, str):
#             level = level.lower()
#             if level in LOG_LEVELS:
#                 return LOG_LEVELS[level]
#             else:
#                 raise ValueError(f"Invalid log level: {level}")
#         return level

#     def set_log_level(self, level: str | int):
#         log_level = self._get_log_level(level)
#         self.logger.setLevel(log_level)
#         for handler in self.logger.handlers:
#             handler.setLevel(log_level)

#     def get_logger(self) -> logging.Logger:
#         return self.logger

#     def log_with_extra(self, level: int, msg: str, **kwargs):
#         """
#         Logs a message with extra key-value pairs for structured logging.

#         Args:
#             level: The logging level (eg. 'info', 'warning').
#             msg: The log message.
#             **kwargs: Arbitrary keyword arguments to be added to the log entry.
#         """
#         # Ensure extra data is nested under 'extra_data'
#         self.logger.log(level, msg, extra={"extra_data": kwargs})

#     @staticmethod
#     def load_config_from_json(json_path: str) -> LogConfig:
#         with open(json_path, "r") as f:
#             config_data = json.load(f)
#         return LogConfig(**config_data)

#     def reload_config(self, config: LogConfig):
#         """Reloads the logger configuration."""
#         self.logger.setLevel(self._get_log_level(config.level))
#         for handler in self.logger.handlers:
#             handler.setLevel(self._get_log_level(config.level))
#             if isinstance(handler.formatter, JSONFormatter) and not config.use_json:
#                 handler.setFormatter(logging.Formatter(DEFAULT_FORMAT))
#             elif not isinstance(handler.formatter, JSONFormatter) and config.use_json:
#                 handler.setFormatter(JSONFormatter())

#     def add_file_handler(self, log_file: str, formatter: logging.Formatter):
#         """Adds a file handler with the specified formatter."""
#         file_handler = RotatingFileHandler(
#             log_file, maxBytes=10 * 1024 * 1024, backupCount=5
#         )
#         file_handler.setLevel(self.logger.level)
#         file_handler.setFormatter(formatter)
#         self.logger.addHandler(file_handler)

#     def add_async_handler(self, handler: logging.Handler):
#         """Wraps a handler to make it asynchronous."""
#         async_handler = AsyncHandler(handler)
#         self.logger.addHandler(async_handler)

#     def archive_logs(self, log_file: str):
#         """Archives the specified log file."""
#         with open(log_file, "rb") as f_in:
#             with gzip.open(f"{log_file}.gz", "wb") as f_out:
#                 shutil.copyfileobj(f_in, f_out)
#         os.remove(log_file)


# def convert_jsonl_to_json(jsonl_file_path: str, json_file_path: str):
#     """
#     Converts a JSONL file to a JSON file.

#     Args:
#         jsonl_file_path: The path to the JSONL file.
#         json_file_path: The path where the JSON file will be saved.
#     """
#     json_array = []

#     with open(jsonl_file_path, "r") as jsonl_file:
#         for line in jsonl_file:
#             json_object = json.loads(line)
#             json_array.append(json_object)

#     with open(json_file_path, "w") as json_file:
#         json.dump(json_array, json_file, indent=4)
