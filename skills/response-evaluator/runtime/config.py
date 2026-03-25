"""Configuration for response evaluation."""

from dataclasses import dataclass


@dataclass
class EvaluationConfig:
    """Configuration for the response evaluator."""

    # Confidence thresholds
    confidence_level: float = 0.95
    min_confidence_threshold: float = 0.3

    # Hallucination sensitivity (0-1, higher = more sensitive)
    hallucination_sensitivity: float = 0.5
    hallucination_flag_threshold: float = 0.6

    # Ordinal scale settings
    ordinal_scale: int = 5
    ordinal_min: int = 1

    # Scoring weights
    relevance_weight: float = 0.35
    coherence_weight: float = 0.25
    completeness_weight: float = 0.25
    hallucination_penalty_weight: float = 0.15

    # Collision detection
    collision_severity_threshold: float = 0.5

    # Weak area threshold
    weak_area_threshold: float = 0.5

    # Keyword matching
    keyword_match_weight: float = 0.4
    context_grounding_weight: float = 0.3
    specificity_weight: float = 0.3

    # Recommendations
    max_recommendations: int = 10

    def validate(self) -> None:
        """Validate configuration values."""
        weights = [self.relevance_weight, self.coherence_weight, self.completeness_weight]
        total = sum(weights) + self.hallucination_penalty_weight
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"Scoring weights must sum to 1.0, got {total}")
        if not 0 <= self.hallucination_sensitivity <= 1:
            raise ValueError("hallucination_sensitivity must be between 0 and 1")
        if self.ordinal_scale < 2:
            raise ValueError("ordinal_scale must be at least 2")


# Default configuration instance
DEFAULT_CONFIG = EvaluationConfig()
