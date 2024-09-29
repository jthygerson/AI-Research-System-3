# experiment_execution.py

import os
import subprocess
import requests
import openai
from utils.logger import setup_logger
from utils.resource_manager import ResourceManager
import json
import traceback
import re
from utils.openai_utils import create_completion, handle_api_error
from utils.config import initialize_openai
from utils.json_utils import parse_llm_response, extract_json_from_text
from abc import ABC, abstractmethod
import importlib
import inspect
import tempfile
import sys
import warnings
import logging

class ActionStrategy(ABC):
    @abstractmethod
    def execute(self, step, executor):
        pass

class ExperimentExecutor:
    _instance = None

    def __new__(cls, resource_manager, model_name):
        if cls._instance is None:
            cls._instance = super(ExperimentExecutor, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_name, max_tokens, resource_manager=None):
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.resource_manager = resource_manager
        self.logger = setup_logger('experiment_execution', 'logs/experiment_execution.log', console_level=logging.INFO)
        initialize_openai()

    def execute_experiment(self, experiment_package):
        self.logger.info("Preparing to execute experiment...")
        
        if not isinstance(experiment_package, dict) or 'code' not in experiment_package:
            self.logger.error("Invalid experiment package format.")
            return None
        
        code = experiment_package['code']
        requirements = experiment_package.get('requirements', [])
        
        # Set up the execution environment
        self.setup_environment(requirements)
        
        # Execute the experiment code with error handling and code review
        results = self.run_experiment_code_with_review(code, requirements)
        
        return results

    def run_experiment_code_with_review(self, code, requirements):
        max_attempts = 3
        for attempt in range(max_attempts):
            self.logger.info(f"Execution attempt {attempt + 1}/{max_attempts}")
            
            results = self.run_experiment_code(code)
            
            if 'error' not in results:
                return results
            
            self.logger.warning(f"Execution failed. Reviewing code...")
            reviewed_code = self.review_and_correct_code(code, results['error'], requirements)
            
            if reviewed_code == code:
                self.logger.error("Code review did not produce any changes. Aborting execution.")
                return results
            
            code = reviewed_code

        self.logger.error("Max execution attempts reached. Experiment failed.")
        return results

    def review_and_correct_code(self, code, error_message, requirements):
        self.logger.info("Reviewing and correcting code...")
        
        prompt = {
            "task": "review_and_correct_code",
            "code": code,
            "error_message": error_message,
            "requirements": requirements,
            "instructions": (
                "Review the provided code and error message. Identify and fix any issues, "
                "ensuring compatibility with the given requirements. Provide the corrected "
                "code as a JSON response."
            ),
            "response_format": {
                "corrected_code": "The complete corrected Python code",
                "explanation": "Explanation of the changes made"
            }
        }
        
        try:
            response = create_completion(
                self.model_name,
                messages=[
                    {"role": "system", "content": "You are an AI code reviewer and debugger."},
                    {"role": "user", "content": json.dumps(prompt)}
                ],
                max_tokens=self.max_tokens,
                temperature=0.7,
            )
            
            reviewed_package = parse_llm_response(response)
            
            if reviewed_package and isinstance(reviewed_package, dict) and 'corrected_code' in reviewed_package:
                self.logger.info(f"Code review complete. Explanation: {reviewed_package.get('explanation', 'No explanation provided.')}")
                return reviewed_package['corrected_code']
            else:
                self.logger.error("Failed to get valid reviewed code.")
                return code
        except Exception as e:
            self.logger.error(f"Error during code review: {str(e)}")
            return code

    def setup_environment(self, requirements):
        self.logger.info("Setting up execution environment...")
        for req in requirements:
            try:
                if req not in sys.modules:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", req])
                    self.logger.info(f"Installed requirement: {req}")
                else:
                    self.logger.info(f"Requirement already satisfied: {req}")
            except subprocess.CalledProcessError:
                self.logger.error(f"Failed to install requirement: {req}")

    def run_experiment_code(self, code):
        self.logger.info("Executing experiment code...")
        try:
            # Create a temporary file to store the experiment code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name

            # Execute the temporary file
            result = subprocess.run([sys.executable, temp_file_path], capture_output=True, text=True)
            
            # Clean up the temporary file
            os.unlink(temp_file_path)

            if result.returncode == 0:
                self.logger.info("Experiment executed successfully.")
                return {'stdout': result.stdout, 'stderr': result.stderr}
            else:
                self.logger.error(f"Experiment execution failed with return code {result.returncode}")
                return {'error': result.stderr}
        except Exception as e:
            self.logger.error(f"Error executing experiment: {str(e)}")
            return {'error': str(e)}

    # Remove the initialize_openai method as it's not needed in this class anymore

    # The use_llm_api method can be simplified or removed if it's not directly used in execution
    # If you want to keep it for potential future use, you can simplify it:
    def use_llm_api(self, prompt, llm_endpoint=None, payload=None):
        try:
            if not payload:
                payload = {
                    "task": "experiment_execution_assistance",
                    "prompt": prompt,
                    "instructions": "Provide assistance for executing the experiment. Respond with a JSON object containing your analysis and suggestions.",
                    "response_format": {
                        "analysis": "Your analysis of the situation",
                        "suggestions": ["List of suggestions for proceeding with the experiment"],
                        "potential_issues": ["List of potential issues to be aware of"]
                    }
                }

            response = create_completion(
                self.model_name,
                messages=[
                    {"role": "system", "content": "You are an AI assistant helping with experiment execution. Always respond with valid JSON."},
                    {"role": "user", "content": json.dumps(payload)}
                ],
                max_tokens=3500
            )
            parsed_response = parse_llm_response(response)
            if parsed_response and isinstance(parsed_response, dict):
                return {"response": parsed_response}
            else:
                return {"error": "Invalid response format from LLM"}
        except Exception as e:
            self.logger.error(f"Error in use_llm_api: {str(e)}")
            return {"error": str(e)}

    # Remove or simplify other methods that are no longer directly used in execution:
    # clean_llm_response, process_parsed_response, format_code, map_to_existing_action

    # Keep the make_web_request and use_gpu methods as they might be useful for experiment execution

    def make_web_request(self, url, method='GET', retry_without_ssl=True):
        try:
            response = requests.request(method, url, verify=True)
            return {'status_code': response.status_code, 'content': response.text}
        except requests.exceptions.SSLError as e:
            self.logger.warning(f"SSL Error occurred: {str(e)}")
            if retry_without_ssl:
                self.logger.warning("Retrying request without SSL verification. This is not secure and should not be used in production.")
                warnings.warn("Unverified HTTPS request is being made. This is not secure and should not be used in production.")
                try:
                    response = requests.request(method, url, verify=False)
                    return {'status_code': response.status_code, 'content': response.text}
                except requests.RequestException as retry_error:
                    self.logger.error(f"Request failed even without SSL verification: {str(retry_error)}")
                    raise
            else:
                raise

    def use_gpu(self, task):
        if isinstance(task, str):
            # If task is a string, assume it's Python code and execute it
            return self.resource_manager.execute_gpu_task(task)
        elif callable(task):
            # If task is a callable (function), execute it
            return self.resource_manager.execute_gpu_task(task)
        else:
            return {"error": "Invalid GPU task format. Expected string (code) or callable (function)."}

