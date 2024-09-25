# idea_evaluation.py

import os
import re  # Import regex module
import json  # Import JSON module for parsing
import ast  # Import AST module for safer parsing
from utils.logger import setup_logger
from utils.openai_utils import create_completion
from utils.config import initialize_openai
import time
from utils.constants import chat_models
import traceback  # Import traceback module for logging full error stack
import openai
from logging import getLogger

class IdeaEvaluator:
    _instance = None

    def __new__(cls, model_name):
        if cls._instance is None:
            cls._instance = super(IdeaEvaluator, cls).__new__(cls)
            cls._instance.model_name = model_name
            cls._instance.logger = setup_logger('idea_evaluation', 'logs/idea_evaluation.log')
            cls._instance.debug_logger = setup_logger('debug', 'logs/detailed_debug.log')
            cls._instance.initialize_openai()
        return cls._instance

    def initialize_openai(self):
        if not hasattr(self, 'openai_initialized'):
            self.logger.info("Initializing OpenAI client for IdeaEvaluator")
            initialize_openai()
            self.openai_initialized = True

    def evaluate_ideas(self, ideas):
        self.debug_logger.debug(f"Starting evaluation of {len(ideas)} ideas")
        self.logger.info(f"Evaluating {len(ideas)} ideas")
        scored_ideas = []
        
        for idea in ideas:
            scored_idea = self.evaluate_single_idea(idea)
            if scored_idea:
                scored_ideas.append(scored_idea)
                self.logger.info(f"Evaluated idea with score: {scored_idea['score']}")

        return scored_ideas

    def evaluate_single_idea(self, idea):
        try:
            prompt = {
                "task": "evaluate_research_idea",
                "idea": idea,
                "criteria": [
                    "Potential to improve idea generation quality",
                    "Potential to enhance idea evaluation effectiveness",
                    "Potential to improve experiment design quality",
                    "Potential to increase experiment execution efficiency and accuracy",
                    "Potential to enhance application of research findings",
                    "Potential to improve system reliability and performance",
                    "Potential to enhance benchmark performance on coding tasks",
                    "Potential to improve report quality and comprehensiveness",
                    "Potential to increase log file error-checking accuracy",
                    "Potential to improve error fixing effectiveness"
                ],
                "instructions": "Evaluate the given idea on a scale of 1-10 for each criterion. Provide a brief justification for each score. Return the result as a JSON object with 'scores' and 'justifications' keys.",
                "output_format": "JSON"
            }
            
            self.debug_logger.debug(f"Evaluation prompt: {json.dumps(prompt)}")
            
            response = create_completion(
                self.model_name,
                messages=[
                    {"role": "system", "content": "You are an AI research evaluator."},
                    {"role": "user", "content": json.dumps(prompt)}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            self.debug_logger.debug(f"Raw API response: {response}")
            
            try:
                evaluation_data = json.loads(response)
            except json.JSONDecodeError:
                self.logger.error(f"Failed to parse JSON response for idea '{idea[:50]}...'. Raw response: {response}")
                return self.fallback_evaluation(idea, response)

            scores = evaluation_data.get('scores', {})
            total_score = sum(int(score) for score in scores.values() if isinstance(score, (int, str)) and str(score).isdigit())
            justifications = evaluation_data.get('justifications', {})
            
            self.logger.info(f"Total score for idea '{idea[:50]}...': {total_score}")
            return {
                'idea': idea,
                'score': total_score,
                'justifications': justifications
            }

        except Exception as e:
            self.logger.error(f"Error evaluating idea '{idea[:50]}...': {str(e)}")
            self.logger.error(traceback.format_exc())
            return None

    def fallback_evaluation(self, idea, response):
        self.logger.warning(f"Using fallback evaluation for idea '{idea[:50]}...'")
        # Implement a simple scoring mechanism based on keyword matching
        keywords = ["improve", "enhance", "increase", "optimize", "innovative"]
        score = sum(10 for keyword in keywords if keyword.lower() in response.lower())
        return {
            'idea': idea,
            'score': score,
            'justifications': {"fallback": "Evaluation based on keyword matching due to JSON parsing failure."}
        }

# Note: This IdeaEvaluator class is used by the orchestrator to evaluate and score the ideas
# generated by the IdeaGenerator. The scored ideas are then used to select the best idea
# for further experimentation and research.
