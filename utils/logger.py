# utils/logger.py

import logging
import os

def ensure_log_file(log_file):
    """Ensure that the log file and its directory exist."""
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    if not os.path.exists(log_file):
        open(log_file, 'a').close()

def setup_logger(name, log_file, level=logging.INFO, console_level=logging.INFO):
    """Set up a logger with file and console handlers."""
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Create a custom logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create handlers
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)

    # Create formatters and add it to handlers
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)
    console_handler.setFormatter(console_format)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
