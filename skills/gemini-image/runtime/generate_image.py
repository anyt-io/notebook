#!/usr/bin/env python3
"""
Generate and edit images using the Google Gemini API.
Run with: uv run --project runtime runtime/generate_image.py <prompt> [options]

Requires GEMINI_API_KEY environment variable.
"""

import argparse
import io
import os
import sys
from datetime import datetime
from pathlib import Path

from google import genai
from google.genai import types
from PIL import Image

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = SKILL_DIR / "output"

DEFAULT_MODEL = "gemini-2.5-flash-image"

AVAILABLE_MODELS = [
    "gemini-2.5-flash-image",
    "gemini-3-pro-image-preview",
]

SUPPORTED_ASPECT_RATIOS = [
    "1:1",
    "2:3",
    "3:2",
    "3:4",
    "4:3",
    "4:5",
    "5:4",
    "9:16",
    "16:9",
    "21:9",
]

SUPPORTED_IMAGE_SIZES = ["1K", "2K", "4K"]

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


def validate_input_image(path: Path) -> str | None:
    """Return an error message if the input image is invalid, else None."""
    if not path.exists():
        return f"Input image not found: {path}"
    if not path.is_file():
        return f"Not a file: {path}"
    if path.suffix.lower() not in SUPPORTED_INPUT_EXTENSIONS:
        return (
            f"Unsupported format '{path.suffix}': {path} (supported: {', '.join(sorted(SUPPORTED_INPUT_EXTENSIONS))})"
        )
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > MAX_INPUT_SIZE_MB:
        return f"Input image too large: {size_mb:.1f}MB (max: {MAX_INPUT_SIZE_MB}MB)"
    return None


def load_image_as_part(path: Path) -> types.Part:
    """Load an image file and return a Gemini Part with inline data."""
    mime_type = MIME_TYPES[path.suffix.lower()]
    data = path.read_bytes()
    return types.Part.from_bytes(data=data, mime_type=mime_type)


def generate_images(
    client: genai.Client,
    prompt: str,
    model: str = DEFAULT_MODEL,
    input_image: Path | None = None,
    count: int = 1,
    aspect_ratio: str | None = None,
    image_size: str | None = None,
    person_generation: str | None = None,
) -> list[tuple[Image.Image | None, str | None]]:
    """Generate images using the Gemini API.

    Returns a list of (image, text) tuples. Each tuple may have an image, text, or both.
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

    # Build contents: string for text-to-image, list of parts for editing
    contents: str | list[types.Part]
    if input_image is not None:
        contents = [types.Part.from_text(text=prompt), load_image_as_part(input_image)]
    else:
        contents = prompt

    response = client.models.generate_content(
        model=model,
        contents=contents,  # type: ignore[arg-type]
        config=config,
    )

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

    # If there was trailing text with no image
    if text and not img:
        results.append((None, text))

    return results


def save_images(
    results: list[tuple[Image.Image | None, str | None]],
    output_dir: Path,
) -> list[Path]:
    """Save generated images to the output directory. Returns list of saved paths."""
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

    return saved


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate and edit images using the Google Gemini API")
    parser.add_argument("prompt", help="Text prompt for image generation or editing instruction")
    parser.add_argument(
        "--input",
        help="Input image path for editing (omit for text-to-image generation)",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        choices=AVAILABLE_MODELS,
        help=f"Gemini model to use (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--aspect-ratio",
        choices=SUPPORTED_ASPECT_RATIOS,
        help="Aspect ratio for generated image (e.g. 16:9)",
    )
    parser.add_argument(
        "--image-size",
        choices=SUPPORTED_IMAGE_SIZES,
        help="Output resolution: 1K, 2K, 4K (gemini-3-pro-image-preview only)",
    )
    parser.add_argument(
        "--person-generation",
        choices=PERSON_GENERATION_OPTIONS,
        help="Person generation policy (default: model default)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        choices=range(1, 5),
        metavar="N",
        help="Number of images to generate (1-4, default: 1)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    args = parser.parse_args()

    api_key = get_api_key()
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
        print("Get an API key at: https://aistudio.google.com/apikey", file=sys.stderr)
        return 1

    input_path: Path | None = None
    if args.input:
        input_path = Path(args.input)
        error = validate_input_image(input_path)
        if error:
            print(f"Error: {error}", file=sys.stderr)
            return 1

    mode = "edit" if input_path else "generate"
    print(f"Mode: {mode}")
    print(f"Model: {args.model}")
    print(f"Prompt: {args.prompt}")
    if args.aspect_ratio:
        print(f"Aspect ratio: {args.aspect_ratio}")
    if args.image_size:
        print(f"Image size: {args.image_size}")
    if args.person_generation:
        print(f"Person generation: {args.person_generation}")
    if input_path:
        print(f"Input: {input_path}")
    print(f"Count: {args.count}")
    print(f"Output: {args.output}\n")

    client = genai.Client(api_key=api_key)

    try:
        results = generate_images(
            client=client,
            prompt=args.prompt,
            model=args.model,
            input_image=input_path,
            count=args.count,
            aspect_ratio=args.aspect_ratio,
            image_size=args.image_size,
            person_generation=args.person_generation,
        )
    except Exception as e:
        print(f"Error: API call failed: {e}", file=sys.stderr)
        return 1

    output_dir = Path(args.output)
    saved = save_images(results, output_dir)

    image_count = len(saved)
    if image_count == 0:
        print("\nNo images were generated. Try adjusting your prompt.")
        return 1

    print(f"\nDone! {image_count} image(s) generated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
