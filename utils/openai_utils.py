# utils/openai_utils.py

import openai
import logging
import time
import traceback
from tenacity import retry, stop_after_attempt, wait_exponential

# Setup a logger for openai_utils
logger = logging.getLogger('openai_utils')
logger.setLevel(logging.DEBUG)  # Set to DEBUG for detailed logging

# Initialize the OpenAI client
client = openai.OpenAI()

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def create_completion(model, messages=None, prompt=None, max_tokens=100, temperature=0.7):
    logger.debug(f"Creating completion with model: {model}")
    logger.debug(f"Messages: {messages}")
    logger.debug(f"Prompt: {prompt}")
    logger.debug(f"Max tokens: {max_tokens}")
    logger.debug(f"Temperature: {temperature}")
    try:
        if messages:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            logger.info(f"Chat completion response: {response}")
            return response.choices[0].message.content
        elif prompt:
            response = client.completions.create(
                model=model,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            logger.info(f"Completion response: {response}")
            return response.choices[0].text
        else:
            raise ValueError("Either 'messages' or 'prompt' must be provided")
    except Exception as e:
        logger.error(f"Error in create_completion: {str(e)}")
        logger.error(traceback.format_exc())
        raise
