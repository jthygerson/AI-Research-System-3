# utils/openai_utils.py

import openai
import logging
import time

# Setup a logger for openai_utils
logger = logging.getLogger('openai_utils')
logger.setLevel(logging.DEBUG)  # Set to DEBUG for detailed logging

def create_completion(model, messages=None, prompt=None, max_tokens=100, temperature=0.7):
    try:
        if messages:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        elif prompt:
            response = client.completions.create(
                model=model,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].text
        else:
            raise ValueError("Either 'messages' or 'prompt' must be provided")
    except Exception as e:
        # Log the error here
        raise
