import logging

class SafetyChecker:
    def __init__(self):
        self.logger = logging.getLogger('safety_checker')
        self.logger.setLevel(logging.DEBUG)

    def check_experiment_plan(self, experiment_plan):
        """
        Checks the safety of the experiment plan.
        
        Parameters:
            experiment_plan (list): List of steps in the experiment plan.
        
        Returns:
            bool: True if the plan is safe, False otherwise.
        """
        self.logger.info("Checking experiment plan for safety...")
        # Implement safety checks here
        for step in experiment_plan:
            if not self.is_step_safe(step):
                self.logger.error(f"Unsafe step detected: {step}")
                return False
        return True

    def is_step_safe(self, step):
        """
        Checks if a single step is safe.
        
        Parameters:
            step (dict): A single step in the experiment plan.
        
        Returns:
            bool: True if the step is safe, False otherwise.
        """
        # Implement specific safety checks for each step
        action = step.get('action')
        if action == 'run_python_code':
            code = step.get('code', '')
            if 'import os' in code or 'import subprocess' in code:
                return False
        # Add more checks as needed
        return True