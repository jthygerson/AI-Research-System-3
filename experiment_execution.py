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

from experiment_design import ExperimentDesigner
import warnings

class ActionStrategy(ABC):
    @abstractmethod
    def execute(self, step, executor):
        pass

class InitializeOpenAIStrategy(ActionStrategy):
    def execute(self, step, executor):
        return executor.initialize_openai()

class RunPythonCodeStrategy(ActionStrategy):
    def execute(self, step, executor):
        code = step.get('code', 'print("No code provided")')
        return executor.run_python_code(code)

class UseLLMAPIStrategy(ActionStrategy):
    def execute(self, step, executor):
        prompt = step.get('prompt')
        if prompt is None and 'parameters' in step:
            prompt = step['parameters'].get('prompt')
            if prompt is None and 'args' in step['parameters']:
                prompt = step['parameters']['args'].get('prompt')
        
        if prompt is None:
            raise ValueError(f"No prompt provided for LLM API action. Step details: {step}")
        return executor.use_llm_api(prompt)

class WebRequestStrategy(ActionStrategy):
    def execute(self, step, executor):
        url = step.get('url')
        method = step.get('method', 'GET')
        if url is None:
            raise ValueError("No URL provided for web request action")
        return executor.make_web_request(url, method, retry_without_ssl=True)

class UseGPUStrategy(ActionStrategy):
    def execute(self, step, executor):
        task = step.get('task')
        if task is None:
            raise ValueError("No task provided for GPU action")
        return executor.use_gpu(task)

class ExperimentExecutor:
    def __init__(self, model_name, resource_manager, action_strategies):
        self.model_name = model_name
        self.resource_manager = resource_manager
        self.logger = setup_logger('experiment_execution', 'logs/experiment_execution.log')
        self.experiment_designer = None
        initialize_openai()
        self.action_strategies = action_strategies

    def execute_experiment(self, experiment_plan):
        self.experiment_designer = ExperimentDesigner(self.model_name)
        self.logger.info("Executing experiment...")
        
        if not isinstance(experiment_plan, dict):
            self.logger.error("Invalid experiment plan format. Expected a dictionary.")
            return None
        
        methodology = experiment_plan.get('methodology', [])
        if not isinstance(methodology, list):
            self.logger.error("Invalid methodology format. Expected a list of steps.")
            return None
        
        results = []
        for step_number, step in enumerate(methodology, 1):
            if not isinstance(step, dict):
                self.logger.error(f"Invalid step format in step {step_number}. Expected a dictionary.")
                return None
            
            step_result = self.execute_step(step)
            if 'error' in step_result:
                fixed_step = self.attempt_fix_step(step, step_result['error'])
                if fixed_step:
                    step_result = self.execute_step(fixed_step)
                    if 'error' in step_result:
                        self.logger.error(f"Step {step_number} failed even after attempted fix. Stopping experiment.")
                        return None
                else:
                    self.logger.error(f"Unable to fix step {step_number}. Stopping experiment.")
                    return None
            
            results.append({"step": step_number, "action": step['action'], "result": step_result, "status": "success" if 'error' not in step_result else "error"})
        
        return results

    def execute_step(self, step):
        action = step.get('action')
        try:
            strategy = self.action_strategies.get(action)
            if strategy:
                return strategy.execute(step, self)
            else:
                raise ValueError(f"Unknown action: {action}")
        except Exception as e:
            self.logger.error(f"Error executing step with action '{action}': {str(e)}")
            return {"error": str(e)}

    def attempt_fix_step(self, step, error):
        self.logger.info(f"Attempting to fix step: {step['action']}")
        prompt = f"Fix the following experiment step that produced an error:\nStep: {json.dumps(step)}\nError: {error}\nProvide a fixed version of the step as a JSON object."
        
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
                # Ensure the fixed step has the correct structure
                if 'action' not in fixed_step:
                    fixed_step['action'] = step['action']
                if 'prompt' not in fixed_step and 'parameters' in fixed_step:
                    if 'prompt' in fixed_step['parameters']:
                        fixed_step['prompt'] = fixed_step['parameters']['prompt']
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

    def use_llm_api(self, prompt):
        try:
            response = create_completion(
                self.model_name,
                messages=[
                    {"role": "system", "content": "You are an AI assistant helping with experiments."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3500
            )
            
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
                    return {"raw_response": cleaned_response}
            else:
                return {"error": "Unexpected response format from LLM"}
        except Exception as e:
            self.logger.error(f"Error in use_llm_api: {str(e)}")
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
        return self.resource_manager.execute_gpu_task(task)

    def register_action(self, action_name, strategy):
        self.action_strategies[action_name] = strategy
