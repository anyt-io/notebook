"""Tests for expression mapping and interpolation."""

from config import SUPPORTED_EMOTIONS
from expression_map import EXPRESSION_MAP, NEUTRAL, interpolate_expression


def test_all_emotions_mapped() -> None:
    """All 7 supported emotions have entries in the expression map."""
    for emotion in SUPPORTED_EMOTIONS:
        assert emotion in EXPRESSION_MAP, f"Missing expression map entry for '{emotion}'"
    assert len(SUPPORTED_EMOTIONS) == 7


def test_interpolate_zero_is_neutral() -> None:
    """Intensity 0 should produce values approaching neutral."""
    for emotion, base in EXPRESSION_MAP.items():
        result = interpolate_expression(base, 0.0)
        assert abs(result.eyebrow_angle - NEUTRAL.eyebrow_angle) < 1e-6, f"{emotion}: eyebrow_angle not neutral at 0"
        assert abs(result.eye_openness - NEUTRAL.eye_openness) < 1e-6, f"{emotion}: eye_openness not neutral at 0"
        assert abs(result.mouth_curve - NEUTRAL.mouth_curve) < 1e-6, f"{emotion}: mouth_curve not neutral at 0"


def test_interpolate_one_is_full() -> None:
    """Intensity 1.0 should return the full expression parameters."""
    for emotion, base in EXPRESSION_MAP.items():
        result = interpolate_expression(base, 1.0)
        assert abs(result.eyebrow_angle - base.eyebrow_angle) < 1e-6, f"{emotion}: eyebrow_angle mismatch at 1.0"
        assert abs(result.eye_openness - base.eye_openness) < 1e-6, f"{emotion}: eye_openness mismatch at 1.0"
        assert abs(result.mouth_curve - base.mouth_curve) < 1e-6, f"{emotion}: mouth_curve mismatch at 1.0"


def test_interpolate_midpoint() -> None:
    """Intensity 0.5 should produce values between neutral and full expression."""
    base = EXPRESSION_MAP["surprised"]
    result = interpolate_expression(base, 0.5)

    # Each param should be midpoint between neutral and base
    expected_eyebrow_height = (NEUTRAL.eyebrow_height + base.eyebrow_height) / 2
    assert abs(result.eyebrow_height - expected_eyebrow_height) < 1e-6

    expected_eye_openness = (NEUTRAL.eye_openness + base.eye_openness) / 2
    assert abs(result.eye_openness - expected_eye_openness) < 1e-6

    expected_mouth_openness = (NEUTRAL.mouth_openness + base.mouth_openness) / 2
    assert abs(result.mouth_openness - expected_mouth_openness) < 1e-6
