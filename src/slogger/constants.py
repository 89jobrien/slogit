import logging

LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warn": logging.WARNING,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}

DEFAULT_LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s - %(funcName)s:%(lineno)d | %(message)s"
)

