# benchmarking.py

from utils.logger import setup_logger
from system_augmentation import SystemAugmentor

class Benchmarking:
    def __init__(self, system_augmentor=None):
        self.logger = setup_logger('benchmarking', 'logs/benchmarking.log')
        self.system_augmentor = system_augmentor

    def run_benchmarks(self):
        self.logger.info("Running benchmarks...")
        try:
            performance_metrics = {
                'idea_quality': self._evaluate_idea_quality(),
                'idea_evaluation_effectiveness': self._evaluate_idea_evaluation(),
                'experiment_design_quality': self._evaluate_experiment_design(),
                'experiment_execution_efficiency': self._evaluate_experiment_execution(),
                'research_application_creativity': self._evaluate_research_application(),
                'system_reliability': self._evaluate_system_reliability(),
                'coding_task_performance': self._evaluate_coding_task_performance(),
                'report_quality': self._evaluate_report_quality(),
                'log_error_checking_accuracy': self._evaluate_log_error_checking(),
                'error_fixing_effectiveness': self._evaluate_error_fixing()
            }
            self.logger.info(f"Benchmark performance metrics: {performance_metrics}")
            return performance_metrics
        except Exception as e:
            self.logger.error(f"Error running benchmarks: {e}")
            return {}

    def _evaluate_idea_quality(self):
        return self._fallback_benchmark() if not self.system_augmentor else self.system_augmentor._benchmark_idea_quality()

    def _evaluate_idea_evaluation(self):
        return self._fallback_benchmark() if not self.system_augmentor else self.system_augmentor._benchmark_idea_evaluation()

    def _evaluate_experiment_design(self):
        return self._fallback_benchmark() if not self.system_augmentor else self.system_augmentor._benchmark_experiment_design()

    def _evaluate_experiment_execution(self):
        return self._fallback_benchmark() if not self.system_augmentor else self.system_augmentor._benchmark_experiment_execution()

    def _evaluate_research_application(self):
        return self._fallback_benchmark() if not self.system_augmentor else self.system_augmentor._benchmark_research_application()

    def _evaluate_system_reliability(self):
        return self._fallback_benchmark() if not self.system_augmentor else self.system_augmentor._benchmark_system_reliability()

    def _evaluate_coding_task_performance(self):
        return self._fallback_benchmark() if not self.system_augmentor else self.system_augmentor._benchmark_coding_task()

    def _evaluate_report_quality(self):
        return self._fallback_benchmark() if not self.system_augmentor else self.system_augmentor._benchmark_report_quality()

    def _evaluate_log_error_checking(self):
        return self._fallback_benchmark() if not self.system_augmentor else self.system_augmentor._benchmark_log_error_checking()

    def _evaluate_error_fixing(self):
        return self._fallback_benchmark() if not self.system_augmentor else self.system_augmentor._benchmark_error_fixing()

    def _fallback_benchmark(self):
        self.logger.warning("Using fallback benchmark method. SystemAugmentor not available.")
        return 0.5  # Return a default value
