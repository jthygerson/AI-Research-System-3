# feedback_loop.py

import os
from utils.logger import setup_logger
from utils.openai_utils import create_completion
from utils.config import initialize_openai

class FeedbackLoop:
    def __init__(self, model_name, max_iterations=3):
        initialize_openai()  # Initialize OpenAI API key
        self.model_name = model_name
        self.max_iterations = max_iterations
        self.logger = setup_logger('feedback_loop', 'logs/feedback_loop.log')

    def refine_experiment(self, experiment_plan, initial_results):
        self.logger.info("Refining experiment plan based on initial results...")
        refined_plan = experiment_plan
        try:
            for iteration in range(self.max_iterations):
                prompt = (
                    f"Based on the following initial experiment results:\n\n{initial_results}\n\n"
                    f"Refine the experiment plan to improve outcomes. Provide the updated experiment plan."
                )
                
                chat_models = ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-0314', 'gpt-4-32k', 'gpt-3.5-turbo-0301', 'gpt-4o', 'gpt-4o-mini', 'o1-preview', 'o1-mini']
                is_chat_model = any(self.model_name.lower().startswith(model.lower()) for model in chat_models)
                
                if is_chat_model:
                    response = create_completion(
                        self.model_name,
                        messages=[
                            {"role": "system", "content": "You are an AI research assistant."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=1000,
                        temperature=0.7,
                    )
                else:
                    response = create_completion(
                        self.model_name,
                        prompt=prompt,
                        max_tokens=1000,
                        temperature=0.7,
                    )
                
                self.logger.info(f"Refined experiment plan (Iteration {iteration+1}): {response}")

                if self.should_continue_refinement(refined_plan, response):
                    refined_plan = response
                else:
                    break

            return refined_plan
        except Exception as e:
            self.logger.error(f"Error refining experiment plan: {e}")
            return experiment_plan

    def should_continue_refinement(self, old_plan, new_plan):
        """
        Determines whether to continue refining the experiment plan.
        Implement logic based on your criteria.
        """
        # Placeholder implementation
        return old_plan != new_plan
