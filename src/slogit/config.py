import json
import logging
import logging.config
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class FileConfig(BaseModel):
    """Configuration for file-based logging."""

    enabled: bool = True
    path: Path = Field(
        default=Path("logs/app.log"), description="Path to the log file."
    )
    level: str = "DEBUG"
    format: Literal["json", "text"] = "json"
    max_bytes: int = Field(
        default=10 * 1024 * 1024,  # 10 MB
        description="Maximum log file size before rotation.",
    )
    backup_count: int = Field(
        default=5, description="Number of backup log files to keep."
    )


class ConsoleConfig(BaseModel):
    """Configuration for console (stdout) logging."""

    enabled: bool = True
    level: str = "INFO"
    format: Literal["color", "json", "text"] = "color"


class LogConfig(BaseModel):
    """
    Master configuration for the logger, validated by Pydantic.
    Provides a single source of truth for all logging settings.
    """

    level: str = Field(default="DEBUG")
    console: ConsoleConfig = Field(default_factory=ConsoleConfig)
    file: FileConfig = Field(default_factory=FileConfig)

    @field_validator("level", "file", "console", mode="before")
    def validate_levels(cls, value):
        """Validates that log levels are correct."""
        if isinstance(value, str):
            if value.upper() not in logging._nameToLevel:
                raise ValueError(f"Invalid log level: {value}")
        elif isinstance(value, (FileConfig, ConsoleConfig)):
            if value.level.upper() not in logging._nameToLevel:
                raise ValueError(f"Invalid log level: {value.level}")
        return value

    @classmethod
    def load(cls, path: str | Path) -> "LogConfig":
        """Loads configuration from a JSON file."""
        with open(path, "r") as f:
            config_data = json.load(f)
        return cls(**config_data)


# import logging

# from pydantic import BaseModel, Field, field_validator


# class LogConfig(BaseModel):
#     """Configuration for the structured logger."""

#     log_file: str = Field(default="app_log.jsonl")
#     level: str = Field(default=logging.INFO)
#     use_color: bool = Field(default=True)
#     use_json: bool = Field(default=False)

#     @field_validator("log_file")
#     def validate_log_file(cls, v):
#         if not v.endswith(".jsonl"):
#             raise ValueError("Log file must have a .jsonl extension")
#         return v

#     @field_validator("level")
#     def validate_level(cls, v):
#         if v not in [
#             "debug",
#             "info",
#             "warn",
#             "warning",
#             "error",
#             "critical",
#         ]:
#             raise ValueError("Invalid logging level")
#         return v
