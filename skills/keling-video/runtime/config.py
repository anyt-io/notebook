"""Configuration constants and exception hierarchy for the keling-video skill."""

import os
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = SKILL_DIR / "output"

# ---------------------------------------------------------------------------
# Endpoint map: ENDPOINTS[mode][quality]
# ---------------------------------------------------------------------------
ENDPOINTS: dict[str, dict[str, str]] = {
    "text-to-video": {
        "standard": "fal-ai/kling-video/o3/standard/text-to-video",
        "pro": "fal-ai/kling-video/o3/pro/text-to-video",
    },
    "image-to-video": {
        "standard": "fal-ai/kling-video/o3/standard/image-to-video",
        "pro": "fal-ai/kling-video/o3/pro/image-to-video",
    },
    "reference-to-video": {
        "standard": "fal-ai/kling-video/o3/standard/reference-to-video",
        "pro": "fal-ai/kling-video/o3/pro/reference-to-video",
    },
    "edit-video": {
        "standard": "fal-ai/kling-video/o3/standard/video-to-video/edit",
        "pro": "fal-ai/kling-video/o3/pro/video-to-video/edit",
    },
}

SUPPORTED_MODES = list(ENDPOINTS.keys())
SUPPORTED_QUALITY = ["standard", "pro"]
DEFAULT_QUALITY = "standard"

SUPPORTED_ASPECT_RATIOS = ["16:9", "9:16", "1:1"]
DEFAULT_ASPECT_RATIO = "16:9"

SUPPORTED_DURATIONS = [str(d) for d in range(3, 16)]
DEFAULT_DURATION = "5"

SUPPORTED_INPUT_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
MAX_IMAGE_SIZE_MB = 10
MAX_VIDEO_SIZE_MB = 200
SUPPORTED_VIDEO_EXTENSIONS = {".mp4", ".mov"}
MAX_ELEMENTS = 2
MAX_ELEMENT_REFS = 3
MAX_REF_IMAGES = 4


def get_api_key() -> str | None:
    """Return the fal API key from environment, or None if not set."""
    return os.environ.get("FAL_KEY")


def get_endpoint(mode: str, quality: str) -> str:
    """Get the fal endpoint ID for the given mode and quality."""
    return ENDPOINTS[mode][quality]


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------


class KelingError(Exception):
    """Base exception for keling-video skill errors."""


class ConfigError(KelingError):
    """Configuration errors (missing API key, invalid settings)."""


class ValidationError(KelingError):
    """Input validation errors (bad file, unsupported format, size limit)."""


class UploadError(KelingError):
    """File upload failures."""


class ApiError(KelingError):
    """API call failures."""


class OutputError(KelingError):
    """Output/save failures (no video in response, download failure)."""
