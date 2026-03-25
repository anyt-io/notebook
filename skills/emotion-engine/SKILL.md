---
name: emotion-engine
description: Map user response sentiment and tone to avatar emotional states. Use when building interview simulations that need dynamic avatar expressions, emotional state transitions, and animation script generation. Analyzes text sentiment and produces emotion sequences for avatar rendering.
---

# Emotion Engine

Analyze text sentiment and generate avatar emotional state transitions and animation scripts.

## Prerequisites

- `uv` (Python package manager)

## Usage

Analyze sentiment and generate emotion states:

```bash
uv run --project runtime runtime/analyze_emotion.py --input "I'm going to buy a couch and visit my mother" --context interview --output output/
```

Process a full interview transcript:

```bash
uv run --project runtime runtime/analyze_emotion.py --transcript path/to/transcript.json --output output/
```

### Emotion Model

The engine works with these base emotions:
- **neutral** — default resting state
- **attentive** — actively listening, engaged
- **skeptical** — questioning, doubtful
- **satisfied** — positive response to good answers
- **stern** — serious, probing deeper
- **surprised** — unexpected answer detected
- **concerned** — detecting evasion or inconsistency

Each emotion has intensity (0.0-1.0), transition duration, and associated facial expression parameters.

### Output

Produces `emotion_states.json` and `animation_script.json`:

- **emotion_states.json**: Per-response emotion analysis with original, transitional, and baseline emotions
- **animation_script.json**: Sequence of emotive expressions with timing for avatar rendering
