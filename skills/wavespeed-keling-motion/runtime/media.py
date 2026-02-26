"""Input media validation and URL resolution."""

import base64
import mimetypes
from pathlib import Path

from config import (
    MAX_IMAGE_SIZE_MB,
    MAX_VIDEO_SIZE_MB,
    SUPPORTED_IMAGE_EXTENSIONS,
    SUPPORTED_VIDEO_EXTENSIONS,
    ValidationError,
)


def validate_input_image(path: Path) -> None:
    """Validate input image. Raises ValidationError if invalid."""
    if not path.exists():
        raise ValidationError(f"Input image not found: {path}")
    if not path.is_file():
        raise ValidationError(f"Not a file: {path}")
    if path.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
        raise ValidationError(
            f"Unsupported image format '{path.suffix}': {path} "
            f"(supported: {', '.join(sorted(SUPPORTED_IMAGE_EXTENSIONS))})"
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


def file_to_data_url(path: Path) -> str:
    """Convert a local file to a data URL."""
    mime_type, _ = mimetypes.guess_type(str(path))
    if mime_type is None:
        # Fallback based on extension
        ext = path.suffix.lower()
        mime_map = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".mp4": "video/mp4",
            ".mov": "video/quicktime",
        }
        mime_type = mime_map.get(ext, "application/octet-stream")

    with open(path, "rb") as f:
        data = f.read()

    base64_data = base64.b64encode(data).decode("utf-8")
    return f"data:{mime_type};base64,{base64_data}"


def resolve_image_url(image_arg: str) -> str:
    """Resolve an image argument to a URL. Converts local files to data URLs, passes URLs through."""
    if image_arg.startswith(("http://", "https://", "data:")):
        return image_arg
    path = Path(image_arg)
    validate_input_image(path)
    return file_to_data_url(path)


def resolve_video_url(video_arg: str) -> str:
    """Resolve a video argument to a URL. Converts local files to data URLs, passes URLs through."""
    if video_arg.startswith(("http://", "https://", "data:")):
        return video_arg
    path = Path(video_arg)
    validate_input_video(path)
    return file_to_data_url(path)
