"""Configuration constants and exception hierarchy for the gemini-image skill."""

import os
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = SKILL_DIR / "output"

DEFAULT_MODEL = "gemini-2.5-flash-image"

AVAILABLE_MODELS = [
    "gemini-2.5-flash-image",
    "gemini-3.1-flash-image-preview",
    "gemini-3-pro-image-preview",
]

SUPPORTED_ASPECT_RATIOS = [
    "1:1",
    "1:4",
    "1:8",
    "2:3",
    "3:2",
    "3:4",
    "4:1",
    "4:3",
    "4:5",
    "5:4",
    "8:1",
    "9:16",
    "16:9",
    "21:9",
]

SUPPORTED_IMAGE_SIZES = ["0.5K", "1K", "2K", "4K"]

PERSON_GENERATION_OPTIONS = ["DONT_ALLOW", "ALLOW_ADULT", "ALLOW_ALL"]

SUPPORTED_INPUT_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
MAX_INPUT_SIZE_MB = 20

MIME_TYPES: dict[str, str] = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
}


def get_api_key() -> str | None:
    """Return the Gemini API key from environment, or None if not set."""
    return os.environ.get("GEMINI_API_KEY")


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------


class GeminiImageError(Exception):
    """Base exception for gemini-image skill errors."""


class ConfigError(GeminiImageError):
    """Configuration errors (missing API key, invalid settings)."""


class ValidationError(GeminiImageError):
    """Input validation errors (bad file, unsupported format, size limit)."""


class ApiError(GeminiImageError):
    """API call failures."""


class OutputError(GeminiImageError):
    """Output/save failures (no images generated)."""
