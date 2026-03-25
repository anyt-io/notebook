"""Main response evaluator combining all components."""

import uuid

from config import DEFAULT_CONFIG, EvaluationConfig
from hallucination_detector import HallucinationDetector
from models import CollidingAnswer, EvaluationReport, ResponseEvaluation
from ordinal_mapper import OrdinalMapper
from statistical_analyzer import StatisticalAnalyzer


class ResponseEvaluator:
    """Orchestrates hallucination detection, ordinal mapping, and statistical analysis."""

    def __init__(self, config: EvaluationConfig | None = None) -> None:
        self.config = config or DEFAULT_CONFIG
        self.hallucination_detector = HallucinationDetector(self.config)
        self.ordinal_mapper = OrdinalMapper(self.config)
        self.statistical_analyzer = StatisticalAnalyzer(self.config)

    def evaluate_response(
        self,
        response: str,
        question: dict,
        context: str = "",
    ) -> ResponseEvaluation:
        """Evaluate a single response against a question.

        Args:
            response: The user's response text.
            question: Dict with keys like 'question_id', 'text', 'expected_keywords', 'known_facts'.
            context: Optional context for grounding checks.

        Returns:
            A ResponseEvaluation with all scores populated.
        """
        question_id = question.get("question_id", str(uuid.uuid4()))
        question_text = question.get("text", "")
        expected_keywords = question.get("expected_keywords", [])
        known_facts = question.get("known_facts", [])

        # Hallucination detection
        hallucination_score = self.hallucination_detector.detect(
            response=response,
            question=question_text,
            expected_keywords=expected_keywords,
            context=context,
        )

        # Ordinal mapping
        ordinal_rank = self.ordinal_mapper.map_response(
            response=response,
            question_id=question_id,
            scale=self.config.ordinal_scale,
        )

        # Score components
        relevance_score = self._score_relevance(response, question_text, expected_keywords)
        coherence_score = self._score_coherence(response)
        completeness_score = self._score_completeness(response, expected_keywords)

        # Confidence based on response characteristics
        confidence = self._compute_confidence(response, expected_keywords, context)

        # Flags
        flags: list[str] = []
        if hallucination_score >= self.config.hallucination_flag_threshold:
            flags.append("high_hallucination")

        fabrications = self.hallucination_detector.flag_fabrications(response, known_facts)
        if fabrications:
            flags.append("fabricated_claims")

        if relevance_score < 0.3:
            flags.append("low_relevance")

        if len(response.split()) < 5:
            flags.append("very_short_response")

        return ResponseEvaluation(
            response_id=question_id,
            original_response=response,
            relevance_score=round(relevance_score, 4),
            coherence_score=round(coherence_score, 4),
            completeness_score=round(completeness_score, 4),
            hallucination_score=hallucination_score,
            ordinal_rank=ordinal_rank,
            confidence=round(confidence, 4),
            flags=flags,
        )

    def evaluate_session(
        self,
        transcript: list[dict],
        question_bank: dict,
    ) -> EvaluationReport:
        """Evaluate a full session transcript against a question bank.

        Args:
            transcript: List of dicts with 'response_id', 'question_id', 'response' keys.
            question_bank: Dict mapping question_id to question dicts.

        Returns:
            A full EvaluationReport.
        """
        session_id = str(uuid.uuid4())
        evaluations: list[ResponseEvaluation] = []

        for entry in transcript:
            question_id = entry.get("question_id", "")
            response_text = entry.get("response", "")
            context = entry.get("context", "")

            question = question_bank.get(question_id, {"question_id": question_id, "text": ""})

            evaluation = self.evaluate_response(
                response=response_text,
                question=question,
                context=context,
            )
            # Override response_id with transcript's ID if available
            if "response_id" in entry:
                evaluation.response_id = entry["response_id"]

            evaluations.append(evaluation)

        # Aggregate statistics
        aggregate_score = self.statistical_analyzer.calculate_aggregate_score(evaluations)

        all_scores = [(e.relevance_score + e.coherence_score + e.completeness_score) / 3 for e in evaluations]
        confidence_interval = self.statistical_analyzer.calculate_confidence_interval(
            all_scores, self.config.confidence_level
        )

        hallucination_count = sum(
            1 for e in evaluations if e.hallucination_score >= self.config.hallucination_flag_threshold
        )

        # Detect collisions
        responses_for_collision = [
            {
                "response_id": e.response_id,
                "response": e.original_response,
                "question_id": e.response_id,
            }
            for e in evaluations
        ]
        mappings = {e.response_id: e.ordinal_rank for e in evaluations}
        raw_collisions = self.ordinal_mapper.detect_collisions(mappings, responses_for_collision)
        colliding_answers = [
            CollidingAnswer(
                response_id_a=c["response_id_a"],
                response_id_b=c["response_id_b"],
                contradiction_description=c["contradiction_description"],
                severity=c["severity"],
            )
            for c in raw_collisions
        ]

        # Recommendations
        recommendations = self._generate_recommendations(evaluations, hallucination_count)

        return EvaluationReport(
            session_id=session_id,
            evaluations=evaluations,
            colliding_answers=colliding_answers,
            aggregate_score=aggregate_score,
            confidence_interval=confidence_interval,
            hallucination_count=hallucination_count,
            recommendations=recommendations,
        )

    def _score_relevance(self, response: str, question_text: str, expected_keywords: list[str]) -> float:
        """Score how relevant the response is to the question."""
        if not response.strip():
            return 0.0

        score = 0.0

        # Keyword overlap
        if expected_keywords:
            response_lower = response.lower()
            matches = sum(1 for kw in expected_keywords if kw.lower() in response_lower)
            score += 0.6 * (matches / len(expected_keywords))

        # Question-response word overlap
        if question_text:
            q_words = set(question_text.lower().split())
            r_words = set(response.lower().split())
            stop_words = {"the", "a", "an", "is", "are", "was", "were", "what", "how", "why", "do", "does", "your"}
            q_content = q_words - stop_words
            r_content = r_words - stop_words
            if q_content:
                overlap = len(q_content & r_content) / len(q_content)
                score += 0.4 * overlap

        return min(1.0, score)

    def _score_coherence(self, response: str) -> float:
        """Score the coherence of a response based on structural heuristics."""
        if not response.strip():
            return 0.0

        import re

        score = 0.3  # Base score for any non-empty response

        words = response.split()
        sentences = [s.strip() for s in re.split(r"[.!?]+", response) if s.strip()]

        # Sentence count bonus
        if len(sentences) >= 2:
            score += 0.2
        if len(sentences) >= 3:
            score += 0.1

        # Average sentence length (too short or too long = less coherent)
        if sentences:
            avg_words_per_sentence = len(words) / len(sentences)
            if 5 <= avg_words_per_sentence <= 25:
                score += 0.2
            elif 3 <= avg_words_per_sentence <= 35:
                score += 0.1

        # Vocabulary diversity
        if words:
            unique = set(w.lower() for w in words)
            diversity = len(unique) / len(words)
            score += diversity * 0.2

        return min(1.0, score)

    def _score_completeness(self, response: str, expected_keywords: list[str]) -> float:
        """Score the completeness of a response."""
        if not response.strip():
            return 0.0

        score = 0.0

        # Length-based completeness
        word_count = len(response.split())
        if word_count >= 5:
            score += 0.2
        if word_count >= 15:
            score += 0.2
        if word_count >= 30:
            score += 0.1

        # Keyword coverage
        if expected_keywords:
            response_lower = response.lower()
            covered = sum(1 for kw in expected_keywords if kw.lower() in response_lower)
            score += 0.5 * (covered / len(expected_keywords))

        return min(1.0, score)

    def _compute_confidence(self, response: str, expected_keywords: list[str], context: str) -> float:
        """Compute confidence in the evaluation based on available information."""
        confidence = 0.3  # Base confidence

        if expected_keywords:
            confidence += 0.3
        if context.strip():
            confidence += 0.2
        if len(response.split()) >= 10:
            confidence += 0.2

        return min(1.0, confidence)

    def _generate_recommendations(self, evaluations: list[ResponseEvaluation], hallucination_count: int) -> list[str]:
        """Generate recommendations based on evaluation results."""
        recommendations: list[str] = []

        if not evaluations:
            return recommendations

        weak_areas = self.statistical_analyzer.identify_weak_areas(evaluations, self.config.weak_area_threshold)

        if "relevance" in weak_areas:
            recommendations.append("Improve response relevance by addressing the question directly.")
        if "coherence" in weak_areas:
            recommendations.append("Improve response coherence with better structure and flow.")
        if "completeness" in weak_areas:
            recommendations.append("Provide more complete answers covering all key aspects.")
        if "hallucination" in weak_areas:
            recommendations.append("Reduce fabricated or unsupported claims in responses.")

        if hallucination_count > 0:
            recommendations.append(f"{hallucination_count} response(s) flagged for hallucination. Review for accuracy.")

        avg_confidence = sum(e.confidence for e in evaluations) / len(evaluations)
        if avg_confidence < 0.5:
            recommendations.append("Low evaluation confidence. Consider providing more context or expected keywords.")

        return recommendations[: self.config.max_recommendations]
