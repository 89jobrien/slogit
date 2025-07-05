# Slogger: A Simple, Structured Logging Library for Python

Slogger is a logging library for Python that makes structured, configurable logging simple and intuitive.

## Features

- Structured JSON Logging: Automatically formats logs into JSON lines (`.jsonl`), perfect for log aggregation services like Datadog, Splunk, or the ELK stack.
- Colored Console Output: Provides level-differentiated, human-readable logs in the console during development.
- Configuration as Code: Uses Pydantic models for a type-safe, validated, and easily-serializable configuration.
- Log Rotation: Built-in support for `RotatingFileHandler` to manage log file size and backups automatically.
- Modern Tooling: Developed with `uv` for dependency management and `ruff` for formatting and linting, ensuring high code quality.
- Extensible: Simple, class-based design that's easy to extend with custom formatters or handlers.

## Installation

This project uses `uv` for package and environment management.

1. Clone the repository

```bash
git clone https://github.com/89jobrien/slogger
cd slogger
```

2. Create a virtual environment and install dependencies:

```bash
uv venv
uv sync
```

This will install all necessary dependencies listed in pyproject.toml.

## Quick Start

Using slogger is designed to be straightforward.
Instantiate the StructuredLogger with a name and an optional configuration, and then use the standard logging interface.

```python
# main.py
from pathlib import Path
from slogger import StructuredLogger, LogConfig, ConsoleConfig, FileConfig

# 1. Define a configuration (or use the default)
my_config = LogConfig(
    level="DEBUG",
    console=ConsoleConfig(level="INFO", format="color"),
    file=FileConfig(level="DEBUG", format="json", path=Path("logs/app.jsonl")),
)

# 2. Instantiate the logger
# This sets up all handlers and formatters based on the config
logger_wrapper = StructuredLogger(name="my_app", config=my_config)

## 3. Get the underlying logger instance to use in your application
log = logger_wrapper.get_logger()


## 4. Log messages
log.info("Application starting up.")
log.debug("This is a detailed debug message for the file.")
log.warning("API key is not set, using a default value.")
log.error(
    "Failed to connect to the database.",
    extra={"db_host": "localhost", "port": 5432}
)

try:
    1 / 0
except ZeroDivisionError:
    log.critical("A critical error occurred!", exc_info=True)

print("✅ Logging complete. Check the console and 'logs/app.jsonl'.")
```

## Configuration

Logging behavior is controlled by the `LogConfig` Pydantic model. You can configure it programmatically (as above) or by loading it from a JSON file.

### Programmatic Configuration

Create an instance of `LogConfig` and pass it to the `StructuredLogger`.

```python
from slogger import LogConfig, ConsoleConfig, FileConfig

# Disable file logging and only show warnings on the console

prod_config = LogConfig(
    level="WARNING",
    console=ConsoleConfig(level="WARNING", format="text"),
    file=FileConfig(enabled=False)
)
```

### Loading from a File

You can also manage configurations in a file, which is ideal for different environments (dev, staging, prod).

#### 1. Create a config.json file

```json
{
  "level": "INFO",
  "console": {
    "level": "INFO",
    "format": "color"
  },
  "file": {
    "enabled": true,
    "path": "logs/production.jsonl",
    "level": "INFO",
    "format": "json"
  }
}
```

#### 2. Load it in your application

```python
from slogger import StructuredLogger, LogConfig

# Load the configuration from the file

config = LogConfig.load("config.json")

# Initialize the logger with the loaded config

logger_wrapper = StructuredLogger(name="from_file_app", config=config)
log = logger_wrapper.get_logger()

log.info("This logger was configured from a file.")

```

## Running Tests

This project uses `pytest` for testing. To run the test suite, execute the following command from the project root:

```bash
uv run pytest
```

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
