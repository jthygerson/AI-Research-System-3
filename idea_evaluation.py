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
        chat_models = ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-0314', 'gpt-4-32k', 'gpt-3.5-turbo-0301', 'gpt-4o', 'gpt-4o-mini', 'o1-preview', 'o1-mini']
        try:
            evaluated_ideas = []
            for idea in ideas:
                prompt = (
                    f"Evaluate the following idea on a scale of 1-10 for each of these criteria:\n"
                    f"1. Potential to improve idea generation quality\n"
                    f"2. Potential to enhance idea evaluation effectiveness\n"
                    f"3. Potential to improve experiment design quality\n"
                    f"4. Potential to increase experiment execution efficiency and accuracy\n"
                    f"5. Potential to enhance application of research findings\n"
                    f"6. Potential to improve system reliability and performance\n"
                    f"7. Potential to enhance benchmark performance on coding tasks\n"
                    f"8. Potential to improve report quality and comprehensiveness\n"
                    f"9. Potential to increase log file error-checking accuracy\n"
                    f"10. Potential to improve error fixing effectiveness\n\n"
                    f"Idea: {idea}\n\n"
                    f"Provide the scores and a brief justification for each criterion."
                )
                
                if any(self.model_name.lower().startswith(model.lower()) for model in chat_models):
                    response = create_completion(
                        self.model_name,
                        messages=[
                            {"role": "system", "content": "You are an AI research evaluator."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=1000,
                        temperature=0.7
                    )
                else:
                    response = create_completion(
                        self.model_name,
                        prompt=prompt,
                        max_tokens=1000,
                        temperature=0.7
                    )
                
                # Parse JSON response
                try:
                    evaluation_json = json.loads(response)
                    score = evaluation_json.get('score', 0)
                    justification = evaluation_json.get('justification', '')
                except json.JSONDecodeError:
                    self.logger.error(f"Failed to parse evaluation response as JSON for idea '{idea}'.")
                    score = 0
                    justification = ''

                evaluated_ideas.append({'idea': idea, 'score': score, 'justification': justification})
                self.logger.info(f"Idea: {idea}, Score: {score}, Justification: {justification}")
            return evaluated_ideas
        except Exception as e:
            self.logger.error(f"Error evaluating ideas: {e}")
        return evaluated_ideas
