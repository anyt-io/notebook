"""Mapping of emotions to facial expression parameters."""

from __future__ import annotations

from dataclasses import fields

from models import ExpressionParams

# Neutral is the baseline - all values at default
NEUTRAL = ExpressionParams()

EXPRESSION_MAP: dict[str, ExpressionParams] = {
    "neutral": ExpressionParams(
        eyebrow_angle=0.0,
        eyebrow_height=0.0,
        eye_openness=1.0,
        pupil_size=1.0,
        mouth_curve=0.05,
        mouth_openness=0.0,
        head_tilt=0.0,
    ),
    "attentive": ExpressionParams(
        eyebrow_angle=0.1,
        eyebrow_height=0.3,
        eye_openness=1.3,
        pupil_size=1.1,
        mouth_curve=0.0,
        mouth_openness=0.0,
        head_tilt=0.0,
    ),
    "skeptical": ExpressionParams(
        eyebrow_angle=-0.3,
        eyebrow_height=0.2,
        eye_openness=0.7,
        pupil_size=0.9,
        mouth_curve=-0.2,
        mouth_openness=0.0,
        head_tilt=3.0,
    ),
    "satisfied": ExpressionParams(
        eyebrow_angle=0.1,
        eyebrow_height=0.2,
        eye_openness=0.9,
        pupil_size=1.0,
        mouth_curve=0.6,
        mouth_openness=0.1,
        head_tilt=0.0,
    ),
    "stern": ExpressionParams(
        eyebrow_angle=-0.3,
        eyebrow_height=-0.3,
        eye_openness=0.8,
        pupil_size=0.95,
        mouth_curve=-0.1,
        mouth_openness=0.0,
        head_tilt=0.0,
    ),
    "surprised": ExpressionParams(
        eyebrow_angle=0.2,
        eyebrow_height=0.6,
        eye_openness=1.6,
        pupil_size=1.2,
        mouth_curve=0.0,
        mouth_openness=0.7,
        head_tilt=0.0,
    ),
    "concerned": ExpressionParams(
        eyebrow_angle=0.25,
        eyebrow_height=0.2,
        eye_openness=1.0,
        pupil_size=1.0,
        mouth_curve=-0.3,
        mouth_openness=0.05,
        head_tilt=-2.0,
    ),
}


def interpolate_expression(base: ExpressionParams, intensity: float) -> ExpressionParams:
    """Interpolate an expression toward neutral based on intensity.

    Args:
        base: The full-intensity expression parameters.
        intensity: Value from 0.0 (neutral) to 1.0 (full expression).

    Returns:
        Interpolated ExpressionParams.
    """
    intensity = max(0.0, min(1.0, intensity))
    neutral = NEUTRAL
    result_kwargs: dict[str, float] = {}
    for f in fields(ExpressionParams):
        neutral_val = getattr(neutral, f.name)
        base_val = getattr(base, f.name)
        result_kwargs[f.name] = neutral_val + (base_val - neutral_val) * intensity
    return ExpressionParams(**result_kwargs)
