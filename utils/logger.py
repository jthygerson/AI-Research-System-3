# utils/logger.py

import logging
import os

def setup_logger(name, log_file, level=logging.INFO):
    """
    Sets up a logger with the specified name and log file.
    """
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    # Create a directory for logs if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Create a file handler
    handler = logging.FileHandler(log_file, mode='a')
    handler.setFormatter(formatter)

    # Get or create the logger
    logger = logging.getLogger(name)

    # Prevent duplication of log entries
    if not logger.handlers:
        logger.setLevel(level)
        logger.addHandler(handler)

    return logger
