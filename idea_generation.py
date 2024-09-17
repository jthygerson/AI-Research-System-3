# idea_generation.py

import os
from utils.logger import setup_logger
from utils.openai_utils import create_completion
from utils.config import initialize_openai

class IdeaGenerator:
    def __init__(self, model_name, num_ideas):
        initialize_openai()  # Initialize OpenAI API key
        self.model_name = model_name
        self.num_ideas = num_ideas
        self.logger = setup_logger('idea_generation', 'logs/idea_generation.log')

    def generate_ideas(self):
        """
        Generates research ideas using the OpenAI API.
        """
        self.logger.info("Generating ideas...")
        try:
            prompt = (
                f"Generate a list of {self.num_ideas} innovative research ideas in the field of AI, focusing on discovering new ways "
                "to improve an AI Research System's own research performance, considering resource constraints. "
                "Each idea should be concise and clear."
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
                    max_tokens=150 * self.num_ideas,
                    temperature=0.7
                )
            else:
                response = create_completion(
                    self.model_name,
                    prompt=prompt,
                    max_tokens=150 * self.num_ideas,
                    temperature=0.7
                )
            
            # Process ideas_text to extract individual ideas
            ideas = [idea.strip() for idea in response.split('\n') if idea.strip()]
            self.logger.info(f"Generated {len(ideas)} ideas")
            return ideas
        except Exception as e:
            self.logger.error(f"Error generating ideas: {e}")
            return []
