# src/emrpy/logging/logger_config.py
"""
Logger Configuration Utilities

Safe, high-level logging setup for scripts and notebooks with support for
colorised console output and optional rotating file handlers.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Union

try:
    # Multi-process-safe rotating handler; falls back if optional extra missing.
    from concurrent_log_handler import ConcurrentRotatingFileHandler as _RFH  # type: ignore
except ModuleNotFoundError:  # pragma: no cover  optional dependency missing
    from logging.handlers import RotatingFileHandler as _RFH  # type: ignore

__all__ = [
    "configure",
    "get_logger",
]

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
DEFAULT_FMT = "%(asctime)s %(levelname)s ▶ %(name)s: %(message)s"
DEFAULT_DATEFMT = "%Y-%m-%d %H:%M:%S"
DEFAULT_LOG_DIR_ENV = "EMRPY_LOG_DIR"


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------


def get_logger(name: str = "emrpy") -> logging.Logger:
    """
    Return a namespaced logger with a NullHandler attached.

    This function ensures safe logger creation without modifying the root logger.
    Ideal for use in libraries or scripts where central configuration is handled separately.

    Parameters:
    -----------
    name : str, default "emrpy"
        The name of the logger to retrieve.

    Returns:
    --------
    logging.Logger
        A logger instance with a NullHandler attached if none exists.

    Examples:
    ---------
    >>> from emrpy.logging import get_logger
    >>> log = get_logger(__name__)
    >>> log.debug("This won't output unless configured.")
    """
    logger = logging.getLogger(name)
    if not any(isinstance(h, logging.NullHandler) for h in logger.handlers):
        logger.addHandler(logging.NullHandler())
    return logger


def _has_handler(logger: logging.Logger, handler_type: type) -> bool:
    """
    Check whether a logger already has a specific type of handler.

    Parameters:
    -----------
    logger : logging.Logger
        Logger instance to inspect.
    handler_type : type
        Type of the handler to search for (e.g., StreamHandler, FileHandler).

    Returns:
    --------
    bool
        True if the logger has at least one handler of the specified type, else False.
    """
    return any(isinstance(h, handler_type) for h in logger.handlers)


def configure(
    name: str = "emrpy",
    *,
    level: int | str = logging.INFO,
    log_dir: Union[str, os.PathLike, None] | None = None,
    filename: str = "emrpy.log",
    rotate_bytes: int = 5_000_000,  # 5 MB (set to 0 to disable file handler)
    backups: int = 3,
    fmt: str = DEFAULT_FMT,
    datefmt: str = DEFAULT_DATEFMT,
    coloured_console: bool = True,
) -> logging.Logger:
    """
    Configure a logger with console and optional rotating file output.

    This function sets up a logger with colorised console output and (optionally)
    a rotating file handler. Safe to call multiple times without duplicating handlers.

    Parameters:
    -----------
    name : str, default "emrpy"
        Logger name to configure.
    level : int or str, default logging.INFO
        Logging level (e.g., "DEBUG", "INFO").
    log_dir : str or Path, optional
        Directory to store log files. Defaults to $EMRPY_LOG_DIR or "logs".
    filename : str, default "emrpy.log"
        Name of the log file (if file logging is enabled).
    rotate_bytes : int, default 5_000_000
        Max file size before rotation (in bytes). Set to 0 to disable file logging.
    backups : int, default 3
        Number of backup files to keep when rotating.
    fmt : str, default DEFAULT_FMT
        Log message format string.
    datefmt : str, default DEFAULT_DATEFMT
        Date format string.
    coloured_console : bool, default True
        Whether to use colorlog for console output.

    Returns:
    --------
    logging.Logger
        Configured logger instance.

    Examples:
    ---------
    >>> # Script with file logging
    >>> configure(level="INFO", log_dir="logs", filename="pipeline.log")

    >>> # Notebook console-only logging
    >>> configure(level="DEBUG", rotate_bytes=0)

    >>> log = get_logger(__name__)
    >>> log.info("Logger ready ✔")
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # -------------------------------------------------------------
    # Prevent duplicate configuration on subsequent calls.
    # -------------------------------------------------------------
    if _has_handler(logger, _RFH if rotate_bytes else logging.StreamHandler):
        return logger

    formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)

    # ---------------------------- console ------------------------
    console = logging.StreamHandler()
    console.setLevel(level)
    if coloured_console:
        try:
            from colorlog import ColoredFormatter  # optional extra

            console.setFormatter(ColoredFormatter("%(log_color)s" + fmt, datefmt))
        except ModuleNotFoundError:
            console.setFormatter(formatter)
    else:
        console.setFormatter(formatter)
    logger.addHandler(console)

    # ---------------------------- file ---------------------------
    if rotate_bytes > 0:
        log_dir_path = Path(log_dir or os.getenv(DEFAULT_LOG_DIR_ENV, "logs")).expanduser()
        log_dir_path.mkdir(parents=True, exist_ok=True)

        file_handler = _RFH(
            filename=str(log_dir_path / filename),
            mode="a",
            maxBytes=rotate_bytes,
            backupCount=backups,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
