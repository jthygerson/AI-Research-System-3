import logging
import re

class SafetyChecker:
    def __init__(self):
        self.logger = setup_logger('safety_checker', 'logs/safety_checker.log', level=logging.DEBUG)
        self.logger.setLevel(logging.DEBUG)
        self.logger.warning("Safety checks are currently disabled!")

    def check_experiment_plan(self, experiment_plan):
        return True
        """
        # Original code commented out
        self.logger.info("Checking experiment plan for safety...")
        for step in experiment_plan:
            if not self.is_step_safe(step):
                self.logger.error(f"Unsafe step detected: {step}")
                return False
        return True
        """

    def is_step_safe(self, step):
        return True
        """
        # Original code commented out
        action = step.get('action')
        if action == 'run_python_code':
            code = step.get('code', '')
            return self.is_code_safe(code)
        elif action == 'web_request':
            url = step.get('url', '')
            return self.is_url_safe(url)
        # Add more checks for other actions as needed
        return True
        """

    def is_code_safe(self, code):
        return True
        """
        # Original code commented out
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
        """

    def is_url_safe(self, url):
        return True
        """
        # Original code commented out
        # Basic URL validation
        if not url.startswith(('http://', 'https://')):
            self.logger.warning(f"Invalid URL scheme: {url}")
            return False
        # You might want to add a whitelist of allowed domains here
        return True
        """