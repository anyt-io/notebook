---
name: response-evaluator
description: NLP-based answer evaluation with statistical analysis, hallucination detection, ordinal mapping, and confidence scoring. Use when evaluating user responses in interview simulations to detect hallucinated or irrelevant answers, score response quality, and perform statistical analysis across answer sets.
---

# Response Evaluator

Evaluate interview responses with hallucination detection, statistical analysis, and confidence scoring.

## Prerequisites

- `uv` (Python package manager)

## Usage

Evaluate responses against a question bank:

```bash
uv run --project runtime runtime/evaluate.py --transcript path/to/transcript.json --question-bank path/to/question_bank.json --output output/
```

### Features

- **Hallucination Detection**: Identifies responses that contain fabricated information not grounded in the question context or expected knowledge
- **Ordinal Mapping**: Maps free-text answers to ordinal rankings for statistical comparison
- **Confidence Scoring**: Statistical confidence intervals for response quality
- **Colliding Answer Detection**: Identifies contradictory answers within the same session
- **Response Validation**: Post-validation of AI-generated corrections against original responses

### Output

Produces `evaluation_report.json` with per-response scores, hallucination flags, ordinal mappings, confidence intervals, and aggregate statistics.
