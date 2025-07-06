import json
from pathlib import Path

from pydantic import BaseModel


class ConsoleConfig(BaseModel):
    """Configuration for console (stdout) logging."""

    enabled: bool = True
    level: str = "INFO"
    format: str = "color"


class FileConfig(BaseModel):
    """Configuration for file-based logging."""

    enabled: bool = True
    path: Path = Path("logs/app.log")
    level: str = "DEBUG"
    format: str = "json"
    max_bytes: int = 10 * 1024 * 1024
    backup_count: int = 5


class LogConfig(BaseModel):
    """Master configuration for the logger."""

    level: str = "DEBUG"
    console: ConsoleConfig = ConsoleConfig()
    file: FileConfig = FileConfig()

    @classmethod
    def load(cls, path: str | Path) -> "LogConfig":
        """Loads configuration from a JSON file."""
        with open(path, "r") as f:
            config_data = json.load(f)
        return cls(**config_data)

    # TODO: Finish field validator

    # @field_validator("level", "file", "console", mode="before")
    # def validate_levels(cls, value):
    #     """Validates that log levels are correct."""
    #     if isinstance(value, str):
    #         if value.upper() not in logging._nameToLevel:
    #             raise ValueError(f"Invalid log level: {value}")
    #     elif isinstance(value, (FileConfig, ConsoleConfig)):
    #         if value.level.upper() not in logging._nameToLevel:
    #             raise ValueError(f"Invalid log level: {value.level}")
    #     return value
