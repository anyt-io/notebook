"""Scoring engine for interview responses."""

from __future__ import annotations

import math

from models import InterviewSession, Question


class ScoreEngine:
    """Scores interview responses and calculates confidence metrics."""

    def score_response(self, question: Question, response: str) -> float:
        """Score a response based on keyword matching (0-1).

        Calculates the fraction of expected keywords present in the response.
        Matching is case-insensitive.
        """
        if not question.expected_answer_keywords:
            return 1.0

        response_lower = response.lower()
        matched = sum(1 for kw in question.expected_answer_keywords if kw.lower() in response_lower)
        return matched / len(question.expected_answer_keywords)

    def calculate_confidence(self, scores: list[float]) -> float:
        """Calculate a confidence value from a list of scores.

        Returns the mean score as the confidence estimate.
        Returns 0.0 for empty input.
        """
        if not scores:
            return 0.0
        return sum(scores) / len(scores)

    def meets_threshold(self, session: InterviewSession) -> bool:
        """Check if the session's overall confidence meets the configured threshold."""
        scores = [r.score for r in session.responses]
        confidence = self.calculate_confidence(scores)
        return confidence >= session.config.confidence_threshold

    def get_confidence_interval(self, scores: list[float], confidence_level: float = 0.95) -> tuple[float, float]:
        """Calculate a statistical confidence interval for the scores.

        Uses a normal approximation. Returns (lower, upper) bounds clamped to [0, 1].
        For fewer than 2 scores, returns the mean as both bounds.
        """
        if not scores:
            return (0.0, 0.0)

        mean = sum(scores) / len(scores)
        n = len(scores)

        if n < 2:
            return (max(0.0, mean), min(1.0, mean))

        variance = sum((s - mean) ** 2 for s in scores) / (n - 1)
        std_err = math.sqrt(variance / n)

        # Z-scores for common confidence levels
        z_scores = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
        z = z_scores.get(confidence_level, 1.96)

        margin = z * std_err
        lower = max(0.0, mean - margin)
        upper = min(1.0, mean + margin)
        return (lower, upper)
