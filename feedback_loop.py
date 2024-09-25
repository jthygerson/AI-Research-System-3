# feedback_loop.py

import os
from utils.logger import setup_logger
from utils.openai_utils import create_completion
from utils.config import initialize_openai
from utils.json_utils import parse_llm_response
import json
import traceback

class FeedbackLoop:
    _instance = None

    def __new__(cls, model_name, max_iterations=3):
        if cls._instance is None:
            cls._instance = super(FeedbackLoop, cls).__new__(cls)
            cls._instance.model_name = model_name
            cls._instance.max_iterations = max_iterations
            cls._instance.logger = setup_logger('feedback_loop', 'logs/feedback_loop.log')
            cls._instance.initialize_openai()
        return cls._instance

    def initialize_openai(self):
        if not hasattr(self, 'openai_initialized'):
            self.logger.info("Initializing OpenAI client for FeedbackLoop")
            initialize_openai()
            self.openai_initialized = True

    def refine_experiment(self, experiment_plan, initial_results):
        self.logger.info("Refining experiment plan based on initial results...")
        refined_plan = experiment_plan
        try:
            for iteration in range(self.max_iterations):
                prompt = {
                    "task": "refine_experiment",
                    "initial_results": initial_results,
                    "current_plan": refined_plan,
                    "instructions": "Refine the experiment plan to improve outcomes based on the initial results. Provide the updated experiment plan in the same format as the current plan.",
                    "output_format": "JSON"
                }
                
                response = create_completion(
                    self.model_name,
                    messages=[
                        {"role": "system", "content": "You are an AI research assistant specializing in experiment refinement."},
                        {"role": "user", "content": json.dumps(prompt)}
                    ],
                    max_tokens=3500,
                    temperature=0.7,
                )
                
                self.logger.info(f"Raw API response (Iteration {iteration+1}): {response}")

                parsed_response = parse_llm_response(response)
                if parsed_response:
                    new_plan = parsed_response
                    if self.should_continue_refinement(refined_plan, new_plan):
                        refined_plan = new_plan
                    else:
                        break
                else:
                    self.logger.warning("Failed to parse JSON response. Skipping this iteration.")

            return refined_plan
        except Exception as e:
            self.logger.error(f"Error refining experiment: {str(e)}")
            self.logger.error(traceback.format_exc())
            return experiment_plan

    def should_continue_refinement(self, old_plan, new_plan):
        """
        Determines whether to continue refining the experiment plan.
        """
        # Example logic: Continue refinement if the new plan is significantly different from the old plan
        return old_plan != new_plan and self._calculate_plan_difference(old_plan, new_plan) > 0.1

    def _calculate_plan_difference(self, old_plan, new_plan):
        # Implement logic to calculate the difference between two plans
        # This is a placeholder and should be implemented based on your criteria
        return 0.2  # Placeholder value
