"""Data models for emotion states, transitions, and animation keyframes."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EmotionState:
    """Represents an emotional state with intensity and confidence."""

    emotion: str
    intensity: float  # 0.0 - 1.0
    confidence: float  # 0.0 - 1.0

    def __post_init__(self) -> None:
        self.intensity = max(0.0, min(1.0, self.intensity))
        self.confidence = max(0.0, min(1.0, self.confidence))

    def to_dict(self) -> dict[str, str | float]:
        return {
            "emotion": self.emotion,
            "intensity": round(self.intensity, 3),
            "confidence": round(self.confidence, 3),
        }


@dataclass
class EmotionTransition:
    """Represents a transition between two emotion states."""

    from_emotion: EmotionState
    to_emotion: EmotionState
    duration_ms: int
    trigger: str

    def to_dict(self) -> dict[str, object]:
        return {
            "from_emotion": self.from_emotion.to_dict(),
            "to_emotion": self.to_emotion.to_dict(),
            "duration_ms": self.duration_ms,
            "trigger": self.trigger,
        }


@dataclass
class FacialExpression:
    """Facial expression parameters for avatar rendering."""

    eyebrows: str
    eyes: str
    mouth: str
    head_tilt: float

    def to_dict(self) -> dict[str, str | float]:
        return {
            "eyebrows": self.eyebrows,
            "eyes": self.eyes,
            "mouth": self.mouth,
            "head_tilt": round(self.head_tilt, 1),
        }


@dataclass
class AnimationKeyframe:
    """A single keyframe in an animation sequence."""

    timestamp_ms: int
    emotion: EmotionState
    expression: FacialExpression
    duration_ms: int

    def to_dict(self) -> dict[str, object]:
        return {
            "timestamp_ms": self.timestamp_ms,
            "emotion": self.emotion.to_dict(),
            "expression": self.expression.to_dict(),
            "duration_ms": self.duration_ms,
        }


@dataclass
class EmotionSequence:
    """Full emotion sequence for a single response."""

    response_id: str
    original_emotion: EmotionState
    transitional_emotions: list[EmotionTransition] = field(default_factory=list)
    final_emotion: EmotionState = field(default_factory=lambda: EmotionState("neutral", 0.3, 0.5))
    baseline_emotion: EmotionState = field(default_factory=lambda: EmotionState("attentive", 0.5, 0.8))

    def to_dict(self) -> dict[str, object]:
        return {
            "response_id": self.response_id,
            "original_emotion": self.original_emotion.to_dict(),
            "transitional_emotions": [t.to_dict() for t in self.transitional_emotions],
            "final_emotion": self.final_emotion.to_dict(),
            "baseline_emotion": self.baseline_emotion.to_dict(),
        }
