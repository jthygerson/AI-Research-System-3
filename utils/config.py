# utils/config.py

import os
import logging
from openai import OpenAI
from .logger import setup_logger  # Add this import

# Setup a logger for config
logger = setup_logger('config', 'logs/config.log', level=logging.DEBUG)

def initialize_openai():
    """
    Initializes the OpenAI API key from environment variables.

    Raises:
        ValueError: If the OPENAI_API_KEY environment variable is not set.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    client = OpenAI(api_key=api_key)
    logger.info("OpenAI client initialized successfully")
    return client

# Add more configuration options as needed
MODEL_TEMPERATURE = float(os.getenv('MODEL_TEMPERATURE', 0.7))
MAX_TOKENS = int(os.getenv('MAX_TOKENS', 3500))
