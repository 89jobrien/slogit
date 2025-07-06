from .config import ConsoleConfig, FileConfig, LogConfig
from .logger import StructuredLogger

slogger = StructuredLogger()

__all__ = ["StructuredLogger", "LogConfig", "FileConfig", "ConsoleConfig", "slogger"]
