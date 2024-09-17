# log_error_checker.py

import os
from utils.logger import setup_logger
from utils.openai_utils import create_completion
from utils.config import initialize_openai

class LogErrorChecker:
    def __init__(self, model_name):
        initialize_openai()  # Initialize OpenAI API key
        self.model_name = model_name
        self.logger = setup_logger('log_error_checker', 'logs/log_error_checker.log')

    def check_logs(self, log_file_path):
        self.logger.info(f"Checking logs for errors and warnings in {log_file_path}")
        try:
            with open(log_file_path, 'r') as log_file:
                log_contents = log_file.read()

            prompt = (
                f"Analyze the following log file contents and identify any errors or warnings. "
                f"Provide a list of issues found and suggest possible fixes.\n\n{log_contents}"
            )
            
            chat_models = ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-0314', 'gpt-4-32k', 'gpt-3.5-turbo-0301']
            is_chat_model = any(self.model_name.lower().startswith(model.lower()) for model in chat_models)
            
            if is_chat_model:
                response = create_completion(
                    self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a system log analyzer."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.5,
                )
            else:
                response = create_completion(
                    self.model_name,
                    prompt=prompt,
                    max_tokens=1000,
                    temperature=0.5,
                )
            
            self.logger.info(f"Log analysis results: {response}")
            return response
        except Exception as e:
            self.logger.error(f"Error checking logs: {e}")
            return ""
