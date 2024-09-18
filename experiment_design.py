# experiment_design.py

import os
from utils.logger import setup_logger
from utils.openai_utils import create_completion
from utils.config import initialize_openai
import json

class ExperimentDesigner:
    def __init__(self, model_name):
        initialize_openai()  # Initialize OpenAI API key
        self.model_name = model_name
        self.logger = setup_logger('experiment_design', 'logs/experiment_design.log')

    def design_experiment(self, idea):
        self.logger.info(f"Designing experiment for idea: {idea}")
        try:
            prompt = {
                "task": "design_experiment",
                "idea": idea,
                "instructions": (
                    "Design a concrete, executable experiment plan to test the given idea "
                    "for improving AI-Research-System-3. The experiment plan should be a list of steps, "
                    "where each step is a dictionary containing an 'action' key and any necessary parameters. "
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
                    "5. Evaluation criteria: How to measure the success of the experiment\n"
                    "Provide the experiment plan as a JSON object with an 'experiment_plan' key containing the list of steps."
                ),
                "output_format": "JSON"
            }

            response = create_completion(
                self.model_name,
                messages=[
                    {"role": "system", "content": "You are a world-class computer scientist specializing in AI model and system improvement."},
                    {"role": "user", "content": json.dumps(prompt)}
                ],
                max_tokens=2000,
                temperature=0.7,
            )
            
            self.logger.debug(f"Raw API response: {response}")

            try:
                experiment_data = json.loads(response)
                experiment_plan = experiment_data.get('experiment_plan', [])
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse JSON response. Attempting to parse as text.")
                experiment_plan = self.parse_text_response(response)

            self.logger.info(f"Experiment plan: {experiment_plan}")
            return experiment_plan
        except Exception as e:
            self.logger.error(f"Error designing experiment: {e}")
            return []

    def parse_text_response(self, response):
        # Implement a method to parse non-JSON responses if needed
        # This is a placeholder and should be implemented based on the expected format of text responses
        return []
