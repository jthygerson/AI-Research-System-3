# system_augmentation.py

import os
from utils.logger import setup_logger
from utils.openai_utils import create_completion
from utils.config import initialize_openai

class SystemAugmentor:
    def __init__(self, model_name):
        initialize_openai()  # Initialize OpenAI API key consistently
        self.model_name = model_name
        self.logger = setup_logger('system_augmentation', 'logs/system_augmentation.log')

    def augment_system(self, experiment_results):
        """
        Self-improves the AI Research System by adjusting its own code based on experiment results.
        """
        self.logger.info("Augmenting system based on experiment results...")
        try:
            prompt = (
                f"Based on the following experiment results:\n\n{experiment_results}\n\n"
                "Identify specific improvements that can be made to the AI Research System's code to enhance its performance. "
                "Provide the exact code modifications needed, including the file names and line numbers."
            )
            chat_models = ['gpt-3.5-turbo', 'gpt-4']
            
            self.logger.debug(f"Using model: {self.model_name}")
            
            if self.model_name in chat_models:
                self.logger.debug("Using chat model format")
                messages = [
                    {"role": "system", "content": "You are an AI research assistant."},
                    {"role": "user", "content": prompt}
                ]
                response = create_completion(
                    model=self.model_name,
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.7,
                )
            else:
                self.logger.debug("Using non-chat model format")
                response = create_completion(
                    model=self.model_name,
                    prompt=prompt,
                    max_tokens=1000,
                    temperature=0.7,
                )
            
            self.logger.info(f"Code modifications suggested: {response}")

            # Apply the code modifications
            self.apply_code_modifications(response)
        except Exception as e:
            self.logger.error(f"Error augmenting system: {e}", exc_info=True)

    def apply_code_modifications(self, code_modifications):
        """
        Applies the suggested code modifications to the system.
        """
        self.logger.info("Applying code modifications...")
        # Implement parsing of code_modifications and apply changes to files
        # Due to safety concerns, actual code modification is not implemented
        self.logger.info("Code modifications logged but not applied for safety.")
