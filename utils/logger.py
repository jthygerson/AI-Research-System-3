# utils/logger.py

import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(name, log_file, level=logging.INFO, max_bytes=5*1024*1024, backup_count=5):
    """
    Sets up a logger with rotation.
    
    Parameters:
        name (str): Name of the logger.
        log_file (str): Path to the log file.
        level (int): Logging level.
        max_bytes (int): Maximum size in bytes before rotation.
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

    # Check if the logger already has handlers to prevent duplication
    if not logger.handlers:
        handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger
