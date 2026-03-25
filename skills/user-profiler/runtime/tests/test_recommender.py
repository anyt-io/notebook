"""Tests for Recommender."""

from models import CategoryTrend, UserProfile
from recommender import Recommender


def _make_profile_with_trends(trends_data: dict[str, tuple[list[float], str, float]]) -> UserProfile:
    """Helper to create a profile with specific trend configurations.

    trends_data: {category: (scores, direction, improvement_rate)}
    """
    trends: dict[str, CategoryTrend] = {}
    for cat, (scores, direction, rate) in trends_data.items():
        trends[cat] = CategoryTrend(
            category=cat,
            scores=scores,
            timestamps=[f"2026-01-{i + 1:02d}T00:00:00Z" for i in range(len(scores))],
            trend_direction=direction,
            improvement_rate=rate,
        )

    # Create minimal session list so recommendations are generated
    from models import SessionRecord

    sessions = [
        SessionRecord(
            session_id="s1",
            timestamp="2026-01-01T00:00:00Z",
            domain="general",
            overall_score=0.5,
            category_scores={cat: scores[-1] for cat, (scores, _, _) in trends_data.items()},
            difficulty_avg=3.0,
            questions_count=5,
        )
    ]

    return UserProfile(
        user_id="test_user",
        created_at="2026-01-01T00:00:00Z",
        category_trends=trends,
        sessions=sessions,
        total_sessions=1,
    )


def test_high_priority_for_declining() -> None:
    """Declining category should get high priority recommendation."""
    profile = _make_profile_with_trends(
        {
            "technical": ([0.7, 0.6, 0.5], "declining", -0.1),
        }
    )
    recs = Recommender.generate_recommendations(profile)
    assert len(recs) == 1
    assert recs[0].priority == "high"
    assert recs[0].category == "technical"


def test_medium_priority_for_weak_stable() -> None:
    """Weak but stable category should get medium priority."""
    profile = _make_profile_with_trends(
        {
            "communication": ([0.4, 0.4, 0.4], "stable", 0.0),
        }
    )
    recs = Recommender.generate_recommendations(profile)
    assert len(recs) == 1
    assert recs[0].priority == "medium"


def test_low_priority_for_improving() -> None:
    """Improving category should get low priority."""
    profile = _make_profile_with_trends(
        {
            "behavioral": ([0.5, 0.6, 0.7], "improving", 0.1),
        }
    )
    recs = Recommender.generate_recommendations(profile)
    assert len(recs) == 1
    assert recs[0].priority == "low"


def test_difficulty_suggestion() -> None:
    """Suggested difficulty should scale with current score."""
    profile = _make_profile_with_trends(
        {
            "technical": ([0.8, 0.85, 0.9], "improving", 0.05),
        }
    )
    recs = Recommender.generate_recommendations(profile)
    assert len(recs) == 1
    # Score 0.9 -> difficulty should be 4 (int(0.9 * 4) + 1 = 4)
    assert recs[0].suggested_difficulty == 4


def test_empty_profile() -> None:
    """No recommendations for a user with no sessions."""
    profile = UserProfile(
        user_id="empty_user",
        created_at="2026-01-01T00:00:00Z",
    )
    recs = Recommender.generate_recommendations(profile)
    assert recs == []
