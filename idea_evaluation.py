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
        self.logger.info("Evaluating ideas...")
        try:
            evaluated_ideas = []
            for i, idea in enumerate(ideas, 1):
                idea_start_time = time.time()
                
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

                self.logger.info(f"Evaluating idea: {idea}")
                self.logger.info(f"Calling OpenAI API with model: {self.model_name}")
                self.logger.info(f"Is chat model: {is_chat_model}")
                self.logger.info(f"Prompt: {json.dumps(prompt, indent=2)}")

                is_chat_model = any(self.model_name.lower().startswith(model.lower()) for model in chat_models)
                
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
                
                self.logger.info(f"Raw API response for idea '{idea}': {response}")

                # Parse response
                try:
                    evaluation_data = json.loads(response)
                    scores = [evaluation_data[f'criterion_{i+1}']['score'] for i in range(10)]
                    justifications = {f'criterion_{i+1}': evaluation_data[f'criterion_{i+1}']['justification'] for i in range(10)}
                except json.JSONDecodeError:
                    # If it's not JSON, try to parse the text response
                    scores, justifications = self.parse_text_evaluation(response)

                average_score = sum(scores) / len(scores)

                evaluated_idea = {
                    'idea': idea, 
                    'score': round(average_score, 2),
                    'justifications': justifications
                }
                evaluated_ideas.append(evaluated_idea)
                
                self.logger.info(f"Idea: {idea}, Average Score: {average_score}, Justifications: {justifications}")
            
            return evaluated_ideas
        except Exception as e:
            error_message = f"Error evaluating ideas: {str(e)}"
            self.logger.error(error_message)
            self.logger.error(traceback.format_exc())
            return []

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
