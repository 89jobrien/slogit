# Slogit: A Simple, Structured Logging Library for Python

Slogit is a logging library for Python that makes structured, configurable logging simple and intuitive.

## Features

- Structured JSON Logging: Automatically formats logs into JSON lines (`.jsonl`), perfect for log aggregation services like Datadog, Splunk, or the ELK stack.
- Colored Console Output: Provides level-differentiated, human-readable logs in the console during development.
- Configuration as Code: Uses Pydantic models for a type-safe, validated, and easily-serializable configuration.
- Log Rotation: Built-in support for `RotatingFileHandler` to manage log file size and backups automatically.
- Modern Tooling: Developed with `uv` for dependency management and `ruff` for formatting and linting, ensuring high code quality.
- Extensible: Simple, class-based design that's easy to extend with custom formatters or handlers.

## Installation

This project uses `uv` for package and environment management.

### PyPI

`slogit` is available on PyPI. To install it in your project, run:

```bash
uv add slogit
```

### GitHub

Or clone the `slogit` repository from github:

```bash
git clone https://github.com/89jobrien/slogit
cd slogit
```

```bash
uv venv
uv sync
```

This will install all necessary dependencies listed in `pyproject.toml`.

## Quick Start

Using slogit is designed to be as simple as possible. Instantiate the `StructuredLogger`, and you're ready to go.

```python
# main.py
from slogit import StructuredLogger

# 1. Instantiate the logger. That's it!
slog = StructuredLogger(name="my_awesome_app")

# 2. Log messages with the clean, direct API!
slog.info("Application starting up.")
slog.debug("Connecting to the database at host: 'localhost'.")
slog.success("Database connection established successfully!")
slog.warning("API key is not set; using a default value.")

try:
    1 / 0
except ZeroDivisionError:
    slog.error("A critical error occurred while processing a request!")

# You can even call the logger instance directly for a quick info log:
slog("This is a shortcut for an info log.")
```

The code above would produce a clean, readable console output like this:

![](data/terminal-output1.jpg)

To see the exception, use `exc_info=True':

```python
try:
    1 / 0
except ZeroDivisionError:
    slog.error("A critical error occurred while processing a request!", exc_info=True)
```

## Super Quick Start

I made the  `slogger` to make things even simpler:

```python
from slogit import slogger
slogger("Hello, World! I'm super easy!")
```

```text
ℹ️ INFO     | your_app.your_module:<module>:22 - Hello, World! I'm super easy!
```

## Configuration

For more control, you can pass a `LogConfig` object during instantiation. This allows you to change log levels, file paths, formats, and more.

```python
from pathlib import Path
from slogit import StructuredLogger, LogConfig, ConsoleConfig, FileConfig

# Create a custom configuration for a production environment
custom_config = LogConfig(
    level="INFO",  # Set the root level to INFO
    console=ConsoleConfig(level="INFO", format="text"), # Use plain text in console
    file=FileConfig(
        enabled=True,
        level="INFO",
        path=Path("logs/your_app.jsonl"), # Log to a specific file path
    )
)
slog = StructuredLogger(name="my_awesome_app", config=custom_config)


def main():
    slog.info("This is an INFO message.")
if __name__ == "__main__":
    main()

```

Output in `logs/your_app.jsonl`:

```json
{"timestamp":"2025-07-06T04:36:49.884610Z","level":" INFO","message":"This is an INFO message.","logger_name":"prod_app","pathname":"/path/to/your/prod_app/main.py","line":20,"function":"main","exception":null,"stack_info":null,"extra":{}}
```

Formatted JSON:

```json
{
  "timestamp": "2025-07-06T04:36:49.884610Z",
  "level": " INFO",
  "message": "This is an INFO message.",
  "logger_name": "prod_app",
  "pathname": "path/to/prod_app/main.py",
  "line": 20,
  "function": "main",
  "exception": null,
  "stack_info": null,
  "extra": {}
}
```

### Loading from a File

You can also manage configurations in a file, which is ideal for different environments (dev, staging, prod).

#### 1. Create a config.json file

```json
{
  "level": "DEBUG",
  "console": {
    "enabled": true,
    "level": "INFO",
    "format": "color" // or "text"
  },
  "file": {
    "enabled": true,
    "path": "path/to/logs/app.jsonl",
    "level": "DEBUG",
    "format": "json",
    "max_bytes": 10485760,
    "backup_count": 5
  }
}
```

#### 2. Load it in your application

```python
from slogit import StructuredLogger, LogConfig

# Load the configuration from the file
config = LogConfig.load("path/to/config.json")

# Initialize the logger with the loaded config
slog = StructuredLogger(name="from_file_app", config=config)

slog("This logger was configured from a file.")
```

## Running Tests

This project uses `pytest` for testing. To run the test suite, execute the following command from the project root:

```bash
uv run pytest
```

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
