# idea_evaluation.py

import os
import re  # Import regex module
import json  # Import JSON module for parsing
import ast  # Import AST module for safer parsing
from utils.logger import setup_logger
from utils.openai_utils import create_completion
from utils.config import initialize_openai
from utils.json_utils import parse_llm_response, extract_json_from_text  # Import the new function
import time
from utils.constants import chat_models
import traceback  # Import traceback module for logging full error stack
# Remove import of openai here
from logging import getLogger
import logging

class IdeaEvaluator:
    def __init__(self, model_name, max_tokens=4000):
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.logger = setup_logger('idea_evaluation', 'logs/idea_evaluation.log', console_level=logging.INFO)
        self.debug_logger = setup_logger('idea_evaluation_debug', 'logs/idea_evaluation_debug.log', level=logging.DEBUG)
        initialize_openai()

    def evaluate_ideas(self, ideas):
        self.logger.info(f"Evaluating {len(ideas)} ideas")
        prompt = self._generate_evaluation_prompt(ideas)
        
        try:
            response = create_completion(
                self.model_name,
                messages=[
                    {"role": "system", "content": "You are an AI research assistant. Evaluate the given ideas based on their potential impact, feasibility, and originality."},
                    {"role": "user", "content": json.dumps(prompt)}
                ],
                max_tokens=self.max_tokens
            )
            
            evaluation = json.loads(response)
            
            if not evaluation.get('scores') or not evaluation.get('justifications'):
                self.logger.error("Invalid evaluation response structure")
                return []
            
            scored_ideas = []
            for i, idea in enumerate(ideas):
                score = sum(evaluation['scores'][i])
                justifications = evaluation['justifications'][i]
                scored_ideas.append({
                    'idea': idea,
                    'score': score,
                    'justifications': justifications
                })
            
            return scored_ideas
        
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse response as JSON: {response}")
            return []
        except Exception as e:
            self.logger.error(f"Error evaluating ideas: {e}")
            return []

    def _generate_evaluation_prompt(self, ideas):
        return {
            "task": "evaluate_ideas",
            "ideas": ideas,
            "instructions": """
Evaluate each idea based on its potential impact, feasibility, and originality. Provide a score for each criterion (0-10) and a brief justification.

Example output format:
{
    "scores": [
        [8, 7, 9],
        [6, 8, 7]
    ],
    "justifications": [
        {
            "impact": "High potential for revolutionizing the field",
            "feasibility": "Requires advanced technology, but achievable",
            "originality": "Novel approach not seen before"
        },
        {
            "impact": "Moderate improvement over existing methods",
            "feasibility": "Can be implemented with current resources",
            "originality": "Builds on existing ideas with some new elements"
        }
    ]
}
            """,
            "output_format": "JSON"
        }

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
                    {"role": "system", "content": "You are an AI assistant specialized in evaluating research ideas."},
                    {"role": "user", "content": json.dumps(prompt)}
                ],
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            
            self.debug_logger.debug(f"Raw API response: {response}")
            
            evaluation_data = parse_llm_response(response)
            
            if evaluation_data is None:
                self.logger.warning(f"Failed to parse response for idea '{idea[:50]}...'. Attempting to extract JSON from text.")
                evaluation_data = extract_json_from_text(response)

            if evaluation_data is None:
                self.logger.error(f"Failed to parse response for idea '{idea[:50]}...'. Raw response: {response}")
                return self.fallback_evaluation(idea, response)

            # Ensure evaluation_data is a dictionary
            if not isinstance(evaluation_data, dict):
                self.logger.error(f"Parsed data is not a dictionary for idea '{idea[:50]}...'. Parsed data: {evaluation_data}")
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
