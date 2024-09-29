# feedback_loop.py

import json
from utils.logger import setup_logger
from utils.openai_utils import create_completion

class FeedbackLoop:
    def __init__(self, model_name, max_tokens=4000):
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.logger = setup_logger('feedback_loop', 'logs/feedback_loop.log')

    def refine_experiment(self, initial_plan, results):
        self.logger.info("Refining experiment based on results")
        prompt = self._generate_refinement_prompt(initial_plan, results)
        
        try:
            response = create_completion(
                self.model_name,
                messages=[
                    {"role": "system", "content": "You are an AI research assistant. Refine the experiment plan based on the initial results."},
                    {"role": "user", "content": json.dumps(prompt)}
                ],
                max_tokens=self.max_tokens
            )
            
            refined_plan = json.loads(response)
            
            if not refined_plan.get('refined_plan'):
                self.logger.error("No refined plan found in the response")
                return initial_plan
            
            return refined_plan['refined_plan']
        
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse response as JSON: {response}")
            return initial_plan
        except Exception as e:
            self.logger.error(f"Error refining experiment: {e}")
            return initial_plan

    def _generate_refinement_prompt(self, initial_plan, results):
        return {
            "task": "refine_experiment",
            "initial_plan": initial_plan,
            "results": results,
            "instructions": """
Refine the experiment plan based on the initial results. Suggest improvements or modifications to the plan.

Example output format:
{
    "refined_plan": [
        {"action": "run_python_code", "code": "print('Refined experiment')"},
        {"action": "use_llm_api", "prompt": "Generate a refined test prompt"}
    ]
}
            """,
            "output_format": "JSON"
        }