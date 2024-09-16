# experiment_design.py

import os
import openai
from utils.logger import setup_logger

class ExperimentDesigner:
    def __init__(self, model_name):
        self.model_name = model_name
        self.logger = setup_logger('experiment_design', 'logs/experiment_design.log')
        openai.api_key = os.getenv('OPENAI_API_KEY')

    def design_experiment(self, idea):
        """
        Designs an experiment based on the best idea.
        """
        self.logger.info(f"Designing experiment for idea: {idea}")
        try:
            prompt = (
                f"Design a detailed experiment plan to test the following idea:\n\n{idea}\n\n"
                "The experiment plan should include objectives, methodology, resources required, "
                "procedures, and expected outcomes."
            )
            response = openai.Completion.create(
                engine=self.model_name,
                prompt=prompt,
                max_tokens=1000,
                n=1,
                stop=None,
                temperature=0.7,
            )
            experiment_plan = response['choices'][0]['text'].strip()
            self.logger.info(f"Experiment plan: {experiment_plan}")
            return experiment_plan
        except Exception as e:
            self.logger.error(f"Error designing experiment: {e}")
            return ""
