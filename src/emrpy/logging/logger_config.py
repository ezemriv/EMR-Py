import logging
from logging.handlers import RotatingFileHandler
import os

def scripts_logger(
    level=logging.INFO,
    log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    date_format="%m/%d/%Y %I:%M:%S %p",
    log_file="logs/logfile.log",
    max_bytes=2 * 1024 * 1024,  # 2MB
    backup_count=1
):
    """
    OPTIONAL in any new project.
    Configures logging for library users in a flexible and modular way.

    Parameters:
        level (str): The logging level to use (e.g., DEBUG, INFO, WARNING, etc.). 
                     Determines the severity of messages to capture.
        log_format (str): A string defining the structure of log messages. For example:
                          "%(asctime)s - %(name)s - %(levelname)s - %(message)s" captures
                          timestamps, logger names, and levels of the messages.
        date_format (str): The format for timestamps in log entries, e.g., 
                           "%m/%d/%Y %I:%M:%S %p" for `MM/DD/YYYY HH:MM:SS AM/PM`.
        log_file (str): The file path where logs will be saved. Defaults to `logs/app.log`.
                        Rotating logs will append extensions like `.1`, `.2`, etc., for backups.
        max_bytes (int): Maximum file size before logs are rotated. Default is 2MB.
        backup_count (int): Number of backup files to retain. For example, a value of 1 keeps
                            the latest rotated log in addition to the current log file.

    Returns:
        None
    """
    
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Retrieve the root logger. This allows the function to configure logging globally
    logger = logging.getLogger()
    logger.setLevel(level)  # Set the severity level for capturing logs.

    # Remove existing handlers to prevent duplication of log messages.
    if logger.hasHandlers():
        logger.handlers.clear()

    # Define a formatter to standardize log message appearance.
    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)

    # Set up a console handler for real-time log output in the terminal or console.
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)  # Apply the same logging level as the root logger.
    console_handler.setFormatter(formatter)  # Attach the formatter to the console handler.

    # Set up a file handler with rotation to manage log file size and backups.
    file_handler = RotatingFileHandler(
        filename=log_file,  # File to write logs to.
        mode="a",           # Open the file in append mode.
        maxBytes=max_bytes, # Rotate when the file exceeds the specified size.
        backupCount=backup_count  # Retain the specified number of backup files.
    )
    file_handler.setLevel(level)  # Apply the same logging level as the root logger.
    file_handler.setFormatter(formatter)  # Attach the formatter to the file handler.

    # Add both handlers to the logger. This ensures logs are written to the console
    # and the file simultaneously.
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

def notebooks_logger(
    level=logging.INFO,
    log_format="%(asctime)s - %(message)s",
    date_format="%H:%M:%S"):
    """
    Configures a simple logger for use in Jupyter notebooks.

    Parameters:
        level (str): The logging level to use (e.g., DEBUG, INFO, WARNING, etc.).
        log_format (str): The simplified structure of log messages.
                          Default: "%(asctime)s - %(message)s" (time and message).
        date_format (str): The format for timestamps in log entries.
                           Default: "%H:%M:%S" for `HH:MM:SS`.

    Returns:
        None
    """
    # Retrieve the root logger
    logger = logging.getLogger()
    logger.setLevel(level)

    # Clear any existing handlers to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    # Define a simple formatter
    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)

    # Set up a console handler for notebook output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    # Add the console handler to the logger
    logger.addHandler(console_handler)
