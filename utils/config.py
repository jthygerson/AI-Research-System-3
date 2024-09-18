# utils/config.py

import os
import logging
from openai import OpenAI

# Setup a logger for config
logger = logging.getLogger('config')
logger.setLevel(logging.DEBUG)  # Set to DEBUG for detailed logging

def initialize_openai():
    """
    Initializes the OpenAI API key from environment variables.

    Raises:
        ValueError: If the OPENAI_API_KEY environment variable is not set.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    OpenAI(api_key=api_key)
    logger.info("OpenAI client initialized successfully")

# Add more configuration options as needed
MODEL_TEMPERATURE = float(os.getenv('MODEL_TEMPERATURE', 0.7))
MAX_TOKENS = int(os.getenv('MAX_TOKENS', 1000))
