# experiment_execution.py

import os
import openai
from utils.logger import setup_logger

class ExperimentExecutor:
    def __init__(self, model_name):
        self.model_name = model_name
        self.logger = setup_logger('experiment_execution', 'logs/experiment_execution.log')
        openai.api_key = os.getenv('OPENAI_API_KEY')

    def execute_experiment(self, experiment_plan):
        """
        Executes the experiment as per the plan.
        """
        self.logger.info("Executing experiment...")
        try:
            # For simulation purposes, we'll assume execution via LLM
            prompt = (
                f"Execute the following experiment plan step by step and report the outcomes of each step:\n\n{experiment_plan}"
            )
            response = openai.Completion.create(
                engine=self.model_name,
                prompt=prompt,
                max_tokens=1000,
                n=1,
                stop=None,
                temperature=0.7,
            )
            execution_results = response['choices'][0]['text'].strip()
            self.logger.info(f"Experiment execution results: {execution_results}")
            return execution_results
        except Exception as e:
            self.logger.error(f"Error executing experiment: {e}")
            return ""
