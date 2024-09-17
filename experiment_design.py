# experiment_design.py

import os
from utils.logger import setup_logger
from utils.openai_utils import create_completion
from utils.config import initialize_openai

class ExperimentDesigner:
    def __init__(self, model_name):
        initialize_openai()  # Initialize OpenAI API key
        self.model_name = model_name
        self.logger = setup_logger('experiment_design', 'logs/experiment_design.log')

    def design_experiment(self, idea):
        self.logger.info(f"Designing experiment for idea: {idea}")
        try:
            prompt = (
                f"Design a detailed experiment plan to test the following idea:\n\n{idea}\n\n"
                "The experiment plan should include:\n"
                "1. Objectives: Clearly state which performance metrics the experiment aims to improve\n"
                "2. Methodology: Describe the steps to implement and test the idea\n"
                "3. Resources required: List any additional tools or data needed\n"
                "4. Procedures: Provide a step-by-step guide for conducting the experiment\n"
                "5. Expected outcomes: Describe the anticipated improvements in specific performance metrics\n"
                "6. Evaluation criteria: Define how the success of the experiment will be measured\n"
                "Ensure that the experiment directly addresses one or more of the system's performance metrics."
            )
            
            chat_models = ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-0314', 'gpt-4-32k', 'gpt-3.5-turbo-0301', 'gpt-4o', 'gpt-4o-mini', 'o1-preview', 'o1-mini']
            is_chat_model = any(self.model_name.lower().startswith(model.lower()) for model in chat_models)
            
            if is_chat_model:
                response = create_completion(
                    self.model_name,
                    messages=[
                        {"role": "system", "content": "You are an AI research assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.7,
                )
            else:
                response = create_completion(
                    self.model_name,
                    prompt=prompt,
                    max_tokens=1000,
                    temperature=0.7,
                )
            
            self.logger.info(f"Experiment plan: {response}")
            return response
        except Exception as e:
            self.logger.error(f"Error designing experiment: {e}")
            return ""
