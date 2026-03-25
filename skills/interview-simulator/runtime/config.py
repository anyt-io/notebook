"""Default configuration for the interview simulator."""

# Interview limits
DEFAULT_MAX_QUESTIONS = 20
DEFAULT_CONFIDENCE_THRESHOLD = 0.7
DEFAULT_ADAPTIVE_DIFFICULTY = True

# Difficulty range
MIN_DIFFICULTY = 1
MAX_DIFFICULTY = 5
DEFAULT_DIFFICULTY = 1

# Scoring weights
DEFAULT_SCORING_WEIGHTS = {
    "keyword_match": 0.6,
    "completeness": 0.25,
    "relevance": 0.15,
}

# Adaptive difficulty tuning
DIFFICULTY_INCREASE_THRESHOLD = 0.8  # Score above this -> increase difficulty
DIFFICULTY_DECREASE_THRESHOLD = 0.4  # Score below this -> decrease difficulty
RECENT_WINDOW_SIZE = 3  # Number of recent responses to consider for adaptation
