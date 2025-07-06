import gzip
import json
import logging
from pathlib import Path

import pytest

from slogit.config import (
    ConsoleConfig,
    FileConfig,
    LogConfig,
)
from slogit.logger import StructuredLogger


@pytest.fixture
def tmp_log_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for logs."""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    return log_dir


def test_log_config_defaults():
    """Test that LogConfig initializes with default values."""
    config = LogConfig()
    assert config.level == "DEBUG"
    assert config.console.enabled is True
    assert config.console.level == "INFO"
    assert config.file.enabled is True
    assert config.file.level == "DEBUG"


def test_log_config_validation_invalid_level():
    """Test that LogConfig raises an error for an invalid log level."""
    with pytest.raises(ValueError, match=r"Invalid log level: JUNK"):
        LogConfig(level="JUNK")

    with pytest.raises(ValueError, match=r"Invalid log level: FANCY"):
        LogConfig(console=ConsoleConfig(level="FANCY"))


def test_log_config_load_from_file(tmp_path: Path):
    """Test loading a valid configuration from a JSON file."""
    config_path = tmp_path / "config.json"
    config_data = {
        "level": "INFO",
        "console": {"level": "WARNING"},
        "file": {"path": str(tmp_path / "test.log"), "format": "text"},
    }
    config_path.write_text(json.dumps(config_data))

    config = LogConfig.load(config_path)
    assert config.level == "INFO"
    assert config.console.level == "WARNING"
    assert config.file.path == tmp_path / "test.log"
    assert config.file.format == "text"


def test_logger_initialization(tmp_log_dir: Path):
    """Test that the logger is initialized correctly based on config."""
    log_path = tmp_log_dir / "init_test.log"
    config = LogConfig(file=FileConfig(path=log_path))

    logger_wrapper = StructuredLogger(name="init_logger", config=config)
    logger = logger_wrapper.get_logger()

    assert logger.name == "init_logger"
    assert logger.level == logging.DEBUG  # Set by the config's root level
    assert len(logger.handlers) == 2  # Console and File
    assert not logger.propagate


def test_console_logging_color(capsys):
    """Test that colored text is output to the console."""
    config = LogConfig(console=ConsoleConfig(level="INFO", format="color"))
    logger_wrapper = StructuredLogger(name="console_color_logger", config=config)
    log = logger_wrapper.get_logger()

    log.info("This is an info message.")
    log.error("This is an error message.")

    captured = capsys.readouterr()
    # Check for ANSI escape codes for color
    assert "\x1b[" in captured.out
    assert "This is an info message." in captured.out
    assert "This is an error message." in captured.out


def test_file_logging_json(tmp_log_dir: Path):
    """Test that logs are written to a file in JSONL format."""
    log_path = tmp_log_dir / "test.jsonl"
    config = LogConfig(
        level="DEBUG",
        console=ConsoleConfig(enabled=False),
        file=FileConfig(path=log_path, level="DEBUG", format="json"),
    )
    logger_wrapper = StructuredLogger(name="json_file_logger", config=config)
    log = logger_wrapper.get_logger()

    log.info("JSON message", extra={"user_id": 123})
    log.warning("Something might be wrong.")

    assert log_path.exists()
    lines = log_path.read_text().strip().split("\n")
    assert len(lines) == 2

    log1 = json.loads(lines[0])
    assert log1["level"] == "INFO"
    assert log1["message"] == "JSON message"
    assert log1["logger_name"] == "json_file_logger"
    assert log1["extra"] == {"user_id": 123}

    log2 = json.loads(lines[1])
    assert log2["level"] == "WARNING"
    assert log2["message"] == "Something might be wrong."


def test_log_file_archiving(tmp_log_dir: Path):
    """Test the archive_log_file method."""
    log_path = tmp_log_dir / "archive_me.log"
    log_path.write_text("some log data\n" * 10)

    config = LogConfig(file=FileConfig(path=log_path))
    logger_wrapper = StructuredLogger(name="archiver", config=config)

    logger_wrapper.archive_log_file()

    archive_path = log_path.with_suffix(".log.gz")
    assert not log_path.exists()
    assert archive_path.exists()

    with gzip.open(archive_path, "rt") as f:
        content = f.read()
        assert content == "some log data\n" * 10


def test_convert_log_to_json(tmp_log_dir: Path):
    """Test the convert_log_to_json method."""
    jsonl_path = tmp_log_dir / "source.jsonl"
    output_path = tmp_log_dir / "output.json"

    # Create a sample JSONL file
    with open(jsonl_path, "w") as f:
        f.write('{"msg": "line 1"}\n')
        f.write('{"msg": "line 2"}\n')

    config = LogConfig(file=FileConfig(path=jsonl_path, format="json"))
    logger_wrapper = StructuredLogger(name="converter", config=config)

    logger_wrapper.convert_log_to_json(output_path)

    assert output_path.exists()
    with open(output_path, "r") as f:
        data = json.load(f)

    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["msg"] == "line 1"
    assert data[1]["msg"] == "line 2"


def test_multiple_loggers_no_interference(tmp_log_dir: Path, capsys):
    """Test that two StructuredLogger instances do not interfere."""
    # Logger 1: High-level, console only
    config1 = LogConfig(level="WARNING", file=FileConfig(enabled=False))
    logger1_wrapper = StructuredLogger(name="logger_one", config=config1)
    log1 = logger1_wrapper.get_logger()

    # Logger 2: Low-level, file only
    log_path2 = tmp_log_dir / "logger2.log"
    config2 = LogConfig(
        level="DEBUG",
        console=ConsoleConfig(enabled=False),
        file=FileConfig(path=log_path2),
    )
    logger2_wrapper = StructuredLogger(name="logger_two", config=config2)
    log2 = logger2_wrapper.get_logger()

    # Log messages
    log1.info("This should not appear anywhere.")
    log1.warning("Warning from logger one.")
    log2.debug("Debug from logger two.")

    # Check console output
    captured = capsys.readouterr()
    assert "Warning from logger one." in captured.out
    assert "This should not appear anywhere." not in captured.out
    assert "Debug from logger two." not in captured.out

    # Check file output
    assert log_path2.exists()
    file_content = log_path2.read_text()
    assert "Debug from logger two." in file_content
    assert "Warning from logger one." not in file_content
