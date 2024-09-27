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

from experiment_design import ExperimentDesigner
import warnings

class ActionStrategy(ABC):
    @abstractmethod
    def execute(self, step, executor):
        pass

class ExperimentExecutor:
    def __init__(self, model_name, resource_manager):
        self.model_name = model_name
        self.resource_manager = resource_manager
        self.logger = setup_logger('experiment_execution', 'logs/experiment_execution.log')
        self.experiment_designer = None
        initialize_openai()
        self.action_strategies = {}
        self.load_action_strategies()

    def load_action_strategies(self):
        # Dynamically load all action strategies from a dedicated module
        strategy_module = importlib.import_module('action_strategies')
        for name, obj in inspect.getmembers(strategy_module):
            if inspect.isclass(obj) and issubclass(obj, ActionStrategy) and obj != ActionStrategy:
                self.register_action(name.lower().replace('strategy', ''), obj())

    def register_action(self, action_name, strategy):
        self.action_strategies[action_name] = strategy
        self.logger.info(f"Registered new action: {action_name}")

    def execute_experiment(self, experiment_plan):
        self.logger.info("Executing experiment...")
        
        if not isinstance(experiment_plan, dict) or 'methodology' not in experiment_plan:
            self.logger.error("Invalid experiment plan format.")
            return None
        
        methodology = experiment_plan['methodology']
        results = []

        for step_number, step in enumerate(methodology, 1):
            if not isinstance(step, dict) or 'action' not in step:
                self.logger.error(f"Invalid step format in step {step_number}.")
                continue

            step_result = self.execute_step(step)
            if step_result.get('error'):
                self.logger.error(f"Error in step {step_number}: {step_result['error']}")
                fixed_step = self.attempt_fix_step(step, step_result['error'])
                if fixed_step:
                    step_result = self.execute_step(fixed_step)
                    if step_result.get('error'):
                        mapped_action = self.map_to_existing_action(fixed_step['action'])
                        if mapped_action:
                            fixed_step['action'] = mapped_action
                            step_result = self.execute_step(fixed_step)
                        if step_result.get('error'):
                            self.logger.error(f"Step {step_number} failed even after attempted fix and mapping. Error: {step_result['error']}")
                            continue
                else:
                    self.logger.error(f"Unable to fix step {step_number}. Skipping this step.")
                    continue

            results.append({
                "step": step_number,
                "action": step['action'],
                "result": step_result,
                "status": "success" if not step_result.get('error') else "error"
            })

        return results

    def execute_step(self, step):
        action = step.get('action')
        try:
            # Convert action name to lowercase and remove underscores
            normalized_action = action.lower().replace('_', '')
            strategy = self.action_strategies.get(normalized_action)
            if strategy:
                return strategy.execute(step, self)
            else:
                return {"error": f"Unknown action: {action}"}
        except Exception as e:
            self.logger.error(f"Error executing step with action '{action}': {str(e)}")
            return {"error": str(e)}

    def attempt_fix_step(self, step, error):
        self.logger.info(f"Attempting to fix step: {step['action']}")
        prompt = f"Fix the following experiment step that produced an error:\nStep: {json.dumps(step)}\nError: {error}\nProvide a fixed version of the step as a JSON object. Ensure the 'action' field matches one of these valid actions: {', '.join(self.action_strategies.keys())}."

        try:
            response = create_completion(
                self.model_name,
                messages=[
                    {"role": "system", "content": "You are an AI assistant specialized in fixing errors in experiment steps."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3500,
                temperature=0.7,
            )
            
            fixed_step = None
            if isinstance(response, str):
                fixed_step = parse_llm_response(response)
                if fixed_step is None:
                    fixed_step = extract_json_from_text(response)
            elif hasattr(response, 'choices') and response.choices:
                response_content = response.choices[0].message.content
                fixed_step = parse_llm_response(response_content)
                if fixed_step is None:
                    fixed_step = extract_json_from_text(response_content)
            
            if fixed_step:
                # Ensure the fixed step has the correct structure and action name
                if 'action' not in fixed_step or fixed_step['action'].lower().replace('_', '') not in self.action_strategies:
                    self.logger.warning(f"Invalid action in fixed step. Defaulting to original action: {step['action']}")
                    fixed_step['action'] = step['action']
                
                # Ensure there are no duplicate 'code' keys in parameters
                if 'parameters' in fixed_step and 'code' in fixed_step['parameters']:
                    if isinstance(fixed_step['parameters']['code'], list):
                        fixed_step['parameters']['code'] = '\n'.join(filter(None, fixed_step['parameters']['code']))
                    elif not fixed_step['parameters']['code']:
                        del fixed_step['parameters']['code']
                
                self.logger.info(f"Step fixed: {fixed_step}")
                return fixed_step
            else:
                self.logger.error("Failed to parse LLM response for step fix")
                return None
        except Exception as e:
            self.logger.error(f"Error in attempt_fix_step: {str(e)}")
            return None

    def initialize_openai(self):
        try:
            initialize_openai()
            return {"status": "OpenAI initialized successfully"}
        except Exception as e:
            return {"error": f"Failed to initialize OpenAI: {str(e)}"}

    def run_python_code(self, code):
        result = subprocess.run(['python', '-c', code], capture_output=True, text=True)
        return {'stdout': result.stdout, 'stderr': result.stderr}

    def use_llm_api(self, prompt, endpoint=None, payload=None):
        try:
            # If an endpoint is provided, use it to call a specific API
            if endpoint:
                # Implement the logic to call the specific endpoint with the payload
                # This is a placeholder and should be replaced with actual API call logic
                response = f"API call to {endpoint} with payload {payload}"
            else:
                # Use the default OpenAI completion if no specific endpoint is provided
                response = create_completion(
                    self.model_name,
                    messages=[
                        {"role": "system", "content": "You are an AI assistant helping with experiments."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=3500
                )
            
            # Process the response as before
            if isinstance(response, str):
                return {"raw_response": response}
            elif hasattr(response, 'choices') and response.choices:
                response_content = response.choices[0].message.content
                cleaned_response = self.clean_llm_response(response_content)
                parsed_response = parse_llm_response(cleaned_response)
                
                if parsed_response is None:
                    parsed_response = extract_json_from_text(cleaned_response)
                
                if parsed_response:
                    return self.process_parsed_response(parsed_response)
                else:
                    self.logger.warning(f"Failed to parse LLM response: {cleaned_response}")
                    return {"raw_response": cleaned_response}
            else:
                self.logger.error(f"Unexpected response format from LLM: {response}")
                return {"error": "Unexpected response format from LLM"}
        except Exception as e:
            self.logger.error(f"Error in use_llm_api: {str(e)}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return {"error": str(e)}

    def clean_llm_response(self, response):
        cleaned = re.sub(r'```(?:json)?\s*|\s*```', '', response.strip())
        return cleaned.strip()

    def process_parsed_response(self, parsed_response):
        if isinstance(parsed_response, dict):
            if 'code' in parsed_response:
                parsed_response['code'] = self.format_code(parsed_response['code'])
            return parsed_response
        else:
            return {"parsed_response": parsed_response}

    def format_code(self, code):
        lines = code.split('\n')
        if lines:
            min_indent = min(len(line) - len(line.lstrip()) for line in lines if line.strip())
            return '\n'.join(line[min_indent:] if line.strip() else '' for line in lines)
        return code

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

    def map_to_existing_action(self, action):
        normalized_action = action.lower().replace('_', '')
        for existing_action in self.action_strategies.keys():
            if normalized_action in existing_action:
                return existing_action
        return None

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
