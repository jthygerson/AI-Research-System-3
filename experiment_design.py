# experiment_design.py

import os
from utils.logger import setup_logger
from utils.openai_utils import create_completion
from utils.config import initialize_openai
import json
from utils.json_utils import parse_llm_response
import textwrap
from pprint import pformat
import traceback  # Add this import at the top of the file
import re  # Add this import at the top of the file
import logging

class ExperimentDesigner:
    _instance = None

    def __new__(cls, model_name):
        if cls._instance is None:
            cls._instance = super(ExperimentDesigner, cls).__new__(cls)
            cls._instance.model_name = model_name
            cls._instance.logger = setup_logger('experiment_design', 'logs/experiment_design.log', console_level=logging.INFO)
            cls._instance.initialize_openai()
        return cls._instance

    def initialize_openai(self):
        if not hasattr(self, 'openai_initialized'):
            self.logger.info("Initializing OpenAI client for ExperimentDesigner")
            initialize_openai()
            self.openai_initialized = True

    def design_experiment(self, idea):
        self.logger.info(f"Designing experiment for idea: {idea}")
        try:
            prompt = {
                "task": "design_experiment",
                "idea": idea,
                "instructions": (
                    "Design a concrete, executable experiment plan to test the given idea "
                    "for improving AI-Research-System-3. Provide the experiment plan as a valid JSON object "
                    "with an 'experiment_plan' key containing a list of steps. Each step should be a dictionary "
                    "with an 'action' key and any necessary parameters.\n\n"
                    "Possible actions include:\n"
                    "1. 'run_python_code': Execute Python code (provide 'code' parameter)\n"
                    "2. 'use_llm_api': Make a request to an LLM API (provide 'prompt' parameter)\n"
                    "3. 'web_request': Make a web request (provide 'url' and optionally 'method' parameters)\n"
                    "4. 'use_gpu': Perform a GPU task (provide 'task' parameter)\n\n"
                    "Include the following in your plan:\n"
                    "1. Objectives: Which performance metrics the experiment aims to improve\n"
                    "2. Methodology: Steps to implement and test the idea\n"
                    "3. Resources required: Additional tools or data needed\n"
                    "4. Expected outcomes: Anticipated improvements in specific performance metrics\n"
                    "5. Evaluation criteria: How to measure the success of the experiment\n\n"
                    "Example of expected JSON format:\n"
                    "{\n"
                    "  \"experiment_plan\": [\n"
                    "    {\n"
                    "      \"action\": \"run_python_code\",\n"
                    "      \"code\": \"import tensorflow as tf\\n# Rest of the code...\"\n"
                    "    },\n"
                    "    {\n"
                    "      \"action\": \"use_llm_api\",\n"
                    "      \"prompt\": \"Analyze the following experiment results...\"\n"
                    "    },\n"
                    "    {\n"
                    "      \"action\": \"web_request\",\n"
                    "      \"url\": \"https://api.example.com/data\",\n"
                    "      \"method\": \"GET\"\n"
                    "    },\n"
                    "    {\n"
                    "      \"action\": \"use_gpu\",\n"
                    "      \"task\": \"Train neural network model XYZ\"\n"
                    "    }\n"
                    "  ],\n"
                    "  \"objectives\": [\"Improve idea generation quality\", \"Enhance experiment execution efficiency\"],\n"
                    "  \"resources_required\": [\"TensorFlow library\", \"GPU access\"],\n"
                    "  \"expected_outcomes\": [\"20% increase in idea quality scores\", \"30% reduction in experiment execution time\"],\n"
                    "  \"evaluation_criteria\": [\"Compare idea quality scores before and after implementation\", \"Measure average experiment execution time\"]\n"
                    "}\n\n"
                    "Ensure your response is a single, valid JSON object following this structure. "
                    "Ensure that all steps are executable and do not rely on non-existent resources or APIs. "
                    "For web requests, use real, accessible URLs. For GPU tasks, include a check for GPU availability."
                ),
                "output_format": "JSON"
            }

            response = create_completion(
                self.model_name,
                messages=[
                    {"role": "system", "content": "You are a world-class computer scientist specializing in AI model and system improvement. Always respond with valid JSON exactly as specified in the instructions."},
                    {"role": "user", "content": json.dumps(prompt)}
                ],
                max_tokens=3500,
                temperature=0.7,
            )
            
            self.logger.debug(f"Raw API response: {response}")

            parsed_response = parse_llm_response(response)
            if parsed_response and isinstance(parsed_response, dict) and 'experiment_plan' in parsed_response:
                experiment_plan = parsed_response['experiment_plan']
                experiment_plan = self.validate_and_fix_plan(experiment_plan)
            else:
                self.logger.warning("Failed to parse JSON response or invalid structure.")
                return None

            if not experiment_plan or not isinstance(experiment_plan, list):
                self.logger.error("Failed to generate a valid experiment plan.")
                return None

            # Validate each step in the experiment plan
            for step in experiment_plan:
                if not isinstance(step, dict) or 'action' not in step:
                    self.logger.error(f"Invalid step in experiment plan: {step}")
                    return None

            # Check for required modules
            required_modules = ['rpa']  # Add other required modules here
            for module in required_modules:
                try:
                    __import__(module)
                except ImportError:
                    self.logger.warning(f"Required module '{module}' is not installed. Please install it before running the experiment.")

            # Fix indentation in generated Python code
            for step in experiment_plan:
                if step['action'] == 'run_python_code' and 'code' in step:
                    step['code'] = textwrap.dedent(step['code']).strip()

            self.logger.info("Experiment plan:")
            self.pretty_print_experiment_plan(experiment_plan)
            return experiment_plan
        except Exception as e:
            self.logger.error(f"Error designing experiment: {str(e)}")
            self.logger.error(traceback.format_exc())
            return None

    def validate_and_fix_plan(self, plan):
        fixed_plan = []
        for step in plan:
            if step['action'] == 'web_request':
                step = self.fix_web_request_step(step, max_retries=3)
            elif step['action'] == 'use_gpu':
                step = self.add_gpu_check(step)
            fixed_plan.append(step)
        return fixed_plan

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
                    max_tokens=200,
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
        for i, step in enumerate(experiment_plan, 1):
            self.logger.info(f"Step {i}:")
            self.logger.info(f"  Action: {step['action']}")
            for key, value in step.items():
                if key != 'action':
                    if isinstance(value, str) and len(value) > 100:
                        self.logger.info(f"  {key.capitalize()}: (truncated) {value[:100]}...")
                    else:
                        self.logger.info(f"  {key.capitalize()}: {pformat(value, indent=4)}")
            self.logger.info("")  # Add a blank line between steps
