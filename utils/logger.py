# utils/logger.py

import logging
import os
from logging.handlers import RotatingFileHandler

def ensure_log_file(log_file):
    """Ensure that the log file and its directory exist."""
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    if not os.path.exists(log_file):
        open(log_file, 'a').close()

def setup_logger(name, log_file, level=logging.DEBUG, console_level=logging.INFO):
    """To setup as many loggers as you want"""
    ensure_log_file(log_file)
    
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    
    # File handler
    file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(console_level)

    # Logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
