# orchestrator.py

# Import necessary standard libraries
import os
import sys
import argparse
import traceback
import logging
import hashlib
import json
import time
import random
import openai
from openai import OpenAIError

# Import custom modules for different stages of the AI research process
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
from utils.safety_checker import SafetyChecker
from experiment_coder import ExperimentCoder

# Import utility functions
from utils.logger import setup_logger, ensure_log_file
from utils.code_backup import backup_code, restore_code
from utils.config import initialize_openai
from utils.resource_manager import ResourceManager

# Set up loggers
main_logger = setup_logger('main', 'logs/main.log')
debug_logger = setup_logger('debug', 'logs/debug.log', level=logging.DEBUG)

# Initialize a list to store API call history for debugging purposes
api_call_history = []

def log_api_call(model, prompt, response):
    """
    Log API calls for debugging and analysis.
    """
    api_call_history.append({
        'model': model,
        'prompt': prompt,
        'response': response
    })

def hash_idea(idea):
    """
    Generate a hash for an idea to check for duplicates.
    """
    return hashlib.md5(idea.encode()).hexdigest()

def parse_and_validate_plan(plan):
    """
    Parse and validate the experiment plan.
    """
    try:
        if isinstance(plan, str):
            plan = json.loads(plan)
        if not isinstance(plan, dict):
            return None
        required_keys = ['hypothesis', 'variables', 'methodology', 'data_collection', 'analysis_plan']
        if not all(key in plan for key in required_keys):
            return None
        if not isinstance(plan['methodology'], list):
            return None
        for step in plan['methodology']:
            if not isinstance(step, dict) or 'action' not in step:
                return None
        return plan
    except json.JSONDecodeError:
        return None

