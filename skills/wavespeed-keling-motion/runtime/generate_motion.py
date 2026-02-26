#!/usr/bin/env python3
"""
Transfer motion from reference videos to animate still images using WaveSpeed AI.
Run with: uv run --project runtime runtime/generate_motion.py --image <image> --video <video>

Requires WAVESPEED_API_KEY environment variable.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from api import (
    build_motion_control_args,
    generate_motion_video,
    save_video,
)
from config import (
    DEFAULT_ORIENTATION,
    DEFAULT_OUTPUT_DIR,
    SUPPORTED_ORIENTATIONS,
    ApiError,
    ConfigError,
    MotionError,
    OutputError,
    ValidationError,
    get_api_key,
)
from media import (
    resolve_image_url,
    resolve_video_url,
)

# Maps exception types to human-readable pipeline stage prefixes
_ERROR_PREFIXES: dict[type[MotionError], str] = {
    ConfigError: "Configuration error",
    ValidationError: "Validation error",
    ApiError: "API error",
    OutputError: "Output error",
}


def _print_summary(
    args: argparse.Namespace,
    image_url: str,
    video_url: str,
) -> None:
    """Print a summary of the generation request."""
    print("Mode: motion-control")
    print(f"Image: {args.image}")
    print(f"Video: {args.video}")
    print(f"Character orientation: {args.orientation}")
    if args.prompt:
        print(f"Prompt: {args.prompt}")
    if args.negative_prompt:
        print(f"Negative prompt: {args.negative_prompt}")
    print(f"Keep audio: {args.keep_audio}")
    print(f"Output: {args.output}\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Transfer motion from reference videos to animate still images using WaveSpeed AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""examples:
  # Basic motion transfer
  %(prog)s --image person.png --video dance.mp4

  # With prompt guidance
  %(prog)s "A person dancing gracefully" --image person.png --video dance.mp4

  # Character orientation from video
  %(prog)s --image face.png --video nod.mp4 --orientation video

  # With negative prompt
  %(prog)s "A robot walking" --image robot.png --video walk.mp4 \\
    --negative-prompt "blurry, distorted"

  # Discard original audio
  %(prog)s --image singer.png --video lip_sync.mp4 --no-keep-audio

  # Custom output
  %(prog)s --image cat.png --video stretch.mp4 --filename cat_stretch.mp4 -o output/
""",
    )

    # --- Positional ---
    parser.add_argument("prompt", nargs="?", help="Text prompt for video generation (optional)")

    # --- Required inputs ---
    parser.add_argument("--image", required=True, help="Still image to animate (path or URL)")
    parser.add_argument("--video", required=True, help="Reference video with motion (path or URL)")

    # --- Options ---
    parser.add_argument(
        "--orientation",
        default=DEFAULT_ORIENTATION,
        choices=SUPPORTED_ORIENTATIONS,
        help=f"Character orientation source (default: {DEFAULT_ORIENTATION})",
    )
    parser.add_argument(
        "--negative-prompt",
        help="Negative prompt to avoid unwanted elements",
    )
    parser.add_argument(
        "--keep-audio",
        action="store_true",
        default=True,
        help="Keep original video audio (default: true)",
    )
    parser.add_argument(
        "--no-keep-audio",
        action="store_false",
        dest="keep_audio",
        help="Discard original video audio",
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
                "WAVESPEED_API_KEY environment variable is not set.\n"
                "  Get an API key at: https://wavespeed.ai\n"
                "  Note: API keys require a top-up to activate."
            )

        # Stage 2: Resolve URLs (validates + converts local files)
        print("Resolving inputs...")
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
            negative_prompt=args.negative_prompt,
            keep_original_sound=args.keep_audio,
        )
        print("Generating motion video...")
        result = generate_motion_video(api_key, arguments)

        # Stage 5: Save output
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = args.filename or f"motion_{timestamp}.mp4"
        output_dir = Path(args.output)
        saved = save_video(result, output_dir, filename)
        print(f"\nDone! Video saved to {saved}")
        return 0

    except MotionError as e:
        prefix = _ERROR_PREFIXES.get(type(e), "Error")
        print(f"\n{prefix}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
