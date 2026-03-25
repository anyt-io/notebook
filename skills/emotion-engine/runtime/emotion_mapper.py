"""Maps sentiment analysis results to avatar emotion states."""

from __future__ import annotations

from config import (
    BASELINE_EMOTION,
    BASELINE_INTENSITY,
    CONFIDENCE_LOW_THRESHOLD,
    EMOTION_TYPES,
    EVASION_THRESHOLD,
    NEGATIVE_THRESHOLD,
    POSITIVE_THRESHOLD,
    TRANSITION_DURATIONS,
)
from models import EmotionSequence, EmotionState, EmotionTransition
from sentiment import SentimentAnalyzer


class EmotionMapper:
    """Maps sentiment analysis to avatar emotion states."""

    def __init__(self) -> None:
        self.analyzer = SentimentAnalyzer()

    def map_to_emotion(self, sentiment: dict[str, object], context: str = "interview") -> EmotionState:
        """Map sentiment analysis result to an emotion state.

        Args:
            sentiment: Dict with polarity, subjectivity, and keywords.
            context: Context for the analysis (e.g., "interview").

        Returns:
            The mapped EmotionState.
        """
        polarity = float(sentiment.get("polarity", 0.0))  # type: ignore[arg-type]
        evasion = float(sentiment.get("evasion", 0.0))  # type: ignore[arg-type]
        confidence = float(sentiment.get("confidence", 0.5))  # type: ignore[arg-type]

        # Determine emotion based on rules
        if evasion > EVASION_THRESHOLD:
            emotion = "skeptical"
            intensity = 0.4 + (evasion * 0.5)
        elif polarity > POSITIVE_THRESHOLD and confidence > CONFIDENCE_LOW_THRESHOLD:
            emotion = "satisfied"
            intensity = 0.5 + (polarity * 0.4)
        elif polarity < NEGATIVE_THRESHOLD:
            emotion = "stern"
            intensity = 0.4 + (abs(polarity) * 0.4)
        elif confidence < CONFIDENCE_LOW_THRESHOLD:
            emotion = "concerned"
            intensity = 0.4 + ((1.0 - confidence) * 0.3)
        elif abs(polarity) < 0.1 and context == "interview":
            emotion = "attentive"
            intensity = float(EMOTION_TYPES["attentive"]["default_intensity"])
        else:
            emotion = "neutral"
            intensity = float(EMOTION_TYPES["neutral"]["default_intensity"])

        # Clamp intensity within the emotion's range
        emotion_config = EMOTION_TYPES[emotion]
        min_i = float(emotion_config["min_intensity"])
        max_i = float(emotion_config["max_intensity"])
        intensity = max(min_i, min(max_i, intensity))

        return EmotionState(
            emotion=emotion,
            intensity=round(intensity, 3),
            confidence=round(max(0.0, min(1.0, abs(polarity) + confidence * 0.5)), 3),
        )

    def get_transition_duration(self, from_emotion: str, to_emotion: str) -> int:
        """Get transition duration between two emotions in milliseconds."""
        key = f"{from_emotion}_to_{to_emotion}"
        return TRANSITION_DURATIONS.get(key, TRANSITION_DURATIONS["default"])

    def generate_transition(
        self, current: EmotionState, target: EmotionState, trigger: str = "response_analysis"
    ) -> EmotionTransition:
        """Generate a smooth transition between two emotion states.

        Args:
            current: The current emotion state.
            target: The target emotion state.
            trigger: What triggered the transition.

        Returns:
            An EmotionTransition object.
        """
        duration = self.get_transition_duration(current.emotion, target.emotion)
        return EmotionTransition(
            from_emotion=current,
            to_emotion=target,
            duration_ms=duration,
            trigger=trigger,
        )

    def generate_sequence(self, responses: list[dict[str, str]]) -> list[EmotionSequence]:
        """Generate full emotion sequences for a list of interview responses.

        Args:
            responses: List of dicts with 'id', 'text', and optionally 'expected_keywords'.

        Returns:
            List of EmotionSequence objects.
        """
        sequences: list[EmotionSequence] = []
        baseline = EmotionState(BASELINE_EMOTION, BASELINE_INTENSITY, 0.8)
        current_emotion = baseline

        for response in responses:
            response_id = response.get("id", f"response_{len(sequences)}")
            text = response.get("text", "")
            expected_keywords = response.get("expected_keywords", "")

            # Analyze the response
            sentiment = self.analyzer.analyze(text)

            kw_list = [k.strip() for k in expected_keywords.split(",") if k.strip()] if expected_keywords else None
            sentiment["evasion"] = self.analyzer.detect_evasion(text, kw_list)
            sentiment["confidence"] = self.analyzer.detect_confidence_level(text)

            # Map to emotion
            target_emotion = self.map_to_emotion(sentiment)

            # Generate transition from current to target
            transition = self.generate_transition(current_emotion, target_emotion, trigger=f"response:{response_id}")

            # Generate transition back to baseline
            return_transition = self.generate_transition(target_emotion, baseline, trigger="return_to_baseline")

            sequence = EmotionSequence(
                response_id=response_id,
                original_emotion=target_emotion,
                transitional_emotions=[transition, return_transition],
                final_emotion=target_emotion,
                baseline_emotion=baseline,
            )
            sequences.append(sequence)

            # Update current emotion for next response
            current_emotion = target_emotion

        return sequences
