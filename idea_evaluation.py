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
        start_time = time.time()
        self.logger.info("Evaluating ideas...")
        chat_models = ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-0314', 'gpt-4-32k', 'gpt-3.5-turbo-0301', 'gpt-4o', 'gpt-4o-mini', 'o1-preview', 'o1-mini']
        try:
            evaluated_ideas = []
            for idea in ideas:
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
                    "instructions": "Evaluate the given idea on a scale of 1-10 for each criterion. Provide a brief justification for each score."
                }

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
                
                # Log the raw response for debugging
                self.logger.debug(f"Raw response for idea '{idea}': {response}")

                # Parse JSON response
                try:
                    evaluation_data = json.loads(response)
                    scores = [evaluation_data[f'criterion_{i+1}']['score'] for i in range(10)]
                    justifications = {f'criterion_{i+1}': evaluation_data[f'criterion_{i+1}']['justification'] for i in range(10)}
                    
                    average_score = sum(scores) / len(scores)
                    
                    evaluated_idea = {
                        'idea': idea, 
                        'score': round(average_score, 2),
                        'justifications': justifications
                    }
                    evaluated_ideas.append(evaluated_idea)
                    
                    # Print the idea and its score to the terminal
                    print(f"Idea: {idea}")
                    print(f"Score: {evaluated_idea['score']}")
                    print("-" * 50)  # Separator for readability
                    
                    self.logger.info(f"Idea: {idea}, Average Score: {average_score}, Justifications: {justifications}")
                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to parse evaluation response for idea '{idea}': {e}")
                    self.logger.error(f"Raw response: {response}")  # Log the raw response for debugging
                    evaluated_idea = {
                        'idea': idea, 
                        'score': 1,  # Lowest possible score as a fallback
                        'justifications': {'error': f'Failed to parse response: {str(e)}'}
                    }
                    evaluated_ideas.append(evaluated_idea)
                    
                    # Print the idea and its score to the terminal (error case)
                    print(f"Idea: {idea}")
                    print(f"Score: {evaluated_idea['score']} (Error in evaluation)")
                    print("-" * 50)  # Separator for readability
                    
                except openai.OpenAIError as e:
                    self.logger.error(f"OpenAI API error for idea '{idea}': {str(e)}")
                    evaluated_idea = {
                        'idea': idea, 
                        'score': 1,  # Lowest possible score as a fallback
                        'justifications': {'error': f'OpenAI API error: {str(e)}'}
                    }
                    evaluated_ideas.append(evaluated_idea)
                    
                    # Print the idea and its score to the terminal (error case)
                    print(f"Idea: {idea}")
                    print(f"Score: {evaluated_idea['score']} (OpenAI API error)")
                    print("-" * 50)  # Separator for readability
                    
                idea_end_time = time.time()
                self.logger.info(f"Time to evaluate idea: {idea_end_time - idea_start_time:.2f} seconds")
            end_time = time.time()
            self.logger.info(f"Total evaluation time: {end_time - start_time:.2f} seconds")
        
            return evaluated_ideas
        except Exception as e:
            self.logger.error(f"Error evaluating ideas: {str(e)}")
            self.logger.error(traceback.format_exc())  # Log the full traceback for debugging
        return []
