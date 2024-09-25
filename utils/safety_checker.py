import logging
import re

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
        action = step.get('action')
        if action == 'run_python_code':
            code = step.get('code', '')
            return self.is_code_safe(code)
        elif action == 'web_request':
            url = step.get('url', '')
            return self.is_url_safe(url)
        # Add more checks for other actions as needed
        return True

    def is_code_safe(self, code):
        # Check for potentially dangerous patterns
        dangerous_patterns = [
            r'subprocess\.call',
            r'os\.system',
            r'eval\(',
            r'exec\(',
            r'__import__\(',
            r'open\(.+,\s*[\'"]w[\'"]\)',  # Writing to files
            r'requests\.post',  # Prevent unauthorized data exfiltration
        ]
        for pattern in dangerous_patterns:
            if re.search(pattern, code):
                self.logger.warning(f"Potentially unsafe code pattern detected: {pattern}")
                return False
        return True

    def is_url_safe(self, url):
        # Basic URL validation
        if not url.startswith(('http://', 'https://')):
            self.logger.warning(f"Invalid URL scheme: {url}")
            return False
        # You might want to add a whitelist of allowed domains here
        return True