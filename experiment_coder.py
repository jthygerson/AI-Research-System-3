# experiment_coder.py

import json
from utils.logger import setup_logger
from utils.openai_utils import create_completion
from utils.config import initialize_openai
from utils import parse_llm_response  # Add this import at the top of the file

class ExperimentCoder:
    def __init__(self, model_name):
        self.model_name = model_name
        self.logger = setup_logger('experiment_coder', 'logs/experiment_coder.log')
        initialize_openai()

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
                    {"role": "system", "content": "You are an AI assistant specialized in writing Python code for scientific experiments. Always respond with valid JSON."},
                    {"role": "user", "content": json.dumps(prompt)}
                ],
                max_tokens=3500,
                temperature=0.7,
            )
            
            experiment_package = parse_llm_response(response)
            
            if experiment_package and isinstance(experiment_package, dict) and 'code' in experiment_package:
                self.logger.info("Experiment code generated successfully.")
                return experiment_package
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