def main():
    # Initialize argument parser for command-line options
    parser = argparse.ArgumentParser(description='AI Research System Orchestrator')
    parser.add_argument('--model_name', type=str, required=True, help='Name of the OpenAI model to use')
    parser.add_argument('--num_ideas', type=int, default=20, help='Maximum number of ideas to generate')
    parser.add_argument('--num_experiments', type=int, required=True, help='Number of experiment runs')
    parser.add_argument('--max_tokens', type=int, default=4000, help='Maximum number of tokens for API calls')
    args = parser.parse_args()

    # Define supported models for validation
    chat_models = ['gpt-3.5-turbo', 'gpt-4', 'gpt-4o', 'gpt-4o-mini', 'o1-preview', 'o1-mini']
    completion_models = ['text-davinci-003', 'text-curie-001', 'text-babbage-001', 'text-ada-001']
    supported_models = chat_models + completion_models

    # Normalize and validate the model name
    model_name = args.model_name.strip()
    if not any(model_name.lower().startswith(model.lower()) for model in supported_models):
        print(f"Error: Unsupported model_name '{model_name}'. Please choose a supported model.")
        sys.exit(1)

    main_logger.info(f"Starting AI Research System with model: {model_name}, {args.num_ideas} ideas, {args.num_experiments} experiments.")

    # Backup code before starting to allow for reverting changes if needed
    backup_dir = 'code_backups'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    backup_path = backup_code('.', backup_dir)
    if backup_path:
        main_logger.info(f"Code backed up at {backup_path}")
    else:
        main_logger.error("Failed to back up code.")

    # Initialize safety checker for experiment plans
    safety_checker = SafetyChecker()

    # Create a ResourceManager instance
    resource_manager = ResourceManager()

    try:
        # Initialize OpenAI client once at the start
        initialize_openai()
        
        # Initialize variable to store previous performance metrics
        previous_performance = None

        # Set to store hashes of generated ideas to avoid duplicates
        all_idea_hashes = set()

        # Main experiment loop
        for experiment_run in range(args.num_experiments):
            debug_logger.info(f"\n--- Experiment Run {experiment_run + 1} ---")

            try:
                # Reset state for the new experiment run
                best_idea = None
                current_run_ideas = []

                # Create new instances for each run to ensure fresh state
                idea_generator = IdeaGenerator(args.model_name, args.num_ideas, args.max_tokens)
                idea_evaluator = IdeaEvaluator(args.model_name, args.max_tokens)
                experiment_designer = ExperimentDesigner(args.model_name, args.max_tokens)
                experiment_executor = ExperimentExecutor(resource_manager, args.model_name, args.max_tokens)
                feedback_loop = FeedbackLoop(args.model_name, args.max_tokens)
                system_augmentor = SystemAugmentor(args.model_name, args.max_tokens)
                error_fixer = ErrorFixer(args.model_name, args.max_tokens)

                # Generate new ideas for this run
                main_logger.info("Generating ideas for this experiment run...")
                generated_ideas = []
                while len(generated_ideas) < args.num_ideas:
                    new_ideas = idea_generator.generate_ideas()
                    for idea in new_ideas:
                        idea_hash = hash_idea(idea)
                        if idea_hash not in all_idea_hashes:
                            all_idea_hashes.add(idea_hash)
                            generated_ideas.append(idea)
                            if len(generated_ideas) == args.num_ideas:
                                break
                    if len(generated_ideas) == args.num_ideas:
                        break
                main_logger.info(f"Generated {len(generated_ideas)} unique ideas for this run")

                # Evaluate all generated ideas
                main_logger.info("Evaluating ideas...")
                scored_ideas = idea_evaluator.evaluate_ideas(generated_ideas)
                
                # Find the best idea
                best_idea = None
                for scored_idea in scored_ideas:
                    if best_idea is None or scored_idea['score'] > best_idea['score']:
                        best_idea = scored_idea
                    if best_idea['score'] > 80:
                        break

                if best_idea:
                    main_logger.info(f"Selected Best Idea: {best_idea['idea']} with score {best_idea['score']}")
                else:
                    main_logger.warning("No valid ideas were generated. Skipping this experiment run.")
                    continue

                # Log all generated ideas for this run
                with open(f'logs/ideas_run_{experiment_run + 1}.log', 'w') as f:
                    for idea in current_run_ideas:
                        f.write(f"{idea}\n")

                # Step 3: Experiment Design
                main_logger.info("Designing experiment...")
                experiment_plan = experiment_designer.design_experiment(best_idea['idea'])
                if not experiment_plan:
                    main_logger.error("Failed to design experiment. Skipping this experiment run.")
                    continue

                main_logger.info("Experiment plan designed successfully.")

                # New Step: Experiment Coding
                main_logger.info("Generating experiment code...")
                experiment_coder = ExperimentCoder(args.model_name, args.max_tokens)
                experiment_package = experiment_coder.generate_experiment_code(experiment_plan)
                if not experiment_package:
                    main_logger.error("Failed to generate experiment code. Skipping this experiment run.")
                    continue

                main_logger.info("Experiment code generated successfully.")

                # Step 4: Experiment Execution
                main_logger.info("Executing experiment...")
                results = experiment_executor.execute_experiment(experiment_package)
                if not results:
                    main_logger.error("Failed to execute experiment. Skipping this experiment run.")
                    continue
                main_logger.info("Experiment executed successfully.")

                # Step 5: Feedback Loop
                main_logger.info("Refining experiment plan...")
                refined_plan = feedback_loop.refine_experiment(experiment_plan, results)
                refined_plan = parse_and_validate_plan(refined_plan)
                if not refined_plan:
                    main_logger.error("Failed to refine experiment plan. Skipping this experiment run.")
                    continue

                main_logger.info("Experiment plan refined successfully.")

                # Step 6: Refined Experiment Execution
                main_logger.info("Executing refined experiment...")
                final_results = experiment_executor.execute_experiment(refined_plan)
                if not final_results:
                    main_logger.error("Failed to execute refined experiment. Skipping this experiment run.")
                    continue
                main_logger.info("Refined experiment executed successfully.")

                # Step 7: System Augmentation
                main_logger.info("Augmenting system...")
                system_augmentor.augment_system(final_results)
                main_logger.info("System augmentation completed.")

                # Step 8: Benchmarking
                main_logger.info("Running benchmarks...")
                benchmarking = Benchmarking()
                current_performance = benchmarking.run_benchmarks()
                main_logger.info(f"Performance Metrics: {current_performance}")

                # Compare current performance with previous performance
                if previous_performance:
                    improvement = compare_performance(previous_performance, current_performance)
                    main_logger.info(f"Performance Improvement: {improvement}")

                    # Revert changes if no improvement is detected
                    if not improvement:
                        main_logger.warning("No performance improvement detected. Reverting changes.")
                        if backup_path:
                            restore_code(backup_path, '.')
                            main_logger.info("Restored code from backup.")
                        continue

                previous_performance = current_performance

                # Step 9: Report Writing
                main_logger.info("Writing report...")
                report_writer = ReportWriter()
                report_writer.write_report(best_idea, refined_plan, final_results, current_performance)
                main_logger.info("Report written successfully.")

                # Step 10: Log Error Checking
                main_logger.info("Checking logs for errors and warnings...")
                log_error_checker = LogErrorChecker(args.model_name, args.max_tokens)
                errors_warnings = log_error_checker.check_logs('logs/main.log')
                main_logger.info(f"Log Analysis: {len(errors_warnings)} issues found")

                # Step 11: Error Fixing
                if errors_warnings:
                    main_logger.info("Fixing errors...")
                    error_fixer.fix_errors(errors_warnings)
                    main_logger.info("Error fixing completed.")
                else:
                    main_logger.info("No errors or warnings found in logs.")

                # Run tests after modifications
                main_logger.info("Running all tests...")
                test_result = os.system('python -m unittest discover tests')
                if test_result != 0:
                    main_logger.error("Tests failed. Reverting changes and terminating the experiment run.")
                    if backup_path:
                        restore_code(backup_path, '.')
                        main_logger.info("Restored code from backup.")
                    continue
                else:
                    main_logger.info("All tests passed successfully.")

                main_logger.info("Experiment run completed.")

            except Exception as e:
                main_logger.error(f"Error in experiment run {experiment_run + 1}: {str(e)}")
                main_logger.error(traceback.format_exc())
                continue

        main_logger.info("AI Research System execution completed.")

    except OpenAIError as oe:
        main_logger.error(f"OpenAI API error occurred: {oe}")
        main_logger.error(traceback.format_exc())
    except ValueError as ve:
        main_logger.error(f"Value error occurred: {ve}")
        main_logger.error(traceback.format_exc())
    except IOError as io:
        main_logger.error(f"I/O error occurred: {io}")
        main_logger.error(traceback.format_exc())
    except Exception as e:
        main_logger.error(f"An unexpected error occurred: {e}")
        main_logger.error(traceback.format_exc())
    finally:
        if backup_path:
            restore_code(backup_path, '.')
            main_logger.info("Restored code from backup due to error.")

def compare_performance(previous, current):
    """
    Compare current performance metrics with previous metrics.
    This function will be used in the main experiment loop to determine if the system's
    performance has improved after each iteration.

    Args:
    previous (dict): A dictionary containing the previous performance metrics.
    current (dict): A dictionary containing the current performance metrics.

    Returns:
    bool: True if there's an overall improvement, False otherwise.

    Note:
    - This function will be called after each experiment run to compare the results.
    - It will be used to decide whether to keep the changes made in the current iteration
      or to revert to the previous state.
    - The specific implementation of this function should consider various performance
      metrics and their relative importance to determine overall improvement.
    """
    # TODO: Implement logic to compare performance metrics
    # Consider using a weighted average of different metrics
    # Return True if the overall performance has improved, False otherwise
    pass

if __name__ == "__main__":
    main()