"""Trend analysis for user performance data."""

from config import (
    DECLINE_RATE_THRESHOLD,
    DEFAULT_WEAK_THRESHOLD,
    IMPROVEMENT_RATE_THRESHOLD,
    MIN_SESSIONS_FOR_TREND,
)
from models import CategoryTrend, ProgressReport, TrainingRecommendation, UserProfile
from recommender import Recommender


class TrendAnalyzer:
    """Analyzes performance trends and generates progress reports."""

    @staticmethod
    def calculate_trend(scores: list[float]) -> str:
        """Return 'improving', 'declining', or 'stable' based on score progression."""
        if len(scores) < MIN_SESSIONS_FOR_TREND:
            return "stable"
        rate = TrendAnalyzer.calculate_improvement_rate(scores)
        if rate > IMPROVEMENT_RATE_THRESHOLD:
            return "improving"
        elif rate < DECLINE_RATE_THRESHOLD:
            return "declining"
        return "stable"

    @staticmethod
    def calculate_improvement_rate(scores: list[float]) -> float:
        """Calculate rate of improvement from -1 to 1."""
        if len(scores) < 2:
            return 0.0
        changes = [scores[i + 1] - scores[i] for i in range(len(scores) - 1)]
        avg_change = sum(changes) / len(changes)
        return max(-1.0, min(1.0, avg_change))

    @staticmethod
    def identify_weak_areas(profile: UserProfile, threshold: float = DEFAULT_WEAK_THRESHOLD) -> list[str]:
        """Identify categories where latest scores are below the threshold."""
        weak: list[str] = []
        for category, trend in profile.category_trends.items():
            if trend.scores and trend.scores[-1] < threshold:
                weak.append(category)
        return weak

    @staticmethod
    def identify_strong_areas(profile: UserProfile, threshold: float = 0.8) -> list[str]:
        """Identify categories where latest scores are above the threshold."""
        strong: list[str] = []
        for category, trend in profile.category_trends.items():
            if trend.scores and trend.scores[-1] >= threshold:
                strong.append(category)
        return strong

    @staticmethod
    def generate_progress_report(profile: UserProfile, last_n_sessions: int = 5) -> ProgressReport:
        """Generate a progress report for the last N sessions."""
        recent = profile.sessions[-last_n_sessions:] if profile.sessions else []

        if len(recent) >= 2:
            score_change = recent[-1].overall_score - recent[0].overall_score
        elif len(recent) == 1:
            score_change = 0.0
        else:
            score_change = 0.0

        # Determine period description
        period = f"{recent[0].timestamp} to {recent[-1].timestamp}" if recent else "no sessions"

        # Collect per-category trends from recent sessions
        cat_scores: dict[str, list[float]] = {}
        for session in recent:
            for cat, score in session.category_scores.items():
                cat_scores.setdefault(cat, []).append(score)

        improving: list[str] = []
        declining: list[str] = []
        temp_trends: dict[str, CategoryTrend] = {}
        for cat, scores in cat_scores.items():
            direction = TrendAnalyzer.calculate_trend(scores)
            rate = TrendAnalyzer.calculate_improvement_rate(scores)
            temp_trends[cat] = CategoryTrend(
                category=cat,
                scores=scores,
                timestamps=[],
                trend_direction=direction,
                improvement_rate=rate,
            )
            if direction == "improving":
                improving.append(cat)
            elif direction == "declining":
                declining.append(cat)

        # Build a temporary profile-like object for recommendations
        temp_profile = UserProfile(
            user_id=profile.user_id,
            created_at=profile.created_at,
            sessions=list(recent),
            category_trends=temp_trends,
            overall_trend=profile.overall_trend,
            total_sessions=len(recent),
            best_score=profile.best_score,
            latest_score=profile.latest_score,
        )
        recommendations: list[TrainingRecommendation] = Recommender.generate_recommendations(temp_profile)

        return ProgressReport(
            user_id=profile.user_id,
            period=period,
            sessions_completed=len(recent),
            score_change=round(score_change, 4),
            improving_categories=improving,
            declining_categories=declining,
            recommendations=recommendations,
        )
