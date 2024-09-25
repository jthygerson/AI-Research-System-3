# experiment_design.py

import os
from utils.logger import setup_logger
from utils.openai_utils import create_completion
from utils.config import initialize_openai
import json
from utils.json_utils import parse_llm_response
import textwrap

class ExperimentDesigner:
    _instance = None

    def __new__(cls, model_name):
        if cls._instance is None:
            cls._instance = super(ExperimentDesigner, cls).__new__(cls)
            cls._instance.model_name = model_name
            cls._instance.logger = setup_logger('experiment_design', 'logs/experiment_design.log')
            cls._instance.initialize_openai()
        return cls._instance

    def initialize_openai(self):
        if not hasattr(self, 'openai_initialized'):
            self.logger.info("Initializing OpenAI client for ExperimentDesigner")
            initialize_openai()
            self.openai_initialized = True

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

            parsed_response = parse_llm_response(response)
            if parsed_response:
                experiment_plan = parsed_response.get('experiment_plan', [])
            else:
                self.logger.warning("Failed to parse JSON response. Attempting to parse as text.")
                experiment_plan = self.parse_text_response(response)

            # Check for required modules
            required_modules = ['rpa']  # Add other required modules here
            for module in required_modules:
                try:
                    __import__(module)
                except ImportError:
                    self.logger.warning(f"Required module '{module}' is not installed. Please install it before running the experiment.")

            # Fix indentation in generated Python code
            for step in experiment_plan:
                if step['action'] == 'run_python_code':
                    step['code'] = textwrap.dedent(step['code']).strip()

            self.logger.info(f"Experiment plan: {experiment_plan}")
            return experiment_plan
        except Exception as e:
            self.logger.error(f"Error designing experiment: {e}")
            self.logger.error(traceback.format_exc())
            return []

    def parse_text_response(self, response):
        # Implement a method to parse non-JSON responses if needed
        # This is a placeholder and should be implemented based on the expected format of text responses
        return []
