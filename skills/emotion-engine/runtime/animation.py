"""Animation script generator for avatar rendering."""

from __future__ import annotations

from config import FACIAL_EXPRESSION_PARAMS
from models import AnimationKeyframe, EmotionSequence, EmotionState, FacialExpression


class AnimationScriptGenerator:
    """Generates animation scripts from emotion sequences."""

    def generate_expression(self, emotion: EmotionState) -> FacialExpression:
        """Map an emotion state to facial expression parameters.

        Args:
            emotion: The emotion state to map.

        Returns:
            FacialExpression with appropriate parameters.
        """
        params = FACIAL_EXPRESSION_PARAMS.get(emotion.emotion, FACIAL_EXPRESSION_PARAMS["neutral"])

        # Scale head tilt by intensity
        base_tilt = float(params["head_tilt"])
        scaled_tilt = base_tilt * emotion.intensity

        return FacialExpression(
            eyebrows=str(params["eyebrows"]),
            eyes=str(params["eyes"]),
            mouth=str(params["mouth"]),
            head_tilt=round(scaled_tilt, 1),
        )

    def generate_keyframes(self, sequence: EmotionSequence) -> list[AnimationKeyframe]:
        """Generate animation keyframes from an emotion sequence.

        Args:
            sequence: The emotion sequence to convert.

        Returns:
            List of AnimationKeyframe objects with timing.
        """
        keyframes: list[AnimationKeyframe] = []
        current_time = 0

        # Start with baseline expression
        baseline_expr = self.generate_expression(sequence.baseline_emotion)
        keyframes.append(
            AnimationKeyframe(
                timestamp_ms=current_time,
                emotion=sequence.baseline_emotion,
                expression=baseline_expr,
                duration_ms=200,
            )
        )
        current_time += 200

        # Add transitional keyframes
        for transition in sequence.transitional_emotions:
            expr = self.generate_expression(transition.to_emotion)
            keyframes.append(
                AnimationKeyframe(
                    timestamp_ms=current_time,
                    emotion=transition.to_emotion,
                    expression=expr,
                    duration_ms=transition.duration_ms,
                )
            )
            current_time += transition.duration_ms

        # End with final emotion held
        final_expr = self.generate_expression(sequence.final_emotion)
        keyframes.append(
            AnimationKeyframe(
                timestamp_ms=current_time,
                emotion=sequence.final_emotion,
                expression=final_expr,
                duration_ms=1000,
            )
        )

        return keyframes

    def generate_script(self, sequences: list[EmotionSequence]) -> list[dict[str, object]]:
        """Generate a full animation script from multiple emotion sequences.

        Args:
            sequences: List of emotion sequences to process.

        Returns:
            List of serializable dicts representing the animation script.
        """
        script: list[dict[str, object]] = []
        cumulative_time = 0

        for sequence in sequences:
            keyframes = self.generate_keyframes(sequence)

            entry: dict[str, object] = {
                "response_id": sequence.response_id,
                "start_time_ms": cumulative_time,
                "keyframes": [kf.to_dict() for kf in keyframes],
            }

            # Calculate total duration for this sequence
            if keyframes:
                last_kf = keyframes[-1]
                total_duration = last_kf.timestamp_ms + last_kf.duration_ms
                entry["total_duration_ms"] = total_duration
                cumulative_time += total_duration
            else:
                entry["total_duration_ms"] = 0

            script.append(entry)

        return script
