"""CLI entry point for response evaluation."""

import argparse
import json
import os

from config import EvaluationConfig
from evaluator import ResponseEvaluator


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate interview responses.")
    parser.add_argument(
        "--transcript",
        required=True,
        help="Path to transcript JSON file (list of response entries).",
    )
    parser.add_argument(
        "--question-bank",
        required=True,
        help="Path to question bank JSON file (mapping question_id to question dicts).",
    )
    parser.add_argument(
        "--output",
        default="output/",
        help="Output directory for evaluation report (default: output/).",
    )
    parser.add_argument(
        "--confidence-level",
        type=float,
        default=0.95,
        help="Confidence level for statistical intervals (default: 0.95).",
    )

    args = parser.parse_args()

    # Load transcript
    with open(args.transcript) as f:
        transcript = json.load(f)

    # Load question bank
    with open(args.question_bank) as f:
        question_bank = json.load(f)

    # Configure and run
    config = EvaluationConfig(confidence_level=args.confidence_level)
    evaluator = ResponseEvaluator(config)
    report = evaluator.evaluate_session(transcript, question_bank)

    # Write output
    os.makedirs(args.output, exist_ok=True)
    output_path = os.path.join(args.output, "evaluation_report.json")
    with open(output_path, "w") as f:
        json.dump(report.to_dict(), f, indent=2)

    print(f"Evaluation report written to {output_path}")
    print(f"Aggregate score: {report.aggregate_score}")
    print(f"Confidence interval: {report.confidence_interval}")
    print(f"Hallucination count: {report.hallucination_count}")
    if report.recommendations:
        print("Recommendations:")
        for rec in report.recommendations:
            print(f"  - {rec}")


if __name__ == "__main__":
    main()
