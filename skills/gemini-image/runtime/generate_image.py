#!/usr/bin/env python3
"""
Generate and edit images using the Google Gemini API.
Run with: uv run --project runtime runtime/generate_image.py <prompt> [options]

Requires GEMINI_API_KEY environment variable.
"""

import argparse
import sys
from pathlib import Path

from google import genai

from api import generate_images, save_images, validate_input_image
from config import (
    AVAILABLE_MODELS,
    DEFAULT_MODEL,
    DEFAULT_OUTPUT_DIR,
    PERSON_GENERATION_OPTIONS,
    SUPPORTED_ASPECT_RATIOS,
    SUPPORTED_IMAGE_SIZES,
    ApiError,
    ConfigError,
    GeminiImageError,
    OutputError,
    ValidationError,
    get_api_key,
)

_ERROR_PREFIXES: dict[type[GeminiImageError], str] = {
    ConfigError: "Configuration error",
    ValidationError: "Validation error",
    ApiError: "API error",
    OutputError: "Output error",
}


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
        help="Output resolution: 0.5K, 1K, 2K, 4K (Nano Banana 2 and Nano Banana Pro only)",
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

    try:
        # Stage 1: Check configuration
        api_key = get_api_key()
        if not api_key:
            raise ConfigError(
                "GEMINI_API_KEY environment variable is not set.\n"
                "  Get an API key at: https://aistudio.google.com/apikey"
            )

        # Stage 2: Validate input image
        input_path: Path | None = None
        if args.input:
            input_path = Path(args.input)
            validate_input_image(input_path)

        # Stage 3: Print summary
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

        # Stage 4: Generate images
        client = genai.Client(api_key=api_key)
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

        # Stage 5: Save output
        output_dir = Path(args.output)
        saved = save_images(results, output_dir)
        print(f"\nDone! {len(saved)} image(s) generated.")
        return 0

    except GeminiImageError as e:
        prefix = _ERROR_PREFIXES.get(type(e), "Error")
        print(f"\n{prefix}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
