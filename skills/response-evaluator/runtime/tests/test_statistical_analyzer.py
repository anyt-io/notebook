"""Tests for statistical analysis."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models import ResponseEvaluation
from statistical_analyzer import StatisticalAnalyzer


class TestStatisticalAnalyzer:
    def setup_method(self) -> None:
        self.analyzer = StatisticalAnalyzer()

    def test_confidence_interval(self) -> None:
        """Verify confidence interval calculation."""
        scores = [0.7, 0.8, 0.75, 0.85, 0.9]
        lower, upper = self.analyzer.calculate_confidence_interval(scores, 0.95)
        assert lower < upper, f"Lower ({lower}) should be less than upper ({upper})"
        mean = sum(scores) / len(scores)
        assert lower <= mean <= upper, "Mean should be within confidence interval"

    def test_confidence_interval_single(self) -> None:
        """Single score should return identical bounds."""
        lower, upper = self.analyzer.calculate_confidence_interval([0.5])
        assert lower == upper == 0.5

    def test_confidence_interval_empty(self) -> None:
        """Empty scores should return (0, 0)."""
        assert self.analyzer.calculate_confidence_interval([]) == (0.0, 0.0)

    def test_aggregate_score(self) -> None:
        """Verify weighted aggregate scoring."""
        evaluations = [
            ResponseEvaluation(
                response_id="r1",
                original_response="test",
                relevance_score=0.8,
                coherence_score=0.7,
                completeness_score=0.9,
                hallucination_score=0.1,
                ordinal_rank=4,
                confidence=0.8,
            ),
            ResponseEvaluation(
                response_id="r2",
                original_response="test2",
                relevance_score=0.6,
                coherence_score=0.5,
                completeness_score=0.7,
                hallucination_score=0.3,
                ordinal_rank=3,
                confidence=0.6,
            ),
        ]
        score = self.analyzer.calculate_aggregate_score(evaluations)
        assert 0.0 <= score <= 1.0, f"Aggregate score {score} out of range"
        assert score > 0.5, f"Expected reasonably high aggregate, got {score}"

    def test_weak_areas(self) -> None:
        """Low-scoring categories should be identified."""
        evaluations = [
            ResponseEvaluation(
                response_id="r1",
                original_response="test",
                relevance_score=0.3,
                coherence_score=0.8,
                completeness_score=0.4,
                hallucination_score=0.2,
                ordinal_rank=2,
                confidence=0.5,
            ),
        ]
        weak = self.analyzer.identify_weak_areas(evaluations, threshold=0.5)
        assert "relevance" in weak
        assert "completeness" in weak
        assert "coherence" not in weak

    def test_score_distribution(self) -> None:
        """Verify distribution statistics."""
        scores = [0.5, 0.6, 0.7, 0.8, 0.9]
        dist = self.analyzer.score_distribution(scores)
        assert dist["mean"] == 0.7
        assert dist["median"] == 0.7
        assert dist["min"] == 0.5
        assert dist["max"] == 0.9
        assert dist["std_dev"] > 0

    def test_score_distribution_empty(self) -> None:
        """Empty scores should return zeros."""
        dist = self.analyzer.score_distribution([])
        assert dist["mean"] == 0.0
