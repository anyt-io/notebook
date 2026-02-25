"""Configuration constants and exception hierarchy for the gemini-video skill."""

import os
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = SKILL_DIR / "output"

DEFAULT_MODEL = "veo-3.1-generate-preview"

AVAILABLE_MODELS = [
    "veo-3.1-generate-preview",
    "veo-3.1-fast-generate-preview",
]

SUPPORTED_ASPECT_RATIOS = ["16:9", "9:16"]

SUPPORTED_RESOLUTIONS = ["720p", "1080p", "4k"]

SUPPORTED_DURATIONS = [4, 6, 8]

PERSON_GENERATION_OPTIONS = ["allow_all", "allow_adult", "dont_allow"]

MAX_REFERENCE_IMAGES = 3

SUPPORTED_INPUT_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
MAX_INPUT_SIZE_MB = 20

MIME_TYPES: dict[str, str] = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
}

DEFAULT_POLL_INTERVAL = 10

# Concat video constants
SUPPORTED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}


def get_api_key() -> str | None:
    """Return the Gemini API key from environment, or None if not set."""
    return os.environ.get("GEMINI_API_KEY")


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------


class GeminiVideoError(Exception):
    """Base exception for gemini-video skill errors."""


class ConfigError(GeminiVideoError):
    """Configuration errors (missing API key, invalid settings)."""


class ValidationError(GeminiVideoError):
    """Input validation errors (bad file, unsupported format, size limit)."""


class ApiError(GeminiVideoError):
    """API call failures."""


class OutputError(GeminiVideoError):
    """Output/save failures (no video generated)."""
