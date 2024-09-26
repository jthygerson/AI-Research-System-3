# utils/logger.py

import logging
import os

def ensure_log_file(log_file):
    """Ensure that the log file and its directory exist."""
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    if not os.path.exists(log_file):
        open(log_file, 'a').close()

def setup_logger(name, log_file, level=logging.DEBUG, console_level=logging.INFO):
    """To setup as many loggers as you want"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Capture all levels of logs

    # Console Handler (for INFO and ERROR only)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)

    # File Handler (for INFO and above)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # Detailed File Handler (for DEBUG and above)
    detailed_log_file = log_file.replace('.log', '_detailed.log')
    ensure_log_file(detailed_log_file)
    detailed_file_handler = logging.FileHandler(detailed_log_file)
    detailed_file_handler.setLevel(logging.DEBUG)
    detailed_file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    detailed_file_handler.setFormatter(detailed_file_formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(detailed_file_handler)

    return logger
