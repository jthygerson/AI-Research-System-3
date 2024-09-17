# experiment_design.py

import os
from utils.logger import setup_logger
from utils.openai_utils import create_completion
from utils.config import initialize_openai

class ExperimentDesigner:
    def __init__(self, model_name):
        initialize_openai()  # Initialize OpenAI API key
        self.model_name = model_name
        self.logger = setup_logger('experiment_design', 'logs/experiment_design.log')

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
            
            chat_models = ['gpt-3.5-turbo', 'gpt-4']
            if self.model_name in chat_models:
                messages = [
                    {"role": "system", "content": "You are an AI research assistant."},
                    {"role": "user", "content": prompt}
                ]
                response = create_completion(
                    self.model_name,
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.7,
                )
                # Use the response directly, no need for ['choices'][0]['message']['content'] or ['choices'][0]['text']
            else:
                response = create_completion(
                    self.model_name,
                    prompt=prompt,
                    max_tokens=1000,
                    temperature=0.7,
                )
                # Use the response directly, no need for ['choices'][0]['message']['content'] or ['choices'][0]['text']
            
            self.logger.info(f"Experiment plan: {response}")
            return response
        except Exception as e:
            self.logger.error(f"Error designing experiment: {e}")
            return ""
