"""Configuration constants and exception hierarchy for the keling-motion skill."""

import os
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = SKILL_DIR / "output"

# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------
ENDPOINT = "fal-ai/kling-video/v2.6/standard/motion-control"

SUPPORTED_ORIENTATIONS = ["image", "video"]
DEFAULT_ORIENTATION = "image"

SUPPORTED_INPUT_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
MAX_IMAGE_SIZE_MB = 10
SUPPORTED_VIDEO_EXTENSIONS = {".mp4", ".mov"}
MAX_VIDEO_SIZE_MB = 200


def get_api_key() -> str | None:
    """Return the fal API key from environment, or None if not set."""
    return os.environ.get("FAL_KEY")


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------


class KelingMotionError(Exception):
    """Base exception for keling-motion skill errors."""


class ConfigError(KelingMotionError):
    """Configuration errors (missing API key, invalid settings)."""


class ValidationError(KelingMotionError):
    """Input validation errors (bad file, unsupported format, size limit)."""


class UploadError(KelingMotionError):
    """File upload failures."""


class ApiError(KelingMotionError):
    """API call failures."""


class OutputError(KelingMotionError):
    """Output/save failures (no video in response, download failure)."""