class UseLLMAPIStrategy(ActionStrategy):
    def execute(self, step, executor):
        parameters = step.get('parameters', {})
        prompt = parameters.get('prompt')
        
        if not prompt:
            payload = parameters.get('payload', {})
            prompt = payload.get('prompt')

        if not prompt:
            # Generate a default prompt based on the step description and parameters
            prompt = f"Based on the following information, {step['description']} "
            prompt += f"Endpoint: {parameters.get('llm_endpoint', 'Unknown')}. "
            prompt += f"Payload: {parameters.get('payload', 'Not provided')}. "
            prompt += "Please provide a detailed response."

        return executor.use_llm_api(prompt, parameters.get('llm_endpoint'), parameters.get('payload'))

class UseGPUStrategy(ActionStrategy):
    def execute(self, step, executor):
        parameters = step.get('parameters', {})
        task = parameters.get('task') or parameters.get('code')
        
        if not task:
            executor.logger.warning("No specific GPU task provided. Using a default task.")
            task = """
import torch

if not torch.cuda.is_available():
    print("GPU not available. Skipping GPU task.")
else:
    # Example task: Perform matrix multiplication on GPU
    a = torch.randn(1000, 1000, device='cuda')
    b = torch.randn(1000, 1000, device='cuda')
    c = torch.matmul(a, b)
    print("GPU task completed: Matrix multiplication")
"""
        
        return executor.use_gpu(task)