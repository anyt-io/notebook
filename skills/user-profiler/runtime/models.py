"""Data models for user-profiler skill."""

from dataclasses import dataclass, field


@dataclass
class SessionRecord:
    """A single interview session record."""

    session_id: str
    timestamp: str
    domain: str
    overall_score: float
    category_scores: dict[str, float]
    difficulty_avg: float
    questions_count: int
    duration_seconds: int | None = None


@dataclass
class CategoryTrend:
    """Performance trend for a specific category."""

    category: str
    scores: list[float] = field(default_factory=list)
    timestamps: list[str] = field(default_factory=list)
    trend_direction: str = "stable"  # "improving" | "declining" | "stable"
    improvement_rate: float = 0.0


@dataclass
class UserProfile:
    """Complete user profile with session history and trends."""

    user_id: str
    created_at: str
    sessions: list[SessionRecord] = field(default_factory=list)
    category_trends: dict[str, CategoryTrend] = field(default_factory=dict)
    overall_trend: str = "stable"
    total_sessions: int = 0
    best_score: float = 0.0
    latest_score: float = 0.0


@dataclass
class TrainingRecommendation:
    """A personalized training recommendation."""

    category: str
    priority: str  # "high" | "medium" | "low"
    description: str
    suggested_difficulty: int
    focus_areas: list[str] = field(default_factory=list)


@dataclass
class ProgressReport:
    """Progress report over a period of sessions."""

    user_id: str
    period: str
    sessions_completed: int
    score_change: float
    improving_categories: list[str] = field(default_factory=list)
    declining_categories: list[str] = field(default_factory=list)
    recommendations: list[TrainingRecommendation] = field(default_factory=list)
