"""Profile management for loading, saving, and updating user profiles."""

import json
import os
from dataclasses import asdict
from datetime import datetime, timezone

from models import CategoryTrend, SessionRecord, UserProfile


class ProfileManager:
    """Manages user profile persistence and updates."""

    def __init__(self, storage_dir: str) -> None:
        """Initialize with directory where profiles are stored."""
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

    def _profile_path(self, user_id: str) -> str:
        """Get the file path for a user's profile."""
        return os.path.join(self.storage_dir, f"{user_id}_profile.json")

    def load_profile(self, user_id: str) -> UserProfile:
        """Load an existing profile or create a new one."""
        path = self._profile_path(user_id)
        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)
            return self._deserialize_profile(data)
        return UserProfile(
            user_id=user_id,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    def save_profile(self, profile: UserProfile) -> None:
        """Save profile to JSON file."""
        path = self._profile_path(profile.user_id)
        with open(path, "w") as f:
            json.dump(asdict(profile), f, indent=2)

    def add_session(self, profile: UserProfile, session_data: dict) -> UserProfile:
        """Add session results to a user profile."""
        record = SessionRecord(
            session_id=session_data.get("session_id", f"session_{len(profile.sessions) + 1}"),
            timestamp=session_data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            domain=session_data.get("domain", "general"),
            overall_score=float(session_data.get("overall_score", 0.0)),
            category_scores={k: float(v) for k, v in session_data.get("category_scores", {}).items()},
            difficulty_avg=float(session_data.get("difficulty_avg", 3.0)),
            questions_count=int(session_data.get("questions_count", 0)),
            duration_seconds=session_data.get("duration_seconds"),
        )
        profile.sessions.append(record)
        profile.total_sessions = len(profile.sessions)
        profile.latest_score = record.overall_score
        if record.overall_score > profile.best_score:
            profile.best_score = record.overall_score
        return self.update_trends(profile)

    def update_trends(self, profile: UserProfile) -> UserProfile:
        """Recalculate category trends from session history."""
        category_data: dict[str, CategoryTrend] = {}

        for session in profile.sessions:
            for category, score in session.category_scores.items():
                if category not in category_data:
                    category_data[category] = CategoryTrend(category=category)
                category_data[category].scores.append(score)
                category_data[category].timestamps.append(session.timestamp)

        for trend in category_data.values():
            if len(trend.scores) >= 2:
                trend.improvement_rate = self._compute_improvement_rate(trend.scores)
                trend.trend_direction = self._direction_from_rate(trend.improvement_rate)
            else:
                trend.trend_direction = "stable"
                trend.improvement_rate = 0.0

        profile.category_trends = category_data

        # Update overall trend from session overall scores
        overall_scores = [s.overall_score for s in profile.sessions]
        if len(overall_scores) >= 2:
            rate = self._compute_improvement_rate(overall_scores)
            profile.overall_trend = self._direction_from_rate(rate)
        else:
            profile.overall_trend = "stable"

        return profile

    @staticmethod
    def _compute_improvement_rate(scores: list[float]) -> float:
        """Compute simple improvement rate from a list of scores."""
        if len(scores) < 2:
            return 0.0
        # Average change per step normalized by score range
        changes = [scores[i + 1] - scores[i] for i in range(len(scores) - 1)]
        avg_change = sum(changes) / len(changes)
        return max(-1.0, min(1.0, avg_change))

    @staticmethod
    def _direction_from_rate(rate: float) -> str:
        """Convert improvement rate to direction label."""
        from config import DECLINE_RATE_THRESHOLD, IMPROVEMENT_RATE_THRESHOLD

        if rate > IMPROVEMENT_RATE_THRESHOLD:
            return "improving"
        elif rate < DECLINE_RATE_THRESHOLD:
            return "declining"
        return "stable"

    @staticmethod
    def _deserialize_profile(data: dict) -> UserProfile:
        """Deserialize a profile from a JSON-compatible dict."""
        sessions = [SessionRecord(**s) for s in data.get("sessions", [])]
        category_trends = {k: CategoryTrend(**v) for k, v in data.get("category_trends", {}).items()}
        return UserProfile(
            user_id=data["user_id"],
            created_at=data["created_at"],
            sessions=sessions,
            category_trends=category_trends,
            overall_trend=data.get("overall_trend", "stable"),
            total_sessions=data.get("total_sessions", 0),
            best_score=data.get("best_score", 0.0),
            latest_score=data.get("latest_score", 0.0),
        )
