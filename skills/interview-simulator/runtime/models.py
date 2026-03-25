"""Data models for the interview simulator."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from config import DEFAULT_ADAPTIVE_DIFFICULTY, DEFAULT_CONFIDENCE_THRESHOLD, DEFAULT_MAX_QUESTIONS


@dataclass
class Question:
    """A single interview question from the question bank."""

    id: str
    text: str
    category: str
    difficulty: int
    expected_answer_keywords: list[str]
    source_section: str = ""
    follow_ups: list[str] = field(default_factory=list)
    domain: str = ""


@dataclass
class SimulationConfig:
    """Configuration for an interview simulation session."""

    max_questions: int = DEFAULT_MAX_QUESTIONS
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD
    adaptive_difficulty: bool = DEFAULT_ADAPTIVE_DIFFICULTY
    time_limit_seconds: int | None = None
    domain: str = ""


@dataclass
class ResponseRecord:
    """Record of a single question-response pair."""

    question_id: str
    question_text: str
    user_response: str
    score: float
    confidence: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    difficulty: int = 1


@dataclass
class InterviewSession:
    """State of an entire interview session."""

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    domain: str = ""
    config: SimulationConfig = field(default_factory=SimulationConfig)
    responses: list[ResponseRecord] = field(default_factory=list)
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    end_time: str | None = None
    status: str = "in_progress"
