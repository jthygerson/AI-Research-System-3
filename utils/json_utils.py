import json
import re

def parse_llm_response(response):
    if isinstance(response, str):
        cleaned_response = response.strip()
    elif hasattr(response, 'choices') and response.choices:
        cleaned_response = response.choices[0].message.content.strip()
    else:
        print("Unexpected response format")
        return None

    # Remove any line breaks and extra spaces within the JSON structure
    cleaned_response = re.sub(r'\s+', ' ', cleaned_response)
    
    # Remove any potential non-JSON content before the opening brace
    cleaned_response = re.sub(r'^[^{]*', '', cleaned_response)
    
    # Remove any potential non-JSON content after the closing brace
    cleaned_response = re.sub(r'}[^}]*$', '}', cleaned_response)
    
    try:
        # Parse the cleaned response
        parsed_json = json.loads(cleaned_response)
        return parsed_json
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Problematic JSON string: {cleaned_response}")
        
        # Attempt to fix common JSON issues
        try:
            # Replace single quotes with double quotes
            cleaned_response = cleaned_response.replace("'", '"')
            # Ensure boolean values are lowercase
            cleaned_response = cleaned_response.replace("True", "true").replace("False", "false")
            parsed_json = json.loads(cleaned_response)
            return parsed_json
        except json.JSONDecodeError:
            print("Failed to fix JSON parsing issues.")
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
