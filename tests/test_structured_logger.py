import gzip
import json
import logging
from pathlib import Path

# Assuming your project structure is `slogit/`
from slogit.config import ConsoleConfig, FileConfig, LogConfig
from slogit.levels import LEVEL_MAP
from slogit.logger import StructuredLogger


def test_log_config_defaults():
    """Test that LogConfig initializes with default values."""
    config = LogConfig()
    assert config.level == "DEBUG"
    assert config.console.enabled is True
    assert config.console.level == "INFO"
    assert config.file.enabled is True
    assert config.file.level == "DEBUG"


def test_logger_initialization(configured_logger: StructuredLogger):
    """Test that the logger is initialized correctly using a fixture."""
    assert "test_logger" in configured_logger.name
    # The logger attribute is still the underlying logging.Logger
    assert configured_logger.logger.level == logging.DEBUG
    assert len(configured_logger.logger.handlers) == 2  # Console and File
    assert not configured_logger.logger.propagate


def test_console_logging_with_icons_and_color(capsys):
    """Test that colored text and icons are output to the console."""
    # This test creates its own logger to control the config precisely
    config = LogConfig(console=ConsoleConfig(level="INFO", format="color"))
    slog = StructuredLogger(name="console_icon_logger", config=config)

    slog.info("This is an info message.")
    slog.error("This is an error message.")

    captured = capsys.readouterr()
    output = captured.out

    # Check for icons from the Level objects
    assert LEVEL_MAP[logging.INFO].icon in output
    assert LEVEL_MAP[logging.ERROR].icon in output

    # Check for message content
    assert "This is an info message." in output
    assert "This is an error message." in output

    # Check for ANSI escape code for color
    assert "\033[" in output


def test_custom_level_methods(tmp_log_dir: Path, capsys):
    """Test that custom level methods like .success() and .trace() work."""
    # This test requires a specific config to capture all levels
    log_path = tmp_log_dir / "custom_levels.jsonl"
    config = LogConfig(
        level="TRACE",
        console=ConsoleConfig(level="TRACE"),
        file=FileConfig(path=log_path, level="TRACE", format="json"),
    )
    slog = StructuredLogger(name="custom_level_logger", config=config)

    # Use the custom methods
    slog.success("Operation was successful.")
    slog.trace("Entering a sensitive function.")

    # --- Verify Console Output ---
    captured = capsys.readouterr()
    console_output = captured.out
    assert LEVEL_MAP[25].icon in console_output  # ✅ for SUCCESS
    assert "Operation was successful" in console_output
    assert LEVEL_MAP[5].icon in console_output  # ➤ for TRACE
    assert "Entering a sensitive function" in console_output

    # --- Verify File Output ---
    assert log_path.exists()
    lines = log_path.read_text().strip().split("\n")
    assert len(lines) == 2

    log1 = json.loads(lines[0])
    assert log1["level"] == "SUCCESS"
    assert log1["message"] == "Operation was successful."

    log2 = json.loads(lines[1])
    assert log2["level"] == "TRACE"
    assert log2["message"] == "Entering a sensitive function."


def test_file_logging_json(json_file_config: LogConfig):
    """Test that logs are written to a file in JSONL format using a fixture."""
    slog = StructuredLogger(name="json_file_logger", config=json_file_config)
    log_path = json_file_config.file.path

    slog.info("JSON message")
    slog.warning("Something might be wrong.")

    assert log_path.exists()
    lines = log_path.read_text().strip().split("\n")
    assert len(lines) == 2

    log1 = json.loads(lines[0])
    assert log1["level"] == "INFO"
    assert log1["message"] == "JSON message"
    assert log1["logger_name"] == "json_file_logger"

    log2 = json.loads(lines[1])
    assert log2["level"] == "WARNING"
    assert log2["message"] == "Something might be wrong."


def test_multiple_loggers_no_interference(tmp_log_dir: Path, capsys):
    """Test that two StructuredLogger instances do not interfere."""
    # This test still requires custom configs, which is fine.
    # Logger 1: High-level, console only
    config1 = LogConfig(level="WARNING", file=FileConfig(enabled=False))
    slog1 = StructuredLogger(name="logger_one", config=config1)

    # Logger 2: Low-level, file only
    log_path2 = tmp_log_dir / "logger2.log"
    config2 = LogConfig(
        level="DEBUG",
        console=ConsoleConfig(enabled=False),
        file=FileConfig(path=log_path2, format="text"),  # Use text for simple assertion
    )
    slog2 = StructuredLogger(name="logger_two", config=config2)

    # Log messages using the direct API
    slog1.info("This should not appear anywhere.")
    slog1.warning("Warning from logger one.")
    slog2.debug("Debug from logger two.")

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


def test_log_file_archiving(configured_logger: StructuredLogger):
    """Test the archive_log_file method using a fixture."""
    log_path = configured_logger.config.file.path
    log_path.write_text("some log data\n" * 10)

    configured_logger.archive_log_file()

    archive_path = log_path.with_suffix(".log.gz")
    assert not log_path.exists()
    assert archive_path.exists()

    with gzip.open(archive_path, "rt") as f:
        content = f.read()
        assert content == "some log data\n" * 10


def test_convert_log_to_json(json_file_config: LogConfig):
    """Test the convert_log_to_json method using a fixture."""
    slog = StructuredLogger(name="converter", config=json_file_config)
    jsonl_path = json_file_config.file.path
    output_path = jsonl_path.with_suffix(".json")

    # Create a sample JSONL file
    with open(jsonl_path, "w") as f:
        f.write('{"msg": "line 1"}\n')
        f.write('{"msg": "line 2"}\n')

    slog.convert_log_to_json(output_path)

    assert output_path.exists()
    with open(output_path, "r") as f:
        data = json.load(f)

    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["msg"] == "line 1"
    assert data[1]["msg"] == "line 2"
