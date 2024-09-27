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
from experiment_design import ExperimentDesigner  # Add this import at the top of the file
import warnings
from utils.json_utils import parse_llm_response, extract_json_from_text

class ExperimentExecutor:
    def __init__(self, model_name, resource_manager):
        self.model_name = model_name
        self.resource_manager = resource_manager
        self.logger = setup_logger('experiment_execution', 'logs/experiment_execution.log')
        self.experiment_designer = None  # Remove the initialization here

    def execute_experiment(self, experiment_plan):
        self.experiment_designer = ExperimentDesigner(self.model_name)  # Create a new instance here
        self.logger.info("Executing experiment...")
        
        if not isinstance(experiment_plan, dict):
            self.logger.error("Invalid experiment plan format. Expected a dictionary.")
            return []
        
        methodology = experiment_plan.get('methodology', [])
        if not isinstance(methodology, list):
            self.logger.error("Invalid methodology format. Expected a list of steps.")
            return []
        
        results = []
        for step_number, step in enumerate(methodology, 1):
            if not isinstance(step, dict):
                self.logger.error(f"Invalid step format in step {step_number}. Expected a dictionary.")
                continue
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
                code = step.get('code')
                if code is None:
                    raise ValueError("No code provided for 'run_python_code' action")
                return self.run_python_code(code)
            elif action == 'use_llm_api':
                return self.use_llm_api(step.get('prompt'))
            elif action == 'web_request':
                try:
                    return self.make_web_request(step.get('url'), step.get('method', 'GET'), retry_without_ssl=True)
                except requests.exceptions.RequestException as e:
                    new_step = self.experiment_designer.request_plan_adjustment(step, str(e))
                    if new_step:
                        self.logger.info(f"Retrying with new step: {new_step}")
                        return self.execute_step(new_step)  # Recursively try the new step
                    else:
                        self.logger.error(f"Failed to create a new step. Original error: {str(e)}. Skipping this step.")
                        return {"error": f"Original error: {str(e)}. Failed to create a new step."}
            elif action == 'use_gpu':
                return self.use_gpu(step.get('task'))
            else:
                raise ValueError(f"Unknown action: {action}")
        except Exception as e:
            self.logger.error(f"Error executing step with action '{action}': {str(e)}")
            return {"error": str(e)}

    def attempt_fix_step(self, step, error):
        self.logger.info(f"Attempting to fix step: {step['action']}")
        prompt = json.dumps({
            "task": "fix_experiment_step",
            "step": step,
            "error": str(error),
            "instructions": "Analyze the given step and the error it produced. Propose a fix for the step that addresses the error. Return the fixed step as a JSON object with the same structure as the original step."
        })
        
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
            
            # Extract the content from the response
            response_content = response.choices[0].message.content if response.choices else None
            
            if response_content:
                fixed_step = parse_llm_response(response_content)
                if fixed_step is None:
                    fixed_step = extract_json_from_text(response_content)
                
                if fixed_step:
                    self.logger.info(f"Step fixed: {fixed_step}")
                    return fixed_step
                else:
                    self.logger.error("Failed to parse LLM response for step fix")
                    return None
            else:
                self.logger.error("Empty response from LLM")
                return None
        except Exception as e:
            self.logger.error(f"Error in attempt_fix_step: {str(e)}")
            return None

    def run_python_code(self, code):
        # CAUTION: Running arbitrary code can be dangerous
        # Implement strict sandboxing and validation here
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
            
            # Extract the content from the response
            response_content = response.choices[0].message.content if response.choices else None
            
            if response_content:
                cleaned_response = self.clean_llm_response(response_content)
                parsed_response = parse_llm_response(cleaned_response)
                
                if parsed_response is None:
                    parsed_response = extract_json_from_text(cleaned_response)
                
                if parsed_response:
                    return self.process_parsed_response(parsed_response)
                else:
                    return {"raw_response": cleaned_response}
            else:
                return {"error": "Empty response from LLM"}
        except Exception as e:
            self.logger.error(f"Error in use_llm_api: {str(e)}")
            return {"error": str(e)}

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

    def make_web_request(self, url, method='GET', retry_without_ssl=True):
        # Implement rate limiting and respect robots.txt
        try:
            response = requests.request(method, url, verify=True)  # First attempt with SSL verification
            return {'status_code': response.status_code, 'content': response.text}
        except requests.exceptions.SSLError as e:
            self.logger.warning(f"SSL Error occurred: {str(e)}")
            if retry_without_ssl:
                self.logger.warning("Retrying request without SSL verification. This is not secure and should not be used in production.")
                warnings.warn("Unverified HTTPS request is being made. This is not secure and should not be used in production.")
                try:
                    response = requests.request(method, url, verify=False)  # Retry without SSL verification
                    return {'status_code': response.status_code, 'content': response.text}
                except requests.RequestException as retry_error:
                    self.logger.error(f"Request failed even without SSL verification: {str(retry_error)}")
                    raise  # Re-raise the exception to be handled by the calling method
            else:
                raise  # Re-raise the original SSL exception if retry_without_ssl is False

    def use_gpu(self, task):
        # Implement GPU task execution
        # This is a placeholder and would need to be implemented based on your specific GPU tasks
        return self.resource_manager.execute_gpu_task(task)
