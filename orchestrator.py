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
from utils.code_backup import backup_code, restore_code

def main():
    # Initialize argument parser
    parser = argparse.ArgumentParser(description='AI Research System Orchestrator')
    parser.add_argument('--model_name', type=str, required=True, help='Name of the OpenAI model to use')
    parser.add_argument('--num_ideas', type=int, required=True, help='Number of ideas to generate')
    parser.add_argument('--num_experiments', type=int, required=True, help='Number of experiment runs')
    args = parser.parse_args()

    # Define supported models
    chat_models = ['gpt-3.5-turbo', 'gpt-4', 'gpt-4o', 'gpt-4o-mini', 'o1-preview', 'o1-mini']
    completion_models = ['text-davinci-003', 'text-curie-001', 'text-babbage-001', 'text-ada-001']  # Add more if needed
    supported_models = chat_models + completion_models

    # Normalize and validate model name
    model_name = args.model_name.strip()
    if not any(model_name.lower().startswith(model.lower()) for model in supported_models):
        print(f"Error: Unsupported model_name '{model_name}'. Please choose a supported model.")
        sys.exit(1)

    # Setup main logger
    main_logger = setup_logger('main_logger', 'logs/main.log')
    main_logger.info(f"Starting AI Research System with model: {model_name}, {args.num_ideas} ideas, {args.num_experiments} experiments.")
    print(f"Starting AI Research System with model: {model_name}, num_ideas: {args.num_ideas}, num_experiments: {args.num_experiments}")

    # Backup code before starting
    backup_dir = 'code_backups'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    backup_path = backup_code('.', backup_dir)
    if backup_path:
        main_logger.info(f"Code backed up at {backup_path}")
        print(f"Code backed up at {backup_path}")
    else:
        main_logger.error("Failed to back up code.")
        print("Failed to back up code.")

    try:
        for experiment_run in range(args.num_experiments):
            main_logger.info(f"Starting experiment run {experiment_run + 1}")
            print(f"\nStarting experiment run {experiment_run + 1}")

            # Step 1: Idea Generation
            print("Generating ideas...")
            idea_generator = IdeaGenerator(model_name, args.num_ideas)
            ideas = idea_generator.generate_ideas()
            if not ideas:
                main_logger.error(f"No ideas generated in experiment run {experiment_run + 1}. Skipping.")
                print(f"No ideas generated in experiment run {experiment_run + 1}. Skipping.")
                continue
            print(f"Generated {len(ideas)} ideas")

            # Step 2: Idea Evaluation
            print("Evaluating ideas...")
            idea_evaluator = IdeaEvaluator(model_name)
            scored_ideas = idea_evaluator.evaluate_ideas(ideas)
            if not scored_ideas:
                main_logger.error("No ideas were scored. Skipping this experiment run.")
                print("No ideas were scored. Skipping this experiment run.")
                continue
            print(f"Evaluated {len(scored_ideas)} ideas")

            # Select the best idea based on the highest score
            best_idea = max(scored_ideas, key=lambda x: x['score'])
            main_logger.info(f"Selected Best Idea: {best_idea['idea']} with score {best_idea['score']}")
            print(f"Selected Best Idea: {best_idea['idea']} with score {best_idea['score']}")

            # Step 3: Experiment Design
            print("Designing experiment...")
            experiment_designer = ExperimentDesigner(model_name)
            experiment_plan = experiment_designer.design_experiment(best_idea['idea'])
            if not experiment_plan:
                main_logger.error("Failed to design experiment. Skipping this experiment run.")
                print("Failed to design experiment. Skipping this experiment run.")
                continue
            main_logger.info(f"Designed Experiment Plan: {experiment_plan}")
            print(f"Designed Experiment Plan: {experiment_plan}")

            # Step 4: Experiment Execution
            print("Executing experiment...")
            experiment_executor = ExperimentExecutor(model_name)
            initial_results = experiment_executor.execute_experiment(experiment_plan)
            if not initial_results:
                main_logger.error("Failed to execute experiment. Skipping this experiment run.")
                print("Failed to execute experiment. Skipping this experiment run.")
                continue
            main_logger.info(f"Initial Execution Results: {initial_results}")
            print(f"Initial Execution Results: {initial_results}")

            # Step 5: Feedback Loop
            print("Refining experiment plan...")
            feedback_loop = FeedbackLoop(model_name)
            refined_plan = feedback_loop.refine_experiment(experiment_plan, initial_results)
            if not refined_plan:
                main_logger.error("Failed to refine experiment plan. Skipping this experiment run.")
                print("Failed to refine experiment plan. Skipping this experiment run.")
                continue
            main_logger.info(f"Refined Experiment Plan: {refined_plan}")
            print(f"Refined Experiment Plan: {refined_plan}")

            # Step 6: Refined Experiment Execution
            print("Executing refined experiment...")
            final_results = experiment_executor.execute_experiment(refined_plan)
            if not final_results:
                main_logger.error("Failed to execute refined experiment. Skipping this experiment run.")
                print("Failed to execute refined experiment. Skipping this experiment run.")
                continue
            main_logger.info(f"Final Execution Results: {final_results}")
            print(f"Final Execution Results: {final_results}")

            # Step 7: System Augmentation
            print("Augmenting system...")
            system_augmentor = SystemAugmentor(model_name)
            system_augmentor.augment_system(final_results)
            main_logger.info("System augmentation completed.")
            print("System augmentation completed.")

            # Step 8: Benchmarking
            print("Running benchmarks...")
            benchmarking = Benchmarking()
            performance_metrics = benchmarking.run_benchmarks()
            main_logger.info(f"Performance Metrics: {performance_metrics}")
            print(f"Performance Metrics: {performance_metrics}")

            # Step 9: Report Writing
            print("Writing report...")
            report_writer = ReportWriter()
            report_writer.write_report(best_idea, refined_plan, final_results, performance_metrics)
            main_logger.info("Report written successfully.")
            print("Report written successfully.")

            # Step 10: Log Error Checking
            print("Checking logs for errors and warnings...")
            log_error_checker = LogErrorChecker(model_name)
            errors_warnings = log_error_checker.check_logs('logs/main.log')
            main_logger.info(f"Log Analysis: {errors_warnings}")
            print(f"Log Analysis: {errors_warnings}")

            # Step 11: Error Fixing
            if errors_warnings:
                print("Fixing errors...")
                error_fixer = ErrorFixer(model_name)
                error_fixer.fix_errors(errors_warnings)
                main_logger.info("Error fixing completed.")
                print("Error fixing completed.")
            else:
                main_logger.info("No errors or warnings found in logs.")
                print("No errors or warnings found in logs.")

            # Run tests after modifications
            print("Running unit tests...")
            main_logger.info("Running unit tests...")
            test_result = os.system('python -m unittest discover tests')
            if test_result != 0:
                main_logger.error("Unit tests failed. Check the test reports for details.")
                print("Unit tests failed. Check the test reports for details.")
            else:
                main_logger.info("All unit tests passed successfully.")
                print("All unit tests passed successfully.")

        main_logger.info("All experiment runs completed successfully.")
        print("\nAI Research System execution completed.")

    except Exception as e:
        main_logger.error(f"Exception occurred: {str(e)}")
        main_logger.error(traceback.format_exc())
        print(f"An error occurred during execution: {e}")

        # Restore code from backup in case of critical failure
        if backup_path:
            restore_code(backup_path, '.')
            main_logger.info("Restored code from backup.")
            print("Restored code from backup.")
        else:
            main_logger.error("No backup available to restore.")
            print("No backup available to restore.")

        sys.exit(1)

if __name__ == "__main__":
    main()
