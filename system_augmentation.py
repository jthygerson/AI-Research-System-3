# system_augmentation.py

import os
import ast
import astor
import subprocess
from utils.logger import setup_logger
from utils.openai_utils import create_completion
from utils.config import initialize_openai
from utils.metrics import evaluate_system_performance

class SystemAugmentor:
    def __init__(self, model_name):
        initialize_openai()  # Initialize OpenAI API key consistently
        self.model_name = model_name
        self.logger = setup_logger('system_augmentation', 'logs/system_augmentation.log')

    def augment_system(self, experiment_results):
        """
        Self-improves the AI Research System by adjusting its own code based on experiment results.
        """
        self.logger.info("Augmenting system based on experiment results...")
        try:
            prompt = self._generate_augmentation_prompt(experiment_results)
            response = self._get_model_response(prompt)
            
            self.logger.info(f"Code modifications suggested: {response}")

            if self._validate_modifications(response):
                self._apply_code_modifications(response)
                if self._run_tests():
                    performance_improvement = self._evaluate_performance_improvement()
                    if performance_improvement:
                        self.logger.info("System successfully augmented and performance improved.")
                    else:
                        self._revert_changes()
                        self.logger.info("Changes reverted due to no performance improvement.")
                else:
                    self._revert_changes()
            else:
                self.logger.warning("Invalid code modifications suggested. Skipping application.")
        except Exception as e:
            self.logger.error(f"Error augmenting system: {e}", exc_info=True)

    def _evaluate_performance_improvement(self):
        # Implement logic to compare performance before and after changes
        # Return True if there's an improvement, False otherwise
        pass

    def _generate_augmentation_prompt(self, experiment_results):
        return f"""Based on the following experiment results:

{experiment_results}

Identify specific improvements that can be made to the AI Research System's code to enhance its performance in the following areas:
1. Quality of ideas generated
2. Effectiveness of idea evaluation
3. Quality of experiment designs
4. Efficiency and accuracy of experiment executions
5. Creativeness and precision in applying research findings
6. System reliability and performance improvement after adjustments
7. Benchmark performance on difficult coding tasks
8. Quality and comprehensiveness of reports
9. Accuracy of log file error-checking
10. Effectiveness of applied code changes in fixing previous errors

Provide the exact code modifications needed, including the file names and line numbers. Ensure that your suggestions are safe, maintainable, and improve the system's overall performance."""

    def _get_model_response(self, prompt):
        """
        Gets the response from the OpenAI model.
        """
        self.logger.debug(f"Using model: {self.model_name}")
        
        if any(self.model_name.lower().startswith(model.lower()) for model in ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-0314', 'gpt-4-32k', 'gpt-3.5-turbo-0301', 'gpt-4o', 'gpt-4o-mini', 'o1-preview', 'o1-mini']):
            self.logger.debug("Using chat model format")
            messages = [
                {"role": "system", "content": "You are an AI research assistant."},
                {"role": "user", "content": prompt}
            ]
            response = create_completion(
                self.model_name,
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
            )
        else:
            self.logger.debug("Using non-chat model format")
            response = create_completion(
                self.model_name,
                prompt=prompt,
                max_tokens=1000,
                temperature=0.7,
            )
        
        return response

    def _validate_modifications(self, modifications):
        self.logger.info("Validating proposed modifications...")
        
        # Check for potentially dangerous operations
        dangerous_keywords = ['os.system', 'subprocess.run', 'exec', 'eval']
        for keyword in dangerous_keywords:
            if keyword in modifications:
                self.logger.warning(f"Potentially dangerous operation found: {keyword}")
                return False
        
        # Validate syntax of proposed changes
        for file_path, changes in self._parse_modifications(modifications):
            try:
                ast.parse(changes)
            except SyntaxError as e:
                self.logger.error(f"Syntax error in proposed changes for {file_path}: {e}")
                return False
        
        # Add more validation checks as needed
        
        return True

    def _apply_code_modifications(self, code_modifications):
        self.logger.info("Applying code modifications...")
        for file_path, changes in self._parse_modifications(code_modifications):
            self._modify_file(file_path, changes)
        
        # Run tests after applying modifications
        if not self._run_tests():
            self._revert_changes()

    def _parse_modifications(self, code_modifications):
        # Implement parsing logic to extract file paths and changes
        # This is a placeholder and should be implemented based on the expected format
        return [("path/to/file.py", "changes")]

    def _modify_file(self, file_path, changes):
        with open(file_path, 'r') as file:
            tree = ast.parse(file.read())
        
        # Apply changes to the AST
        # This is a simplified example and should be expanded
        modified_tree = self._apply_changes_to_ast(tree, changes)
        
        # Write the modified AST back to the file
        with open(file_path, 'w') as file:
            file.write(astor.to_source(modified_tree))

    def _apply_changes_to_ast(self, tree, changes):
        # Implement logic to modify the AST based on the changes
        # This is a placeholder and should be implemented based on the expected change format
        return tree

    def _run_tests(self):
        self.logger.info("Running unit tests...")
        try:
            result = subprocess.run(['python', '-m', 'unittest', 'discover', 'tests'], capture_output=True, text=True)
            if result.returncode == 0:
                self.logger.info("All tests passed successfully.")
                return True
            else:
                self.logger.error(f"Tests failed. Output: {result.stdout}\nErrors: {result.stderr}")
                return False
        except Exception as e:
            self.logger.error(f"Error running tests: {e}")
            return False

    def _is_performance_improved(self, performance_metrics):
        # Implement logic to determine if the system's performance has improved
        # This should consider all the metrics you've specified
        # Return True if improved, False otherwise
        return True  # Placeholder

    def _revert_changes(self):
        self.logger.warning("Tests failed. Reverting changes...")
        # Implement logic to revert the applied changes
        # This could involve keeping backups of modified files and restoring them
