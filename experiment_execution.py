# experiment_execution.py

import os
from utils.logger import setup_logger
from utils.openai_utils import create_completion
from utils.config import initialize_openai

class ExperimentExecutor:
    def __init__(self, model_name):
        initialize_openai()  # Initialize OpenAI API key
        self.model_name = model_name
        self.logger = setup_logger('experiment_execution', 'logs/experiment_execution.log')

    def execute_experiment(self, experiment_plan):
        """
        Executes the experiment as per the plan.
        """
        self.logger.info("Executing experiment...")
        try:
            prompt = (
                f"Execute the following experiment plan step by step and report the outcomes of each step:\n\n{experiment_plan}"
            )
            
            chat_models = ['gpt-3.5-turbo', 'gpt-4']
            if self.model_name in chat_models:
                messages = [
                    {"role": "system", "content": "You are an AI experiment executor."},
                    {"role": "user", "content": prompt}
                ]
                response = create_completion(
                    self.model_name,
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.7,
                )
                execution_results = response['choices'][0]['message']['content'].strip()
            else:
                response = create_completion(
                    self.model_name,
                    prompt=prompt,
                    max_tokens=1000,
                    temperature=0.7,
                )
                execution_results = response['choices'][0]['text'].strip()
            
            self.logger.info(f"Experiment execution results: {execution_results}")
            return execution_results
        except Exception as e:
            self.logger.error(f"Error executing experiment: {e}")
            return ""
