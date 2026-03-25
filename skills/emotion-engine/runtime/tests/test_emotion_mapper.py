"""Tests for the emotion mapper."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from emotion_mapper import EmotionMapper
from models import EmotionState


class TestEmotionMapper:
    """Tests for EmotionMapper."""

    def setup_method(self) -> None:
        self.mapper = EmotionMapper()

    def test_map_positive_to_satisfied(self) -> None:
        """Positive sentiment with good confidence should map to satisfied."""
        sentiment: dict[str, object] = {"polarity": 0.8, "subjectivity": 0.6, "evasion": 0.0, "confidence": 0.8}
        result = self.mapper.map_to_emotion(sentiment, context="interview")
        assert result.emotion == "satisfied"
        assert result.intensity > 0.0

    def test_map_evasive_to_skeptical(self) -> None:
        """High evasion should map to skeptical."""
        sentiment: dict[str, object] = {"polarity": 0.0, "subjectivity": 0.3, "evasion": 0.7, "confidence": 0.3}
        result = self.mapper.map_to_emotion(sentiment, context="interview")
        assert result.emotion == "skeptical"

    def test_map_neutral_to_attentive(self) -> None:
        """Neutral sentiment in interview context should map to attentive."""
        sentiment: dict[str, object] = {"polarity": 0.0, "subjectivity": 0.1, "evasion": 0.0, "confidence": 0.5}
        result = self.mapper.map_to_emotion(sentiment, context="interview")
        assert result.emotion == "attentive"

    def test_map_negative_to_stern(self) -> None:
        """Negative sentiment should map to stern."""
        sentiment: dict[str, object] = {"polarity": -0.7, "subjectivity": 0.5, "evasion": 0.0, "confidence": 0.6}
        result = self.mapper.map_to_emotion(sentiment, context="interview")
        assert result.emotion == "stern"

    def test_generate_transition(self) -> None:
        """Verify transition structure between two emotions."""
        current = EmotionState("neutral", 0.3, 0.5)
        target = EmotionState("skeptical", 0.7, 0.8)
        transition = self.mapper.generate_transition(current, target)

        assert transition.from_emotion == current
        assert transition.to_emotion == target
        assert transition.duration_ms > 0
        assert transition.trigger == "response_analysis"

    def test_generate_sequence(self) -> None:
        """Verify sequence generation from multiple responses."""
        responses = [
            {"id": "r1", "text": "I absolutely love working on challenging projects!"},
            {"id": "r2", "text": "I don't remember, it's complicated, can we move on?"},
            {"id": "r3", "text": "The project was completed on time with great results."},
        ]
        sequences = self.mapper.generate_sequence(responses)

        assert len(sequences) == 3
        assert sequences[0].response_id == "r1"
        assert sequences[1].response_id == "r2"
        assert sequences[2].response_id == "r3"

        # Each sequence should have transitional emotions
        for seq in sequences:
            assert len(seq.transitional_emotions) > 0
            assert seq.baseline_emotion.emotion == "attentive"
