"""Tests for TrendAnalyzer."""

from models import CategoryTrend, SessionRecord, UserProfile
from trend_analyzer import TrendAnalyzer


def _make_profile(category_data: dict[str, list[float]], sessions: list[SessionRecord] | None = None) -> UserProfile:
    """Helper to create a profile with category trends."""
    trends: dict[str, CategoryTrend] = {}
    for cat, scores in category_data.items():
        rate = TrendAnalyzer.calculate_improvement_rate(scores)
        direction = TrendAnalyzer.calculate_trend(scores)
        trends[cat] = CategoryTrend(
            category=cat,
            scores=scores,
            timestamps=[f"2026-01-{i + 1:02d}T00:00:00Z" for i in range(len(scores))],
            trend_direction=direction,
            improvement_rate=rate,
        )
    return UserProfile(
        user_id="test_user",
        created_at="2026-01-01T00:00:00Z",
        category_trends=trends,
        sessions=sessions or [],
        total_sessions=len(sessions) if sessions else 0,
    )


def test_improving_trend() -> None:
    """Ascending scores should yield 'improving'."""
    scores = [0.4, 0.5, 0.6, 0.7, 0.8]
    assert TrendAnalyzer.calculate_trend(scores) == "improving"


def test_declining_trend() -> None:
    """Descending scores should yield 'declining'."""
    scores = [0.8, 0.7, 0.6, 0.5, 0.4]
    assert TrendAnalyzer.calculate_trend(scores) == "declining"


def test_stable_trend() -> None:
    """Flat scores should yield 'stable'."""
    scores = [0.6, 0.6, 0.6, 0.6]
    assert TrendAnalyzer.calculate_trend(scores) == "stable"


def test_weak_areas() -> None:
    """Categories with latest score below threshold are identified as weak."""
    profile = _make_profile(
        {
            "technical": [0.3, 0.4, 0.5],
            "behavioral": [0.7, 0.8, 0.85],
            "communication": [0.4, 0.35, 0.3],
        }
    )
    weak = TrendAnalyzer.identify_weak_areas(profile, threshold=0.6)
    assert "technical" in weak
    assert "communication" in weak
    assert "behavioral" not in weak


def test_progress_report_structure() -> None:
    """Progress report has all required fields."""
    sessions = [
        SessionRecord(
            session_id=f"s{i}",
            timestamp=f"2026-01-{i + 1:02d}T00:00:00Z",
            domain="general",
            overall_score=0.5 + i * 0.1,
            category_scores={"technical": 0.4 + i * 0.1, "behavioral": 0.6 + i * 0.05},
            difficulty_avg=3.0,
            questions_count=5,
        )
        for i in range(3)
    ]
    profile = _make_profile(
        {"technical": [0.4, 0.5, 0.6], "behavioral": [0.6, 0.65, 0.7]},
        sessions=sessions,
    )
    report = TrendAnalyzer.generate_progress_report(profile, last_n_sessions=3)
    assert report.user_id == "test_user"
    assert report.sessions_completed == 3
    assert isinstance(report.score_change, float)
    assert isinstance(report.improving_categories, list)
    assert isinstance(report.declining_categories, list)
    assert isinstance(report.recommendations, list)
    assert report.period != "no sessions"
