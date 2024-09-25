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
from utils.openai_utils import create_completion  # Make sure this import exists
from utils.config import initialize_openai
import requests.exceptions

class ExperimentExecutor:
    def __init__(self, model_name, resource_manager):
        self.model_name = model_name
        self.resource_manager = resource_manager
        self.logger = setup_logger('experiment_execution', 'logs/experiment_execution.log')

    def execute_experiment(self, experiment_plan):
        self.logger.info("Executing experiment...")
        results = []
        for step_number, step in enumerate(experiment_plan, 1):
            try:
                step_result = self.execute_step(step)
                if 'error' in step_result:
                    fixed_step = self.attempt_fix_step(step, step_result['error'])
                    if fixed_step:
                        step_result = self.execute_step(fixed_step)
                    else:
                        self.logger.warning(f"Unable to fix step {step_number}. Continuing with next step.")
                results.append({"step": step_number, "action": step['action'], "result": step_result, "status": "success" if 'error' not in step_result else "error"})
            except Exception as e:
                self.logger.error(f"Unexpected error in step {step_number}: {e}")
                results.append({"step": step_number, "action": step['action'], "error": str(e), "status": "unexpected_error"})
        return results

    def execute_step(self, step):
        action = step.get('action')
        try:
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
        except Exception as e:
            self.logger.error(f"Error executing step with action '{action}': {str(e)}")
            return {"error": str(e)}

    def attempt_fix_step(self, step, error):
        self.logger.info(f"Attempting to fix step: {step['action']}")
        prompt = {
            "task": "fix_experiment_step",
            "step": step,
            "error": error,
            "instructions": "Analyze the given step and the error it produced. Propose a fix for the step that addresses the error. Return the fixed step as a JSON object with the same structure as the original step."
        }
        
        response = create_completion(
            self.model_name,
            messages=[
                {"role": "system", "content": "You are an AI assistant specialized in fixing errors in experiment steps."},
                {"role": "user", "content": json.dumps(prompt)}
            ],
            max_tokens=3500,
            temperature=0.7,
        )
        
        try:
            fixed_step = json.loads(response)
            self.logger.info(f"Step fixed: {fixed_step}")
            return fixed_step
        except json.JSONDecodeError:
            self.logger.error("Failed to parse LLM response for step fix")
            return None

    def run_python_code(self, code):
        # CAUTION: Running arbitrary code can be dangerous
        # Implement strict sandboxing and validation here
        result = subprocess.run(['python', '-c', code], capture_output=True, text=True)
        return {'stdout': result.stdout, 'stderr': result.stderr}

    def use_llm_api(self, prompt):
        response = create_completion(
            self.model_name,
            messages=[
                {"role": "system", "content": "You are an AI assistant helping with experiments."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=3500  # Increased to allow for longer responses
        )
        
        # Clean and parse the response
        cleaned_response = self.clean_llm_response(response)
        
        try:
            # Attempt to parse as JSON
            parsed_response = json.loads(cleaned_response)
            return self.process_parsed_response(parsed_response)
        except json.JSONDecodeError:
            # If it's not valid JSON, return the original cleaned response
            return {"raw_response": cleaned_response}

    def clean_llm_response(self, response):
        # Remove any markdown code block syntax
        cleaned = re.sub(r'```(?:json)?\s*|\s*```', '', response.strip())
        # Remove any leading/trailing whitespace
        return cleaned.strip()

    def process_parsed_response(self, parsed_response):
        if isinstance(parsed_response, dict):
            # If there's a 'code' key, ensure it's properly formatted
            if 'code' in parsed_response:
                parsed_response['code'] = self.format_code(parsed_response['code'])
            return parsed_response
        else:
            # If it's not a dict, wrap it in a dict
            return {"parsed_response": parsed_response}

    def format_code(self, code):
        # Remove any extra indentation
        lines = code.split('\n')
        if lines:
            # Find minimum indentation
            min_indent = min(len(line) - len(line.lstrip()) for line in lines if line.strip())
            # Remove that amount of indentation from each line
            return '\n'.join(line[min_indent:] if line.strip() else '' for line in lines)
        return code

    def make_web_request(self, url, method='GET'):
        # Implement rate limiting and respect robots.txt
        response = requests.request(method, url)
        return {'status_code': response.status_code, 'content': response.text}

    def use_gpu(self, task):
        # Implement GPU task execution
        # This is a placeholder and would need to be implemented based on your specific GPU tasks
        return self.resource_manager.execute_gpu_task(task)
