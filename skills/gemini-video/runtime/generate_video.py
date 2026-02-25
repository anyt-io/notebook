#!/usr/bin/env python3
"""
Generate videos using the Google Gemini Veo 3.1 API.
Run with: uv run --project runtime runtime/generate_video.py <prompt> [options]

Requires GEMINI_API_KEY environment variable.
"""

import argparse
import os
import sys
import time
from pathlib import Path

from google import genai
from google.genai import types

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = SKILL_DIR / "output"

DEFAULT_MODEL = "veo-3.1-generate-preview"

AVAILABLE_MODELS = [
    "veo-3.1-generate-preview",
    "veo-3.1-fast-generate-preview",
]

SUPPORTED_ASPECT_RATIOS = ["16:9", "9:16"]

SUPPORTED_RESOLUTIONS = ["720p", "1080p", "4k"]

SUPPORTED_DURATIONS = [4, 6, 8]

PERSON_GENERATION_OPTIONS = ["allow_all", "allow_adult", "dont_allow"]

MAX_REFERENCE_IMAGES = 3

SUPPORTED_INPUT_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
MAX_INPUT_SIZE_MB = 20

MIME_TYPES: dict[str, str] = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
}

DEFAULT_POLL_INTERVAL = 10


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


def generate_video(
    client: genai.Client,
    prompt: str,
    model: str = DEFAULT_MODEL,
    input_image: Path | None = None,
    last_frame: Path | None = None,
    reference_images: list[Path] | None = None,
    aspect_ratio: str | None = None,
    resolution: str | None = None,
    duration_seconds: int | None = None,
    negative_prompt: str | None = None,
    person_generation: str | None = None,
    poll_interval: int = DEFAULT_POLL_INTERVAL,
) -> types.GenerateVideosResponse:
    """Generate a video using the Gemini Veo 3.1 API. Polls until complete."""
    config_kwargs: dict[str, object] = {}
    if aspect_ratio:
        config_kwargs["aspect_ratio"] = aspect_ratio
    if resolution:
        config_kwargs["resolution"] = resolution
    if duration_seconds:
        config_kwargs["duration_seconds"] = duration_seconds
    if negative_prompt:
        config_kwargs["negative_prompt"] = negative_prompt
    if person_generation:
        config_kwargs["person_generation"] = person_generation
    if last_frame:
        config_kwargs["last_frame"] = load_image(last_frame)
    if reference_images:
        config_kwargs["reference_images"] = build_reference_images(reference_images)

    config = types.GenerateVideosConfig(**config_kwargs) if config_kwargs else None  # type: ignore[arg-type]

    image = load_image(input_image) if input_image else None

    operation = client.models.generate_videos(
        model=model,
        prompt=prompt,
        image=image,
        config=config,
    )

    while not operation.done:
        print(f"  Waiting for video generation to complete (polling every {poll_interval}s)...")
        time.sleep(poll_interval)
        operation = client.operations.get(operation)

    return operation.response  # type: ignore[return-value]


def save_video(
    client: genai.Client,
    response: types.GenerateVideosResponse,
    output_dir: Path,
    filename: str,
) -> Path | None:
    """Download and save the first generated video. Returns the saved path or None."""
    output_dir.mkdir(parents=True, exist_ok=True)

    if not response.generated_videos:
        print("  No videos were generated.")
        return None

    generated_video = response.generated_videos[0]
    video_file = generated_video.video  # type: ignore[union-attr]

    if video_file is None:
        print("  Video object is empty.")
        return None

    client.files.download(file=video_file)
    out_path = output_dir / filename
    video_file.save(str(out_path))
    print(f"  Saved: {out_path}")
    return out_path


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

    # --- Validation ---
    api_key = get_api_key()
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
        print("Get an API key at: https://aistudio.google.com/apikey", file=sys.stderr)
        return 1

    if args.last_frame and not args.image:
        print("Error: --last-frame requires --image (first frame).", file=sys.stderr)
        return 1

    ref_paths: list[Path] = []
    if args.references:
        if len(args.references) > MAX_REFERENCE_IMAGES:
            print(f"Error: At most {MAX_REFERENCE_IMAGES} reference images allowed.", file=sys.stderr)
            return 1
        for ref in args.references:
            p = Path(ref)
            error = validate_input_image(p)
            if error:
                print(f"Error (reference): {error}", file=sys.stderr)
                return 1
            ref_paths.append(p)

    input_path: Path | None = None
    if args.image:
        input_path = Path(args.image)
        error = validate_input_image(input_path)
        if error:
            print(f"Error: {error}", file=sys.stderr)
            return 1

    last_frame_path: Path | None = None
    if args.last_frame:
        last_frame_path = Path(args.last_frame)
        error = validate_input_image(last_frame_path)
        if error:
            print(f"Error (last-frame): {error}", file=sys.stderr)
            return 1

    # --- Print summary ---
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

    # --- Generate ---
    client = genai.Client(api_key=api_key)

    try:
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
    except Exception as e:
        print(f"Error: API call failed: {e}", file=sys.stderr)
        return 1

    if response is None:
        print("\nError: No response from API.", file=sys.stderr)
        return 1

    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = args.filename or f"veo_{timestamp}.mp4"

    output_dir = Path(args.output)
    saved = save_video(client, response, output_dir, filename)

    if saved is None:
        print("\nNo video was generated. Try adjusting your prompt.")
        return 1

    print(f"\nDone! Video saved to {saved}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
