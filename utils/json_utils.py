import json
import re

def parse_llm_response(response):
    # Remove any leading/trailing whitespace
    cleaned_response = response.strip()
    
    # Remove any line breaks and extra spaces within the JSON structure
    cleaned_response = re.sub(r'\s+', ' ', cleaned_response)
    
    try:
        # Parse the cleaned response
        parsed_json = json.loads(cleaned_response)
        return parsed_json
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Problematic JSON string: {cleaned_response}")
        return None

# Add a new function to handle potential nested JSON structures
def extract_json_from_text(text):
    json_pattern = r'\{(?:[^{}]|(?R))*\}'
    match = re.search(json_pattern, text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            return None
    return None
