# utils/openai_utils.py

import openai
import logging
import time
import traceback
from tenacity import retry, stop_after_attempt, wait_random_exponential
from utils.logger import setup_logger

# Setup a logger for openai_utils
logger = setup_logger('openai_utils', 'logs/openai_utils.log')

# Initialize the OpenAI client
client = openai.OpenAI()

@retry(stop=stop_after_attempt(3), wait=wait_random_exponential(min=1, max=60))
def create_completion(model, messages, max_tokens=4000, temperature=0.7):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content if response.choices else None
    except Exception as e:
        logger.error(f"Error in create_completion: {str(e)}")
        raise

def handle_api_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"API Error: {str(e)}")
            return str(e)
    return wrapper
