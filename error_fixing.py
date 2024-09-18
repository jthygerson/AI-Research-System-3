# error_fixing.py

import os
from utils.logger import setup_logger
from utils.openai_utils import create_completion
from utils.config import initialize_openai
from utils.json_utils import parse_llm_response
import traceback

class ErrorFixer:
    def __init__(self, model_name):
        initialize_openai()  # Initialize OpenAI API key
        self.model_name = model_name
        self.logger = setup_logger('error_fixing', 'logs/error_fixing.log')

    def fix_errors(self, errors_warnings):
        """
        Adjusts the system's code to correct any errors or warnings found.
        """
        self.logger.info("Fixing errors and warnings found in logs...")
        try:
            prompt = {
                "task": "fix_errors",
                "errors_warnings": errors_warnings,
                "instructions": "Provide specific code changes to fix these issues, including the file names and line numbers. Ensure the changes improve the system's reliability and performance.",
                "output_format": "JSON"
            }
            
            response = create_completion(
                self.model_name,
                messages=[
                    {"role": "system", "content": "You are a code fixer and system optimizer."},
                    {"role": "user", "content": json.dumps(prompt)}
                ],
                max_tokens=1000,
                temperature=0.7,
            )
            
            self.logger.info(f"Raw API response: {response}")
            
            parsed_response = parse_llm_response(response)
            if parsed_response:
                self.logger.info(f"Suggested code fixes: {parsed_response}")
                # Apply the code fixes
                self.apply_code_fixes(json.dumps(parsed_response))
            else:
                self.logger.warning("Failed to parse the API response.")
        except Exception as e:
            self.logger.error(f"Error fixing errors: {e}")
            self.logger.error(traceback.format_exc())

    def apply_code_fixes(self, fixes):
        """
        Applies the suggested code fixes to the system.
        """
        self.logger.info("Applying code fixes...")
        # Implement parsing of fixes and apply changes to files
        # Due to safety concerns, actual code modification is not implemented
        self.logger.info("Code fixes logged but not applied for safety.")
