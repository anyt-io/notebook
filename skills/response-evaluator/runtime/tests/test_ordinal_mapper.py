"""Tests for ordinal mapping."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ordinal_mapper import OrdinalMapper


class TestOrdinalMapper:
    def setup_method(self) -> None:
        self.mapper = OrdinalMapper()

    def test_map_response(self) -> None:
        """Verify ordinal assignment produces valid rank."""
        response = "Python is a versatile programming language used for web development, data science, and automation."
        rank = self.mapper.map_response(response, "q1", scale=5)
        assert 1 <= rank <= 5, f"Expected rank 1-5, got {rank}"

    def test_map_batch(self) -> None:
        """Verify batch mapping returns results for all responses."""
        responses = [
            {"response_id": "r1", "response": "Short answer.", "question_id": "q1"},
            {
                "response_id": "r2",
                "response": "A much more detailed and comprehensive answer covering multiple aspects of the topic.",
                "question_id": "q1",
            },
            {"response_id": "r3", "response": "", "question_id": "q2"},
        ]
        result = self.mapper.map_batch(responses)
        assert len(result) == 3
        assert "r1" in result
        assert "r2" in result
        assert "r3" in result
        # Detailed answer should rank higher than empty
        assert result["r2"] >= result["r3"]

    def test_detect_collisions(self) -> None:
        """Contradictory answers to the same question should be detected."""
        responses = [
            {"response_id": "r1", "response": "Yes absolutely.", "question_id": "q1"},
            {
                "response_id": "r2",
                "response": "This is a very detailed comprehensive answer covering all important points and aspects.",
                "question_id": "q1",
            },
        ]
        mappings = {"r1": 1, "r2": 5}
        collisions = self.mapper.detect_collisions(mappings, responses)
        assert len(collisions) > 0, "Expected at least one collision"

    def test_ordinal_range(self) -> None:
        """All mapped values should be within the specified scale."""
        responses = [
            "Short.",
            "A moderate length response with some detail.",
            "A very detailed, comprehensive, and well-structured response that covers multiple aspects "
            "of the topic with examples and supporting evidence.",
            "",
        ]
        for resp in responses:
            rank = self.mapper.map_response(resp, "q1", scale=5)
            assert 1 <= rank <= 5, f"Rank {rank} out of range for response: {resp!r}"

    def test_generate_ordinal_list(self) -> None:
        """Verify ordinal list generation produces correct structure."""
        answers = [
            "Brief.",
            "A detailed answer with examples and thorough explanation of the concept.",
            "Medium length answer.",
        ]
        result = self.mapper.generate_ordinal_list(answers, "test context")
        assert len(result) == 3
        assert result[0]["ordinal_rank"] == 1
        assert result[1]["ordinal_rank"] == 2
        assert result[2]["ordinal_rank"] == 3
        # First should have highest quality score
        assert result[0]["quality_score"] >= result[1]["quality_score"]
