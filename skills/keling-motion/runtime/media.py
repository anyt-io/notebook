"""Input media validation and URL resolution."""

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
