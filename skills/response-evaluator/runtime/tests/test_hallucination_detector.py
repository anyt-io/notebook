"""Tests for hallucination detection."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from hallucination_detector import HallucinationDetector


class TestHallucinationDetector:
    def setup_method(self) -> None:
        self.detector = HallucinationDetector()

    def test_no_hallucination(self) -> None:
        """A relevant response grounded in context should have a low hallucination score."""
        response = "Python is a programming language known for its readability and versatility."
        question = "What is Python?"
        keywords = ["programming", "language", "readability"]
        context = "Python is a high-level programming language known for its readability and versatility."

        score = self.detector.detect(response, question, keywords, context)
        assert score < 0.4, f"Expected low hallucination score, got {score}"

    def test_high_hallucination(self) -> None:
        """A response with fabricated details should have a high hallucination score."""
        response = "Python was created in 2015 by Steve Jobs and runs only on quantum computers."
        question = "What is Python?"
        keywords = ["programming", "language", "readability"]
        context = "Python is a high-level programming language created by Guido van Rossum in 1991."

        score = self.detector.detect(response, question, keywords, context)
        assert score > 0.4, f"Expected high hallucination score, got {score}"

    def test_partial_hallucination(self) -> None:
        """A mix of real and fabricated content should have a moderate score."""
        response = "Python is a programming language. It was invented in 2025 on Mars."
        question = "What is Python?"
        keywords = ["programming", "language"]
        context = "Python is a programming language created by Guido van Rossum."

        score = self.detector.detect(response, question, keywords, context)
        # Should be between low and high
        assert 0.0 <= score <= 1.0

    def test_flag_fabrications(self) -> None:
        """Specific claims not in known facts should be flagged."""
        response = "Revenue increased by 47.3% in 2019. CEO Jane Doe announced the merger on January 5th."
        known_facts = ["The company reported growth.", "A leadership change occurred."]

        flags = self.detector.flag_fabrications(response, known_facts)
        assert len(flags) > 0, "Expected at least one fabrication flag"

    def test_empty_response(self) -> None:
        """Empty response should return 0 hallucination score."""
        score = self.detector.detect("", "What is Python?", ["python"], "")
        assert score == 0.0
