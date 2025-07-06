from dataclasses import dataclass


@dataclass(frozen=True)
class Level:
    """Represents a logging level with metadata."""

    name: str
    no: int
    color: str
    icon: str


LEVELS = [
    Level(name="TRACE ", no=5, color="<cyan>", icon="➤"),
    Level(name="DEBUG", no=10, color="<blue>", icon="🐞"),
    Level(name="INFO", no=20, color="<bold>", icon="ℹ️"),
    Level(name="SUCCESS", no=25, color="<green>", icon="✅"),
    Level(name="WARNING ", no=30, color="<yellow>", icon="⚠️"),
    Level(name="ERROR", no=40, color="<red>", icon="❌"),
    Level(name="CRITICAL", no=50, color="<RED><bold>", icon="💀"),
]

LEVEL_MAP = {level.no: level for level in LEVELS}
