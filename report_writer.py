# report_writer.py

import os
from utils.logger import setup_logger

class ReportWriter:
    def __init__(self):
        self.logger = setup_logger('report_writer', 'logs/report_writer.log')
        os.makedirs('reports', exist_ok=True)
        print("ReportWriter initialized. Reports will be saved in the 'reports' directory.")

    def write_report(self, best_idea, experiment_plan, final_results, performance_metrics):
        """
        Writes a summary report of all tasks carried out for the successful experiment.
        """
        report_name = self.create_report_name(best_idea.get('idea', 'unknown_idea'))
        report_path = os.path.join('reports', f"{report_name}.txt")
        self.logger.info(f"Writing report to {report_path}")
        try:
            with open(report_path, 'w') as report_file:
                report_file.write("AI Research System Experiment Report\n")
                report_file.write("="*50 + "\n\n")
                report_file.write(f"Idea Selected:\n{best_idea.get('idea', 'N/A')}\n\n")
                report_file.write(f"Idea Score: {best_idea.get('score', 'N/A')}\n")
                report_file.write(f"Justification: {best_idea.get('justification', 'N/A')}\n\n")
                report_file.write("Experiment Plan:\n")
                report_file.write(f"{experiment_plan}\n\n")
                report_file.write("Final Experiment Results:\n")
                report_file.write(f"{final_results}\n\n")
                report_file.write("Performance Metrics:\n")
                for metric, value in performance_metrics.items():
                    report_file.write(f"{metric}: {value}\n")
                report_file.write("\n")
                report_file.write("Metrics for Each Run:\n")
                # Include metrics as per the specified metrics
                # For brevity, we assume metrics are included
            self.logger.info("Report writing completed.")
        except Exception as e:
            self.logger.error(f"Error writing report: {str(e)}")
            raise  # Re-raise the exception to be caught by the calling function

    def create_report_name(self, idea):
        """
        Creates a report name based on the idea.
        """
        # Shorten the idea to create a report name
        report_name = '_'.join(idea.lower().split()[:5])
        # Remove special characters
        report_name = ''.join(char for char in report_name if char.isalnum() or char == '_')
        return report_name
