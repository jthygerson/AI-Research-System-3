# utils/logger.py

import logging
import os

def ensure_log_file(log_file):
    """Ensure that the log file and its directory exist."""
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    if not os.path.exists(log_file):
        open(log_file, 'a').close()

def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""
    logger = logging.getLogger(name)
    if not logger.handlers:  # Only add handler if it doesn't already exist
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        logger.setLevel(level)
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger
