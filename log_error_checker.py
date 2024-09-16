# log_error_checker.py

import os
import openai
from utils.logger import setup_logger

class LogErrorChecker:
    def __init__(self, model_name):
        self.model_name = model_name
        self.logger = setup_logger('log_error_checker', 'logs/log_error_checker.log')
        openai.api_key = os.getenv('OPENAI_API_KEY')

    def check_logs(self, log_file_path):
        """
        Parses the log file using an LLM to find any errors or warnings.
        """
        self.logger.info(f"Checking logs for errors and warnings in {log_file_path}")
        try:
            with open(log_file_path, 'r') as log_file:
                log_contents = log_file.read()

            prompt = (
                f"Analyze the following log file contents and identify any errors or warnings. "
                f"Provide a list of issues found and suggest possible fixes.\n\n{log_contents}"
            )
            response = openai.Completion.create(
                engine=self.model_name,
                prompt=prompt,
                max_tokens=1000,
                n=1,
                stop=None,
                temperature=0.5,
            )
            analysis = response['choices'][0]['text'].strip()
            self.logger.info(f"Log analysis results: {analysis}")
            return analysis
        except Exception as e:
            self.logger.error(f"Error checking logs: {e}")
            return ""
