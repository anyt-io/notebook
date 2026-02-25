#!/usr/bin/env python3
"""
Generate videos using the Google Gemini Veo 3.1 API.
Run with: uv run --project runtime runtime/generate_video.py <prompt> [options]

Requires GEMINI_API_KEY environment variable.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from google import genai

from api import generate_video, save_video
from config import (
    AVAILABLE_MODELS,
    DEFAULT_MODEL,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_POLL_INTERVAL,
    MAX_REFERENCE_IMAGES,
    PERSON_GENERATION_OPTIONS,
    SUPPORTED_ASPECT_RATIOS,
    SUPPORTED_DURATIONS,
    SUPPORTED_RESOLUTIONS,
    ApiError,
    ConfigError,
    GeminiVideoError,
    OutputError,
    ValidationError,
    get_api_key,
)
from media import validate_input_image

_ERROR_PREFIXES: dict[type[GeminiVideoError], str] = {
    ConfigError: "Configuration error",
    ValidationError: "Validation error",
    ApiError: "API error",
    OutputError: "Output error",
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate videos using the Google Gemini Veo 3.1 API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""examples:
  # Text-to-video
  %(prog)s "A cinematic shot of a lion in the savannah"

  # Image-to-video (first frame)
  %(prog)s "The scene comes to life" --image start.png

  # First + last frame interpolation
  %(prog)s "A flower blooming" --image first.png --last-frame last.png

  # Reference images (up to 3) for character/style consistency
  %(prog)s "A robot walks through a city" --reference robot.png --reference city.png

  # Portrait, 4k, with negative prompt
  %(prog)s "A waterfall" --aspect-ratio 9:16 --resolution 4k --negative-prompt "cartoon"

  # Fast model for quick iteration
  %(prog)s "A cat playing piano" --model veo-3.1-fast-generate-preview
""",
    )
    parser.add_argument("prompt", help="Text prompt for video generation")
    parser.add_argument(
        "--image",
        help="Input image path used as the starting (first) frame",
    )
    parser.add_argument(
        "--last-frame",
        help="Image path used as the ending (last) frame for interpolation. Must be used with --image",
    )
    parser.add_argument(
        "--reference",
        action="append",
        dest="references",
        metavar="IMAGE",
        help="Reference image for character/style consistency (can be repeated up to 3 times)",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        choices=AVAILABLE_MODELS,
        help=f"Veo model to use (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--aspect-ratio",
        choices=SUPPORTED_ASPECT_RATIOS,
        help="Aspect ratio for generated video (default: 16:9)",
    )
    parser.add_argument(
        "--resolution",
        choices=SUPPORTED_RESOLUTIONS,
        help="Video resolution: 720p, 1080p, 4k (default: 720p)",
    )
    parser.add_argument(
        "--duration",
        type=int,
        choices=SUPPORTED_DURATIONS,
        help="Video duration in seconds: 4, 6, or 8 (default: 8)",
    )
    parser.add_argument(
        "--negative-prompt",
        help="Text describing what not to include in the video",
    )
    parser.add_argument(
        "--person-generation",
        choices=PERSON_GENERATION_OPTIONS,
        help="Person generation policy (default: model default)",
    )
    parser.add_argument(
        "--poll-interval",
        type=int,
        default=DEFAULT_POLL_INTERVAL,
        help=f"Seconds between status polls (default: {DEFAULT_POLL_INTERVAL})",
    )
    parser.add_argument(
        "--filename",
        help="Output filename (default: auto-generated from timestamp)",
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

        if args.last_frame and not args.image:
            raise ConfigError("--last-frame requires --image (first frame).")

        # Stage 2: Validate inputs
        ref_paths: list[Path] = []
        if args.references:
            if len(args.references) > MAX_REFERENCE_IMAGES:
                raise ValidationError(f"At most {MAX_REFERENCE_IMAGES} reference images allowed.")
            for ref in args.references:
                p = Path(ref)
                validate_input_image(p)
                ref_paths.append(p)

        input_path: Path | None = None
        if args.image:
            input_path = Path(args.image)
            validate_input_image(input_path)

        last_frame_path: Path | None = None
        if args.last_frame:
            last_frame_path = Path(args.last_frame)
            validate_input_image(last_frame_path)

        # Stage 3: Print summary
        if input_path and last_frame_path:
            mode = "interpolation (first+last frame)"
        elif input_path:
            mode = "image-to-video"
        elif ref_paths:
            mode = "text-to-video with reference images"
        else:
            mode = "text-to-video"

        print(f"Mode: {mode}")
        print(f"Model: {args.model}")
        print(f"Prompt: {args.prompt}")
        if args.aspect_ratio:
            print(f"Aspect ratio: {args.aspect_ratio}")
        if args.resolution:
            print(f"Resolution: {args.resolution}")
        if args.duration:
            print(f"Duration: {args.duration}s")
        if args.negative_prompt:
            print(f"Negative prompt: {args.negative_prompt}")
        if args.person_generation:
            print(f"Person generation: {args.person_generation}")
        if input_path:
            print(f"First frame: {input_path}")
        if last_frame_path:
            print(f"Last frame: {last_frame_path}")
        if ref_paths:
            print(f"Reference images: {', '.join(str(p) for p in ref_paths)}")
        print(f"Output: {args.output}\n")

        # Stage 4: Generate video
        client = genai.Client(api_key=api_key)
        response = generate_video(
            client=client,
            prompt=args.prompt,
            model=args.model,
            input_image=input_path,
            last_frame=last_frame_path,
            reference_images=ref_paths or None,
            aspect_ratio=args.aspect_ratio,
            resolution=args.resolution,
            duration_seconds=args.duration,
            negative_prompt=args.negative_prompt,
            person_generation=args.person_generation,
            poll_interval=args.poll_interval,
        )

        if response is None:
            raise OutputError("No response from API.")

        # Stage 5: Save output
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = args.filename or f"veo_{timestamp}.mp4"
        output_dir = Path(args.output)
        saved = save_video(client, response, output_dir, filename)
        print(f"\nDone! Video saved to {saved}")
        return 0

    except GeminiVideoError as e:
        prefix = _ERROR_PREFIXES.get(type(e), "Error")
        print(f"\n{prefix}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
