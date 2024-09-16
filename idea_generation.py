# idea_generation.py

import os
import openai
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
                "Generate a list of {} innovative research ideas in the field of AI, focusing on discovering new ways "
                "to improve an AI Research System's own research performance, considering resource constraints. "
                "Each idea should be concise and clear."
            ).format(self.num_ideas)
            
            chat_models = ['gpt-3.5-turbo', 'gpt-4']  # Define chat models
            if self.model_name in chat_models:
                messages = [
                    {"role": "system", "content": "You are an AI research assistant."},
                    {"role": "user", "content": prompt}
                ]
                response = create_completion(
                    self.model_name,
                    messages=messages,
                    max_tokens=150 * self.num_ideas,
                    temperature=0.7
                )
                ideas_text = response['choices'][0]['message']['content'].strip()
            else:
                response = create_completion(
                    self.model_name,
                    prompt=prompt,
                    max_tokens=150 * self.num_ideas,
                    temperature=0.7
                )
                ideas_text = response['choices'][0]['text'].strip()
            
            # Split ideas into a list
            ideas = ideas_text.split('\n')
            # Clean up ideas
            ideas = [idea.strip('- ').strip() for idea in ideas if idea.strip()]
            if len(ideas) > self.num_ideas:
                ideas = ideas[:self.num_ideas]
            self.logger.info(f"Generated ideas: {ideas}")
            return ideas
        except Exception as e:
            self.logger.error(f"Error generating ideas: {e}")
            return []
