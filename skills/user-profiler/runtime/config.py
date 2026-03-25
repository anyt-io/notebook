"""Configuration for user-profiler skill."""

# Default profile settings
DEFAULT_WEAK_THRESHOLD = 0.6
DEFAULT_STRONG_THRESHOLD = 0.8
DEFAULT_TREND_WINDOW = 5  # Number of sessions to consider for trend calculation
MIN_SESSIONS_FOR_TREND = 2  # Minimum sessions needed to calculate a trend

# Improvement thresholds
IMPROVEMENT_RATE_THRESHOLD = 0.05  # Rate above which trend is "improving"
DECLINE_RATE_THRESHOLD = -0.05  # Rate below which trend is "declining"

# Recommendation categories
PRIORITY_HIGH = "high"
PRIORITY_MEDIUM = "medium"
PRIORITY_LOW = "low"

# Difficulty levels (1-5)
MIN_DIFFICULTY = 1
MAX_DIFFICULTY = 5
DEFAULT_DIFFICULTY = 3

# Category descriptions for recommendations
CATEGORY_FOCUS_AREAS: dict[str, list[str]] = {
    "technical": [
        "Data structures and algorithms",
        "System design fundamentals",
        "Code optimization techniques",
        "Language-specific idioms",
    ],
    "behavioral": [
        "STAR method responses",
        "Leadership examples",
        "Conflict resolution scenarios",
        "Team collaboration stories",
    ],
    "communication": [
        "Structured problem explanation",
        "Active listening techniques",
        "Clarifying questions",
        "Concise summarization",
    ],
    "problem_solving": [
        "Breaking down complex problems",
        "Edge case identification",
        "Time complexity analysis",
        "Solution trade-off discussion",
    ],
    "domain_knowledge": [
        "Industry-specific terminology",
        "Current trends and best practices",
        "Regulatory awareness",
        "Tool and framework familiarity",
    ],
}

# Default focus areas for unknown categories
DEFAULT_FOCUS_AREAS: list[str] = [
    "Review fundamentals",
    "Practice with sample questions",
    "Seek feedback on responses",
    "Study common patterns",
]
