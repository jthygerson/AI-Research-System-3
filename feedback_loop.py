# feedback_loop.py

import os
from utils.logger import setup_logger
from utils.openai_utils import create_completion
from utils.config import initialize_openai
from utils.json_utils import parse_llm_response
import json
import traceback
import logging

class FeedbackLoop:
    def __init__(self, model_name):
        self.model_name = model_name
        self.max_iterations = 5  # Example value
        self.logger = setup_logger('feedback_loop', 'logs/feedback_loop.log', console_level=logging.INFO)

    def refine_experiment(self, experiment_plan, initial_results):
        self.logger.info("Refining experiment plan based on initial results...")
        refined_plan = experiment_plan
        try:
            for iteration in range(self.max_iterations):
                prompt = {
                    "task": "refine_experiment",
                    "initial_results": initial_results,
                    "current_plan": refined_plan,
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
                        "Example of expected JSON format:\n"
                        "{\n"
                        "  \"experiment_plan\": [\n"
                        "    {\n"
                        "      \"action\": \"run_python_code\",\n"
                        "      \"code\": \"import tensorflow as tf\\n# Rest of the code...\"\n"
                        "    },\n"
                        "    {\n"
                        "      \"action\": \"use_llm_api\",\n"
                        "      \"prompt\": \"Analyze the following experiment results...\"\n"
                        "    },\n"
                        "    {\n"
                        "      \"action\": \"web_request\",\n"
                        "      \"url\": \"https://api.example.com/data\",\n"
                        "      \"method\": \"GET\"\n"
                        "    },\n"
                        "    {\n"
                        "      \"action\": \"use_gpu\",\n"
                        "      \"task\": \"Train neural network model XYZ\"\n"
                        "    }\n"
                        "  ],\n"
                        "  \"objectives\": [\"Improve idea generation quality\", \"Enhance experiment execution efficiency\"],\n"
                        "  \"resources_required\": [\"TensorFlow library\", \"GPU access\"],\n"
                        "  \"expected_outcomes\": [\"20% increase in idea quality scores\", \"30% reduction in experiment execution time\"],\n"
                        "  \"evaluation_criteria\": [\"Compare idea quality scores before and after implementation\", \"Measure average experiment execution time\"]\n"
                        "}\n\n"
                        "Ensure your response is a single, valid JSON object following this structure. "
                        "Ensure that all steps are executable and do not rely on non-existent resources or APIs. "
                        "For web requests, use real, accessible URLs. For GPU tasks, include a check for GPU availability."
                    ),
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
                
                self.logger.debug(f"Raw API response (Iteration {iteration+1}): {response}")

                parsed_response = parse_llm_response(response)
                if parsed_response:
                    # Extract the updated plan if it exists
                    if 'experiment_plan' in parsed_response:
                        new_plan = parsed_response['experiment_plan']
                    else:
                        new_plan = parsed_response

                    if self.should_continue_refinement(refined_plan, new_plan):
                        refined_plan = new_plan
                    else:
                        break
                else:
                    self.logger.warning("Failed to parse JSON response or invalid structure.")
                    return None

            # Before returning the refined plan
            if isinstance(refined_plan, str):
                try:
                    refined_plan = json.loads(refined_plan)
                except json.JSONDecodeError:
                    self.logger.error("Failed to parse refined plan as JSON.")
                    return None

            if not isinstance(refined_plan, list) or not all(isinstance(step, dict) for step in refined_plan):
                self.logger.error("Refined plan is not in the correct format.")
                return None

            return refined_plan
        except Exception as e:
            self.logger.error(f"Error refining experiment plan: {str(e)}")
            self.logger.error(traceback.format_exc())
            return None

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
