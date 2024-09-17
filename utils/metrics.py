from typing import Dict, List, Tuple

class PerformanceMetrics:
    def __init__(self):
        self.metrics = {
            'idea_quality': 0.0,
            'idea_evaluation_effectiveness': 0.0,
            'experiment_design_quality': 0.0,
            'experiment_execution_efficiency': 0.0,
            'research_application_creativity': 0.0,
            'system_reliability': 0.0,
            'coding_task_performance': 0.0,
            'report_quality': 0.0,
            'log_error_checking_accuracy': 0.0,
            'error_fixing_effectiveness': 0.0
        }

    def update(self, metric: str, value: float):
        if metric in self.metrics:
            self.metrics[metric] = value
        else:
            raise ValueError(f"Invalid metric: {metric}")

    def get_all(self) -> Dict[str, float]:
        return self.metrics.copy()

def evaluate_system_performance(previous_metrics: Dict[str, float], current_metrics: Dict[str, float]) -> Tuple[bool, Dict[str, float], List[str]]:
    improvements = []
    improvement_percentages = {}
    improved_metrics = []

    for metric, current_value in current_metrics.items():
        if metric in previous_metrics:
            previous_value = previous_metrics[metric]
            if previous_value != 0:
                improvement_percentage = ((current_value - previous_value) / previous_value) * 100
            else:
                improvement_percentage = 100 if current_value > 0 else 0
            
            improvement_percentages[metric] = improvement_percentage
            
            if current_value > previous_value:
                improvements.append(1)
                improved_metrics.append(metric)
            elif current_value < previous_value:
                improvements.append(-1)
            else:
                improvements.append(0)
        else:
            improvements.append(1)
            improvement_percentages[metric] = 100
            improved_metrics.append(metric)

    overall_improvement = sum(improvements) > 0

    return overall_improvement, improvement_percentages, improved_metrics

def analyze_performance_changes(improvement_percentages: Dict[str, float], threshold: float = 5.0) -> Dict[str, List[str]]:
    analysis = {
        "significant_improvements": [],
        "minor_improvements": [],
        "no_change": [],
        "minor_regressions": [],
        "significant_regressions": []
    }

    for metric, percentage in improvement_percentages.items():
        if percentage > threshold:
            analysis["significant_improvements"].append(metric)
        elif 0 < percentage <= threshold:
            analysis["minor_improvements"].append(metric)
        elif percentage == 0:
            analysis["no_change"].append(metric)
        elif -threshold <= percentage < 0:
            analysis["minor_regressions"].append(metric)
        else:
            analysis["significant_regressions"].append(metric)

    return analysis

def generate_performance_report(previous_metrics: Dict[str, float], current_metrics: Dict[str, float]) -> str:
    overall_improvement, improvement_percentages, improved_metrics = evaluate_system_performance(previous_metrics, current_metrics)
    analysis = analyze_performance_changes(improvement_percentages)

    report = "Performance Evaluation Report\n"
    report += "============================\n\n"

    report += f"Overall Improvement: {'Yes' if overall_improvement else 'No'}\n\n"

    report += "Metric Changes:\n"
    for metric, percentage in improvement_percentages.items():
        report += f"  {metric}: {percentage:.2f}%\n"

    report += "\nAnalysis:\n"
    for category, metrics in analysis.items():
        if metrics:
            report += f"  {category.replace('_', ' ').title()}:\n"
            for metric in metrics:
                report += f"    - {metric}\n"

    return report

def calculate_overall_performance_score(metrics: Dict[str, float]) -> float:
    weights = {
        'idea_quality': 0.15,
        'idea_evaluation_effectiveness': 0.1,
        'experiment_design_quality': 0.15,
        'experiment_execution_efficiency': 0.1,
        'research_application_creativity': 0.1,
        'system_reliability': 0.1,
        'coding_task_performance': 0.1,
        'report_quality': 0.05,
        'log_error_checking_accuracy': 0.05,
        'error_fixing_effectiveness': 0.1
    }

    score = sum(metrics[metric] * weight for metric, weight in weights.items())
    return score
