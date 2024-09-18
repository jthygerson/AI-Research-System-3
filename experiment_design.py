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
            prompt = (
                "As a world-class computer scientist, design a concrete, executable experiment plan to test the following idea "
                "for improving AI-Research-System-3:\n\n"
                f"{idea}\n\n"
                "The experiment plan should be a list of steps, where each step is a dictionary containing an 'action' key "
                "and any necessary parameters. Possible actions include:\n"
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
                "Provide the experiment plan as a Python list of dictionaries."
            )
            
            chat_models = ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-0314', 'gpt-4-32k', 'gpt-3.5-turbo-0301', 'gpt-4o', 'gpt-4o-mini', 'o1-preview', 'o1-mini']
            is_chat_model = any(self.model_name.lower().startswith(model.lower()) for model in chat_models)
            
            if is_chat_model:
                response = create_completion(
                    self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a world-class computer scientist specializing in AI model and system improvement."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000,
                    temperature=0.7,
                )
            else:
                response = create_completion(
                    self.model_name,
                    prompt=prompt,
                    max_tokens=2000,
                    temperature=0.7,
                )
            
            self.logger.debug(f"Raw API response: {response}")

            # Clean and parse the response
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]  # Remove ```json
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]  # Remove closing ```

            experiment_plan = self.parse_response_to_plan(cleaned_response)
            self.logger.info(f"Experiment plan: {experiment_plan}")
            return experiment_plan
        except Exception as e:
            self.logger.error(f"Error designing experiment: {e}")
            return []

    def parse_response_to_plan(self, response):
        try:
            # Assuming the response is a JSON string representation of a list of dictionaries
            plan = json.loads(response)
            if isinstance(plan, list) and all(isinstance(step, dict) for step in plan):
                return plan
            else:
                self.logger.error("Invalid experiment plan format")
                return []
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing experiment plan: {e}")
            return []
