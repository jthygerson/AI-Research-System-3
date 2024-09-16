# utils/config.py

import os
import openai
from dotenv import load_dotenv

def initialize_openai():
    """
    Initializes the OpenAI API key from environment variables.
    """
    load_dotenv()  # Load variables from .env if it exists
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("The OPENAI_API_KEY environment variable is not set.")
    openai.api_key = api_key
