# feedback_loop.py

import os
from utils.logger import setup_logger
from utils.openai_utils import create_completion
from utils.config import initialize_openai
from utils.json_utils import parse_llm_response, extract_json_from_text
import json
import traceback
import logging
from pprint import pformat

class FeedbackLoop:
    def __init__(self, model_name):
        self.model_name = model_name
        self.max_iterations = 5  # Example value
        self.logger = setup_logger('feedback_loop', 'logs/feedback_loop.log', console_level=logging.INFO)
        initialize_openai()

    def refine_experiment(self, experiment_plan, initial_results):
        self.logger.info("Refining experiment plan based on initial results...")
        
        # Print initial_results to the terminal
        print("Initial Results:")
        print(pformat(initial_results, indent=2))
        
        refined_plan = experiment_plan
        try:
            for iteration in range(self.max_iterations):
                prompt = self.create_refinement_prompt(initial_results, refined_plan)
                
                response = create_completion(
                    self.model_name,
                    messages=[
                        {"role": "system", "content": "You are an AI research assistant specializing in experiment refinement."},
                        {"role": "user", "content": json.dumps(prompt)}
                    ],
                    max_tokens=3500,
                    temperature=0.7,
                )
                
                self.logger.debug(f"Raw API response (Iteration {iteration+1}): {response}")

                parsed_response = self.parse_refinement_response(response)
                if parsed_response:
                    new_plan = parsed_response
                    if self.should_continue_refinement(refined_plan, new_plan):
                        refined_plan = new_plan
                        self.logger.info(f"Refined plan (Iteration {iteration+1}):")
                        self.logger.info(json.dumps(refined_plan, indent=2))
                    else:
                        self.logger.info("Refinement complete. No further improvements found.")
                        break
                else:
                    self.logger.warning("Failed to parse JSON response or invalid structure.")
                    continue

            if not self.validate_refined_plan(refined_plan):
                self.logger.error("Final refined plan is not valid. Returning the last valid plan.")
                return experiment_plan  # Return the original plan instead of None

            return refined_plan
        except Exception as e:
            self.logger.error(f"Error refining experiment plan: {str(e)}")
            self.logger.error(traceback.format_exc())
            return experiment_plan  # Return the original plan instead of None

    def create_refinement_prompt(self, initial_results, current_plan):
        return {
            "task": "refine_experiment",
            "initial_results": initial_results,
            "current_plan": current_plan,
            "instructions": (
                "Refine the experiment plan to improve outcomes based on the initial results. "
                "Provide the updated experiment plan in the same format as the current plan. "
                "Ensure the refined plan is a valid JSON object with an 'experiment_plan' key containing a list of steps. "
                "Each step should be a dictionary with an 'action' key and any necessary parameters.\n\n"
                "Possible actions include:\n"
                "1. 'run_python_code': Execute Python code (provide 'code' parameter)\n"
                "2. 'use_llm_api': Make a request to an LLM API (provide 'prompt' parameter)\n"
                "3. 'web_request': Make a web request (provide 'url' and optionally 'method' parameters)\n"
                "4. 'use_gpu': Perform a GPU task (provide 'task' parameter)\n\n"
                "Include the following in your plan:\n"
                "1. Objectives: Which performance metrics the experiment aims to improve\n"
                "2. Methodology: Steps to implement and test the idea\n"
                "3. Resources required: Additional tools or data needed\n"
                "4. Expected outcomes: Anticipated improvements in specific performance metrics\n"
                "5. Evaluation criteria: How to measure the success of the experiment\n\n"
                "Ensure that each step in the experiment_plan has an 'action' key. "
                "Valid actions are 'run_python_code', 'use_llm_api', 'web_request', and 'use_gpu'.\n\n"
                "Ensure your response is a single, valid JSON object following this structure. "
                "Ensure that all steps are executable and do not rely on non-existent resources or APIs. "
                "For web requests, use real, accessible URLs. For GPU tasks, include a check for GPU availability."
            ),
            "output_format": "JSON"
        }

    def parse_refinement_response(self, response):
        if isinstance(response, str):
            parsed_response = parse_llm_response(response)
            if parsed_response is None:
                parsed_response = extract_json_from_text(response)
        elif hasattr(response, 'choices') and response.choices:
            response_content = response.choices[0].message.content
            parsed_response = parse_llm_response(response_content)
            if parsed_response is None:
                parsed_response = extract_json_from_text(response_content)
        else:
            self.logger.error("Unexpected response format from LLM")
            return None
        
        # Ensure the parsed response has the correct structure
        if parsed_response and isinstance(parsed_response, dict):
            if 'experiment_plan' not in parsed_response:
                # If the response is a list of steps, wrap it in the correct structure
                if isinstance(parsed_response, list) and all(isinstance(step, dict) for step in parsed_response):
                    parsed_response = {'experiment_plan': parsed_response}
                else:
                    # If the response doesn't have the correct structure, create a minimal valid structure
                    parsed_response = {
                        'experiment_plan': [],
                        'objectives': 'Improve experiment based on initial results',
                        'resources_required': 'No additional resources specified',
                        'expected_outcomes': 'Improved performance',
                        'evaluation_criteria': 'Compare results with initial experiment'
                    }
                    self.logger.warning("Refined plan didn't have the expected structure. Created a minimal valid structure.")
        
        # Ensure each step in the experiment_plan has an 'action' key
        for step in parsed_response['experiment_plan']:
            if 'action' not in step:
                if 'step' in step:
                    step['action'] = 'run_python_code'  # Default action
                    self.logger.warning(f"Added missing 'action' key to step: {step['step']}")
                else:
                    self.logger.warning(f"Removing invalid step without 'action' or 'step' key: {step}")
                    parsed_response['experiment_plan'].remove(step)
    
        return parsed_response

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

    def validate_refined_plan(self, plan):
        """
        Validates the structure and content of the refined plan.
        """
        if not isinstance(plan, dict):
            self.logger.error(f"Invalid plan type: expected dict, got {type(plan)}")
            return False
        
        if 'experiment_plan' not in plan:
            self.logger.error("Missing 'experiment_plan' key in the plan")
            return False
        
        if not isinstance(plan['experiment_plan'], list):
            self.logger.error(f"Invalid 'experiment_plan' type: expected list, got {type(plan['experiment_plan'])}")
            return False
        
        for i, step in enumerate(plan['experiment_plan'], 1):
            if not isinstance(step, dict):
                self.logger.error(f"Step {i} is not a dictionary")
                return False
            
            if 'action' not in step:
                self.logger.error(f"Step {i} is missing 'action' key")
                return False
            
            if step['action'] not in ['run_python_code', 'use_llm_api', 'web_request', 'use_gpu']:
                self.logger.error(f"Step {i} has invalid action: {step['action']}")
                return False
        
        required_keys = ['objectives', 'resources_required', 'expected_outcomes', 'evaluation_criteria']
        missing_keys = [key for key in required_keys if key not in plan]
        if missing_keys:
            self.logger.error(f"Plan is missing required keys: {', '.join(missing_keys)}")
            return False
        
        self.logger.info("Refined plan validation successful")
        return True
