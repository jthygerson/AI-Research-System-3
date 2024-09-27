import json
import re

def parse_llm_response(response):
    # Remove markdown code block formatting if present
    cleaned_response = re.sub(r'^```json\s*|```\s*$', '', response.strip())
    
    # Remove any line breaks within the JSON structure
    cleaned_response = re.sub(r'\n\s*', ' ', cleaned_response)
    
    try:
        # Parse the cleaned response
        parsed_json = json.loads(cleaned_response)
        return parsed_json  # Return the parsed JSON directly without wrapping it
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Problematic JSON string: {cleaned_response}")
        return None
