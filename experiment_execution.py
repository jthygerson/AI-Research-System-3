# experiment_execution.py

import os
import subprocess
import requests
import openai
from utils.logger import setup_logger
from utils.resource_manager import ResourceManager
import json
import traceback
from utils.openai_utils import create_completion  # Make sure this import exists
from utils.config import initialize_openai
import requests.exceptions

class ExperimentExecutor:
    _instance = None

    def __new__(cls, model_name):
        if cls._instance is None:
            cls._instance = super(ExperimentExecutor, cls).__new__(cls)
            cls._instance.model_name = model_name
            cls._instance.logger = setup_logger('experiment_execution', 'logs/experiment_execution.log')
            cls._instance.resource_manager = ResourceManager()
            cls._instance.initialize_openai()
        return cls._instance

    def initialize_openai(self):
        if not hasattr(self, 'openai_initialized'):
            self.logger.info("Initializing OpenAI client for ExperimentExecutor")
            self.openai_client = initialize_openai()
            self.openai_initialized = True

    def execute_experiment(self, experiment_plan):
        self.logger.info("Executing experiment...")
        if not experiment_plan or not isinstance(experiment_plan, list):
            self.logger.error("Invalid experiment plan. Aborting execution.")
            return []

        results = []
        for step_number, step in enumerate(experiment_plan, 1):
            if not isinstance(step, dict) or 'action' not in step:
                self.logger.error(f"Invalid step {step_number} in experiment plan. Skipping.")
                continue

            try:
                step_result = self.execute_step(step)
                results.append({"step": step_number, "action": step['action'], "result": step_result, "status": "success"})
                self.logger.info(f"Step {step_number} completed successfully: {step['action']}")
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Network error in step {step_number}: {e}")
                results.append({"step": step_number, "action": step['action'], "error": str(e), "status": "network_error"})
            except ValueError as e:
                self.logger.error(f"Value error in step {step_number}: {e}")
                results.append({"step": step_number, "action": step['action'], "error": str(e), "status": "value_error"})
            except Exception as e:
                self.logger.error(f"Unexpected error in step {step_number}: {e}")
                self.logger.error(traceback.format_exc())
                results.append({"step": step_number, "action": step['action'], "error": str(e), "status": "unexpected_error"})

        self.logger.info("Experiment execution completed.")
        return results

    def execute_step(self, step):
        action = step.get('action')
        if action == 'run_python_code':
            return self.run_python_code(step.get('code'))
        elif action == 'use_llm_api':
            return self.use_llm_api(step.get('prompt'))
        elif action == 'web_request':
            return self.make_web_request(step.get('url'), step.get('method', 'GET'))
        elif action == 'use_gpu':
            return self.use_gpu(step.get('task'))
        else:
            raise ValueError(f"Unknown action: {action}")

    def run_python_code(self, code):
        # CAUTION: Running arbitrary code can be dangerous
        # Implement strict sandboxing and validation here
        result = subprocess.run(['python', '-c', code], capture_output=True, text=True)
        return {'stdout': result.stdout, 'stderr': result.stderr}

    def use_llm_api(self, prompt):
        # Use the OpenAI API or any other LLM API
        response = create_completion(
            self.model_name,
            messages=[
                {"role": "system", "content": "You are an AI assistant helping with experiments."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )
        
        # Clean and parse the response if it's in JSON format
        cleaned_response = response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]  # Remove ```json
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]  # Remove closing ```
        
        try:
            # Attempt to parse as JSON
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            # If it's not valid JSON, return the original response
            return response

    def make_web_request(self, url, method='GET'):
        # Implement rate limiting and respect robots.txt
        response = requests.request(method, url)
        return {'status_code': response.status_code, 'content': response.text}

    def use_gpu(self, task):
        # Implement GPU task execution
        # This is a placeholder and would need to be implemented based on your specific GPU tasks
        return self.resource_manager.execute_gpu_task(task)
