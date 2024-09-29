# experiment_coder.py

import json
from utils.logger import setup_logger
from utils.openai_utils import create_completion
from utils.config import initialize_openai
from utils.json_utils import parse_llm_response  # Change this line
from experiment_execution import ExperimentExecutor
from utils.resource_manager import ResourceManager
import re
import sys

class ExperimentCoder:
    def __init__(self, model_name):
        self.model_name = model_name
        self.logger = setup_logger('experiment_coder', 'logs/experiment_coder.log')
        initialize_openai()
        self.executor = ExperimentExecutor(ResourceManager(), model_name)

    def generate_experiment_code(self, experiment_plan):
        self.logger.info("Generating experiment code based on the provided plan...")
        
        prompt = {
            "task": "generate_experiment_code",
            "experiment_plan": experiment_plan,
            "instructions": (
                "Based on the provided experiment plan, write a Python program that executes the experiment. "
                "Follow these guidelines:\n"
                "1. Use clear and concise Python code.\n"
                "2. Include necessary imports at the beginning of the file.\n"
                "3. Implement each step of the methodology as a separate function.\n"
                "4. Create a main function that orchestrates the execution of all steps.\n"
                "5. Include error handling and logging where appropriate.\n"
                "6. Add comments to explain complex parts of the code.\n"
                "7. Ensure the code is compatible with Python 3.7+.\n"
                "Provide the complete Python code for this experiment."
            )
        }
        
        try:
            response = create_completion(
                self.model_name,
                messages=[
                    {"role": "system", "content": "You are an AI research assistant specializing in coding experiments."},
                    {"role": "user", "content": json.dumps(prompt)}
                ],
                max_tokens=4096,  # Increase the max_tokens to allow for longer responses
                temperature=0.7,
            )
            
            # Log the full response from the LLM
            self.logger.debug(f"Full LLM response:\n{response}")
            
            # Extract the code from the response
            code = self.extract_code_from_response(response)
            
            if code:
                # Check if the code is complete
                if code.strip().endswith(('```', '"""')):
                    self.logger.info("Experiment code generated successfully.")
                    return {"code": code, "requirements": self.extract_requirements(code)}
                else:
                    self.logger.warning("Generated code appears to be truncated. Attempting to complete it.")
                    complete_code = self.complete_truncated_code(code)
                    if complete_code:
                        self.logger.info("Experiment code completed successfully.")
                        return {"code": complete_code, "requirements": self.extract_requirements(complete_code)}
                    else:
                        self.logger.error("Failed to complete truncated code.")
                        return None
            else:
                self.logger.error("Failed to generate valid experiment code.")
                return None
        except Exception as e:
            self.logger.error(f"Error generating experiment code: {str(e)}")
            return None

    def create_coding_prompt(self, experiment_plan):
        return f"""
        Based on the following experiment plan, write a Python program that executes the experiment:

        Experiment Plan:
        {json.dumps(experiment_plan, indent=2)}

        Please follow these guidelines:
        1. Use clear and concise Python code.
        2. Include necessary imports at the beginning of the file.
        3. Implement each step of the methodology as a separate function.
        4. Create a main function that orchestrates the execution of all steps.
        5. Include error handling and logging where appropriate.
        6. Add comments to explain complex parts of the code.
        7. Ensure the code is compatible with Python 3.7+.

        Provide the complete Python code for this experiment.
        """

    def parse_response(self, response):
        # Extract the Python code from the LLM response
        # This method may need to be adjusted based on the actual response format
        if isinstance(response, str):
            return response.strip()
        elif hasattr(response, 'choices') and response.choices:
            return response.choices[0].message.content.strip()
        else:
            return None

    def extract_requirements(self, code):
        # Extract required libraries from the import statements
        import_lines = [line for line in code.split('\n') if line.startswith('import') or line.startswith('from')]
        requirements = set()
        builtin_modules = set(sys.builtin_module_names)
        stdlib_modules = set(sys.stdlib_module_names) if hasattr(sys, 'stdlib_module_names') else set()
        
        for line in import_lines:
            if line.startswith('import'):
                module = line.split()[1].split('.')[0]
                if module not in builtin_modules and module not in stdlib_modules:
                    requirements.add(module)
            elif line.startswith('from'):
                module = line.split()[1].split('.')[0]
                if module not in builtin_modules and module not in stdlib_modules:
                    requirements.add(module)
        
        # Map some common module names to their correct package names
        package_mapping = {
            'scipy': 'scipy',
            'sklearn': 'scikit-learn',
            'PIL': 'pillow',
        }
        
        return [package_mapping.get(req, req) for req in requirements]

    def generate_execution_instructions(self, experiment_plan):
        # Generate instructions for executing the experiment
        instructions = [
            "1. Ensure all required libraries are installed.",
            "2. Set up the necessary environment variables if any.",
            "3. Run the Python script generated for this experiment.",
            "4. Monitor the execution and check the logs for any errors or warnings.",
            "5. Collect the output data as specified in the data_collection section of the experiment plan.",
            f"6. Analyze the results according to the analysis plan: {experiment_plan.get('analysis_plan', 'Not specified')}",
        ]
        return instructions

    def complete_truncated_code(self, truncated_code):
        completion_prompt = {
            "task": "complete_truncated_code",
            "truncated_code": truncated_code,
            "instructions": "Complete the following truncated Python code. Ensure that all functions and the main block are properly closed. Return only the completed code without any additional text or formatting."
        }
        
        try:
            response = create_completion(
                self.model_name,
                messages=[
                    {"role": "system", "content": "You are an AI research assistant specializing in coding experiments."},
                    {"role": "user", "content": json.dumps(completion_prompt)}
                ],
                max_tokens=2048,
                temperature=0.7,
            )
            
            completed_code = self.extract_code_from_response(response)
            if completed_code:
                return completed_code
            else:
                return None
        except Exception as e:
            self.logger.error(f"Error completing truncated code: {str(e)}")
            return None

    def extract_code_from_response(self, response):
        if isinstance(response, str):
            # Try to extract code from markdown code blocks
            code_blocks = re.findall(r'```python\n(.*?)```', response, re.DOTALL)
            if code_blocks:
                return '\n'.join(code_blocks)
            # If no code blocks found, return the entire response
            return response.strip()
        elif hasattr(response, 'choices') and response.choices:
            content = response.choices[0].message.content.strip()
            # Try to extract code from markdown code blocks
            code_blocks = re.findall(r'```python\n(.*?)```', content, re.DOTALL)
            if code_blocks:
                return '\n'.join(code_blocks)
            # If no code blocks found, return the entire content
            return content
        else:
            return None