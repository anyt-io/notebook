"""Training recommendation engine."""

from config import (
    CATEGORY_FOCUS_AREAS,
    DEFAULT_FOCUS_AREAS,
    DEFAULT_WEAK_THRESHOLD,
    MAX_DIFFICULTY,
    MIN_DIFFICULTY,
    PRIORITY_HIGH,
    PRIORITY_LOW,
    PRIORITY_MEDIUM,
)
from models import TrainingRecommendation, UserProfile


class Recommender:
    """Generates personalized training recommendations based on user profile."""

    @staticmethod
    def generate_recommendations(profile: UserProfile) -> list[TrainingRecommendation]:
        """Generate personalized recommendations based on profile trends."""
        if not profile.sessions:
            return []

        recommendations: list[TrainingRecommendation] = []

        for category, trend in profile.category_trends.items():
            if not trend.scores:
                continue

            latest_score = trend.scores[-1]
            direction = trend.trend_direction

            # Determine priority
            priority = Recommender._determine_priority(direction, latest_score)

            # Determine suggested difficulty
            suggested_difficulty = Recommender._suggest_difficulty(latest_score)

            # Get focus areas
            focus_areas = Recommender._get_focus_areas(category)

            # Build description
            description = Recommender._build_description(category, direction, latest_score)

            recommendations.append(
                TrainingRecommendation(
                    category=category,
                    priority=priority,
                    description=description,
                    suggested_difficulty=suggested_difficulty,
                    focus_areas=focus_areas,
                )
            )

        # Sort by priority: high first, then medium, then low
        priority_order = {PRIORITY_HIGH: 0, PRIORITY_MEDIUM: 1, PRIORITY_LOW: 2}
        recommendations.sort(key=lambda r: priority_order.get(r.priority, 3))

        return recommendations

    @staticmethod
    def _determine_priority(direction: str, latest_score: float) -> str:
        """Determine recommendation priority based on trend and score."""
        if direction == "declining":
            return PRIORITY_HIGH
        elif latest_score < DEFAULT_WEAK_THRESHOLD and direction == "stable":
            return PRIORITY_MEDIUM
        elif direction == "improving":
            return PRIORITY_LOW
        # Weak but not declining/improving
        if latest_score < DEFAULT_WEAK_THRESHOLD:
            return PRIORITY_MEDIUM
        return PRIORITY_LOW

    @staticmethod
    def _suggest_difficulty(latest_score: float) -> int:
        """Suggest difficulty level based on current performance."""
        # Map score (0-1) to difficulty (1-5)
        difficulty = int(latest_score * (MAX_DIFFICULTY - MIN_DIFFICULTY)) + MIN_DIFFICULTY
        return max(MIN_DIFFICULTY, min(MAX_DIFFICULTY, difficulty))

    @staticmethod
    def _get_focus_areas(category: str) -> list[str]:
        """Get focus areas for a category."""
        return CATEGORY_FOCUS_AREAS.get(category, DEFAULT_FOCUS_AREAS)

    @staticmethod
    def _build_description(category: str, direction: str, latest_score: float) -> str:
        """Build a human-readable recommendation description."""
        score_pct = f"{latest_score * 100:.0f}%"
        if direction == "declining":
            return f"Performance in '{category}' is declining (current: {score_pct}). Prioritize focused practice."
        elif direction == "stable" and latest_score < DEFAULT_WEAK_THRESHOLD:
            return f"Performance in '{category}' is stagnant at {score_pct}. Try varied practice approaches."
        elif direction == "improving":
            return f"Good progress in '{category}' ({score_pct}). Continue current approach and increase difficulty."
        return f"Performance in '{category}' is at {score_pct}. Maintain regular practice."
