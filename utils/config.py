# utils/config.py

import os
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
    # No need to set openai.api_key here, as it will be handled by the OpenAI client
    logger.debug("OpenAI API key initialized successfully.")
