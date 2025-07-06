from pathlib import Path

import pytest

# Assuming your project structure is `slogit/`
from slogit.config import ConsoleConfig, FileConfig, LogConfig
from slogit.logger import StructuredLogger


@pytest.fixture
def tmp_log_dir(tmp_path: Path) -> Path:
    """
    A pytest fixture that creates a temporary 'logs' directory for testing.

    This fixture is automatically discovered by pytest and can be used by any
    test function by including it as an argument.

    Args:
        tmp_path: A built-in pytest fixture that provides a temporary directory
                  unique to the test function invocation.

    Returns:
        The path to the created 'logs' subdirectory.
    """
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    return log_dir


@pytest.fixture
def default_log_config(tmp_log_dir: Path) -> LogConfig:
    """
    Provides a default LogConfig instance with the file path pointed to a
    temporary directory.
    """
    return LogConfig(file=FileConfig(path=tmp_log_dir / "default.log"))


@pytest.fixture
def json_file_config(tmp_log_dir: Path) -> LogConfig:
    """
    Provides a LogConfig specifically for testing JSON file output,
    with console logging disabled.
    """
    return LogConfig(
        level="DEBUG",
        console=ConsoleConfig(enabled=False),
        file=FileConfig(path=tmp_log_dir / "test.jsonl", level="DEBUG", format="json"),
    )


@pytest.fixture
def configured_logger(default_log_config: LogConfig) -> StructuredLogger:
    """
    Provides a fully initialized StructuredLogger instance using the
    default_log_config fixture.
    """
    # Using a unique name prevents interference between tests
    logger_name = f"test_logger_{id(default_log_config)}"
    return StructuredLogger(name=logger_name, config=default_log_config)
