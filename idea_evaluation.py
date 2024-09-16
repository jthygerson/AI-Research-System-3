# idea_evaluation.py

import os
import openai
from utils.logger import setup_logger

class IdeaEvaluator:
    def __init__(self, model_name):
        self.model_name = model_name
        self.logger = setup_logger('idea_evaluation', 'logs/idea_evaluation.log')
        openai.api_key = os.getenv('OPENAI_API_KEY')

    def evaluate_ideas(self, ideas):
        """
        Evaluates ideas based on novelty and probability of success.
        """
        self.logger.info("Evaluating ideas...")
        scored_ideas = []
        for idea in ideas:
            try:
                prompt = (
                    f"Evaluate the following research idea based on novelty and probability of success on a scale "
                    f"from 1 to 10 (10 being highest). Provide the score and a brief justification.\n\nIdea: {idea}"
                )
                response = openai.Completion.create(
                    engine=self.model_name,
                    prompt=prompt,
                    max_tokens=150,
                    n=1,
                    stop=None,
                    temperature=0.5,
                )
                evaluation = response['choices'][0]['text'].strip()
                # Extract score and justification
                lines = evaluation.split('\n')
                score_line = next((line for line in lines if 'Score' in line), '')
                justification = '\n'.join(lines[1:]).strip()
                score = int(''.join(filter(str.isdigit, score_line)))
                scored_ideas.append({'idea': idea, 'score': score, 'justification': justification})
                self.logger.info(f"Idea: {idea}, Score: {score}, Justification: {justification}")
            except Exception as e:
                self.logger.error(f"Error evaluating idea '{idea}': {e}")
        return scored_ideas
