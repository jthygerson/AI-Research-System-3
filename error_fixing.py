# error_fixing.py

import os
import openai
from utils.logger import setup_logger
from utils.openai_utils import create_completion
from utils.config import initialize_openai

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
            prompt = (
                f"The following errors and warnings were found in the system logs:\n\n{errors_warnings}\n\n"
                "Provide specific code changes to fix these issues, including the file names and line numbers. "
                "Ensure the changes improve the system's reliability and performance."
            )
            
            chat_models = ['gpt-3.5-turbo', 'gpt-4']
            if self.model_name in chat_models:
                messages = [
                    {"role": "system", "content": "You are a code fixer and system optimizer."},
                    {"role": "user", "content": prompt}
                ]
                response = create_completion(
                    self.model_name,
                    messages=messages,
                    max_tokens=1500,
                    temperature=0.5,
                )
                fixes = response['choices'][0]['message']['content'].strip()
            else:
                response = create_completion(
                    self.model_name,
                    prompt=prompt,
                    max_tokens=1500,
                    temperature=0.5,
                )
                fixes = response['choices'][0]['text'].strip()
            
            self.logger.info(f"Suggested code fixes: {fixes}")
            # Apply the code fixes
            self.apply_code_fixes(fixes)
        except Exception as e:
            self.logger.error(f"Error fixing errors: {e}")

    def apply_code_fixes(self, fixes):
        """
        Applies the suggested code fixes to the system.
        """
        self.logger.info("Applying code fixes...")
        # Implement parsing of fixes and apply changes to files
        # Due to safety concerns, actual code modification is not implemented
        self.logger.info("Code fixes logged but not applied for safety.")
