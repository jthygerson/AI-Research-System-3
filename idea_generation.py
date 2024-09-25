# idea_generation.py

import os
import json
from utils.logger import setup_logger
from utils.openai_utils import create_completion
from utils.config import initialize_openai
import logging
from utils.json_utils import parse_llm_response
from logging import getLogger

# Remove redundant import
# import openai

logger = logging.getLogger(__name__)

class IdeaGenerator:
    def __init__(self, model_name, num_ideas):
        # Initialize the IdeaGenerator with the specified model and number of ideas to generate
        self.model_name = model_name
        self.num_ideas = num_ideas
        
        # Remove redundant logger initialization
        # self.logger = setup_logger('idea_generation', 'logs/idea_generation.log', console_level=logging.DEBUG)
        self.debug_logger = getLogger('debug')
        
        # Initialize the OpenAI client
        self.initialize_openai()

    def initialize_openai(self):
        # Initialize the OpenAI client using the configuration from utils.config
        self.logger.info("Initializing OpenAI client for IdeaGenerator")
        initialize_openai()  # This should reinitialize the OpenAI client

    def generate_ideas(self):
        """
        Generates research ideas using the OpenAI API.
        This method is called by the orchestrator to create new ideas for each experiment run.
        """
        self.debug_logger.info(f"Generating ideas with model: {self.model_name}, num_ideas: {self.num_ideas}")
        try:
            # Construct the prompt for idea generation
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
                "instructions": "Generate innovative research ideas focused on improving the AI Research System's performance in the given areas. Each idea should be concise, clear, and directly related to improving one or more of these aspects. Provide the output as a valid JSON object with a 'research_ideas' key containing an array of idea objects, each with a 'description' field. Do not include any text outside of the JSON object."
            }

            # Log the prompt for debugging purposes
            self.debug_logger.info(f"\nPrompt sent to API:\n{prompt}")

            # Send the prompt to the OpenAI API
            response = create_completion(
                self.model_name,
                messages=[
                    {"role": "system", "content": "You are an AI research assistant."},
                    {"role": "user", "content": json.dumps(prompt)}
                ],
                max_tokens=150 * self.num_ideas,
                temperature=0.7
            )
            
            # Log the raw API response for debugging
            self.debug_logger.info(f"\nRaw API response:\n{response}")
            
            # Parse the JSON response
            parsed_response = parse_llm_response(response)
            if parsed_response:
                # Extract ideas from the parsed JSON response
                ideas = parsed_response.get('research_ideas', [])
                ideas = [idea['description'] for idea in ideas if 'description' in idea]
                return ideas[:self.num_ideas]  # Ensure we return only the requested number of ideas
            else:
                # If JSON parsing fails, attempt to parse as text
                self.logger.warning("Failed to parse JSON response. Attempting to parse as text.")
                ideas = self.parse_text_response(response)

            # Log the generated ideas for debugging
            self.debug_logger.debug(f"Generated ideas: {ideas}")
            if not ideas:
                self.logger.warning("No ideas were generated")
            return ideas
        except Exception as e:
            # Log any errors that occur during idea generation
            error_message = f"Error generating ideas: {str(e)}"
            self.logger.error(error_message)
            self.logger.error(traceback.format_exc())
            return []

    def parse_text_response(self, response):
        # Fallback method to parse ideas from a text response if JSON parsing fails
        ideas = []
        lines = response.strip().split('\n')
        for line in lines:
            if line.strip().startswith('"description":'):
                idea = line.split(':', 1)[1].strip().strip('"').strip(',')
                ideas.append(idea)
        return ideas

# Note: This IdeaGenerator class is used by the orchestrator to generate ideas for each experiment run.
# The generated ideas are then passed to the IdeaEvaluator for scoring and selection of the best idea.
