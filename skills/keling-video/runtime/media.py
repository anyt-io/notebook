"""Input media validation, URL resolution, and structured input parsing."""

import argparse
import json
from pathlib import Path

import fal_client

from config import (
    MAX_IMAGE_SIZE_MB,
    MAX_VIDEO_SIZE_MB,
    SUPPORTED_INPUT_EXTENSIONS,
    SUPPORTED_VIDEO_EXTENSIONS,
    UploadError,
    ValidationError,
)

# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------


def validate_input_image(path: Path) -> None:
    """Validate input image. Raises ValidationError if invalid."""
    if not path.exists():
        raise ValidationError(f"Input image not found: {path}")
    if not path.is_file():
        raise ValidationError(f"Not a file: {path}")
    if path.suffix.lower() not in SUPPORTED_INPUT_EXTENSIONS:
        raise ValidationError(
            f"Unsupported image format '{path.suffix}': {path} "
            f"(supported: {', '.join(sorted(SUPPORTED_INPUT_EXTENSIONS))})"
        )
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > MAX_IMAGE_SIZE_MB:
        raise ValidationError(f"Image too large: {size_mb:.1f}MB (max: {MAX_IMAGE_SIZE_MB}MB)")


def validate_input_video(path: Path) -> None:
    """Validate input video. Raises ValidationError if invalid."""
    if not path.exists():
        raise ValidationError(f"Input video not found: {path}")
    if not path.is_file():
        raise ValidationError(f"Not a file: {path}")
    if path.suffix.lower() not in SUPPORTED_VIDEO_EXTENSIONS:
        raise ValidationError(
            f"Unsupported video format '{path.suffix}': {path} "
            f"(supported: {', '.join(sorted(SUPPORTED_VIDEO_EXTENSIONS))})"
        )
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > MAX_VIDEO_SIZE_MB:
        raise ValidationError(f"Video too large: {size_mb:.1f}MB (max: {MAX_VIDEO_SIZE_MB}MB)")


# ---------------------------------------------------------------------------
# URL resolution
# ---------------------------------------------------------------------------


def resolve_image_url(image_arg: str) -> str:
    """Resolve an image argument to a URL. Uploads local files, passes URLs through."""
    if image_arg.startswith(("http://", "https://")):
        return image_arg
    path = Path(image_arg)
    validate_input_image(path)
    try:
        return fal_client.upload_file(path)  # type: ignore[arg-type]
    except Exception as e:
        raise UploadError(f"Failed to upload image {path}: {e}") from e


def resolve_video_url(video_arg: str) -> str:
    """Resolve a video argument to a URL. Uploads local files, passes URLs through."""
    if video_arg.startswith(("http://", "https://")):
        return video_arg
    path = Path(video_arg)
    validate_input_video(path)
    try:
        return fal_client.upload_file(path)  # type: ignore[arg-type]
    except Exception as e:
        raise UploadError(f"Failed to upload video {path}: {e}") from e


# ---------------------------------------------------------------------------
# Multi-prompt & elements parsing
# ---------------------------------------------------------------------------


def parse_multi_prompt(value: str) -> list[dict[str, str]]:
    """Parse multi-prompt from JSON string or file path."""
    if Path(value).is_file():
        with open(value) as f:
            data = json.load(f)
    else:
        data = json.loads(value)

    if not isinstance(data, list):
        raise ValidationError(
            "multi-prompt must be a JSON array of objects with 'prompt' and optional 'duration' fields"
        )
    for item in data:
        if not isinstance(item, dict) or "prompt" not in item:
            raise ValidationError("Each multi-prompt element must have a 'prompt' field")
    return data


def build_element(
    frontal_url: str,
    ref_urls: list[str] | None = None,
    video_url: str | None = None,
) -> dict[str, object]:
    """Build a single element dict for the reference-to-video or edit-video API."""
    elem: dict[str, object] = {"frontal_image_url": frontal_url}
    if ref_urls:
        elem["reference_image_urls"] = ref_urls
    if video_url:
        elem["video_url"] = video_url
    return elem


def parse_elements_json(value: str) -> list[dict[str, object]]:
    """Parse elements from JSON string or file path."""
    if Path(value).is_file():
        with open(value) as f:
            data = json.load(f)
    else:
        data = json.loads(value)

    if not isinstance(data, list):
        raise ValidationError("elements-json must be a JSON array of element objects")
    return data


# ---------------------------------------------------------------------------
# Mode detection
# ---------------------------------------------------------------------------


def detect_mode(args: argparse.Namespace) -> str:
    """Auto-detect the generation mode from CLI arguments."""
    if args.video:
        return "edit-video"
    if args.element or args.elements_json:
        return "reference-to-video"
    if args.image:
        return "image-to-video"
    return "text-to-video"
