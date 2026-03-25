---
name: interview-sim
description: Core interview simulation orchestration engine. Use when building domain-specific interview simulations that require question flow management, branching logic, scoring, and confidence thresholds. Manages interview sessions with configurable question pools, adaptive difficulty, and generates structured interview transcripts.
---

# Interview Simulator

Orchestrate domain-specific interview simulations with adaptive question flow, branching logic, and confidence-based scoring.

## Prerequisites

- `uv` (Python package manager)

## Usage

Run an interview simulation from a question bank:

```bash
uv run --project runtime runtime/simulate.py --question-bank path/to/question_bank.json --domain immigration --output output/
```

### Input: Question Bank JSON

The question bank should be a JSON file with this structure (produced by the `document-intake` skill):

```json
{
  "domain": "immigration",
  "questions": [
    {
      "id": "q1",
      "text": "What is your purpose for traveling to the United States?",
      "category": "travel_purpose",
      "difficulty": 1,
      "expected_answer_keywords": ["visit", "business", "tourism", "study"],
      "source_section": "Section 1.2",
      "follow_ups": ["q2", "q3"]
    }
  ]
}
```

### Configuration

Pass a simulation config JSON to customize behavior:

```bash
uv run --project runtime runtime/simulate.py --question-bank qb.json --config sim_config.json
```

Config options:
- `max_questions`: Maximum questions per session (default: 20)
- `confidence_threshold`: Minimum confidence score to pass (default: 0.7)
- `adaptive_difficulty`: Enable adaptive difficulty adjustment (default: true)
- `time_limit_seconds`: Optional time limit per question
- `domain`: Interview domain context

### Output

Produces `interview_transcript.json` and `interview_analysis.json` in the output directory.

The transcript contains each Q&A pair with timestamps, scores, and flow metadata. The analysis contains aggregate scores, confidence intervals, weak areas, and recommendations.
