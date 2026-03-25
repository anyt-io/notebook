---
name: user-profiler
description: Track user performance across interview simulation sessions. Use when building interview preparation systems that need to maintain user profiles, track improvement over time, identify weak areas, and generate personalized training recommendations.
---

# User Profiler

Track and analyze user performance across multiple interview simulation sessions.

## Prerequisites

- `uv` (Python package manager)

## Usage

Update a user profile with new session results:

```bash
uv run --project runtime runtime/profile.py --user-id user123 --session path/to/interview_analysis.json --output output/
```

Generate training recommendations:

```bash
uv run --project runtime runtime/profile.py --user-id user123 --recommend --output output/
```

View profile summary:

```bash
uv run --project runtime runtime/profile.py --user-id user123 --summary
```

### Profile Data

Tracks per user:
- Session history with scores and timestamps
- Category-level performance trends
- Difficulty progression
- Weak areas and improvement rate
- Time-to-answer patterns

### Output

- `user_profile.json`: Full user profile with history
- `recommendations.json`: Personalized training plan
- `progress_report.json`: Improvement trends over time
