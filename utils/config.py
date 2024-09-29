# utils/config.py

import os
import logging
import openai
from openai import OpenAI
from .logger import setup_logger  # Add this import

# Setup a logger for config
logger = setup_logger('config', 'logs/config.log', level=logging.DEBUG)

_openai_initialized = False

def is_openai_initialized():
    global _openai_initialized
    return _openai_initialized

def initialize_openai():
    global _openai_initialized
    if _openai_initialized:
        logger.info("OpenAI client already initialized.")
        return

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    openai.api_key = api_key
    _openai_initialized = True
    logger.info("OpenAI client initialized successfully")

# Add more configuration options as needed
MODEL_TEMPERATURE = float(os.getenv('MODEL_TEMPERATURE', 0.7))
MAX_TOKENS = int(os.getenv('MAX_TOKENS', 3500))
