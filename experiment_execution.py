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
import pkg_resources
import venv
import time
import threading

class ActionStrategy(ABC):
    @abstractmethod
    def execute(self, step, executor):
        pass

class ExperimentExecutor:
    _instance = None

    def __new__(cls, model_name, max_tokens, resource_manager=None):
        if cls._instance is None:
            cls._instance = super(ExperimentExecutor, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_name, max_tokens, resource_manager=None):
        if not self._initialized:
            self.model_name = model_name
            self.max_tokens = max_tokens
            self.resource_manager = resource_manager or ResourceManager()
            self.logger = setup_logger('experiment_execution', 'logs/experiment_execution.log', console_level=logging.INFO)
            initialize_openai()
            self._initialized = True
        elif (self.model_name != model_name or 
              self.max_tokens != max_tokens or 
              self.resource_manager != resource_manager):
            self.logger.info("Updating ExperimentExecutor parameters.")
            self.model_name = model_name
            self.max_tokens = max_tokens
            self.resource_manager = resource_manager or self.resource_manager

    def execute_experiment(self, experiment_package):
        self.logger.info("Preparing to execute experiment...")
        
        if not isinstance(experiment_package, dict) or 'code' not in experiment_package:
            self.logger.error("Invalid experiment package format.")
            return {"error": "Invalid experiment package format"}
        
        code = experiment_package['code']
        requirements = experiment_package.get('requirements', [])
        
        # Create a temporary directory for the virtual environment
        with tempfile.TemporaryDirectory() as temp_dir:
            venv_path = os.path.join(temp_dir, 'venv')
            
            # Create a virtual environment
            venv.create(venv_path, with_pip=True)
            
            # Get path to python in the virtual environment
            if sys.platform == "win32":
                python_path = os.path.join(venv_path, 'Scripts', 'python.exe')
            else:
                python_path = os.path.join(venv_path, 'bin', 'python')
            
            # Upgrade pip in the virtual environment
            subprocess.check_call([python_path, "-m", "pip", "install", "--upgrade", "pip"])
            
            # Install requirements in the virtual environment
            for req in requirements:
                try:
                    subprocess.check_call([python_path, "-m", "pip", "install", req])
                    self.logger.info(f"Installed requirement: {req}")
                except subprocess.CalledProcessError:
                    self.logger.error(f"Failed to install requirement: {req}")
            
            # Execute the experiment code in the virtual environment
            results = self.run_experiment_code_in_venv(code, python_path)
        
        return results

    def run_experiment_code_in_venv(self, code, python_path):
        self.logger.info("Executing experiment code in virtual environment...")
        try:
            # Create a temporary file to store the experiment code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name

            # Start a thread to display a progress indicator
            stop_progress = threading.Event()
            progress_thread = threading.Thread(target=self.display_progress, args=(stop_progress,))
            progress_thread.start()

            # Execute the temporary file in the virtual environment
            result = subprocess.run([python_path, temp_file_path], capture_output=True, text=True, timeout=300)  # 5-minute timeout
            
            # Stop the progress indicator
            stop_progress.set()
            progress_thread.join()

            # Clean up the temporary file
            os.unlink(temp_file_path)

            if result.returncode == 0:
                self.logger.info("Experiment executed successfully.")
                return {'stdout': result.stdout, 'stderr': result.stderr}
            else:
                self.logger.error(f"Experiment execution failed with return code {result.returncode}")
                self.logger.error(f"Error output: {result.stderr}")
                return {'error': result.stderr}
        except subprocess.TimeoutExpired:
            self.logger.error("Experiment execution timed out after 5 minutes.")
            return {'error': 'Execution timed out'}
        except Exception as e:
            self.logger.error(f"Error executing experiment: {str(e)}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return {'error': str(e)}

    def display_progress(self, stop_event):
        spinner = ['|', '/', '-', '\\']
        i = 0
        while not stop_event.is_set():
            print(f"\rExecuting experiment... {spinner[i % len(spinner)]}", end='', flush=True)
            time.sleep(0.1)
            i += 1
        print("\rExperiment execution completed.       ")

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
                "Review the provided Python code and error message. Identify and fix any issues, "
                "ensuring compatibility with the given requirements. Pay special attention to "
                "syntax errors, indentation issues, and potential runtime errors. If the error is not "
                "in the provided code snippet, consider potential issues with imported modules or "
                "the execution environment. Provide the corrected code as a JSON response, maintaining "
                "the original structure and formatting where possible. If no changes are needed in the "
                "provided code, suggest potential external factors that might be causing the error."
            ),
            "response_format": {
                "corrected_code": "The complete corrected Python code",
                "explanation": "Detailed explanation of the changes made or potential external issues",
                "additional_suggestions": ["List of additional suggestions to resolve the error"]
            }
        }
        
        try:
            response = create_completion(
                self.model_name,
                messages=[
                    {"role": "system", "content": "You are an AI code reviewer and debugger specializing in Python syntax and best practices."},
                    {"role": "user", "content": json.dumps(prompt)}
                ],
                max_tokens=self.max_tokens,
                temperature=0.7,
            )
            
            reviewed_package = parse_llm_response(response)
            
            if reviewed_package and isinstance(reviewed_package, dict) and 'corrected_code' in reviewed_package:
                self.logger.info(f"Code review complete. Explanation: {reviewed_package.get('explanation', 'No explanation provided.')}")
                
                # Verify that the corrected code doesn't introduce new syntax errors
                try:
                    compile(reviewed_package['corrected_code'], '<string>', 'exec')
                except SyntaxError as se:
                    self.logger.error(f"Corrected code contains syntax errors: {str(se)}")
                    return code  # Return original code if correction introduces new errors
                
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
                self.install_requirement(req)
            except Exception as e:
                self.logger.error(f"Failed to install requirement: {req}. Error: {str(e)}")

    def install_requirement(self, requirement):
        # Check if the requirement is a built-in module
        if requirement in sys.builtin_module_names or (hasattr(sys, 'stdlib_module_names') and requirement in sys.stdlib_module_names):
            self.logger.info(f"Skipping built-in module: {requirement}")
            return

        try:
            # Try to import the module first
            importlib.import_module(requirement)
            self.logger.info(f"Requirement already satisfied: {requirement}")
        except ImportError:
            # If import fails, try to install the package
            self.logger.info(f"Installing requirement: {requirement}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", requirement])
            self.logger.info(f"Successfully installed: {requirement}")

        # Check if the installed package has any post-installation steps
        self.run_post_install_steps(requirement)

    def run_post_install_steps(self, package):
        if package.lower() == 'spacy':
            self.download_language_model('en_core_web_sm')
        # Add more post-installation steps for other packages as needed

    def download_language_model(self, model_name):
        self.logger.info(f"Attempting to download language model: {model_name}")
        try:
            subprocess.check_call([sys.executable, "-m", "spacy", "download", model_name])
            self.logger.info(f"Successfully downloaded language model: {model_name}")
        except subprocess.CalledProcessError:
            self.logger.error(f"Failed to download language model: {model_name}")

    def run_experiment_code(self, code):
        self.logger.info("Executing experiment code...")
        try:
            # Create a temporary file to store the experiment code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                # Add a general package and model handling preamble
                preamble = """
import importlib
import subprocess
import sys

def ensure_package(package_name):
    try:
        importlib.import_module(package_name)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

def ensure_spacy_model(model_name):
    import spacy
    try:
        nlp = spacy.load(model_name)
    except OSError:
        subprocess.check_call([sys.executable, "-m", "spacy", "download", model_name])

# Ensure common packages are available
common_packages = ['numpy', 'pandas', 'scipy', 'sklearn', 'matplotlib', 'spacy']
for package in common_packages:
    ensure_package(package)

# Ensure common language models are available
ensure_spacy_model('en_core_web_sm')

"""
                temp_file.write(preamble + code)
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
                self.logger.error(f"Error output: {result.stderr}")
                return {'error': result.stderr}
        except Exception as e:
            self.logger.error(f"Error executing experiment: {str(e)}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
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