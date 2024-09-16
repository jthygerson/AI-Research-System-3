# utils/config.py

import os
import openai
from dotenv import load_dotenv
import logging

# Setup a logger for config
logger = logging.getLogger('config')
logger.setLevel(logging.DEBUG)  # Set to DEBUG for detailed logging

def initialize_openai():
    """
    Initializes the OpenAI API key from environment variables.

    Raises:
        ValueError: If the OPENAI_API_KEY environment variable is not set.
    """
    load_dotenv()  # Load variables from .env if it exists
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        error_msg = "The OPENAI_API_KEY environment variable is not set."
        logger.error(error_msg)
        raise ValueError(error_msg)
    openai.api_key = api_key
    logger.debug("OpenAI API key initialized successfully.")
