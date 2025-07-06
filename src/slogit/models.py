from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class LogEntry(BaseModel):
    """
    Pydantic model for a structured JSON log entry.
    Using a Pydantic model ensures a consistent, validated schema for logs.
    """

    timestamp: datetime = Field(..., description="Timestamp of the log event.")
    level: str = Field(..., description="Log level (e.g., INFO, ERROR).")
    message: str = Field(..., description="The logged message.")
    logger_name: str = Field(..., description="Name of the logger.")
    pathname: str = Field(..., description="File path where the log was triggered.")
    line: int = Field(..., description="Line number in the file.")
    function: str = Field(..., description="Function name where the log was triggered.")
    exception: str | None = Field(default=None, description="Formatted exception info.")
    stack_info: str | None = Field(default=None, description="Formatted stack trace.")
    extra: dict[str, Any] = Field(
        default_factory=dict, description="Extra context data."
    )
