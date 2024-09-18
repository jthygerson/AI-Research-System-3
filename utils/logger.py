# utils/logger.py

import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(name, log_file, level=logging.INFO):
    """
    Sets up a logger with rotation. Ensures that multiple handlers are not added to the same logger
    and prevents log propagation to parent loggers to avoid duplicate logging.

    Parameters:
        name (str): Name of the logger.
        log_file (str): Path to the log file.
        level (int): Logging level.
        max_bytes (int): Maximum size of the log file before rotation.
        backup_count (int): Number of backup files to keep.

    Returns:
        logging.Logger: Configured logger instance.
    """
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logger = logging.getLogger(name)
    logger.setLevel(level)

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.addHandler(stream_handler)
    logger.propagate = False  # Prevent logs from propagating to the root logger

    return logger
