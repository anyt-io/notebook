"""Data models for response evaluation."""

from dataclasses import dataclass, field


@dataclass
class ResponseEvaluation:
    """Evaluation result for a single response."""

    response_id: str
    original_response: str
    relevance_score: float  # 0-1
    coherence_score: float  # 0-1
    completeness_score: float  # 0-1
    hallucination_score: float  # 0-1, higher = more hallucinated
    ordinal_rank: int
    confidence: float  # 0-1
    flags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "response_id": self.response_id,
            "original_response": self.original_response,
            "relevance_score": self.relevance_score,
            "coherence_score": self.coherence_score,
            "completeness_score": self.completeness_score,
            "hallucination_score": self.hallucination_score,
            "ordinal_rank": self.ordinal_rank,
            "confidence": self.confidence,
            "flags": self.flags,
        }


@dataclass
class CollidingAnswer:
    """A pair of contradictory answers within a session."""

    response_id_a: str
    response_id_b: str
    contradiction_description: str
    severity: float  # 0-1

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "response_id_a": self.response_id_a,
            "response_id_b": self.response_id_b,
            "contradiction_description": self.contradiction_description,
            "severity": self.severity,
        }


@dataclass
class EvaluationReport:
    """Full evaluation report for a session."""

    session_id: str
    evaluations: list[ResponseEvaluation] = field(default_factory=list)
    colliding_answers: list[CollidingAnswer] = field(default_factory=list)
    aggregate_score: float = 0.0
    confidence_interval: tuple[float, float] = (0.0, 0.0)
    hallucination_count: int = 0
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "evaluations": [e.to_dict() for e in self.evaluations],
            "colliding_answers": [c.to_dict() for c in self.colliding_answers],
            "aggregate_score": self.aggregate_score,
            "confidence_interval": list(self.confidence_interval),
            "hallucination_count": self.hallucination_count,
            "recommendations": self.recommendations,
        }
