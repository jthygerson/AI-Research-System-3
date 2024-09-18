# tests/test_system.py

import unittest
from unittest.mock import patch, MagicMock
from idea_generation import IdeaGenerator
from idea_evaluation import IdeaEvaluator
from experiment_design import ExperimentDesigner
from experiment_execution import ExperimentExecutor
from feedback_loop import FeedbackLoop
from log_error_checker import LogErrorChecker
from error_fixing import ErrorFixer
import logging
import json

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

    @patch('idea_generation.create_completion')
    def test_generate_ideas_chat_model(self, mock_create):
        # Setup mock response for chat model
        mock_create.return_value = json.dumps({
            "research_ideas": [
                {"description": "Idea 1"},
                {"description": "Idea 2"},
                {"description": "Idea 3"}
            ]
        })
        generator = IdeaGenerator('gpt-4', 3)
        ideas = generator.generate_ideas()
        self.assertEqual(ideas, ['Idea 1', 'Idea 2', 'Idea 3'])

    @patch('idea_evaluation.create_completion')
    def test_evaluate_ideas_chat_model(self, mock_create):
        # Setup mock response for chat model
        mock_create.return_value = json.dumps({
            "scores": ["8", "7", "9"],  # Scores as strings to test conversion
            "justifications": {
                "criterion_1": "Justification 1",
                "criterion_2": "Justification 2",
                "criterion_3": "Justification 3"
            }
        })
        evaluator = IdeaEvaluator('gpt-4')
        scored_ideas = evaluator.evaluate_ideas(['Idea 1'])
        self.assertEqual(len(scored_ideas), 1)
        self.assertEqual(scored_ideas[0]['score'], 24)
        self.assertEqual(len(scored_ideas[0]['justifications']), 3)

    @patch('experiment_design.create_completion')
    def test_design_experiment_chat_model(self, mock_create):
        # Setup mock response for chat model
        mock_create.return_value = json.dumps({
            "experiment_plan": [
                {"action": "run_python_code", "code": "print('Hello, World!')"},
                {"action": "use_llm_api", "prompt": "Generate a test prompt"}
            ]
        })
        designer = ExperimentDesigner('gpt-4')
        experiment_plan = designer.design_experiment("Test idea")
        self.assertEqual(len(experiment_plan), 2)
        self.assertEqual(experiment_plan[0]['action'], "run_python_code")
        self.assertEqual(experiment_plan[1]['action'], "use_llm_api")

    @patch('feedback_loop.create_completion')
    def test_refine_experiment_chat_model(self, mock_create):
        # Setup mock response for chat model
        mock_create.return_value = json.dumps({
            "refined_plan": [
                {"action": "run_python_code", "code": "print('Refined experiment')"},
                {"action": "use_llm_api", "prompt": "Generate a refined test prompt"}
            ]
        })
        feedback_loop = FeedbackLoop('gpt-4')
        initial_plan = [{"action": "run_python_code", "code": "print('Initial experiment')"}]
        refined_plan = feedback_loop.refine_experiment(initial_plan, "Initial results")
        self.assertEqual(len(refined_plan), 2)
        self.assertEqual(refined_plan[0]['action'], "run_python_code")
        self.assertEqual(refined_plan[1]['action'], "use_llm_api")

    @patch('system_augmentation.create_completion')
    def test_system_augmentation_chat_model(self, mock_create):
        # Setup mock response for chat model
        mock_create.return_value = json.dumps({
            "code_modifications": [
                {"file": "idea_generation.py", "line": 45, "code": "# Modified code here"},
                {"file": "idea_evaluation.py", "line": 30, "code": "# Another modification"}
            ]
        })
        augmentor = SystemAugmentor('gpt-4')
        with patch.object(SystemAugmentor, '_validate_modifications', return_value=True), \
             patch.object(SystemAugmentor, '_apply_code_modifications'), \
             patch.object(SystemAugmentor, '_run_tests', return_value=True), \
             patch.object(SystemAugmentor, '_evaluate_performance_improvement', return_value=True):
            augmentor.augment_system("Test experiment results")
        # Assert that the methods were called (you can add more specific assertions if needed)
        self.assertTrue(augmentor._validate_modifications.called)
        self.assertTrue(augmentor._apply_code_modifications.called)
        self.assertTrue(augmentor._run_tests.called)
        self.assertTrue(augmentor._evaluate_performance_improvement.called)

    @patch('log_error_checker.create_completion')
    def test_log_error_checker_chat_model(self, mock_create):
        # Setup mock response for chat model
        mock_create.return_value = 'Issue 1: Error XYZ\nIssue 2: Warning ABC'
        checker = LogErrorChecker('gpt-4')
        analysis = checker.check_logs('logs/main.log')
        self.assertEqual(analysis, 'Issue 1: Error XYZ\nIssue 2: Warning ABC')

    @patch('error_fixing.create_completion')
    def test_error_fixing_chat_model(self, mock_create):
        # Setup mock response for chat model
        mock_create.return_value = 'File: utils/logger.py\nLine 45: Add log rotation handler.'
        with patch.object(ErrorFixer, 'apply_code_fixes') as mock_apply:
            fixer = ErrorFixer('gpt-4')
            fixer.fix_errors('Issue 1: Error XYZ\nIssue 2: Warning ABC')
            mock_apply.assert_called_once_with('File: utils/logger.py\nLine 45: Add log rotation handler.')

if __name__ == '__main__':
    unittest.main()
