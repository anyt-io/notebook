"""Tests for the interview analyzer."""

from __future__ import annotations

from analyzer import InterviewAnalyzer
from models import InterviewSession, ResponseRecord, SimulationConfig


def _make_session_with_responses(responses: list[ResponseRecord]) -> InterviewSession:
    config = SimulationConfig(confidence_threshold=0.7, domain="test")
    session = InterviewSession(domain="test", config=config)
    session.responses = responses
    return session


class TestAnalyzeSession:
    def test_analyze_session(self) -> None:
        analyzer = InterviewAnalyzer()
        session = _make_session_with_responses(
            [
                ResponseRecord(
                    question_id="basics_q1", question_text="Q?", user_response="A", score=0.8, confidence=0.8
                ),
                ResponseRecord(
                    question_id="basics_q2", question_text="Q?", user_response="A", score=0.9, confidence=0.85
                ),
            ]
        )
        result = analyzer.analyze(session)

        assert "overall_score" in result
        assert "confidence_interval" in result
        assert "category_scores" in result
        assert "weak_areas" in result
        assert "strong_areas" in result
        assert "recommendations" in result
        assert "difficulty_progression" in result
        assert result["total_questions"] == 2

    def test_overall_score_calculation(self) -> None:
        analyzer = InterviewAnalyzer()
        session = _make_session_with_responses(
            [
                ResponseRecord(
                    question_id="basics_q1", question_text="Q?", user_response="A", score=0.6, confidence=0.6
                ),
                ResponseRecord(
                    question_id="basics_q2", question_text="Q?", user_response="A", score=0.8, confidence=0.7
                ),
            ]
        )
        result = analyzer.analyze(session)
        assert abs(result["overall_score"] - 0.7) < 1e-3


class TestCategoryScores:
    def test_category_scores(self) -> None:
        analyzer = InterviewAnalyzer()
        session = _make_session_with_responses(
            [
                ResponseRecord(
                    question_id="basics_q1", question_text="Q?", user_response="A", score=0.9, confidence=0.9
                ),
                ResponseRecord(
                    question_id="basics_q2", question_text="Q?", user_response="A", score=0.7, confidence=0.8
                ),
                ResponseRecord(
                    question_id="advanced_q1", question_text="Q?", user_response="A", score=0.5, confidence=0.7
                ),
            ]
        )
        result = analyzer.analyze(session)
        assert "basics" in result["category_scores"]
        assert "advanced" in result["category_scores"]
        assert abs(result["category_scores"]["basics"] - 0.8) < 1e-3


class TestWeakAreas:
    def test_weak_areas_identified(self) -> None:
        analyzer = InterviewAnalyzer()
        session = _make_session_with_responses(
            [
                ResponseRecord(
                    question_id="basics_q1", question_text="Q?", user_response="A", score=0.9, confidence=0.9
                ),
                ResponseRecord(question_id="hard_q1", question_text="Q?", user_response="A", score=0.3, confidence=0.6),
                ResponseRecord(question_id="hard_q2", question_text="Q?", user_response="A", score=0.2, confidence=0.4),
            ]
        )
        result = analyzer.analyze(session)
        assert "hard" in result["weak_areas"]
        assert "basics" not in result["weak_areas"]


class TestEmptySession:
    def test_empty_session(self) -> None:
        analyzer = InterviewAnalyzer()
        session = _make_session_with_responses([])
        result = analyzer.analyze(session)

        assert result["overall_score"] == 0.0
        assert result["confidence_interval"] == (0.0, 0.0)
        assert result["category_scores"] == {}
        assert result["weak_areas"] == []
        assert result["total_questions"] == 0
        assert len(result["recommendations"]) > 0
