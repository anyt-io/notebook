"""Configuration constants for the document-intake skill."""

from pathlib import Path

# Supported file extensions
SUPPORTED_EXTENSIONS: set[str] = {".pdf", ".txt", ".md", ".markdown"}

# Default output directory (relative to skill root)
DEFAULT_OUTPUT_DIR: Path = Path(__file__).resolve().parent.parent / "output"

# Question categories
CATEGORIES: list[str] = [
    "definition",
    "rule",
    "procedure",
    "eligibility",
    "exception",
]

# Difficulty levels (1-5)
MIN_DIFFICULTY: int = 1
MAX_DIFFICULTY: int = 5

# Patterns used for extraction
DEFINITION_PATTERNS: list[str] = [
    r'"([^"]+)"\s+means\b',
    r'"([^"]+)"\s+refers\s+to\b',
    r"the\s+term\s+\"([^\"]+)\"",
    r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*[:\-]\s+",
]

RULE_INDICATORS: list[str] = [
    "shall",
    "must",
    "required",
    "prohibited",
    "may not",
    "is entitled",
    "is eligible",
    "shall not",
]

SECTION_HEADING_PATTERN: str = (
    r"^(?:#{1,6}\s+|(?:Section|Article|Part|Chapter|Rule)\s+[\dIVXivx]+[.:)]\s*"
    r"|[\d]+[.:)]\s+|\([a-z]\)\s+)"
)
