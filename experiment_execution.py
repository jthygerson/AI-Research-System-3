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

class ExperimentExecutor:
    def __init__(self, model_name):
        self.model_name = model_name
        self.logger = setup_logger('experiment_execution', 'logs/experiment_execution.log')
        self.resource_manager = ResourceManager()

    def execute_experiment(self, experiment_plan):
        self.logger.info("Executing experiment...")
        try:
            results = []
            for step in experiment_plan:
                step_result = self.execute_step(step)
                results.append(step_result)
                self.logger.info(f"Step result: {step_result}")
            
            self.logger.info(f"Experiment execution results: {results}")
            return results
        except Exception as e:
            self.logger.error(f"Error executing experiment: {e}")
            return []

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
        response = create_completion(self.model_name, prompt=prompt, max_tokens=100)
        
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
