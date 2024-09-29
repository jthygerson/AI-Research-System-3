# experiment_coder.py

import json
from utils.logger import setup_logger
from utils.openai_utils import create_completion
from utils.config import initialize_openai
from utils.json_utils import parse_llm_response  # Add this import at the top of the file
from experiment_execution import ExperimentExecutor
from utils.resource_manager import ResourceManager

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
                "Provide the complete Python code for this experiment as a JSON response."
            ),
            "response_format": {
                "code": "The complete Python code for the experiment",
                "requirements": ["List of required libraries"],
                "execution_instructions": ["List of steps to execute the experiment"]
            }
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
            
            experiment_package = parse_llm_response(response)
            
            if experiment_package and isinstance(experiment_package, dict) and 'code' in experiment_package:
                # Check if the code is complete
                if experiment_package['code'].strip().endswith(('```', '"""')):
                    self.logger.info("Experiment code generated successfully.")
                    return experiment_package
                else:
                    self.logger.warning("Generated code appears to be truncated. Attempting to complete it.")
                    complete_code = self.complete_truncated_code(experiment_package['code'])
                    if complete_code:
                        experiment_package['code'] = complete_code
                        self.logger.info("Experiment code completed successfully.")
                        return experiment_package
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
        for line in import_lines:
            if line.startswith('import'):
                requirements.add(line.split()[1].split('.')[0])
            elif line.startswith('from'):
                requirements.add(line.split()[1])
        return list(requirements)

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
            "instructions": "Complete the following truncated Python code. Ensure that all functions and the main block are properly closed."
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
            
            completed_code = parse_llm_response(response)
            if completed_code and isinstance(completed_code, str):
                return completed_code
            else:
                return None
        except Exception as e:
            self.logger.error(f"Error completing truncated code: {str(e)}")
            return None