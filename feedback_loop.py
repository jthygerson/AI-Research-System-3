# feedback_loop.py

import os
import openai
from utils.logger import setup_logger

class FeedbackLoop:
    def __init__(self, model_name, max_iterations=3):
        self.model_name = model_name
        self.max_iterations = max_iterations
        self.logger = setup_logger('feedback_loop', 'logs/feedback_loop.log')
        openai.api_key = os.getenv('OPENAI_API_KEY')

    def refine_experiment(self, experiment_plan, initial_results):
        """
        Updates the experiment plan based on initial outcomes.
        """
        self.logger.info("Refining experiment plan based on initial results...")
        refined_plan = experiment_plan
        try:
            for iteration in range(self.max_iterations):
                prompt = (
                    f"Based on the following initial experiment results:\n\n{initial_results}\n\n"
                    f"Refine the experiment plan to improve outcomes. Provide the updated experiment plan."
                )
                response = openai.Completion.create(
                    engine=self.model_name,
                    prompt=prompt,
                    max_tokens=1000,
                    n=1,
                    stop=None,
                    temperature=0.7,
                )
                refined_plan = response['choices'][0]['text'].strip()
                self.logger.info(f"Refined experiment plan (Iteration {iteration+1}): {refined_plan}")

                # For simplicity, we'll assume the refined plan is acceptable
                break  # Exit after first refinement
            return refined_plan
        except Exception as e:
            self.logger.error(f"Error refining experiment plan: {e}")
            return experiment_plan
