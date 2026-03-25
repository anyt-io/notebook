"""Tests for the flow engine."""

from __future__ import annotations

from flow_engine import FlowEngine
from models import InterviewSession, Question, ResponseRecord, SimulationConfig


def _make_questions() -> list[Question]:
    return [
        Question(id="q1", text="Easy question?", category="basics", difficulty=1, expected_answer_keywords=["yes"]),
        Question(
            id="q2",
            text="Medium question?",
            category="basics",
            difficulty=2,
            expected_answer_keywords=["maybe"],
            follow_ups=["q4"],
        ),
        Question(
            id="q3", text="Hard question?", category="advanced", difficulty=3, expected_answer_keywords=["complex"]
        ),
        Question(
            id="q4",
            text="Follow-up question?",
            category="basics",
            difficulty=2,
            expected_answer_keywords=["detail"],
        ),
        Question(
            id="q5", text="Very hard question?", category="advanced", difficulty=5, expected_answer_keywords=["expert"]
        ),
    ]


class TestSelectFirstQuestion:
    def test_select_first_question(self) -> None:
        questions = _make_questions()
        config = SimulationConfig(adaptive_difficulty=True)
        engine = FlowEngine(questions, config)
        session = InterviewSession(config=config)

        first = engine.select_next_question(session)
        assert first is not None
        assert first.difficulty == 1

    def test_returns_none_when_complete(self) -> None:
        questions = _make_questions()
        config = SimulationConfig(max_questions=1)
        engine = FlowEngine(questions, config)
        session = InterviewSession(config=config)
        session.responses = [
            ResponseRecord(question_id="q1", question_text="Q?", user_response="yes", score=1.0, confidence=1.0),
        ]
        assert engine.select_next_question(session) is None


class TestAdaptiveDifficulty:
    def test_adaptive_difficulty_increase(self) -> None:
        questions = _make_questions()
        config = SimulationConfig(adaptive_difficulty=True)
        engine = FlowEngine(questions, config)
        session = InterviewSession(config=config)
        # High scores should increase difficulty
        session.responses = [
            ResponseRecord(
                question_id="q1", question_text="Q?", user_response="yes", score=0.9, confidence=0.9, difficulty=1
            ),
            ResponseRecord(
                question_id="q2", question_text="Q?", user_response="maybe", score=0.85, confidence=0.87, difficulty=2
            ),
            ResponseRecord(
                question_id="q4", question_text="Q?", user_response="detail", score=0.95, confidence=0.9, difficulty=2
            ),
        ]
        new_difficulty = engine.adjust_difficulty(session)
        assert new_difficulty > 1

    def test_adaptive_difficulty_decrease(self) -> None:
        questions = _make_questions()
        config = SimulationConfig(adaptive_difficulty=True)
        engine = FlowEngine(questions, config)
        engine._current_difficulty = 3
        session = InterviewSession(config=config)
        # Low scores should decrease difficulty
        session.responses = [
            ResponseRecord(
                question_id="q3", question_text="Q?", user_response="wrong", score=0.1, confidence=0.1, difficulty=3
            ),
            ResponseRecord(
                question_id="q5", question_text="Q?", user_response="bad", score=0.2, confidence=0.15, difficulty=5
            ),
            ResponseRecord(
                question_id="q1", question_text="Q?", user_response="no", score=0.3, confidence=0.2, difficulty=1
            ),
        ]
        new_difficulty = engine.adjust_difficulty(session)
        assert new_difficulty < 3


class TestIsComplete:
    def test_is_complete(self) -> None:
        questions = _make_questions()
        config = SimulationConfig(max_questions=2)
        engine = FlowEngine(questions, config)
        session = InterviewSession(config=config)
        session.responses = [
            ResponseRecord(question_id="q1", question_text="Q?", user_response="A", score=0.8, confidence=0.8),
            ResponseRecord(question_id="q2", question_text="Q?", user_response="A", score=0.7, confidence=0.75),
        ]
        assert engine.is_complete(session) is True

    def test_not_complete(self) -> None:
        questions = _make_questions()
        config = SimulationConfig(max_questions=20)
        engine = FlowEngine(questions, config)
        session = InterviewSession(config=config)
        session.responses = [
            ResponseRecord(question_id="q1", question_text="Q?", user_response="A", score=0.8, confidence=0.8),
        ]
        assert engine.is_complete(session) is False


class TestFollowUpSelection:
    def test_follow_up_selection(self) -> None:
        questions = _make_questions()
        config = SimulationConfig(adaptive_difficulty=False)
        engine = FlowEngine(questions, config)
        session = InterviewSession(config=config)
        # After answering q2 (which has follow_ups=["q4"]), q4 should be next
        session.responses = [
            ResponseRecord(
                question_id="q1", question_text="Q?", user_response="yes", score=1.0, confidence=1.0, difficulty=1
            ),
            ResponseRecord(
                question_id="q2", question_text="Q?", user_response="maybe", score=0.8, confidence=0.9, difficulty=2
            ),
        ]
        next_q = engine.select_next_question(session)
        assert next_q is not None
        assert next_q.id == "q4"
