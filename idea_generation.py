# idea_generation.py

import os
import json
from utils.logger import setup_logger
from utils.openai_utils import create_completion
from utils.config import initialize_openai
import logging
from utils.json_utils import parse_llm_response, extract_json_from_text
from logging import getLogger
import traceback

# Remove redundant import
# import openai

logger = setup_logger('idea_generation', 'logs/idea_generation.log')

class IdeaGenerator:
    def __init__(self, model_name, num_ideas, max_tokens=4000):
        # Initialize the IdeaGenerator with the specified model and number of ideas to generate
        self.model_name = model_name
        self.num_ideas = num_ideas
        self.max_tokens = max_tokens
        
        # Remove redundant logger initialization
        # self.logger = setup_logger('idea_generation', 'logs/idea_generation.log', console_level=logging.DEBUG)
        self.logger = logger
        
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
        self.logger.info(f"Generating ideas with model: {self.model_name}, num_ideas: {self.num_ideas}")
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
            self.logger.info(f"\nPrompt sent to API:\n{prompt}")

            # Send the prompt to the OpenAI API
            response = create_completion(
                self.model_name,
                messages=[
                    {"role": "system", "content": "You are an AI research assistant specializing in generating innovative ideas for AI system improvement."},
                    {"role": "user", "content": json.dumps(prompt)}
                ],
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            
            # Log the raw API response for debugging
            self.logger.info(f"\nRaw API response:\n{response}")
            
            parsed_response = parse_llm_response(response)
            if parsed_response is None:
                self.logger.warning("Failed to parse JSON response. Attempting to extract JSON from text.")
                parsed_response = extract_json_from_text(response)

            if parsed_response:
                # Extract ideas from the parsed JSON response
                ideas = parsed_response.get('research_ideas', [])
                ideas = [idea['description'] for idea in ideas if 'description' in idea]
                return ideas[:self.num_ideas]  # Ensure we return only the requested number of ideas
            else:
                # If JSON parsing fails, attempt to parse as text
                self.logger.warning("Failed to parse JSON response. Attempting to parse as text.")
                ideas = self.parse_text_response(response)
                return ideas[:self.num_ideas]

        except Exception as e:
            self.logger.error(f"Error generating ideas: {str(e)}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return []  # Return an empty list if an error occurs

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
