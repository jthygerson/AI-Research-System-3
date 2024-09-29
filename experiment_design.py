# experiment_design.py

import os
import re
import sys
import platform
import psutil
import GPUtil
import subprocess
from utils.logger import setup_logger
from utils.openai_utils import create_completion
from utils.config import initialize_openai
import json
from utils.json_utils import parse_llm_response, extract_json_from_text
import textwrap
from pprint import pformat
import traceback
import logging
from abc import ABC, abstractmethod

class ActionStrategy(ABC):
    @abstractmethod
    def execute(self, step, executor):
        pass

class ExperimentDesigner:
    _instance = None

    def __new__(cls, model_name, max_tokens=4000):
        if cls._instance is None or cls._instance.model_name != model_name:
            cls._instance = super(ExperimentDesigner, cls).__new__(cls)
            cls._instance.model_name = model_name
            cls._instance.max_tokens = max_tokens
            cls._instance.logger = setup_logger('experiment_design', 'logs/experiment_design.log', console_level=logging.INFO)
            cls._instance.initialize_openai()
            cls._instance.action_strategies = {
                'run_python_code': RunPythonCodeStrategy(),
                'use_llm_api': UseLLMAPIStrategy(),
                'web_request': WebRequestStrategy(),
                'use_gpu': UseGPUStrategy(),
            }
        return cls._instance

    def __init__(self, model_name, max_tokens=4000):
        initialize_openai()
        # Rest of the initialization

    def initialize_openai(self):
        self.logger.info("Initializing OpenAI client for ExperimentDesigner")
        initialize_openai()

    def design_experiment(self, idea):
        self.logger.info(f"Designing experiment for idea: {idea}")
        prompt = self._generate_design_prompt(idea)
        
        try:
            response = create_completion(
                self.model_name,
                messages=[
                    {"role": "system", "content": "You are an AI research assistant. Design an experiment based on the given idea."},
                    {"role": "user", "content": json.dumps(prompt)}
                ],
                max_tokens=self.max_tokens
            )
            
            self.logger.debug(f"Raw LLM response: {response}")
            
            # Try to parse the response as JSON
            experiment_plan = parse_llm_response(response)
            
            if not experiment_plan:
                # If parsing fails, try to extract JSON from the text
                json_str = extract_json_from_text(response)
                if json_str:
                    experiment_plan = json.loads(json_str)
                else:
                    self.logger.error("No valid JSON found in the response")
                    return []
            
            if not experiment_plan.get('experiment_plan'):
                self.logger.error("No experiment plan found in the response")
                return []
            
            # Log the experiment plan
            self.log_experiment_plan(experiment_plan['experiment_plan'])
            
            return experiment_plan['experiment_plan']
        
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse response as JSON: {e}")
            self.logger.debug(f"Problematic JSON string: {response}")
            return []
        except Exception as e:
            self.logger.error(f"Error designing experiment: {e}")
            self.logger.debug(traceback.format_exc())
            return []

    def log_experiment_plan(self, experiment_plan):
        self.logger.info("Experiment Plan:")
        for i, step in enumerate(experiment_plan, 1):
            self.logger.info(f"Step {i}:")
            for key, value in step.items():
                if key == 'code':
                    self.logger.info(f"  {key}: <code snippet>")
                else:
                    self.logger.info(f"  {key}: {value}")
            self.logger.info("---")

    def _generate_design_prompt(self, idea):
        return {
            "task": "design_experiment",
            "idea": idea,
            "instructions": """
Design an experiment to test the given idea. The experiment plan should be a list of actions.
Each action should be a dictionary with at least an 'action' key and any necessary parameters.

Example output format:
{
    "experiment_plan": [
        {"action": "run_python_code", "code": "print('Hello, World!')"},
        {"action": "use_llm_api", "prompt": "Generate a test prompt"}
    ]
}

IMPORTANT: Your response must be a valid JSON object containing only the 'experiment_plan' key with a list of action dictionaries as its value. Do not include any additional text or explanations outside of the JSON structure.
            """,
            "output_format": "JSON"
        }

    def validate_and_fix_plan(self, methodology):
        fixed_methodology = []
        for step in methodology:
            if not isinstance(step, dict):
                self.logger.warning(f"Skipping invalid step: {step}")
                continue
            if 'action' not in step:
                self.logger.warning(f"Skipping step without action: {step}")
                continue
            if step['action'] == 'web_request':
                step = self.fix_web_request_step(step, max_retries=3)
            elif step['action'] == 'use_gpu':
                step = self.add_gpu_check(step)
            fixed_methodology.append(step)
        return fixed_methodology

    def fix_web_request_step(self, step, max_retries=3):
        if 'example.com' not in step.get('url', ''):
            return step

        for attempt in range(max_retries):
            try:
                prompt = {
                    "task": "fix_web_request",
                    "step": step,
                    "instructions": (
                        "Replace the example.com URL with a real, accessible URL that serves a similar purpose for the experiment. "
                        "Respond with a JSON object containing ONLY the fixed step, with no additional formatting or explanation. "
                        "The JSON should have 'action', 'url', and optionally 'method' keys."
                    )
                }
                if attempt > 0:
                    prompt["instructions"] += (
                        " Your previous response was invalid. Please ensure you return ONLY a JSON object "
                        "with the structure: {'action': 'web_request', 'url': 'https://real-url.com', 'method': 'GET'}"
                    )

                response = create_completion(
                    self.model_name,
                    messages=[
                        {"role": "system", "content": "You are an AI assistant specialized in fixing experiment steps. Always respond with valid JSON containing only the fixed step."},
                        {"role": "user", "content": json.dumps(prompt)}
                    ],
                    max_tokens=3500,
                    temperature=0.7,
                )
                self.logger.debug(f"LLM response for web request fix (attempt {attempt + 1}): {response}")
                
                # Remove any potential markdown formatting
                cleaned_response = re.sub(r'^```json\n|\n```$', '', response.strip())
                
                fixed_step = json.loads(cleaned_response)
                
                if isinstance(fixed_step, dict) and 'url' in fixed_step and fixed_step.get('action') == 'web_request':
                    return fixed_step
                else:
                    raise ValueError("Invalid structure in LLM response")

            except (json.JSONDecodeError, ValueError) as e:
                self.logger.warning(f"Error in fix_web_request_step (attempt {attempt + 1}): {str(e)}")
                if attempt == max_retries - 1:
                    self.logger.error(f"Failed to fix web request step after {max_retries} attempts. Returning original step.")
                    return step

        return step  # This line should never be reached due to the return in the for loop, but it's here for completeness

    def add_gpu_check(self, step):
        step['code'] = f"""
if not torch.cuda.is_available():
    print("GPU not available. Skipping GPU task.")
else:
    # Original GPU task
    {step.get('code', '# No code provided')}
"""
        return step

    def parse_text_response(self, response):
        """
        Parse a text response to extract the experiment plan.
        """
        self.logger.info("Parsing text response...")
        experiment_plan = []
        step_pattern = re.compile(r'Step (\d+):(.*?)(?=Step \d+:|$)', re.DOTALL)
        steps = step_pattern.findall(response)

        for step_num, step_content in steps:
            action_match = re.search(r'Action: (\w+)', step_content)
            if action_match:
                action = action_match.group(1)
                step = {'action': action}
                
                # Extract other parameters based on the action
                if action == 'run_python_code':
                    code_match = re.search(r'Code:(.*?)(?=\n\w+:|$)', step_content, re.DOTALL)
                    if code_match:
                        step['code'] = code_match.group(1).strip()
                elif action == 'use_llm_api':
                    prompt_match = re.search(r'Prompt:(.*?)(?=\n\w+:|$)', step_content, re.DOTALL)
                    if prompt_match:
                        step['prompt'] = prompt_match.group(1).strip()
                elif action == 'web_request':
                    url_match = re.search(r'URL: (.*?)(?=\n|$)', step_content)
                    method_match = re.search(r'Method: (GET|POST|PUT|DELETE)', step_content)
                    if url_match:
                        step['url'] = url_match.group(1).strip()
                    if method_match:
                        step['method'] = method_match.group(1)
                elif action == 'use_gpu':
                    task_match = re.search(r'Task:(.*?)(?=\n\w+:|$)', step_content, re.DOTALL)
                    if task_match:
                        step['task'] = task_match.group(1).strip()
                
                experiment_plan.append(step)

        self.logger.info(f"Parsed {len(experiment_plan)} steps from text response.")
        return experiment_plan

    def pretty_print_experiment_plan(self, experiment_plan):
        self.logger.info("=== Experiment Plan Summary ===")
        
        if not isinstance(experiment_plan, dict):
            self.logger.error(f"Invalid experiment plan type: {type(experiment_plan)}")
            return

        methodology = experiment_plan.get('methodology', [])
        
        if isinstance(methodology, list):
            self.logger.info(f"Total steps: {len(methodology)}")
            self.logger.info("============================")

            for i, step in enumerate(methodology, 1):
                if isinstance(step, dict):
                    self.logger.info(f"Step {i}:")
                    self.logger.info(f"  Action: {step.get('action', 'Unknown')}")
                    
                    # Add a brief description based on the action type
                    description = self.get_step_description(step)
                    self.logger.info(f"  Description: {description}")
                    
                    for key, value in step.items():
                        if key != 'action':
                            self.logger.info(f"  {key.capitalize()}:")
                            self.logger.info(f"{pformat(value, indent=4)}")
                else:
                    self.logger.warning(f"Step {i}: Invalid step type: {type(step)}")
                self.logger.info("----------------------------")  # Separator between steps
        else:
            self.logger.error(f"Invalid methodology type: {type(methodology)}")
            self.logger.info(f"Raw methodology content: {methodology}")

        self.logger.info("=== End of Experiment Plan ===")

    def get_step_description(self, step):
        action = step['action']
        if action == 'run_python_code':
            return "Execute Python code to perform a specific task or analysis."
        elif action == 'use_llm_api':
            return "Make a request to an LLM API to generate or process text."
        elif action == 'web_request':
            return f"Make a {step.get('method', 'GET')} request to {step.get('url', 'a specified URL')} to fetch or send data."
        elif action == 'use_gpu':
            return "Perform a GPU-intensive task, such as training or running a neural network model."
        else:
            return "Perform a custom action as part of the experiment."

    def adjust_plan(self, step, error_message):
        self.logger.info(f"Requesting plan adjustment for step: {step['action']}")
        try:
            prompt = {
                "task": "adjust_plan",
                "step": step,
                "error_message": error_message,
                "instructions": (
                    "The following step in an experiment plan encountered an error:\n"
                    f"Step: {step}"
                ),
                "output_format": "JSON"
            }

            response = create_completion(
                self.model_name,
                messages=[
                    {"role": "system", "content": "You are an AI assistant helping to adjust experiment plans."},
                    {"role": "user", "content": json.dumps(prompt)}
                ],
                max_tokens=500,
                temperature=0.7
            )

            self.logger.debug(f"Raw LLM response for plan adjustment: {response}")

            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                adjusted_step = json.loads(json_str)
                self.logger.info(f"Successfully adjusted step: {adjusted_step}")
                return adjusted_step
            else:
                self.logger.error("No valid JSON found in LLM response")
                return None

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse LLM response for plan adjustment: {e}")
            self.logger.debug(f"Problematic JSON string: {json_str}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error in plan adjustment: {e}")
            self.logger.debug(traceback.format_exc())
            return None

    def get_codebase_summary(self):
        codebase_summary = {
            "description": "AI-Research-System-3 is an autonomous AI research system designed to generate ideas, design experiments, execute them, and improve itself based on the results.",
            "main_components": [
                "IdeaGenerator: Generates research ideas using LLM API",
                "IdeaEvaluator: Evaluates and scores generated ideas",
                "ExperimentDesigner: Designs experiments based on selected ideas",
                "ExperimentExecutor: Executes designed experiments",
                "FeedbackLoop: Refines experiments based on initial results",
                "SystemAugmentor: Improves the system based on experiment outcomes",
                "Benchmarking: Evaluates system performance",
                "ReportWriter: Generates comprehensive reports of research findings",
                "LogErrorChecker: Analyzes log files for errors and warnings",
                "ErrorFixer: Attempts to fix identified errors automatically"
            ],
            "augmentable_functions": self.get_augmentable_functions()
        }
        return codebase_summary

    def get_augmentable_functions(self):
        augmentable_functions = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith('.py'):
                    with open(os.path.join(root, file), 'r') as f:
                        content = f.read()
                        class_matches = re.findall(r'class\s+(\w+):', content)
                        for class_name in class_matches:
                            method_matches = re.findall(r'def\s+(\w+)\(self', content)
                            for method_name in method_matches:
                                augmentable_functions.append(f"{class_name}.{method_name}")
        return augmentable_functions

    def get_system_specs(self):
        def get_gpu_info():
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    return f"{gpus[0].name}, {gpus[0].memoryTotal}MB"
                else:
                    return "No GPU detected"
            except:
                return "Unable to detect GPU"

        def get_installed_packages():
            return subprocess.check_output([sys.executable, '-m', 'pip', 'freeze']).decode('utf-8').split('\n')

        return {
            "os": f"{platform.system()} {platform.release()}",
            "cpu": platform.processor(),
            "ram": f"{psutil.virtual_memory().total / (1024.0 ** 3):.1f} GB",
            "storage": f"{psutil.disk_usage('/').total / (1024.0 ** 3):.1f} GB",
            "gpu": get_gpu_info(),
            "python_version": platform.python_version(),
            "available_libraries": get_installed_packages()
        }

    def register_new_actions(self, experiment_plan):
        if 'methodology' in experiment_plan and isinstance(experiment_plan['methodology'], list):
            for step in experiment_plan['methodology']:
                if isinstance(step, dict) and 'action' in step:
                    action = step['action']
                    if action not in self.action_strategies:
                        self.logger.info(f"Registering new action: {action}")
                        new_strategy = self.create_dynamic_strategy(step)
                        self.register_action(action, new_strategy)

    def create_dynamic_strategy(self, step):
        class DynamicStrategy(ActionStrategy):
            def execute(self, step, executor):
                # Generic execution logic
                if 'code' in step:
                    return executor.run_python_code(step['code'])
                elif 'prompt' in step:
                    return executor.use_llm_api(step['prompt'])
                elif 'url' in step:
                    return executor.make_web_request(step['url'], step.get('method', 'GET'))
                else:
                    raise ValueError(f"Unsupported parameters for dynamic action: {step}")
        
        return DynamicStrategy()

    def register_action(self, action_name, strategy):
        self.action_strategies[action_name] = strategy

# Define the default strategies
class RunPythonCodeStrategy(ActionStrategy):
    def execute(self, step, executor):
        return executor.run_python_code(step.get('code', ''))

class UseLLMAPIStrategy(ActionStrategy):
    def execute(self, step, executor):
        return executor.use_llm_api(step.get('prompt', ''))

class WebRequestStrategy(ActionStrategy):
    def execute(self, step, executor):
        return executor.make_web_request(step.get('url', ''), step.get('method', 'GET'))

class UseGPUStrategy(ActionStrategy):
    def execute(self, step, executor):
        return executor.use_gpu(step.get('task', ''))