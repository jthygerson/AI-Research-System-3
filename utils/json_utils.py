import json
import re
from utils.logger import setup_logger
import logging
from logging.handlers import RotatingFileHandler

# Update the logger setup
logger = setup_logger('json_utils', 'logs/json_utils.log', log_rotation=True)

def parse_llm_response(response):
    """
    Attempt to parse the LLM response as JSON.
    """
    try:
        if isinstance(response, str):
            return json.loads(response)
        elif hasattr(response, 'choices') and response.choices:
            return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        return None

def extract_json_from_text(text):
    """
    Attempt to extract a JSON object from a text string.
    """
    # Try to find JSON-like structure in the text
    json_match = re.search(r'\{(?:[^{}]|(?R))*\}', text)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            return None
    return None
