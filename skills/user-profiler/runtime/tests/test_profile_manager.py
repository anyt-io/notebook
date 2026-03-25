"""Tests for ProfileManager."""

import json
from pathlib import Path

from profile_manager import ProfileManager


def test_create_new_profile() -> None:
    """New user gets an empty profile."""
    manager = ProfileManager("/tmp/test_profiles_new")
    profile = manager.load_profile("new_user")
    assert profile.user_id == "new_user"
    assert profile.total_sessions == 0
    assert profile.sessions == []
    assert profile.category_trends == {}
    assert profile.best_score == 0.0
    assert profile.latest_score == 0.0


def test_add_session() -> None:
    """Session is added correctly to the profile."""
    manager = ProfileManager("/tmp/test_profiles_add")
    profile = manager.load_profile("test_user")
    session_data = {
        "session_id": "s1",
        "timestamp": "2026-01-01T00:00:00Z",
        "domain": "software_engineering",
        "overall_score": 0.75,
        "category_scores": {"technical": 0.8, "behavioral": 0.7},
        "difficulty_avg": 3.0,
        "questions_count": 10,
    }
    profile = manager.add_session(profile, session_data)
    assert profile.total_sessions == 1
    assert profile.latest_score == 0.75
    assert profile.best_score == 0.75
    assert len(profile.sessions) == 1
    assert profile.sessions[0].session_id == "s1"
    assert profile.sessions[0].category_scores["technical"] == 0.8


def test_save_and_load(tmp_path: Path) -> None:
    """Profile round-trips through save and load."""
    manager = ProfileManager(str(tmp_path))
    profile = manager.load_profile("persist_user")
    session_data = {
        "session_id": "s1",
        "timestamp": "2026-01-01T00:00:00Z",
        "domain": "general",
        "overall_score": 0.65,
        "category_scores": {"communication": 0.6, "problem_solving": 0.7},
        "difficulty_avg": 2.5,
        "questions_count": 5,
    }
    profile = manager.add_session(profile, session_data)
    manager.save_profile(profile)

    # Verify file exists
    profile_path = tmp_path / "persist_user_profile.json"
    assert profile_path.exists()
    with open(profile_path) as f:
        raw = json.load(f)
    assert raw["user_id"] == "persist_user"

    # Reload
    loaded = manager.load_profile("persist_user")
    assert loaded.user_id == "persist_user"
    assert loaded.total_sessions == 1
    assert loaded.latest_score == 0.65
    assert len(loaded.sessions) == 1
    assert loaded.sessions[0].category_scores["communication"] == 0.6


def test_update_trends() -> None:
    """Trends are recalculated after adding multiple sessions."""
    manager = ProfileManager("/tmp/test_profiles_trends")
    profile = manager.load_profile("trend_user")

    sessions = [
        {
            "session_id": "s1",
            "timestamp": "2026-01-01T00:00:00Z",
            "domain": "general",
            "overall_score": 0.5,
            "category_scores": {"technical": 0.4, "behavioral": 0.6},
            "difficulty_avg": 2.0,
            "questions_count": 5,
        },
        {
            "session_id": "s2",
            "timestamp": "2026-01-02T00:00:00Z",
            "domain": "general",
            "overall_score": 0.7,
            "category_scores": {"technical": 0.6, "behavioral": 0.8},
            "difficulty_avg": 3.0,
            "questions_count": 5,
        },
        {
            "session_id": "s3",
            "timestamp": "2026-01-03T00:00:00Z",
            "domain": "general",
            "overall_score": 0.85,
            "category_scores": {"technical": 0.8, "behavioral": 0.9},
            "difficulty_avg": 3.5,
            "questions_count": 5,
        },
    ]

    for s in sessions:
        profile = manager.add_session(profile, s)

    assert profile.total_sessions == 3
    assert "technical" in profile.category_trends
    assert "behavioral" in profile.category_trends
    # Both categories should be improving
    assert profile.category_trends["technical"].trend_direction == "improving"
    assert profile.category_trends["behavioral"].trend_direction == "improving"
    assert profile.overall_trend == "improving"
