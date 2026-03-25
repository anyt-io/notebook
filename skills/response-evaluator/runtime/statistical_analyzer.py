"""Statistical analysis for evaluation scores."""

import math

from config import DEFAULT_CONFIG, EvaluationConfig
from models import ResponseEvaluation


class StatisticalAnalyzer:
    """Performs statistical analysis on evaluation scores."""

    def __init__(self, config: EvaluationConfig | None = None) -> None:
        self.config = config or DEFAULT_CONFIG

    def calculate_confidence_interval(self, scores: list[float], confidence_level: float = 0.95) -> tuple[float, float]:
        """Calculate confidence interval for a set of scores.

        Uses normal approximation for the confidence interval.
        """
        if not scores:
            return (0.0, 0.0)

        n = len(scores)
        mean = sum(scores) / n

        if n == 1:
            return (mean, mean)

        variance = sum((x - mean) ** 2 for x in scores) / (n - 1)
        std_dev = math.sqrt(variance)
        std_error = std_dev / math.sqrt(n)

        # Z-scores for common confidence levels
        z_scores: dict[float, float] = {
            0.90: 1.645,
            0.95: 1.96,
            0.99: 2.576,
        }
        z = z_scores.get(confidence_level, 1.96)

        margin = z * std_error
        lower = max(0.0, round(mean - margin, 4))
        upper = min(1.0, round(mean + margin, 4))

        return (lower, upper)

    def calculate_aggregate_score(self, evaluations: list[ResponseEvaluation]) -> float:
        """Calculate a weighted aggregate score across all evaluations."""
        if not evaluations:
            return 0.0

        total_score = 0.0
        for evaluation in evaluations:
            weighted = (
                self.config.relevance_weight * evaluation.relevance_score
                + self.config.coherence_weight * evaluation.coherence_score
                + self.config.completeness_weight * evaluation.completeness_score
                + self.config.hallucination_penalty_weight * (1.0 - evaluation.hallucination_score)
            )
            total_score += weighted

        return round(total_score / len(evaluations), 4)

    def identify_weak_areas(self, evaluations: list[ResponseEvaluation], threshold: float = 0.5) -> list[str]:
        """Identify evaluation categories where average scores fall below the threshold."""
        if not evaluations:
            return []

        n = len(evaluations)
        avg_relevance = sum(e.relevance_score for e in evaluations) / n
        avg_coherence = sum(e.coherence_score for e in evaluations) / n
        avg_completeness = sum(e.completeness_score for e in evaluations) / n
        avg_hallucination = sum(e.hallucination_score for e in evaluations) / n

        weak: list[str] = []
        if avg_relevance < threshold:
            weak.append("relevance")
        if avg_coherence < threshold:
            weak.append("coherence")
        if avg_completeness < threshold:
            weak.append("completeness")
        if avg_hallucination > (1.0 - threshold):
            weak.append("hallucination")

        return weak

    def score_distribution(self, scores: list[float]) -> dict:
        """Calculate distribution statistics for a set of scores."""
        if not scores:
            return {"mean": 0.0, "median": 0.0, "std_dev": 0.0, "min": 0.0, "max": 0.0}

        n = len(scores)
        mean = sum(scores) / n

        sorted_scores = sorted(scores)
        median = (sorted_scores[n // 2 - 1] + sorted_scores[n // 2]) / 2 if n % 2 == 0 else sorted_scores[n // 2]

        if n > 1:
            variance = sum((x - mean) ** 2 for x in scores) / (n - 1)
            std_dev = math.sqrt(variance)
        else:
            std_dev = 0.0

        return {
            "mean": round(mean, 4),
            "median": round(median, 4),
            "std_dev": round(std_dev, 4),
            "min": round(min(scores), 4),
            "max": round(max(scores), 4),
        }
