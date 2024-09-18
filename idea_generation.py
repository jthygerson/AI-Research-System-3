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
        self.logger = setup_logger('idea_generation', 'logs/idea_generation.log', log_to_console=False)

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
                "output_format": "JSON",
                "instructions": "Generate innovative research ideas focused on improving the AI Research System's performance in the given areas. Each idea should be concise, clear, and directly related to improving one or more of these aspects. Provide the output in JSON format."
            }
            
            chat_models = ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-0314', 'gpt-4-32k', 'gpt-3.5-turbo-0301', 'gpt-4o', 'gpt-4o-mini', 'o1-preview', 'o1-mini']
            is_chat_model = any(self.model_name.lower().startswith(model.lower()) for model in chat_models)
            
            self.logger.info(f"Calling OpenAI API with model: {self.model_name}")
            self.logger.info(f"Is chat model: {is_chat_model}")
            self.logger.info(f"Prompt: {json.dumps(prompt, indent=2)}")
            
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
            
            self.logger.info(f"Raw API response: {response}")
            
            # Check if the response is a JSON string
            try:
                ideas_data = json.loads(response)
                ideas = ideas_data.get('research_ideas', [])
                ideas = [idea['description'] for idea in ideas if 'description' in idea]
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse JSON response. Attempting to parse as text.")
                # If it's not JSON, try to parse the text response
                ideas = self.parse_text_response(response)

            self.logger.debug(f"Generated ideas: {ideas}")
            if not ideas:
                self.logger.warning("No ideas were generated")
            return ideas
        except Exception as e:
            error_message = f"Error generating ideas: {str(e)}"
            self.logger.error(error_message)
            self.logger.error(traceback.format_exc())
            return []

    def parse_text_response(self, response):
        ideas = []
        current_idea = ""
        for line in response.split('\n'):
            if line.strip().startswith("### Idea"):
                if current_idea:
                    ideas.append(current_idea.strip())
                current_idea = line + "\n"
            else:
                current_idea += line + "\n"
        if current_idea:
            ideas.append(current_idea.strip())
        return ideas
