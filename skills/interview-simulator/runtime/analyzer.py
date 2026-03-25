"""Post-interview analysis engine."""

from __future__ import annotations

from models import InterviewSession
from scoring import ScoreEngine


class InterviewAnalyzer:
    """Generates comprehensive analysis from a completed interview session."""

    def __init__(self) -> None:
        self.score_engine = ScoreEngine()

    def analyze(self, session: InterviewSession) -> dict:
        """Generate a full analysis of the interview session.

        Returns a dict with:
        - overall_score
        - confidence_interval
        - category_scores
        - weak_areas
        - strong_areas
        - recommendations
        - difficulty_progression
        """
        if not session.responses:
            return {
                "session_id": session.session_id,
                "domain": session.domain,
                "overall_score": 0.0,
                "confidence_interval": (0.0, 0.0),
                "category_scores": {},
                "weak_areas": [],
                "strong_areas": [],
                "recommendations": ["No responses recorded. Complete the interview to receive analysis."],
                "difficulty_progression": [],
                "total_questions": 0,
            }

        scores = [r.score for r in session.responses]
        overall_score = sum(scores) / len(scores)
        confidence_interval = self.score_engine.get_confidence_interval(scores)

        category_scores = self._compute_category_scores(session)
        weak_areas = self._identify_weak_areas(category_scores)
        strong_areas = self._identify_strong_areas(category_scores)
        recommendations = self._generate_recommendations(weak_areas, overall_score, session)
        difficulty_progression = [r.difficulty for r in session.responses]

        return {
            "session_id": session.session_id,
            "domain": session.domain,
            "overall_score": round(overall_score, 4),
            "confidence_interval": (round(confidence_interval[0], 4), round(confidence_interval[1], 4)),
            "category_scores": {k: round(v, 4) for k, v in category_scores.items()},
            "weak_areas": weak_areas,
            "strong_areas": strong_areas,
            "recommendations": recommendations,
            "difficulty_progression": difficulty_progression,
            "total_questions": len(session.responses),
        }

    def _compute_category_scores(self, session: InterviewSession) -> dict[str, float]:
        """Compute average score per category.

        Uses question_id prefix before the first underscore as category if no explicit
        category is tracked in ResponseRecord. We look up category from question_text
        patterns or fall back to 'general'.
        """
        # Group scores by category - we need to infer category from available data
        # ResponseRecord doesn't store category, so we use a mapping approach
        category_totals: dict[str, list[float]] = {}
        for response in session.responses:
            # Use question_id prefix as a simple category proxy
            category = "general"
            parts = response.question_id.split("_")
            if len(parts) > 1:
                category = parts[0]
            category_totals.setdefault(category, []).append(response.score)

        return {cat: sum(s) / len(s) for cat, s in category_totals.items()}

    def _identify_weak_areas(self, category_scores: dict[str, float], threshold: float = 0.6) -> list[str]:
        """Identify categories with scores below the threshold."""
        return [cat for cat, score in category_scores.items() if score < threshold]

    def _identify_strong_areas(self, category_scores: dict[str, float], threshold: float = 0.8) -> list[str]:
        """Identify categories with scores above the threshold."""
        return [cat for cat, score in category_scores.items() if score >= threshold]

    def _generate_recommendations(
        self,
        weak_areas: list[str],
        overall_score: float,
        session: InterviewSession,
    ) -> list[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations: list[str] = []

        if overall_score < session.config.confidence_threshold:
            recommendations.append(
                f"Overall score ({overall_score:.0%}) is below the confidence threshold "
                f"({session.config.confidence_threshold:.0%}). Additional preparation is recommended."
            )

        for area in weak_areas:
            recommendations.append(f"Review and strengthen knowledge in the '{area}' category.")

        if not weak_areas and overall_score >= session.config.confidence_threshold:
            recommendations.append("Performance meets the confidence threshold. Continue with current preparation.")

        return recommendations
