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
        return json.loads(response)
    except json.JSONDecodeError:
        return None

def extract_json_from_text(text):
    """
    Attempt to extract a JSON object from a text string.
    """
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        return json_match.group(0)
    return None
