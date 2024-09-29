# system_augmentation.py

import os
import ast
import astor
import subprocess
import json
import time
from tenacity import retry, stop_after_attempt, wait_exponential
from utils.logger import setup_logger
from utils.openai_utils import create_completion
from utils.config import initialize_openai
from utils.metrics import PerformanceMetrics, evaluate_system_performance, generate_performance_report, calculate_overall_performance_score
from utils.json_utils import parse_llm_response

class SystemAugmentor:
    def __init__(self, model_name=None, max_tokens=4000):
        initialize_openai()
        self.model_name = model_name or "gpt-4"  # Default model if none provided
        self.max_tokens = max_tokens
        self.logger = setup_logger('system_augmentation', 'logs/system_augmentation.log')
        self.previous_performance = None
        self.max_retries = 3
        self.backoff_factor = 2

    def _run_benchmarks(self) -> PerformanceMetrics:
        # Implement benchmark tests for each metric
        metrics = PerformanceMetrics()
        
        # Example (replace with actual benchmark logic):
        metrics.update('idea_quality', self._benchmark_idea_quality())
        metrics.update('idea_evaluation_effectiveness', self._benchmark_idea_evaluation())
        metrics.update('experiment_design_quality', self._benchmark_experiment_design())
        metrics.update('experiment_execution_efficiency', self._benchmark_experiment_execution())
        metrics.update('research_application_creativity', self._benchmark_research_application())
        metrics.update('system_reliability', self._benchmark_system_reliability())
        metrics.update('coding_task_performance', self._benchmark_coding_task())
        metrics.update('report_quality', self._benchmark_report_quality())
        metrics.update('log_error_checking_accuracy', self._benchmark_log_error_checking())
        metrics.update('error_fixing_effectiveness', self._benchmark_error_fixing())

        return metrics

    def _benchmark_idea_quality(self) -> float:
        # Collect recent ideas generated by the system
        recent_ideas = self._get_recent_ideas(n=10)  # Get last 10 ideas
        
        # Use the AI model to evaluate each idea
        prompt = {
            "task": "evaluate_ideas",
            "ideas": recent_ideas,
            "criteria": [
                "Novelty",
                "Feasibility",
                "Potential impact"
            ],
            "instructions": "Evaluate each idea on a scale of 0 to 10 based on the given criteria. Provide a single numeric score for each idea.",
            "output_format": "JSON"
        }
        
        response = self._get_model_response(prompt)
        parsed_response = parse_llm_response(response)
        if parsed_response:
            scores = parsed_response.get('scores', [])
            scores = [float(score) / 10 for score in scores if isinstance(score, (int, float, str)) and str(score).replace('.', '').isdigit()]
        else:
            self.logger.warning(f"Invalid JSON response: {response}")
            scores = []
        
        return sum(scores) / len(scores) if scores else 0.0

    def _benchmark_idea_evaluation(self) -> float:
        # Compare system's idea evaluations with expert evaluations
        system_evaluations = self._get_recent_idea_evaluations(n=5)
        expert_evaluations = self._get_expert_idea_evaluations(n=5)
        
        accuracy = sum(1 for s, e in zip(system_evaluations, expert_evaluations) if abs(s - e) <= 0.1)
        return accuracy / len(system_evaluations)

    def _benchmark_experiment_design(self) -> float:
        recent_designs = self._get_recent_experiment_designs(n=5)
        
        prompt = {
            "task": "evaluate_experiment_designs",
            "designs": recent_designs,
            "criteria": [
                "Clarity",
                "Feasibility",
                "Potential to yield meaningful results"
            ],
            "instructions": "Evaluate each experiment design on a scale of 0 to 10 based on the given criteria. Provide a single numeric score for each design.",
            "output_format": "JSON"
        }
        
        response = self._get_model_response(prompt)
        parsed_response = parse_llm_response(response)
        if parsed_response:
            scores = parsed_response.get('scores', [])
            scores = [float(score) / 10 for score in scores if isinstance(score, (int, float, str)) and str(score).replace('.', '').isdigit()]
        else:
            self.logger.warning(f"Invalid JSON response: {response}")
            scores = []
        
        return sum(scores) / len(scores) if scores else 0.0

    def _benchmark_experiment_execution(self) -> float:
        recent_executions = self._get_recent_experiment_executions(n=5)
        
        # Calculate average completion time and success rate
        total_time = sum(execution['time'] for execution in recent_executions)
        avg_time = total_time / len(recent_executions)
        success_rate = sum(1 for execution in recent_executions if execution['success']) / len(recent_executions)
        
        # Normalize time (assuming 1 hour is perfect, 24 hours is worst)
        time_score = max(0, min(1, (24 - avg_time) / 23))
        
        return (time_score + success_rate) / 2

    def _benchmark_research_application(self) -> float:
        recent_applications = self._get_recent_research_applications(n=5)
        
        prompt = {
            "task": "evaluate_research_applications",
            "applications": recent_applications,
            "criteria": [
                "Creativity",
                "Effectiveness"
            ],
            "instructions": "Evaluate each application of research findings on a scale of 0 to 10 based on the given criteria. Provide a single numeric score for each application.",
            "output_format": "JSON"
        }
        
        response = self._get_model_response(prompt)
        parsed_response = parse_llm_response(response)
        if parsed_response:
            scores = parsed_response.get('scores', [])
            scores = [float(score) / 10 for score in scores if isinstance(score, (int, float, str)) and str(score).replace('.', '').isdigit()]
        else:
            self.logger.warning(f"Invalid JSON response: {response}")
            scores = []
        
        return sum(scores) / len(scores) if scores else 0.0

    def _benchmark_system_reliability(self) -> float:
        # Check system uptime and error rate over the last 24 hours
        uptime = self._get_system_uptime()
        error_rate = self._get_error_rate()
        
        uptime_score = uptime / 24  # Assuming 24 hours is perfect
        error_score = 1 - min(1, error_rate / 0.1)  # Assuming 10% error rate is worst case
        
        return (uptime_score + error_score) / 2

    def _benchmark_coding_task(self) -> float:
        # Run a set of predefined coding challenges and measure success rate
        challenges = self._get_coding_challenges()
        successful = sum(1 for challenge in challenges if self._run_coding_challenge(challenge))
        return successful / len(challenges)

    def _benchmark_report_quality(self) -> float:
        recent_reports = self._get_recent_reports(n=3)
        
        prompt = {
            "task": "evaluate_reports",
            "reports": recent_reports,
            "criteria": [
                "Clarity",
                "Comprehensiveness",
                "Adherence to report requirements"
            ],
            "instructions": "Evaluate each report on a scale of 0 to 10 based on the given criteria. Provide a single numeric score for each report.",
            "output_format": "JSON"
        }
        
        response = self._get_model_response(prompt)
        parsed_response = parse_llm_response(response)
        if parsed_response:
            scores = parsed_response.get('scores', [])
            scores = [float(score) / 10 for score in scores if isinstance(score, (int, float, str)) and str(score).replace('.', '').isdigit()]
        else:
            self.logger.warning(f"Invalid JSON response: {response}")
            scores = []
        
        return sum(scores) / len(scores) if scores else 0.0

    def _benchmark_log_error_checking(self) -> float:
        # Compare system's error detections with manually identified errors
        system_errors = self._get_system_detected_errors()
        manual_errors = self._get_manually_identified_errors()
        
        true_positives = len(set(system_errors) & set(manual_errors))
        false_positives = len(set(system_errors) - set(manual_errors))
        false_negatives = len(set(manual_errors) - set(system_errors))
        
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        
        return (precision + recall) / 2 if (precision + recall) > 0 else 0

    def _benchmark_error_fixing(self) -> float:
        recent_fixes = self._get_recent_error_fixes(n=10)
        
        successful_fixes = sum(1 for fix in recent_fixes if fix['success'])
        return successful_fixes / len(recent_fixes)

    def _evaluate_performance_improvement(self):
        current_performance = self._run_benchmarks()
        
        if self.previous_performance is None:
            self.previous_performance = current_performance
            return True

        overall_improvement, improvement_percentages, improved_metrics = evaluate_system_performance(
            self.previous_performance.get_all(), 
            current_performance.get_all()
        )
        
        report = generate_performance_report(self.previous_performance.get_all(), current_performance.get_all())
        self.logger.info(f"Performance Report:\n{report}")

        current_score = calculate_overall_performance_score(current_performance.get_all())
        previous_score = calculate_overall_performance_score(self.previous_performance.get_all())

        if current_score > previous_score:
            self.previous_performance = current_performance
            return True
        else:
            return False

    def augment_system(self, final_results):
        self.logger.info("Augmenting system based on experiment results...")
        try:
            prompt = self._generate_augmentation_prompt(final_results)
            response = create_completion(
                self.model_name,
                messages=[
                    {"role": "system", "content": "You are an AI research assistant. Always provide your response in the exact JSON format specified in the instructions."},
                    {"role": "user", "content": json.dumps(prompt)}
                ],
                max_tokens=self.max_tokens,
                temperature=0.7,
            )
            
            self.logger.info(f"Received model response. Length: {len(response)}")
            self.logger.debug(f"Model response content: {response[:500]}...")  # Log first 500 characters

            parsed_response = self._parse_modifications(response)
            if not parsed_response:
                self.logger.warning("No valid modifications found in the model response.")
                return

            if self._validate_modifications(parsed_response):
                self._apply_code_modifications(parsed_response)
                if self._run_tests():
                    performance_improvement = self._evaluate_performance_improvement()
                    if performance_improvement:
                        self.logger.info("System successfully augmented and performance improved.")
                    else:
                        self._revert_changes()
                        self.logger.info("Changes reverted due to no performance improvement.")
                else:
                    self._revert_changes()
                    self.logger.warning("Tests failed after applying modifications. Changes reverted.")
            else:
                self.logger.warning("Invalid code modifications suggested. Skipping application.")
        except Exception as e:
            self.logger.error(f"Error augmenting system: {e}", exc_info=True)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _get_model_response(self, prompt):
        """
        Gets the response from the OpenAI model with retry mechanism.
        """
        self.logger.debug(f"Attempting to get response from model: {self.model_name}")
        
        try:
            response = create_completion(
                self.model_name,
                messages=[
                    {"role": "system", "content": "You are an AI research assistant. Always provide your response in the exact JSON format specified in the instructions."},
                    {"role": "user", "content": json.dumps(prompt)}
                ],
                max_tokens=3500,
                temperature=0.7,
            )
            
            # Attempt to parse the response as JSON
            parsed_response = json.loads(response)
            self.logger.debug(f"Successfully received and parsed response from model.")
            return json.dumps(parsed_response)  # Ensure valid JSON string
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse model response as JSON: {e}")
            raise  # Retry will be triggered
        except Exception as e:
            self.logger.error(f"Error getting model response: {e}")
            raise  # Retry will be triggered

    def _parse_modifications(self, response):
        self.logger.info("Parsing code modifications...")
        parsed_modifications = []
        
        try:
            modifications = json.loads(response)
            
            if not isinstance(modifications, list):
                self.logger.error(f"Expected a JSON array of modifications, got: {type(modifications)}")
                return []
            
            for i, modification in enumerate(modifications):
                if not isinstance(modification, dict):
                    self.logger.warning(f"Skipping invalid modification at index {i}: {modification}")
                    continue
                
                file_path = modification.get('file')
                changes = modification.get('code')
                
                if not file_path or not changes:
                    self.logger.warning(f"Skipping modification with missing 'file' or 'code' at index {i}: {modification}")
                    continue
                
                parsed_modifications.append((file_path, changes))
            
            self.logger.info(f"Successfully parsed {len(parsed_modifications)} modifications.")
        
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse response as JSON: {e}")
        
        return parsed_modifications

    def _validate_modifications(self, modifications):
        self.logger.info("Validating proposed modifications...")
        
        if not modifications:
            self.logger.warning("No modifications to validate.")
            return False
        
        for file_path, changes in modifications:
            if not os.path.exists(file_path):
                self.logger.error(f"File does not exist: {file_path}")
                return False
            
            try:
                ast.parse(changes)
            except SyntaxError as e:
                self.logger.error(f"Syntax error in proposed changes for {file_path}: {e}")
                return False
            
            # Additional validation checks
            if self._contains_unsafe_operations(changes):
                self.logger.error(f"Unsafe operations detected in changes for {file_path}")
                return False
            
            if not self._changes_are_relevant(file_path, changes):
                self.logger.warning(f"Changes for {file_path} don't seem relevant to the file's purpose")
                return False
        
        self.logger.info("All modifications passed validation.")
        return True

    def _contains_unsafe_operations(self, code):
        # This is a basic check and should be expanded based on your specific security requirements
        unsafe_operations = ['os.system', 'subprocess.call', 'eval', 'exec']
        return any(op in code for op in unsafe_operations)

    def _changes_are_relevant(self, file_path, changes):
        # This is a placeholder function. Implement logic to check if changes are relevant to the file's purpose
        # For example, you could check if the changes modify the main classes/functions in the file
        return True

    def _apply_code_modifications(self, code_modifications):
        self.logger.info("Applying code modifications...")
        for file_path, changes in code_modifications:
            self._modify_file(file_path, changes)
        
        # Run tests after applying modifications
        if not self._run_tests():
            self._revert_changes()
            self.logger.warning("Tests failed after applying modifications. Changes reverted.")

    def _modify_file(self, file_path, changes):
        self.logger.info(f"Modifying file: {file_path}")
        backup_path = f"{file_path}.bak"
        
        # Create a backup of the original file
        os.rename(file_path, backup_path)
        
        try:
            with open(file_path, 'w') as file:
                file.write(changes)
            self.logger.info(f"Successfully modified {file_path}")
        except Exception as e:
            self.logger.error(f"Error modifying {file_path}: {e}")
            os.rename(backup_path, file_path)  # Restore from backup
            raise

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

    def _revert_changes(self):
        self.logger.warning("Reverting changes...")
        for root, dirs, files in os.walk("."):
            for file in files:
                if file.endswith(".bak"):
                    original_file = file[:-4]  # Remove .bak extension
                    backup_path = os.path.join(root, file)
                    original_path = os.path.join(root, original_file)
                    os.rename(backup_path, original_path)
                    self.logger.info(f"Reverted changes to {original_file}")
        self.logger.info("All changes have been reverted.")

    def _generate_augmentation_prompt(self, experiment_results):
        return {
            "task": "generate_augmentation_prompt",
            "experiment_results": experiment_results,
            "instructions": """
Based on the given experiment results, identify specific improvements that can be made to the AI Research System's code to enhance its performance in the following areas:
1. Quality of ideas generated
2. Effectiveness of idea evaluation
3. Quality of experiment designs
4. Efficiency and accuracy of experiment executions
5. Application of research findings
6. System reliability and performance improvement after adjustments
7. Benchmark performance on difficult coding tasks
8. Quality and comprehensiveness of reports
9. Accuracy of log file error-checking
10. Effectiveness of applied code changes in fixing previous errors

Provide the exact code modifications needed, including the file names and line numbers. Ensure that your suggestions are safe, maintainable, and improve the system's overall performance.

Format your response as a JSON array of objects, where each object represents a single file modification:

[
  {
    "file": "path/to/file.py",
    "code": "The entire content of the modified file"
  },
  {
    "file": "path/to/another_file.py",
    "code": "The entire content of the modified file"
  }
]

If no modifications are needed, return an empty array: []
            """,
            "output_format": "JSON"
        }
