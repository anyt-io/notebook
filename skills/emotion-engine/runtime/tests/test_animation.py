"""Tests for the animation script generator."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from animation import AnimationScriptGenerator
from config import FACIAL_EXPRESSION_PARAMS
from models import EmotionSequence, EmotionState, EmotionTransition


class TestAnimationScriptGenerator:
    """Tests for AnimationScriptGenerator."""

    def setup_method(self) -> None:
        self.generator = AnimationScriptGenerator()

    def test_generate_expression_for_each_emotion(self) -> None:
        """Verify facial params are generated for each emotion type."""
        for emotion_name in FACIAL_EXPRESSION_PARAMS:
            state = EmotionState(emotion_name, 0.7, 0.8)
            expr = self.generator.generate_expression(state)

            assert expr.eyebrows != ""
            assert expr.eyes != ""
            assert expr.mouth != ""
            assert isinstance(expr.head_tilt, float)

    def test_generate_expression_unknown_emotion(self) -> None:
        """Unknown emotions should fall back to neutral expression."""
        state = EmotionState("unknown_emotion", 0.5, 0.5)
        expr = self.generator.generate_expression(state)
        assert expr.eyebrows == "relaxed"
        assert expr.eyes == "normal"

    def test_generate_keyframes(self) -> None:
        """Verify keyframe timing and structure."""
        baseline = EmotionState("attentive", 0.5, 0.8)
        target = EmotionState("skeptical", 0.7, 0.8)
        transition = EmotionTransition(baseline, target, duration_ms=500, trigger="test")
        return_transition = EmotionTransition(target, baseline, duration_ms=400, trigger="return")

        sequence = EmotionSequence(
            response_id="test_r1",
            original_emotion=target,
            transitional_emotions=[transition, return_transition],
            final_emotion=target,
            baseline_emotion=baseline,
        )

        keyframes = self.generator.generate_keyframes(sequence)

        # Should have: baseline + 2 transitions + final = 4 keyframes
        assert len(keyframes) == 4

        # Timestamps should be monotonically increasing
        for i in range(1, len(keyframes)):
            assert keyframes[i].timestamp_ms > keyframes[i - 1].timestamp_ms

        # First keyframe should start at 0
        assert keyframes[0].timestamp_ms == 0

    def test_generate_script(self) -> None:
        """Verify full script output with multiple sequences."""
        baseline = EmotionState("attentive", 0.5, 0.8)
        target1 = EmotionState("satisfied", 0.7, 0.8)
        target2 = EmotionState("stern", 0.6, 0.7)

        t1 = EmotionTransition(baseline, target1, 400, "response:r1")
        t1_ret = EmotionTransition(target1, baseline, 300, "return")
        t2 = EmotionTransition(baseline, target2, 600, "response:r2")
        t2_ret = EmotionTransition(target2, baseline, 500, "return")

        sequences = [
            EmotionSequence(
                response_id="r1",
                original_emotion=target1,
                transitional_emotions=[t1, t1_ret],
                final_emotion=target1,
                baseline_emotion=baseline,
            ),
            EmotionSequence(
                response_id="r2",
                original_emotion=target2,
                transitional_emotions=[t2, t2_ret],
                final_emotion=target2,
                baseline_emotion=baseline,
            ),
        ]

        script = self.generator.generate_script(sequences)

        assert len(script) == 2
        assert script[0]["response_id"] == "r1"
        assert script[1]["response_id"] == "r2"

        # Second sequence should start after the first
        assert script[0]["start_time_ms"] == 0
        first_duration = script[0]["total_duration_ms"]
        assert isinstance(first_duration, int)
        assert first_duration > 0
        assert script[1]["start_time_ms"] == first_duration

        # Each entry should have keyframes
        for entry in script:
            assert "keyframes" in entry
            kf_list = entry["keyframes"]
            assert isinstance(kf_list, list)
            assert len(kf_list) > 0
