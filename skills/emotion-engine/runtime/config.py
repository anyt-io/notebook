"""Configuration for emotion types, transitions, and intensity ranges."""

from __future__ import annotations

# Base emotion types with default parameters
EMOTION_TYPES: dict[str, dict[str, float | str]] = {
    "neutral": {
        "default_intensity": 0.3,
        "min_intensity": 0.0,
        "max_intensity": 0.5,
        "description": "Default resting state",
    },
    "attentive": {
        "default_intensity": 0.6,
        "min_intensity": 0.3,
        "max_intensity": 1.0,
        "description": "Actively listening, engaged",
    },
    "skeptical": {
        "default_intensity": 0.5,
        "min_intensity": 0.2,
        "max_intensity": 1.0,
        "description": "Questioning, doubtful",
    },
    "satisfied": {
        "default_intensity": 0.7,
        "min_intensity": 0.3,
        "max_intensity": 1.0,
        "description": "Positive response to good answers",
    },
    "stern": {
        "default_intensity": 0.6,
        "min_intensity": 0.3,
        "max_intensity": 1.0,
        "description": "Serious, probing deeper",
    },
    "surprised": {
        "default_intensity": 0.7,
        "min_intensity": 0.4,
        "max_intensity": 1.0,
        "description": "Unexpected answer detected",
    },
    "concerned": {
        "default_intensity": 0.5,
        "min_intensity": 0.2,
        "max_intensity": 0.9,
        "description": "Detecting evasion or inconsistency",
    },
}

# Transition durations in milliseconds between emotion pairs
TRANSITION_DURATIONS: dict[str, int] = {
    "default": 500,
    "neutral_to_attentive": 300,
    "neutral_to_skeptical": 600,
    "neutral_to_satisfied": 400,
    "neutral_to_stern": 700,
    "neutral_to_surprised": 200,
    "neutral_to_concerned": 500,
    "attentive_to_skeptical": 500,
    "attentive_to_satisfied": 300,
    "attentive_to_stern": 600,
    "satisfied_to_skeptical": 700,
    "skeptical_to_stern": 400,
    "surprised_to_attentive": 400,
    "concerned_to_stern": 300,
}

# Facial expression parameter mappings per emotion
FACIAL_EXPRESSION_PARAMS: dict[str, dict[str, str | float]] = {
    "neutral": {"eyebrows": "relaxed", "eyes": "normal", "mouth": "closed", "head_tilt": 0.0},
    "attentive": {"eyebrows": "slightly_raised", "eyes": "wide", "mouth": "slightly_open", "head_tilt": 5.0},
    "skeptical": {"eyebrows": "one_raised", "eyes": "narrowed", "mouth": "pursed", "head_tilt": -3.0},
    "satisfied": {"eyebrows": "relaxed", "eyes": "soft", "mouth": "slight_smile", "head_tilt": 2.0},
    "stern": {"eyebrows": "furrowed", "eyes": "focused", "mouth": "tight", "head_tilt": -2.0},
    "surprised": {"eyebrows": "raised", "eyes": "wide_open", "mouth": "open", "head_tilt": 8.0},
    "concerned": {"eyebrows": "knitted", "eyes": "narrowed", "mouth": "frown", "head_tilt": -5.0},
}

# Baseline emotion for interview context
BASELINE_EMOTION = "attentive"
BASELINE_INTENSITY = 0.5

# Sentiment thresholds for emotion mapping
EVASION_THRESHOLD = 0.5
POSITIVE_THRESHOLD = 0.3
NEGATIVE_THRESHOLD = -0.3
CONFIDENCE_LOW_THRESHOLD = 0.3
CONFIDENCE_HIGH_THRESHOLD = 0.7
