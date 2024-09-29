# error_fixing.py

import os
import json  # Added import for json module
from utils.logger import setup_logger
from utils.openai_utils import create_completion
from utils.config import initialize_openai
from utils.json_utils import parse_llm_response
import traceback
import logging

class ErrorFixer:
    def __init__(self, model_name, max_tokens=4000):
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.logger = setup_logger('error_fixing', 'logs/error_fixing.log', console_level=logging.INFO)

    def fix_errors(self, errors_warnings):
        """
        Adjusts the system's code to correct any errors or warnings found.
        """
        self.logger.info(f"Fixing errors: {errors_warnings}")
        prompt = self._generate_fix_prompt(errors_warnings)
        
        try:
            response = create_completion(
                self.model_name,
                messages=[
                    {"role": "system", "content": "You are an AI research assistant. Suggest fixes for the given errors and warnings."},
                    {"role": "user", "content": json.dumps(prompt)}
                ],
                max_tokens=self.max_tokens,
                temperature=0.7,
            )
            
            self.logger.info(f"Raw API response: {response}")
            
            fixes = json.loads(response)
            
            if not fixes.get('fixes'):
                self.logger.error("No fixes found in the response")
                return
            
            self.apply_code_fixes(fixes['fixes'])
        
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse response as JSON: {response}")
        except Exception as e:
            self.logger.error(f"Error fixing errors: {e}")
            self.logger.error(traceback.format_exc())

    def apply_code_fixes(self, fixes):
        """
        Applies the suggested code fixes to the system.
        """
        self.logger.info(f"Applying code fixes: {fixes}")
        # Implement the logic to apply the fixes to the code
        # This is where you would modify the actual code files
        pass

    def _generate_fix_prompt(self, errors_warnings):
        return {
            "task": "fix_errors",
            "errors_warnings": errors_warnings,
            "instructions": """
Suggest fixes for the given errors and warnings. Provide the exact code modifications needed, including the file names and line numbers.

Example output format:
{
    "fixes": [
        {"file": "utils/logger.py", "line": 45, "fix": "Add log rotation handler."},
        {"file": "experiment_execution.py", "line": 78, "fix": "Handle potential division by zero error."}
    ]
}
            """,
            "output_format": "JSON"
        }
