#!/usr/bin/env python3
"""
Generate motion-controlled videos using the fal.ai Kling Video v2.6 motion control API.
Run with: uv run --project runtime runtime/generate_video.py --image <image> --video <video> [options]

Transfers motion from a reference video onto a character in a reference image.

Requires FAL_KEY environment variable.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from api import build_motion_control_args, generate_video, save_video
from config import (
    DEFAULT_ORIENTATION,
    DEFAULT_OUTPUT_DIR,
    ENDPOINT,
    SUPPORTED_ORIENTATIONS,
    ApiError,
    ConfigError,
    KelingMotionError,
    OutputError,
    UploadError,
    ValidationError,
    get_api_key,
)
from media import resolve_image_url, resolve_video_url

# Maps exception types to human-readable pipeline stage prefixes
_ERROR_PREFIXES: dict[type[KelingMotionError], str] = {
    ConfigError: "Configuration error",
    ValidationError: "Validation error",
    UploadError: "Upload error",
    ApiError: "API error",
    OutputError: "Output error",
}


def _print_summary(
    args: argparse.Namespace,
    image_url: str,
    video_url: str,
) -> None:
    """Print a summary of the generation request."""
    print(f"Endpoint: {ENDPOINT}")
    if args.prompt:
        print(f"Prompt: {args.prompt}")
    print(f"Image: {args.image}")
    print(f"Video: {args.video}")
    print(f"Character orientation: {args.orientation}")
    print(f"Keep original sound: {args.keep_sound}")
    print(f"Output: {args.output}\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate motion-controlled videos using the fal.ai Kling Video v2.6 motion control API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""examples:
  # Basic motion transfer
  %(prog)s --image character.png --video dance.mp4

  # With a descriptive prompt
  %(prog)s "A person dancing gracefully" --image character.png --video dance.mp4

  # Match character orientation to reference video
  %(prog)s --image character.png --video dance.mp4 --orientation video

  # Discard original audio
  %(prog)s --image character.png --video motion.mp4 --no-keep-sound

  # Using URLs
  %(prog)s --image https://example.com/char.png --video https://example.com/dance.mp4

  # Custom output
  %(prog)s --image character.png --video dance.mp4 --filename my_video.mp4 -o output/
""",
    )

    # --- Positional ---
    parser.add_argument("prompt", nargs="?", help="Optional descriptive text prompt")

    # --- Required inputs ---
    parser.add_argument("--image", required=True, help="Reference image (path or URL) — defines character appearance")
    parser.add_argument("--video", required=True, help="Reference video (path or URL) — defines character motion")

    # --- Options ---
    parser.add_argument(
        "--orientation",
        default=DEFAULT_ORIENTATION,
        choices=SUPPORTED_ORIENTATIONS,
        help=f"Character orientation source (default: {DEFAULT_ORIENTATION})",
    )
    parser.add_argument(
        "--keep-sound",
        action="store_true",
        default=True,
        help="Keep original sound from reference video (default: true)",
    )
    parser.add_argument(
        "--no-keep-sound",
        action="store_false",
        dest="keep_sound",
        help="Discard original sound from reference video",
    )
    parser.add_argument("--filename", help="Output filename (default: auto-generated from timestamp)")
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
                "FAL_KEY environment variable is not set.\n  Get an API key at: https://fal.ai/dashboard/keys"
            )

        # Stage 2: Resolve URLs (validates + uploads local files)
        image_url = resolve_image_url(args.image)
        video_url = resolve_video_url(args.video)

        # Stage 3: Print summary
        _print_summary(args, image_url, video_url)

        # Stage 4: Build arguments and call API
        arguments = build_motion_control_args(
            image_url=image_url,
            video_url=video_url,
            character_orientation=args.orientation,
            prompt=args.prompt,
            keep_original_sound=args.keep_sound,
        )
        result = generate_video(ENDPOINT, arguments)

        # Stage 5: Save output
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = args.filename or f"motion_{timestamp}.mp4"
        output_dir = Path(args.output)
        saved = save_video(result, output_dir, filename)
        print(f"\nDone! Video saved to {saved}")
        return 0

    except KelingMotionError as e:
        prefix = _ERROR_PREFIXES.get(type(e), "Error")
        print(f"\n{prefix}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
