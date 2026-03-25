"""Tests for the sentiment analyzer."""

from __future__ import annotations

import sys
from pathlib import Path

# Add runtime to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sentiment import SentimentAnalyzer


class TestSentimentAnalyzer:
    """Tests for SentimentAnalyzer."""

    def setup_method(self) -> None:
        self.analyzer = SentimentAnalyzer()

    def test_positive_sentiment(self) -> None:
        """Positive text should yield positive polarity."""
        result = self.analyzer.analyze("I'm really happy and excited about this great opportunity!")
        polarity = result["polarity"]
        assert isinstance(polarity, float)
        assert polarity > 0.0
        keywords = result["keywords"]
        assert isinstance(keywords, list)
        assert len(keywords) > 0

    def test_negative_sentiment(self) -> None:
        """Negative text should yield negative polarity."""
        result = self.analyzer.analyze("This is terrible and I'm very disappointed with the awful results.")
        polarity = result["polarity"]
        assert isinstance(polarity, float)
        assert polarity < 0.0
        keywords = result["keywords"]
        assert isinstance(keywords, list)
        assert len(keywords) > 0

    def test_neutral_sentiment(self) -> None:
        """Factual text should yield near-zero polarity."""
        result = self.analyzer.analyze("The meeting is scheduled for Tuesday at three in the afternoon.")
        polarity = result["polarity"]
        assert isinstance(polarity, float)
        assert -0.2 <= polarity <= 0.2

    def test_evasion_detection(self) -> None:
        """Evasive answers should be flagged with high evasion score."""
        score = self.analyzer.detect_evasion(
            "I don't remember the details, it's complicated.",
            expected_keywords=["budget", "timeline"],
        )
        assert score > 0.3

    def test_evasion_detection_direct_answer(self) -> None:
        """Direct answers should have low evasion score."""
        score = self.analyzer.detect_evasion(
            "The budget was two million dollars and the timeline was six months.",
            expected_keywords=["budget", "timeline"],
        )
        assert score < 0.3

    def test_confidence_detection_confident(self) -> None:
        """Confident language should yield high confidence score."""
        score = self.analyzer.detect_confidence_level("I am absolutely certain this is the correct approach.")
        assert score > 0.5

    def test_confidence_detection_hedging(self) -> None:
        """Hedging language should yield lower confidence score."""
        score = self.analyzer.detect_confidence_level("Maybe it could possibly work, I think, sort of.")
        assert score < 0.5
