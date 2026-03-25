"""Tests for the scoring engine."""

from __future__ import annotations

from models import InterviewSession, Question, ResponseRecord, SimulationConfig
from scoring import ScoreEngine


def _make_question(keywords: list[str]) -> Question:
    return Question(
        id="q1",
        text="Test question?",
        category="test",
        difficulty=1,
        expected_answer_keywords=keywords,
    )


class TestScoreResponse:
    def test_perfect_match(self) -> None:
        engine = ScoreEngine()
        q = _make_question(["visit", "business", "tourism"])
        score = engine.score_response(q, "I am here to visit for business and tourism purposes.")
        assert score == 1.0

    def test_no_match(self) -> None:
        engine = ScoreEngine()
        q = _make_question(["visit", "business", "tourism"])
        score = engine.score_response(q, "The weather is nice today.")
        assert score == 0.0

    def test_partial_match(self) -> None:
        engine = ScoreEngine()
        q = _make_question(["visit", "business", "tourism", "study"])
        score = engine.score_response(q, "I am here to visit for business.")
        assert score == 0.5

    def test_empty_keywords(self) -> None:
        engine = ScoreEngine()
        q = _make_question([])
        score = engine.score_response(q, "Any response.")
        assert score == 1.0

    def test_case_insensitive(self) -> None:
        engine = ScoreEngine()
        q = _make_question(["Visit", "Business"])
        score = engine.score_response(q, "visit and business")
        assert score == 1.0


class TestConfidenceCalculation:
    def test_confidence_calculation(self) -> None:
        engine = ScoreEngine()
        confidence = engine.calculate_confidence([0.8, 0.9, 0.7])
        assert abs(confidence - 0.8) < 1e-9

    def test_empty_scores(self) -> None:
        engine = ScoreEngine()
        assert engine.calculate_confidence([]) == 0.0

    def test_single_score(self) -> None:
        engine = ScoreEngine()
        assert engine.calculate_confidence([0.5]) == 0.5


class TestMeetsThreshold:
    def test_meets_threshold(self) -> None:
        engine = ScoreEngine()
        config = SimulationConfig(confidence_threshold=0.7)
        session = InterviewSession(config=config)
        session.responses = [
            ResponseRecord(question_id="q1", question_text="Q?", user_response="A", score=0.9, confidence=0.9),
            ResponseRecord(question_id="q2", question_text="Q?", user_response="A", score=0.8, confidence=0.85),
        ]
        assert engine.meets_threshold(session) is True

    def test_below_threshold(self) -> None:
        engine = ScoreEngine()
        config = SimulationConfig(confidence_threshold=0.7)
        session = InterviewSession(config=config)
        session.responses = [
            ResponseRecord(question_id="q1", question_text="Q?", user_response="A", score=0.3, confidence=0.3),
            ResponseRecord(question_id="q2", question_text="Q?", user_response="A", score=0.2, confidence=0.25),
        ]
        assert engine.meets_threshold(session) is False


class TestConfidenceInterval:
    def test_confidence_interval(self) -> None:
        engine = ScoreEngine()
        lower, upper = engine.get_confidence_interval([0.8, 0.9, 0.7, 0.85, 0.75])
        assert lower < upper
        assert lower >= 0.0
        assert upper <= 1.0

    def test_single_score_interval(self) -> None:
        engine = ScoreEngine()
        lower, upper = engine.get_confidence_interval([0.5])
        assert lower == 0.5
        assert upper == 0.5

    def test_empty_interval(self) -> None:
        engine = ScoreEngine()
        assert engine.get_confidence_interval([]) == (0.0, 0.0)
