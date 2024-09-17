# idea_evaluation.py

import os
import re  # Import regex module
import json  # Import JSON module for parsing
from utils.logger import setup_logger
from utils.openai_utils import create_completion
from utils.config import initialize_openai

class IdeaEvaluator:
    def __init__(self, model_name):
        initialize_openai()  # Initialize OpenAI API key
        self.model_name = model_name
        self.logger = setup_logger('idea_evaluation', 'logs/idea_evaluation.log')

    def evaluate_ideas(self, ideas):
        """
        Evaluates ideas based on novelty and probability of success.

        Parameters:
            ideas (list): List of idea strings to evaluate.

        Returns:
            list: List of dictionaries with idea, score, and justification.
        """
        self.logger.info("Evaluating ideas...")
        scored_ideas = []
        chat_models = ['gpt-3.5-turbo', 'gpt-4']
        for idea in ideas:
            try:
                prompt = (
                    f"Evaluate the following research idea based on novelty and probability of success on a scale "
                    f"from 1 to 10 (10 being highest). Provide the score and a brief justification in JSON format.\n\n"
                    f"Idea: {idea}\n\n"
                    f"Example Response:\n"
                    f"{{\n"
                    f'  "score": 8,\n'
                    f'  "justification": "Innovative and feasible."\n'
                    f"}}"
                )
                
                if self.model_name in chat_models:
                    messages = [
                        {"role": "system", "content": "You are an AI research evaluator."},
                        {"role": "user", "content": prompt}
                    ]
                    response = create_completion(
                        self.model_name,
                        messages=messages if self.model_name in chat_models else None,
                        prompt=prompt if self.model_name not in chat_models else None,
                        max_tokens=1000,
                        temperature=0.7
                    )
                    # Use the response directly, no need for parsing
                else:
                    response = create_completion(
                        self.model_name,
                        prompt=prompt,
                        max_tokens=1000,
                        temperature=0.7
                    )
                    # Use the response directly, no need for parsing
                
                # Parse JSON response
                try:
                    evaluation_json = json.loads(evaluation)
                    score = evaluation_json.get('score', 0)
                    justification = evaluation_json.get('justification', '')
                except json.JSONDecodeError:
                    self.logger.error(f"Failed to parse evaluation response as JSON for idea '{idea}'.")
                    score = 0
                    justification = ''
    
                scored_ideas.append({'idea': idea, 'score': score, 'justification': justification})
                self.logger.info(f"Idea: {idea}, Score: {score}, Justification: {justification}")
            except Exception as e:
                self.logger.error(f"Error evaluating idea '{idea}': {e}")
        return scored_ideas
