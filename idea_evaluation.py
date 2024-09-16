# idea_evaluation.py

import os
import openai
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
        """
        self.logger.info("Evaluating ideas...")
        scored_ideas = []
        chat_models = ['gpt-3.5-turbo', 'gpt-4']
        for idea in ideas:
            try:
                prompt = (
                    f"Evaluate the following research idea based on novelty and probability of success on a scale "
                    f"from 1 to 10 (10 being highest). Provide the score and a brief justification.\n\nIdea: {idea}"
                )
                
                if self.model_name in chat_models:
                    messages = [
                        {"role": "system", "content": "You are an AI research evaluator."},
                        {"role": "user", "content": prompt}
                    ]
                    response = create_completion(
                        self.model_name,
                        messages=messages,
                        max_tokens=150,
                        temperature=0.5
                    )
                    evaluation = response['choices'][0]['message']['content'].strip()
                else:
                    response = create_completion(
                        self.model_name,
                        prompt=prompt,
                        max_tokens=150,
                        temperature=0.5
                    )
                    evaluation = response['choices'][0]['text'].strip()
                
                # Extract score and justification
                lines = evaluation.split('\n')
                score_line = next((line for line in lines if 'Score' in line.lower()), '')
                justification = '\n'.join(lines[1:]).strip() if len(lines) > 1 else ''
                
                # Remove 'Justification: ' prefix if present
                if justification.lower().startswith('justification:'):
                    justification = justification[len('Justification:'):].strip()
                
                # Extract score number
                score_str = ''.join(filter(str.isdigit, score_line))
                score = int(score_str) if score_str else 0
                
                scored_ideas.append({'idea': idea, 'score': score, 'justification': justification})
                self.logger.info(f"Idea: {idea}, Score: {score}, Justification: {justification}")
            except Exception as e:
                self.logger.error(f"Error evaluating idea '{idea}': {e}")
        return scored_ideas
