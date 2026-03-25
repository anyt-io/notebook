"""Interview flow management engine."""

from __future__ import annotations

from config import (
    DEFAULT_DIFFICULTY,
    DIFFICULTY_DECREASE_THRESHOLD,
    DIFFICULTY_INCREASE_THRESHOLD,
    MAX_DIFFICULTY,
    MIN_DIFFICULTY,
    RECENT_WINDOW_SIZE,
)
from models import InterviewSession, Question, SimulationConfig


class FlowEngine:
    """Manages interview question flow with adaptive difficulty and branching."""

    def __init__(self, questions: list[Question], config: SimulationConfig) -> None:
        self.questions = questions
        self.config = config
        self._questions_by_id: dict[str, Question] = {q.id: q for q in questions}
        self._current_difficulty = DEFAULT_DIFFICULTY

    def get_question_by_id(self, question_id: str) -> Question | None:
        """Look up a question by its ID."""
        return self._questions_by_id.get(question_id)

    def select_next_question(self, session: InterviewSession) -> Question | None:
        """Select the next question based on adaptive difficulty and follow-ups.

        Priority:
        1. Follow-up questions from the last answered question
        2. Unanswered questions at the current difficulty level
        3. Unanswered questions at the nearest difficulty level
        """
        if self.is_complete(session):
            return None

        answered_ids = {r.question_id for r in session.responses}

        # Check follow-ups from the last response
        if session.responses:
            last_response = session.responses[-1]
            last_question = self.get_question_by_id(last_response.question_id)
            if last_question:
                for follow_up_id in last_question.follow_ups:
                    if follow_up_id not in answered_ids:
                        follow_up = self.get_question_by_id(follow_up_id)
                        if follow_up:
                            return follow_up

        # Adjust difficulty if adaptive mode is enabled
        if self.config.adaptive_difficulty and session.responses:
            self._current_difficulty = self.adjust_difficulty(session)

        # Find unanswered questions at current difficulty
        unanswered = [q for q in self.questions if q.id not in answered_ids]
        if not unanswered:
            return None

        # Prefer questions at current difficulty
        at_difficulty = [q for q in unanswered if q.difficulty == self._current_difficulty]
        if at_difficulty:
            return at_difficulty[0]

        # Find nearest difficulty
        unanswered.sort(key=lambda q: abs(q.difficulty - self._current_difficulty))
        return unanswered[0]

    def adjust_difficulty(self, session: InterviewSession) -> int:
        """Adjust difficulty based on recent performance scores."""
        recent = session.responses[-RECENT_WINDOW_SIZE:]
        if not recent:
            return self._current_difficulty

        avg_score = sum(r.score for r in recent) / len(recent)

        if avg_score >= DIFFICULTY_INCREASE_THRESHOLD:
            return min(self._current_difficulty + 1, MAX_DIFFICULTY)
        elif avg_score <= DIFFICULTY_DECREASE_THRESHOLD:
            return max(self._current_difficulty - 1, MIN_DIFFICULTY)
        return self._current_difficulty

    def is_complete(self, session: InterviewSession) -> bool:
        """Check if the interview is complete.

        Complete when max questions reached or all questions answered.
        """
        if len(session.responses) >= session.config.max_questions:
            return True

        answered_ids = {r.question_id for r in session.responses}
        return len(answered_ids) >= len(self.questions)
