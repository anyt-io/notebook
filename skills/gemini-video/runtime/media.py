"""Input media validation and loading for the gemini-video skill."""

from pathlib import Path

from google.genai import types

from config import (
    MAX_INPUT_SIZE_MB,
    MIME_TYPES,
    SUPPORTED_INPUT_EXTENSIONS,
    ValidationError,
)


def validate_input_image(path: Path) -> None:
    """Validate input image. Raises ValidationError if invalid."""
    if not path.exists():
        raise ValidationError(f"Input image not found: {path}")
    if not path.is_file():
        raise ValidationError(f"Not a file: {path}")
    if path.suffix.lower() not in SUPPORTED_INPUT_EXTENSIONS:
        raise ValidationError(
            f"Unsupported format '{path.suffix}': {path} (supported: {', '.join(sorted(SUPPORTED_INPUT_EXTENSIONS))})"
        )
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > MAX_INPUT_SIZE_MB:
        raise ValidationError(f"Input image too large: {size_mb:.1f}MB (max: {MAX_INPUT_SIZE_MB}MB)")


def load_image(path: Path) -> types.Image:
    """Load an image file and return a Gemini Image object."""
    mime_type = MIME_TYPES[path.suffix.lower()]
    data = path.read_bytes()
    return types.Image(image_bytes=data, mime_type=mime_type)


def build_reference_images(paths: list[Path]) -> list[types.VideoGenerationReferenceImage]:
    """Load image files and return VideoGenerationReferenceImage objects."""
    refs: list[types.VideoGenerationReferenceImage] = []
    for path in paths:
        image = load_image(path)
        refs.append(
            types.VideoGenerationReferenceImage(image=image, reference_type=types.VideoGenerationReferenceType.ASSET)
        )
    return refs
