import json
import re

def parse_llm_response(response):
    # Remove any leading/trailing whitespace
    response = response.strip()

    # Remove code block markers if present
    if response.startswith("```json"):
        response = response[7:]
    if response.endswith("```"):
        response = response[:-3]

    # Try to parse the JSON
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        # If JSON parsing fails, try to extract JSON-like content
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

    # If all parsing attempts fail, return None
    return None
