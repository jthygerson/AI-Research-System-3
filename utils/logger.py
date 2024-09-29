# utils/logger.py

import logging
import os
from logging.handlers import RotatingFileHandler

def ensure_log_file(log_file):
    """Ensure that the log file and its directory exist."""
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    if not os.path.exists(log_file):
        open(log_file, 'a').close()

def setup_logger(name, log_file, level=logging.INFO, console_level=logging.WARNING, log_rotation=False):
    """Set up a logger with file and console handlers."""
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Create a custom logger
    logger = logging.getLogger(name)
    logger.setLevel(level)  # Set logger to level specified

    # Create handlers
    if log_rotation:
        file_handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=5)  # 1MB per file, keep 5 backups
    else:
        file_handler = logging.FileHandler(log_file)
    
    file_handler.setLevel(level)  # Set file handler to level specified
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)  # Keep console level as specified (default INFO)
    console_handler.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)

    return logger
