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

class IdeaEvaluator:
    openai_initialized = False

    def __init__(self, model_name):
        if not IdeaEvaluator.openai_initialized:
            initialize_openai()  # Initialize OpenAI API key
            IdeaEvaluator.openai_initialized = True
        self.model_name = model_name
        self.logger = setup_logger('idea_evaluation', 'logs/idea_evaluation.log')

    def evaluate_ideas(self, ideas):
        """
        Evaluates ideas based on multiple criteria.

        Parameters:
            ideas (list): List of idea strings to evaluate.

        Returns:
            list: List of dictionaries with idea, score, and justifications.
        """
        self.logger.debug("Evaluating ideas...")
        scored_ideas = []
        chat_models = ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-0314', 'gpt-4-32k', 'gpt-3.5-turbo-0301', 'gpt-4o', 'gpt-4o-mini', 'o1-preview', 'o1-mini']
        is_chat_model = any(self.model_name.lower().startswith(model.lower()) for model in chat_models)
        
        self.logger.debug(f"Calling OpenAI API with model: {self.model_name}")
        self.logger.debug(f"Is chat model: {is_chat_model}")

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
                    "instructions": "Evaluate the given idea on a scale of 1-10 for each criterion. Provide a brief justification for each score.",
                    "output_format": "JSON"
                }

                self.logger.debug(f"Evaluating idea: {idea}")
                self.logger.debug(f"Prompt: {json.dumps(prompt, indent=2)}")

                if is_chat_model:
                    response = create_completion(
                        self.model_name,
                        messages=[
                            {"role": "system", "content": "You are an AI research evaluator."},
                            {"role": "user", "content": json.dumps(prompt)}
                        ],
                        max_tokens=1000,
                        temperature=0.7
                    )
                else:
                    response = create_completion(
                        self.model_name,
                        prompt=json.dumps(prompt),
                        max_tokens=1000,
                        temperature=0.7
                    )
                
                self.logger.debug(f"Raw API response for idea '{idea}': {response}")

                # Parse response
                try:
                    cleaned_response = response.strip()
                    if cleaned_response.startswith("```json"):
                        cleaned_response = cleaned_response[7:]  # Remove ```json
                    if cleaned_response.endswith("```"):
                        cleaned_response = cleaned_response[:-3]  # Remove closing ```
                    
                    evaluation_data = json.loads(cleaned_response)
                    scores = []
                    justifications = {}
                    for i, criterion in enumerate(prompt['criteria'], 1):
                        criterion_data = evaluation_data.get(f'criterion_{i}', {})
                        scores.append(criterion_data.get('score', 0))
                        justifications[f'criterion_{i}'] = criterion_data.get('justification', '')
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
                self.logger.error(f"Error evaluating idea '{idea}': {str(e)}")
                self.logger.error(traceback.format_exc())

        return scored_ideas

    def parse_text_evaluation(self, response):
        scores = []
        justifications = {}
        current_criterion = ""
        for line in response.split('\n'):
            if line.strip().startswith("Criterion"):
                current_criterion = line.strip().split(':')[0]
                score_match = re.search(r'Score: (\d+)', line)
                if score_match:
                    scores.append(int(score_match.group(1)))
            elif line.strip().startswith("Justification:"):
                justifications[current_criterion] = line.strip()[14:]
        return scores, justifications
