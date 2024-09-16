# tests/test_system.py

import unittest
from unittest.mock import patch
from idea_generation import IdeaGenerator
from idea_evaluation import IdeaEvaluator
from experiment_design import ExperimentDesigner
from experiment_execution import ExperimentExecutor
from feedback_loop import FeedbackLoop
from log_error_checker import LogErrorChecker
from error_fixing import ErrorFixer
import logging

class TestAIResearchSystem(unittest.TestCase):
    def tearDown(self):
        """
        Remove all handlers associated with the logger to prevent ResourceWarnings.
        """
        loggers = [
            'idea_generation',
            'idea_evaluation',
            'experiment_design',
            'experiment_execution',
            'feedback_loop',
            'log_error_checker',
            'error_fixing'
        ]
        for logger_name in loggers:
            logger = logging.getLogger(logger_name)
            handlers = logger.handlers[:]
            for handler in handlers:
                handler.close()
                logger.removeHandler(handler)

    # Tests for IdeaGenerator
    @patch('idea_generation.openai.Completion.create')
    def test_generate_ideas_completion_model(self, mock_create):
        # Setup mock response for completion model
        mock_create.return_value = {
            'choices': [{'text': '- Idea 1\n- Idea 2\n- Idea 3'}]
        }
        generator = IdeaGenerator('text-davinci-003', 3)
        ideas = generator.generate_ideas()
        self.assertEqual(ideas, ['Idea 1', 'Idea 2', 'Idea 3'])

    @patch('idea_generation.openai.ChatCompletion.create')
    def test_generate_ideas_chat_model(self, mock_create):
        # Setup mock response for chat model
        mock_create.return_value = {
            'choices': [{'message': {'content': '- Idea 1\n- Idea 2\n- Idea 3'}}]
        }
        generator = IdeaGenerator('gpt-4', 3)
        ideas = generator.generate_ideas()
        self.assertEqual(ideas, ['Idea 1', 'Idea 2', 'Idea 3'])

    # Tests for IdeaEvaluator
    @patch('idea_evaluation.openai.Completion.create')
    def test_idea_evaluation_completion_model(self, mock_create):
        # Setup mock response for completion model
        mock_create.return_value = {
            'choices': [{'text': 'Score: 8\nJustification: Innovative and feasible.'}]
        }
        evaluator = IdeaEvaluator('text-davinci-003')
        scored_ideas = evaluator.evaluate_ideas(['Test Idea'])
        self.assertEqual(len(scored_ideas), 1)
        self.assertEqual(scored_ideas[0]['score'], 8)
        self.assertEqual(scored_ideas[0]['justification'], 'Innovative and feasible.')

    @patch('idea_evaluation.openai.ChatCompletion.create')
    def test_idea_evaluation_chat_model(self, mock_create):
        # Setup mock response for chat model
        mock_create.return_value = {
            'choices': [{'message': {'content': 'Score: 9\nJustification: Highly novel and promising.'}}]
        }
        evaluator = IdeaEvaluator('gpt-4')
        scored_ideas = evaluator.evaluate_ideas(['Test Idea'])
        self.assertEqual(len(scored_ideas), 1)
        self.assertEqual(scored_ideas[0]['score'], 9)
        self.assertEqual(scored_ideas[0]['justification'], 'Highly novel and promising.')

    # Tests for ExperimentDesigner
    @patch('experiment_design.openai.Completion.create')
    def test_experiment_design_completion_model(self, mock_create):
        # Setup mock response for completion model
        mock_create.return_value = {
            'choices': [{'text': 'Experiment Plan Content'}]
        }
        designer = ExperimentDesigner('text-davinci-003')
        plan = designer.design_experiment('Test Idea')
        self.assertEqual(plan, 'Experiment Plan Content')

    @patch('experiment_design.openai.ChatCompletion.create')
    def test_experiment_design_chat_model(self, mock_create):
        # Setup mock response for chat model
        mock_create.return_value = {
            'choices': [{'message': {'content': 'Experiment Plan Content'}}]
        }
        designer = ExperimentDesigner('gpt-4')
        plan = designer.design_experiment('Test Idea')
        self.assertEqual(plan, 'Experiment Plan Content')

    # Tests for ExperimentExecutor
    @patch('experiment_execution.openai.Completion.create')
    def test_experiment_execution_completion_model(self, mock_create):
        # Setup mock response for completion model
        mock_create.return_value = {
            'choices': [{'text': 'Execution Results Content'}]
        }
        executor = ExperimentExecutor('text-davinci-003')
        results = executor.execute_experiment('Test Experiment Plan')
        self.assertEqual(results, 'Execution Results Content')

    @patch('experiment_execution.openai.ChatCompletion.create')
    def test_experiment_execution_chat_model(self, mock_create):
        # Setup mock response for chat model
        mock_create.return_value = {
            'choices': [{'message': {'content': 'Execution Results Content'}}]
        }
        executor = ExperimentExecutor('gpt-4')
        results = executor.execute_experiment('Test Experiment Plan')
        self.assertEqual(results, 'Execution Results Content')

    # Tests for FeedbackLoop
    @patch('feedback_loop.openai.Completion.create')
    def test_feedback_loop_completion_model(self, mock_create):
        # Setup mock response for completion model
        mock_create.return_value = {
            'choices': [{'text': 'Refined Experiment Plan Content'}]
        }
        feedback = FeedbackLoop('text-davinci-003')
        refined_plan = feedback.refine_experiment('Test Experiment Plan', 'Test Initial Results')
        self.assertEqual(refined_plan, 'Refined Experiment Plan Content')

    @patch('feedback_loop.openai.ChatCompletion.create')
    def test_feedback_loop_chat_model(self, mock_create):
        # Setup mock response for chat model
        mock_create.return_value = {
            'choices': [{'message': {'content': 'Refined Experiment Plan Content'}}]
        }
        feedback = FeedbackLoop('gpt-4')
        refined_plan = feedback.refine_experiment('Test Experiment Plan', 'Test Initial Results')
        self.assertEqual(refined_plan, 'Refined Experiment Plan Content')

    # Tests for LogErrorChecker
    @patch('log_error_checker.openai.Completion.create')
    def test_log_error_checker_completion_model(self, mock_create):
        # Setup mock response for completion model
        mock_create.return_value = {
            'choices': [{'text': 'Issue 1: Error XYZ\nIssue 2: Warning ABC'}]
        }
        checker = LogErrorChecker('text-davinci-003')
        analysis = checker.check_logs('logs/main.log')
        self.assertEqual(analysis, 'Issue 1: Error XYZ\nIssue 2: Warning ABC')

    @patch('log_error_checker.openai.ChatCompletion.create')
    def test_log_error_checker_chat_model(self, mock_create):
        # Setup mock response for chat model
        mock_create.return_value = {
            'choices': [{'message': {'content': 'Issue 1: Error XYZ\nIssue 2: Warning ABC'}}]
        }
        checker = LogErrorChecker('gpt-4')
        analysis = checker.check_logs('logs/main.log')
        self.assertEqual(analysis, 'Issue 1: Error XYZ\nIssue 2: Warning ABC')

    # Tests for ErrorFixer
    @patch('error_fixing.openai.Completion.create')
    def test_error_fixing_completion_model(self, mock_create):
        # Setup mock response for completion model
        mock_create.return_value = {
            'choices': [{'text': 'File: utils/logger.py\nLine 45: Add log rotation handler.'}]
        }
        fixer = ErrorFixer('text-davinci-003')
        fixer.fix_errors('Issue 1: Error XYZ\nIssue 2: Warning ABC')
        # Since apply_code_fixes does not modify code, we check the log for fixes
        # This can be done by checking the logs manually or enhancing the method to return fixes

    @patch('error_fixing.openai.ChatCompletion.create')
    def test_error_fixing_chat_model(self, mock_create):
        # Setup mock response for chat model
        mock_create.return_value = {
            'choices': [{'message': {'content': 'File: utils/logger.py\nLine 45: Add log rotation handler.'}}]
        }
        fixer = ErrorFixer('gpt-4')
        fixer.fix_errors('Issue 1: Error XYZ\nIssue 2: Warning ABC')
        # Similar to the completion model test

if __name__ == '__main__':
    unittest.main()
