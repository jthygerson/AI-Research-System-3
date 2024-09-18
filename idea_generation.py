# idea_generation.py

import os
import json
from utils.logger import setup_logger
from utils.openai_utils import create_completion
from utils.config import initialize_openai
import openai
import traceback

class IdeaGenerator:
    openai_initialized = False

    def __init__(self, model_name, num_ideas):
        if not IdeaGenerator.openai_initialized:
            initialize_openai()  # Initialize OpenAI API key
            IdeaGenerator.openai_initialized = True
        self.model_name = model_name
        self.num_ideas = num_ideas
        self.logger = setup_logger('idea_generation', 'logs/idea_generation.log')

    def generate_ideas(self):
        """
        Generates research ideas using the OpenAI API.
        """
        self.logger.info("Generating ideas...")
        try:
            prompt = {
                "task": "generate_research_ideas",
                "num_ideas": self.num_ideas,
                "focus_areas": [
                    "Quality of idea generation",
                    "Effectiveness of idea evaluation",
                    "Quality of experiment designs",
                    "Efficiency and accuracy of experiment executions",
                    "Application of research findings",
                    "System reliability and performance",
                    "Benchmark performance on coding tasks",
                    "Report quality and comprehensiveness",
                    "Log file error-checking accuracy",
                    "Effectiveness of error fixing"
                ],
                "instructions": "Generate innovative research ideas focused on improving the AI Research System's performance in the given areas. Each idea should be concise, clear, and directly related to improving one or more of these aspects."
            }
            
            chat_models = ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-0314', 'gpt-4-32k', 'gpt-3.5-turbo-0301', 'gpt-4o', 'gpt-4o-mini', 'o1-preview', 'o1-mini']
            is_chat_model = any(self.model_name.lower().startswith(model.lower()) for model in chat_models)
            
            if is_chat_model:
                response = create_completion(
                    self.model_name,
                    messages=[
                        {"role": "system", "content": "You are an AI research assistant."},
                        {"role": "user", "content": json.dumps(prompt)}
                    ],
                    max_tokens=150 * self.num_ideas,
                    temperature=0.7
                )
            else:
                response = create_completion(
                    self.model_name,
                    prompt=json.dumps(prompt),
                    max_tokens=150 * self.num_ideas,
                    temperature=0.7
                )
            
            # Parse the JSON response
            ideas_data = json.loads(response)
            ideas = ideas_data.get('ideas', [])
            
            self.logger.info(f"Generated {len(ideas)} ideas")
            return ideas
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON response: {str(e)}")
            return []
        except openai.OpenAIError as e:
            self.logger.error(f"OpenAI API error: {str(e)}")
            return []
        except Exception as e:
            self.logger.error(f"Error generating ideas: {str(e)}")
            self.logger.error(traceback.format_exc())
            return []
