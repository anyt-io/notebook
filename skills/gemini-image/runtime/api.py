"""Gemini API interaction: image generation, loading, and saving."""

import io
from datetime import datetime
from pathlib import Path

from google import genai
from google.genai import types
from PIL import Image

from config import (
    MIME_TYPES,
    SUPPORTED_INPUT_EXTENSIONS,
    ApiError,
    OutputError,
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
    from config import MAX_INPUT_SIZE_MB

    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > MAX_INPUT_SIZE_MB:
        raise ValidationError(f"Input image too large: {size_mb:.1f}MB (max: {MAX_INPUT_SIZE_MB}MB)")


def load_image_as_part(path: Path) -> types.Part:
    """Load an image file and return a Gemini Part with inline data."""
    mime_type = MIME_TYPES[path.suffix.lower()]
    data = path.read_bytes()
    return types.Part.from_bytes(data=data, mime_type=mime_type)


def generate_images(
    client: genai.Client,
    prompt: str,
    model: str,
    input_image: Path | None = None,
    count: int = 1,
    aspect_ratio: str | None = None,
    image_size: str | None = None,
    person_generation: str | None = None,
) -> list[tuple[Image.Image | None, str | None]]:
    """Generate images using the Gemini API.

    Returns a list of (image, text) tuples. Raises ApiError on failure.
    """
    image_config = types.ImageConfig()
    if aspect_ratio:
        image_config.aspect_ratio = aspect_ratio
    if image_size:
        image_config.image_size = image_size
    if person_generation:
        image_config.person_generation = person_generation  # type: ignore[assignment]

    config = types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        candidate_count=count,
        image_config=image_config,
    )

    contents: str | list[types.Part]
    if input_image is not None:
        contents = [types.Part.from_text(text=prompt), load_image_as_part(input_image)]
    else:
        contents = prompt

    try:
        response = client.models.generate_content(
            model=model,
            contents=contents,  # type: ignore[arg-type]
            config=config,
        )
    except Exception as e:
        raise ApiError(f"API call failed: {e}") from e

    results: list[tuple[Image.Image | None, str | None]] = []

    if not response.candidates:
        results.append((None, "No candidates returned — prompt may have been blocked by safety filters."))
        return results

    candidate = response.candidates[0]
    if not candidate.content or not candidate.content.parts:
        results.append((None, "Empty response — prompt may have been blocked by safety filters."))
        return results

    img = None
    text = None
    for part in candidate.content.parts:
        if part.text:
            text = part.text
        elif part.inline_data and part.inline_data.data:
            img = Image.open(io.BytesIO(part.inline_data.data))
            results.append((img, text))
            img = None
            text = None

    if text and not img:
        results.append((None, text))

    return results


def save_images(
    results: list[tuple[Image.Image | None, str | None]],
    output_dir: Path,
) -> list[Path]:
    """Save generated images to the output directory.

    Returns list of saved paths. Raises OutputError if no images were generated.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    saved: list[Path] = []

    for i, (img, text) in enumerate(results):
        if text:
            print(f"  Model: {text}")
        if img:
            filename = f"gemini_{timestamp}_{i + 1}.png"
            path = output_dir / filename
            img.save(path)
            saved.append(path)
            print(f"  Saved: {path}")
        elif not text:
            print(f"  Warning: result {i + 1} produced no image or text.")

    if not saved:
        raise OutputError("No images were generated. Try adjusting your prompt.")

    return saved
