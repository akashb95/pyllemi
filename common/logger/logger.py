"""
Utility function for setting up a logger that uses the logging function with a specific format.
"""

import logging  # noqa: LOG001
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

import colorama
from common.logger.notice_level import NOTICE
from common.logger.pretty_formatter import PrettyFormatter


class UpperThresholdFilter(logging.Filter):
    """
    This allows us to set an upper threshold for the log levels since the
    setLevel method only sets a lower one.
    """

    def __init__(self, threshold, *args, **kwargs):
        self._threshold = threshold
        super(UpperThresholdFilter, self).__init__(*args, **kwargs)

    def filter(self, rec):
        return rec.levelno <= self._threshold


def setup_logger(
    name: str,
    formatter: Optional[logging.Formatter] = None,
    filepath: Optional[str] = None,
) -> logging.Logger:
    """

    :param name: Logger name (can be fetched with logging.get_logger(name))
    :param formatter: log message format
    :param filepath: If set, saves log records to this path
    :return: Logger instance
    """

    level_from_env = os.getenv("PYLLEMI_LOG_LEVEL") or NOTICE

    log_fmt = f"{colorama.Style.RESET_ALL}%(asctime)s [%(levelname)s] || %(message)s"

    if formatter is None:
        formatter = PrettyFormatter(log_fmt)

    logger = logging.getLogger(name)
    logger.setLevel(int(level_from_env))

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.addFilter(UpperThresholdFilter(logging.WARNING))
    stdout_handler.setFormatter(formatter)

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.WARNING)
    stderr_handler.setFormatter(formatter)

    # if there are no handlers add both of them otherwise skip.
    if not logger.hasHandlers():
        logger.addHandler(stdout_handler)
        logger.addHandler(stderr_handler)
    logger.propagate = False

    if filepath is not None:
        file_handler = RotatingFileHandler(filepath, maxBytes=1024 * 1024 * 100, backupCount=3)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(log_fmt))
        logger.addHandler(file_handler)

    return logger
