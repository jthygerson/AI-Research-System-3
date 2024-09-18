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
    def __init__(self, model_name):
        self.model_name = model_name
        self.logger = setup_logger('idea_evaluation', 'logs/idea_evaluation.log')
        self.debug_logger = getLogger('debug')
        self.initialize_openai()

    def initialize_openai(self):
        self.logger.info("Initializing OpenAI client for IdeaEvaluator")
        initialize_openai()  # This should reinitialize the OpenAI client

    def evaluate_ideas(self, ideas):
        """
        Evaluates ideas based on multiple criteria.
        """
        self.debug_logger.info(f"Evaluating {len(ideas)} ideas")
        self.logger.debug("Evaluating ideas...")
        scored_ideas = []
        
        for idea in ideas:
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
                    scores = evaluation_data.get('scores', {})
                    self.logger.debug(f"Parsed scores: {scores}")
                    
                    total_score = sum(int(score) for score in scores.values() if isinstance(score, (int, str)) and str(score).isdigit())
                    justifications = evaluation_data.get('justifications', {})
                    
                    self.logger.info(f"Total score for idea '{idea[:50]}...': {total_score}")
                    scored_ideas.append({
                        'idea': idea,
                        'score': total_score,
                        'justifications': justifications
                    })
                except json.JSONDecodeError:
                    self.logger.warning("Failed to parse JSON response. Attempting to parse as text.")
                    scores, justifications = self.parse_text_evaluation(response)
                    total_score = sum(scores)
                    scored_ideas.append({
                        'idea': idea,
                        'score': total_score,
                        'justifications': justifications
                    })

            except Exception as e:
                self.logger.error(f"Error evaluating idea '{idea[:50]}...': {str(e)}")
                self.logger.error(traceback.format_exc())

        self.debug_logger.debug(f"Parsed evaluation data: {json.dumps(evaluation_data)}")
        return scored_ideas

    def parse_text_evaluation(self, response):
        scores = []
        justifications = {}
        current_criterion = ""
        for line in response.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                if key in self.criteria:
                    current_criterion = key
                    score_match = re.search(r'\d+', value)
                    if score_match:
                        scores.append(int(score_match.group()))
                    justifications[current_criterion] = value
        return scores, justifications
