"""CLI entry point for the interview simulator."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from analyzer import InterviewAnalyzer
from flow_engine import FlowEngine
from models import InterviewSession, Question, ResponseRecord, SimulationConfig
from scoring import ScoreEngine


def load_question_bank(path: str) -> tuple[list[Question], str]:
    """Load questions from a question bank JSON file."""
    with open(path) as f:
        data = json.load(f)

    domain = data.get("domain", "")
    questions: list[Question] = []
    for q in data["questions"]:
        questions.append(
            Question(
                id=q["id"],
                text=q["text"],
                category=q.get("category", "general"),
                difficulty=q.get("difficulty", 1),
                expected_answer_keywords=q.get("expected_answer_keywords", []),
                source_section=q.get("source_section", ""),
                follow_ups=q.get("follow_ups", []),
                domain=domain,
            )
        )
    return questions, domain


def load_config(path: str | None, domain: str) -> SimulationConfig:
    """Load simulation config from a JSON file or return defaults."""
    if path is None:
        return SimulationConfig(domain=domain)

    with open(path) as f:
        data = json.load(f)

    return SimulationConfig(
        max_questions=data.get("max_questions", 20),
        confidence_threshold=data.get("confidence_threshold", 0.7),
        adaptive_difficulty=data.get("adaptive_difficulty", True),
        time_limit_seconds=data.get("time_limit_seconds"),
        domain=data.get("domain", domain),
    )


def load_responses(path: str) -> list[str]:
    """Load pre-recorded responses from a JSON file."""
    with open(path) as f:
        return json.load(f)


def run_simulation(
    questions: list[Question],
    config: SimulationConfig,
    responses: list[str],
) -> InterviewSession:
    """Run a non-interactive interview simulation with pre-loaded responses."""
    session = InterviewSession(domain=config.domain, config=config)
    score_engine = ScoreEngine()
    flow_engine = FlowEngine(questions, config)

    response_iter = iter(responses)

    while not flow_engine.is_complete(session):
        question = flow_engine.select_next_question(session)
        if question is None:
            break

        try:
            user_response = next(response_iter)
        except StopIteration:
            break

        score = score_engine.score_response(question, user_response)
        scores_so_far = [r.score for r in session.responses] + [score]
        confidence = score_engine.calculate_confidence(scores_so_far)

        record = ResponseRecord(
            question_id=question.id,
            question_text=question.text,
            user_response=user_response,
            score=score,
            confidence=confidence,
            difficulty=question.difficulty,
        )
        session.responses.append(record)

    session.end_time = datetime.now().isoformat()
    session.status = "completed"
    return session


def save_results(session: InterviewSession, analysis: dict, output_dir: str) -> None:
    """Save transcript and analysis to the output directory."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    transcript = {
        "session_id": session.session_id,
        "domain": session.domain,
        "start_time": session.start_time,
        "end_time": session.end_time,
        "status": session.status,
        "responses": [
            {
                "question_id": r.question_id,
                "question_text": r.question_text,
                "user_response": r.user_response,
                "score": round(r.score, 4),
                "confidence": round(r.confidence, 4),
                "timestamp": r.timestamp,
                "difficulty": r.difficulty,
            }
            for r in session.responses
        ],
    }

    # Convert tuples to lists for JSON serialization
    serializable_analysis = _make_serializable(analysis)

    with open(out / "interview_transcript.json", "w") as f:
        json.dump(transcript, f, indent=2)

    with open(out / "interview_analysis.json", "w") as f:
        json.dump(serializable_analysis, f, indent=2)

    print(f"Transcript saved to {out / 'interview_transcript.json'}")
    print(f"Analysis saved to {out / 'interview_analysis.json'}")


def _make_serializable(obj: object) -> object:
    """Convert tuples and other non-JSON types to serializable forms."""
    if isinstance(obj, dict):
        return {k: _make_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_make_serializable(item) for item in obj]
    return obj


def main() -> None:
    parser = argparse.ArgumentParser(description="Interview Simulator")
    parser.add_argument("--question-bank", required=True, help="Path to question bank JSON file")
    parser.add_argument("--config", default=None, help="Path to simulation config JSON file")
    parser.add_argument("--domain", default="", help="Interview domain context")
    parser.add_argument("--output", default="output/", help="Output directory (default: output/)")
    parser.add_argument("--responses", required=True, help="Path to pre-loaded responses JSON file")

    args = parser.parse_args()

    questions, bank_domain = load_question_bank(args.question_bank)
    if not questions:
        print("Error: No questions found in question bank.", file=sys.stderr)
        sys.exit(1)

    domain = args.domain or bank_domain
    config = load_config(args.config, domain)

    responses = load_responses(args.responses)

    print(f"Starting simulation: domain={domain}, questions={len(questions)}, responses={len(responses)}")
    session = run_simulation(questions, config, responses)

    analyzer = InterviewAnalyzer()
    analysis = analyzer.analyze(session)

    save_results(session, analysis, args.output)

    print(f"\nOverall score: {analysis['overall_score']:.2%}")
    print(f"Confidence interval: {analysis['confidence_interval']}")
    print(f"Status: {'PASS' if analysis['overall_score'] >= config.confidence_threshold else 'NEEDS IMPROVEMENT'}")


if __name__ == "__main__":
    main()
