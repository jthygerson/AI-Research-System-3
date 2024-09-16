# orchestrator.py

import os
import sys
import argparse
import traceback

# Import all modules
from idea_generation import IdeaGenerator
from idea_evaluation import IdeaEvaluator
from experiment_design import ExperimentDesigner
from experiment_execution import ExperimentExecutor
from feedback_loop import FeedbackLoop
from system_augmentation import SystemAugmentor
from benchmarking import Benchmarking
from report_writer import ReportWriter
from log_error_checker import LogErrorChecker
from error_fixing import ErrorFixer

from utils.logger import setup_logger
from utils.code_backup.py import backup_code, restore_code

def main():
    parser = argparse.ArgumentParser(description='AI Research System')
    parser.add_argument('--model_name', type=str, required=True, help='Name of the OpenAI model to use')
    parser.add_argument('--num_ideas', type=int, required=True, help='Number of ideas to generate')
    parser.add_argument('--num_experiments', type=int, required=True, help='Number of experiment runs')
    args = parser.parse_args()

    # Setup main logger
    main_logger = setup_logger('main_logger', 'logs/main.log')

    # Backup code before starting
    backup_dir = 'code_backups'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    backup_path = backup_code('.', backup_dir)
    if backup_path:
        main_logger.info(f"Code backed up at {backup_path}")
    else:
        main_logger.error("Failed to back up code.")

    try:
        for experiment_run in range(args.num_experiments):
            main_logger.info(f"Starting experiment run {experiment_run + 1}")

            # Step 1: Idea Generation
            idea_generator = IdeaGenerator(args.model_name, args.num_ideas)
            ideas = idea_generator.generate_ideas()

            # Step 2: Idea Evaluation
            idea_evaluator = IdeaEvaluator(args.model_name)
            scored_ideas = idea_evaluator.evaluate_ideas(ideas)

            # Select the best idea based on the highest score
            if not scored_ideas:
                main_logger.error("No ideas were scored. Skipping this experiment run.")
                continue
            best_idea = max(scored_ideas, key=lambda x: x['score'])

            # Step 3: Experiment Design
            experiment_designer = ExperimentDesigner(args.model_name)
            experiment_plan = experiment_designer.design_experiment(best_idea['idea'])

            # Step 4: Experiment Execution
            experiment_executor = ExperimentExecutor(args.model_name)
            initial_results = experiment_executor.execute_experiment(experiment_plan)

            # Step 5: Feedback Loop
            feedback_loop = FeedbackLoop(args.model_name)
            refined_plan = feedback_loop.refine_experiment(experiment_plan, initial_results)

            # Step 6: Refined Experiment Execution
            final_results = experiment_executor.execute_experiment(refined_plan)

            # Step 7: System Augmentation
            system_augmentor = SystemAugmentor(args.model_name)
            system_augmentor.augment_system(final_results)

            # Step 8: Benchmarking
            benchmarking = Benchmarking()
            performance_metrics = benchmarking.run_benchmarks()

            # Step 9: Report Writing
            report_writer = ReportWriter()
            report_writer.write_report(best_idea, refined_plan, final_results, performance_metrics)

            # Step 10: Log Error Checking
            log_error_checker = LogErrorChecker(args.model_name)
            errors_warnings = log_error_checker.check_logs('logs/main.log')

            # Step 11: Error Fixing
            error_fixer = ErrorFixer(args.model_name)
            error_fixer.fix_errors(errors_warnings)

            # Run tests after modifications
            os.system('python -m unittest discover tests')

        main_logger.info("All experiment runs completed successfully.")

    except Exception as e:
        main_logger.error(f"Exception occurred: {str(e)}")
        main_logger.error(traceback.format_exc())

        # Restore code from backup in case of critical failure
        if backup_path:
            restore_code(backup_path, '.')
            main_logger.info("Restored code from backup.")
        else:
            main_logger.error("No backup available to restore.")

        sys.exit(1)

if __name__ == '__main__':
    main()
