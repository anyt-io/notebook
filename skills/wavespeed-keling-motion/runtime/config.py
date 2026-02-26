"""Configuration constants and exception hierarchy for the wavespeed-keling-motion skill."""

import os
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = SKILL_DIR / "output"

# ---------------------------------------------------------------------------
# API Configuration
# ---------------------------------------------------------------------------
API_BASE_URL = "https://api.wavespeed.ai/api/v3"
MOTION_CONTROL_ENDPOINT = "/kwaivgi/kling-v2.6-std/motion-control"
RESULT_ENDPOINT_TEMPLATE = "/predictions/{request_id}/result"

# ---------------------------------------------------------------------------
# Parameter options
# ---------------------------------------------------------------------------
SUPPORTED_ORIENTATIONS = ["image", "video"]
DEFAULT_ORIENTATION = "image"

SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
SUPPORTED_VIDEO_EXTENSIONS = {".mp4", ".mov"}
MAX_IMAGE_SIZE_MB = 10
MAX_VIDEO_SIZE_MB = 10
MIN_DIMENSION_PX = 300

# Polling configuration
DEFAULT_POLL_INTERVAL = 5.0  # seconds
MAX_POLL_ATTEMPTS = 120  # 10 minutes at 5s intervals


def get_api_key() -> str | None:
    """Return the WaveSpeed API key from environment, or None if not set."""
    return os.environ.get("WAVESPEED_API_KEY")


def get_motion_control_url() -> str:
    """Get the full URL for the motion control endpoint."""
    return f"{API_BASE_URL}{MOTION_CONTROL_ENDPOINT}"


def get_result_url(request_id: str) -> str:
    """Get the full URL for retrieving a prediction result."""
    return f"{API_BASE_URL}{RESULT_ENDPOINT_TEMPLATE.format(request_id=request_id)}"


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------


class MotionError(Exception):
    """Base exception for wavespeed-keling-motion skill errors."""


class ConfigError(MotionError):
    """Configuration errors (missing API key, invalid settings)."""


class ValidationError(MotionError):
    """Input validation errors (bad file, unsupported format, size limit)."""


class UploadError(MotionError):
    """File upload failures."""


class ApiError(MotionError):
    """API call failures."""


class OutputError(MotionError):
    """Output/save failures (no video in response, download failure)."""
