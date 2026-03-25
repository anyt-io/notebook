"""CLI entry point for emotion analysis and animation script generation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from animation import AnimationScriptGenerator
from emotion_mapper import EmotionMapper
from sentiment import SentimentAnalyzer


def analyze_single(text: str, context: str) -> dict[str, object]:
    """Analyze a single text input and return emotion data."""
    analyzer = SentimentAnalyzer()
    mapper = EmotionMapper()
    anim_gen = AnimationScriptGenerator()

    # Analyze sentiment
    sentiment = analyzer.analyze(text)
    sentiment["evasion"] = analyzer.detect_evasion(text)
    sentiment["confidence"] = analyzer.detect_confidence_level(text)

    # Map to emotion
    emotion = mapper.map_to_emotion(sentiment, context=context)
    expression = anim_gen.generate_expression(emotion)

    return {
        "text": text,
        "context": context,
        "sentiment": {
            "polarity": sentiment["polarity"],
            "subjectivity": sentiment["subjectivity"],
            "evasion": sentiment["evasion"],
            "confidence": sentiment["confidence"],
            "keywords": sentiment["keywords"],
        },
        "emotion": emotion.to_dict(),
        "expression": expression.to_dict(),
    }


def process_transcript(transcript_path: str, context: str) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Process a full interview transcript.

    Args:
        transcript_path: Path to the transcript JSON file.
        context: Analysis context.

    Returns:
        Tuple of (emotion_states, animation_script).
    """
    with open(transcript_path) as f:
        transcript = json.load(f)

    responses: list[dict[str, str]] = transcript.get("responses", [])
    if not responses:
        print("Error: No responses found in transcript.", file=sys.stderr)
        sys.exit(1)

    mapper = EmotionMapper()
    anim_gen = AnimationScriptGenerator()

    # Generate emotion sequences
    sequences = mapper.generate_sequence(responses)

    # Build emotion states output
    emotion_states = [seq.to_dict() for seq in sequences]

    # Generate animation script
    animation_script = anim_gen.generate_script(sequences)

    return emotion_states, animation_script


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Analyze text sentiment and generate avatar emotion states.")
    parser.add_argument("--input", type=str, help="Single text input to analyze.")
    parser.add_argument("--transcript", type=str, help="Path to transcript JSON file.")
    parser.add_argument("--context", type=str, default="interview", help="Analysis context (default: interview).")
    parser.add_argument("--output", type=str, default="output/", help="Output directory (default: output/).")
    args = parser.parse_args()

    if not args.input and not args.transcript:
        parser.error("Either --input or --transcript must be provided.")

    # Ensure output directory exists
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.input:
        # Single text analysis
        result = analyze_single(args.input, args.context)
        output_path = output_dir / "emotion_states.json"
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)
        print(f"Emotion analysis saved to {output_path}")
        print(json.dumps(result, indent=2))

    elif args.transcript:
        # Full transcript processing
        emotion_states, animation_script = process_transcript(args.transcript, args.context)

        states_path = output_dir / "emotion_states.json"
        with open(states_path, "w") as f:
            json.dump(emotion_states, f, indent=2)
        print(f"Emotion states saved to {states_path}")

        script_path = output_dir / "animation_script.json"
        with open(script_path, "w") as f:
            json.dump(animation_script, f, indent=2)
        print(f"Animation script saved to {script_path}")


if __name__ == "__main__":
    main()
