#!/usr/bin/env python3
"""
Generate videos using the fal.ai Kling Video O3 API.
Run with: uv run --project runtime runtime/generate_video.py <prompt> [options]

Supports 4 modes (auto-detected from arguments):
  - text-to-video:       prompt only
  - image-to-video:      prompt + --image
  - reference-to-video:  prompt + --element (Reference I2V / V2V)
  - edit-video:          prompt + --video

Requires FAL_KEY environment variable.
"""

import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

import fal_client

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = SKILL_DIR / "output"

# ---------------------------------------------------------------------------
# Endpoint map: ENDPOINTS[mode][quality]
# ---------------------------------------------------------------------------
ENDPOINTS: dict[str, dict[str, str]] = {
    "text-to-video": {
        "standard": "fal-ai/kling-video/o3/standard/text-to-video",
        "pro": "fal-ai/kling-video/o3/pro/text-to-video",
    },
    "image-to-video": {
        "standard": "fal-ai/kling-video/o3/standard/image-to-video",
        "pro": "fal-ai/kling-video/o3/pro/image-to-video",
    },
    "reference-to-video": {
        "standard": "fal-ai/kling-video/o3/standard/reference-to-video",
        "pro": "fal-ai/kling-video/o3/pro/reference-to-video",
    },
    "edit-video": {
        "standard": "fal-ai/kling-video/o3/standard/video-to-video/edit",
        "pro": "fal-ai/kling-video/o3/pro/video-to-video/edit",
    },
}

SUPPORTED_MODES = list(ENDPOINTS.keys())
SUPPORTED_QUALITY = ["standard", "pro"]
DEFAULT_QUALITY = "standard"

SUPPORTED_ASPECT_RATIOS = ["16:9", "9:16", "1:1"]
DEFAULT_ASPECT_RATIO = "16:9"

SUPPORTED_DURATIONS = [str(d) for d in range(3, 16)]
DEFAULT_DURATION = "5"

SUPPORTED_INPUT_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
MAX_IMAGE_SIZE_MB = 10
MAX_VIDEO_SIZE_MB = 200
SUPPORTED_VIDEO_EXTENSIONS = {".mp4", ".mov"}
MAX_ELEMENTS = 2
MAX_ELEMENT_REFS = 3
MAX_REF_IMAGES = 4


def get_api_key() -> str | None:
    """Return the fal API key from environment, or None if not set."""
    return os.environ.get("FAL_KEY")


def get_endpoint(mode: str, quality: str) -> str:
    """Get the fal endpoint ID for the given mode and quality."""
    return ENDPOINTS[mode][quality]


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------


def validate_input_image(path: Path) -> str | None:
    """Return an error message if the input image is invalid, else None."""
    if not path.exists():
        return f"Input image not found: {path}"
    if not path.is_file():
        return f"Not a file: {path}"
    if path.suffix.lower() not in SUPPORTED_INPUT_EXTENSIONS:
        return (
            f"Unsupported image format '{path.suffix}': {path} "
            f"(supported: {', '.join(sorted(SUPPORTED_INPUT_EXTENSIONS))})"
        )
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > MAX_IMAGE_SIZE_MB:
        return f"Image too large: {size_mb:.1f}MB (max: {MAX_IMAGE_SIZE_MB}MB)"
    return None


def validate_input_video(path: Path) -> str | None:
    """Return an error message if the input video is invalid, else None."""
    if not path.exists():
        return f"Input video not found: {path}"
    if not path.is_file():
        return f"Not a file: {path}"
    if path.suffix.lower() not in SUPPORTED_VIDEO_EXTENSIONS:
        return (
            f"Unsupported video format '{path.suffix}': {path} "
            f"(supported: {', '.join(sorted(SUPPORTED_VIDEO_EXTENSIONS))})"
        )
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > MAX_VIDEO_SIZE_MB:
        return f"Video too large: {size_mb:.1f}MB (max: {MAX_VIDEO_SIZE_MB}MB)"
    return None


def resolve_image_url(image_arg: str) -> str:
    """Resolve an image argument to a URL. Uploads local files, passes URLs through."""
    if image_arg.startswith(("http://", "https://")):
        return image_arg
    path = Path(image_arg)
    error = validate_input_image(path)
    if error:
        raise ValueError(error)
    return fal_client.upload_file(path)  # type: ignore[arg-type]


def resolve_video_url(video_arg: str) -> str:
    """Resolve a video argument to a URL. Uploads local files, passes URLs through."""
    if video_arg.startswith(("http://", "https://")):
        return video_arg
    path = Path(video_arg)
    error = validate_input_video(path)
    if error:
        raise ValueError(error)
    return fal_client.upload_file(path)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Argument builders (one per mode)
# ---------------------------------------------------------------------------


def build_text_to_video_args(
    prompt: str | None = None,
    duration: str | None = None,
    aspect_ratio: str | None = None,
    generate_audio: bool = False,
    multi_prompt: list[dict[str, str]] | None = None,
) -> dict[str, object]:
    """Build arguments for text-to-video endpoint."""
    args: dict[str, object] = {}
    if multi_prompt:
        args["multi_prompt"] = multi_prompt
        args["shot_type"] = "customize"
    elif prompt:
        args["prompt"] = prompt
    if duration:
        args["duration"] = duration
    if aspect_ratio:
        args["aspect_ratio"] = aspect_ratio
    if generate_audio:
        args["generate_audio"] = True
    return args


def build_image_to_video_args(
    image_url: str,
    prompt: str | None = None,
    end_image_url: str | None = None,
    duration: str | None = None,
    generate_audio: bool = False,
    multi_prompt: list[dict[str, str]] | None = None,
) -> dict[str, object]:
    """Build arguments for image-to-video endpoint."""
    args: dict[str, object] = {"image_url": image_url}
    if multi_prompt:
        args["multi_prompt"] = multi_prompt
        args["shot_type"] = "customize"
    elif prompt:
        args["prompt"] = prompt
    if end_image_url:
        args["end_image_url"] = end_image_url
    if duration:
        args["duration"] = duration
    if generate_audio:
        args["generate_audio"] = True
    return args


def build_reference_to_video_args(
    prompt: str | None = None,
    elements: list[dict[str, object]] | None = None,
    ref_images: list[str] | None = None,
    start_image_url: str | None = None,
    end_image_url: str | None = None,
    duration: str | None = None,
    aspect_ratio: str | None = None,
    generate_audio: bool = False,
    multi_prompt: list[dict[str, str]] | None = None,
) -> dict[str, object]:
    """Build arguments for reference-to-video endpoint."""
    args: dict[str, object] = {}
    if multi_prompt:
        args["multi_prompt"] = multi_prompt
        args["shot_type"] = "customize"
    elif prompt:
        args["prompt"] = prompt
    if elements:
        args["elements"] = elements
    if ref_images:
        args["image_urls"] = ref_images
    if start_image_url:
        args["start_image_url"] = start_image_url
    if end_image_url:
        args["end_image_url"] = end_image_url
    if duration:
        args["duration"] = duration
    if aspect_ratio:
        args["aspect_ratio"] = aspect_ratio
    if generate_audio:
        args["generate_audio"] = True
    return args


def build_edit_video_args(
    prompt: str,
    video_url: str,
    ref_images: list[str] | None = None,
    elements: list[dict[str, object]] | None = None,
    keep_audio: bool = True,
) -> dict[str, object]:
    """Build arguments for edit-video endpoint."""
    args: dict[str, object] = {"prompt": prompt, "video_url": video_url}
    if ref_images:
        args["image_urls"] = ref_images
    if elements:
        args["elements"] = elements
    args["keep_audio"] = keep_audio
    return args


# ---------------------------------------------------------------------------
# Generation & saving
# ---------------------------------------------------------------------------


def generate_video(
    endpoint: str,
    arguments: dict[str, object],
) -> dict[str, object]:
    """Submit a video generation request and wait for the result."""

    def on_queue_update(update: object) -> None:
        if isinstance(update, fal_client.Queued):
            print(f"  Queued (position: {update.position})...")
        elif isinstance(update, fal_client.InProgress):
            if update.logs:
                for log in update.logs:
                    print(f"  {log['message']}")
            else:
                print("  In progress...")

    result: dict[str, object] = fal_client.subscribe(
        endpoint,
        arguments=arguments,
        with_logs=True,
        on_queue_update=on_queue_update,
    )
    return result


def save_video(result: dict[str, object], output_dir: Path, filename: str) -> Path | None:
    """Download and save the generated video. Returns the saved path or None."""
    output_dir.mkdir(parents=True, exist_ok=True)

    video = result.get("video")
    if not video or not isinstance(video, dict):
        print("  No video in response.")
        return None

    video_url = video.get("url")
    if not video_url or not isinstance(video_url, str):
        print("  No video URL in response.")
        return None

    out_path = output_dir / filename
    urllib.request.urlretrieve(video_url, str(out_path))
    print(f"  Saved: {out_path}")
    return out_path


# ---------------------------------------------------------------------------
# Multi-prompt & elements parsing
# ---------------------------------------------------------------------------


def parse_multi_prompt(value: str) -> list[dict[str, str]]:
    """Parse multi-prompt from JSON string or file path."""
    if Path(value).is_file():
        with open(value) as f:
            data = json.load(f)
    else:
        data = json.loads(value)

    if not isinstance(data, list):
        raise ValueError("multi-prompt must be a JSON array of objects with 'prompt' and optional 'duration' fields")
    for item in data:
        if not isinstance(item, dict) or "prompt" not in item:
            raise ValueError("Each multi-prompt element must have a 'prompt' field")
    return data


def build_element(
    frontal_url: str,
    ref_urls: list[str] | None = None,
    video_url: str | None = None,
) -> dict[str, object]:
    """Build a single element dict for the reference-to-video or edit-video API."""
    elem: dict[str, object] = {"frontal_image_url": frontal_url}
    if ref_urls:
        elem["reference_image_urls"] = ref_urls
    if video_url:
        elem["video_url"] = video_url
    return elem


def parse_elements_json(value: str) -> list[dict[str, object]]:
    """Parse elements from JSON string or file path."""
    if Path(value).is_file():
        with open(value) as f:
            data = json.load(f)
    else:
        data = json.loads(value)

    if not isinstance(data, list):
        raise ValueError("elements-json must be a JSON array of element objects")
    return data


# ---------------------------------------------------------------------------
# Mode detection
# ---------------------------------------------------------------------------


def detect_mode(args: argparse.Namespace) -> str:
    """Auto-detect the generation mode from CLI arguments."""
    if args.video:
        return "edit-video"
    if args.element or args.elements_json:
        return "reference-to-video"
    if args.image:
        return "image-to-video"
    return "text-to-video"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate videos using the fal.ai Kling Video O3 API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""modes (auto-detected from arguments):
  text-to-video:       prompt only
  image-to-video:      --image <start frame>
  reference-to-video:  --element <frontal image> (Reference I2V / V2V)
  edit-video:          --video <source video>

examples:
  # Text-to-video
  %(prog)s "A cinematic shot of a lion in the savannah"

  # Text-to-video (pro quality)
  %(prog)s "A cinematic shot" --quality pro

  # Image-to-video
  %(prog)s "The scene comes to life" --image start.png

  # Image-to-video with end frame
  %(prog)s "A flower blooming" --image first.png --end-image last.png

  # Reference I2V — element with frontal image
  %(prog)s "@Element1 walks through a city" --element robot.png

  # Reference I2V — element with extra reference angles
  %(prog)s "@Element1 dances" --element char.png --element-ref side.png --element-ref back.png

  # Reference V2V — element with video reference
  %(prog)s "@Element1 runs" --element char.png --element-video motion.mp4

  # Edit video
  %(prog)s "Change background to sunset @Video1" --video input.mp4

  # Edit video with reference images
  %(prog)s "Replace character with @Image1 @Video1" --video input.mp4 --ref-image new_char.png

  # Multi-prompt (inline JSON)
  %(prog)s --multi-prompt '[{"prompt":"Scene 1","duration":"5"},{"prompt":"Scene 2","duration":"5"}]'

  # With audio, portrait, longer duration
  %(prog)s "A waterfall" --audio --aspect-ratio 9:16 --duration 10
""",
    )

    # --- Positional ---
    parser.add_argument("prompt", nargs="?", help="Text prompt for video generation")

    # --- Mode triggers ---
    parser.add_argument("--image", help="Start frame image (path or URL) → image-to-video mode")
    parser.add_argument("--end-image", help="End frame image (path or URL) for interpolation")
    parser.add_argument(
        "--element",
        action="append",
        dest="element",
        metavar="FRONTAL_IMAGE",
        help="Element frontal image (path or URL) → reference-to-video mode (max 2)",
    )
    parser.add_argument(
        "--element-ref",
        action="append",
        dest="element_refs",
        metavar="IMAGE",
        help="Reference angle image for last --element (max 3)",
    )
    parser.add_argument("--element-video", help="Video reference for last --element (V2V reference)")
    parser.add_argument("--video", help="Source video (path or URL) → edit-video mode")

    # --- Shared options ---
    parser.add_argument(
        "--ref-image",
        action="append",
        dest="ref_images",
        metavar="IMAGE",
        help="Style reference image for reference/edit modes (max 4, use @Image1 etc. in prompt)",
    )
    parser.add_argument(
        "--start-image",
        help="Start frame for reference-to-video (path or URL)",
    )
    parser.add_argument(
        "--quality",
        default=DEFAULT_QUALITY,
        choices=SUPPORTED_QUALITY,
        help=f"Quality tier (default: {DEFAULT_QUALITY})",
    )
    parser.add_argument(
        "--aspect-ratio",
        default=DEFAULT_ASPECT_RATIO,
        choices=SUPPORTED_ASPECT_RATIOS,
        help=f"Video aspect ratio (default: {DEFAULT_ASPECT_RATIO})",
    )
    parser.add_argument(
        "--duration",
        default=DEFAULT_DURATION,
        choices=SUPPORTED_DURATIONS,
        help=f"Video duration in seconds (default: {DEFAULT_DURATION})",
    )
    parser.add_argument("--audio", action="store_true", help="Enable native audio generation")
    parser.add_argument(
        "--keep-audio",
        action="store_true",
        default=True,
        help="Keep original audio (edit mode, default: true)",
    )
    parser.add_argument(
        "--no-keep-audio",
        action="store_false",
        dest="keep_audio",
        help="Discard original audio (edit mode)",
    )
    parser.add_argument(
        "--multi-prompt",
        help="JSON array of prompt objects or path to JSON file (overrides positional prompt)",
    )
    parser.add_argument(
        "--elements-json",
        help="JSON array of element objects or path to JSON file (advanced element config)",
    )
    parser.add_argument("--filename", help="Output filename (default: auto-generated from timestamp)")
    parser.add_argument(
        "-o",
        "--output",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    args = parser.parse_args()

    # -----------------------------------------------------------------------
    # Validation
    # -----------------------------------------------------------------------
    api_key = get_api_key()
    if not api_key:
        print("Error: FAL_KEY environment variable is not set.", file=sys.stderr)
        print("Get an API key at: https://fal.ai/dashboard/keys", file=sys.stderr)
        return 1

    # Parse multi-prompt
    multi_prompt_data: list[dict[str, str]] | None = None
    if args.multi_prompt:
        try:
            multi_prompt_data = parse_multi_prompt(args.multi_prompt)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error: Invalid multi-prompt: {e}", file=sys.stderr)
            return 1

    # Detect mode
    mode = detect_mode(args)

    # Require prompt (or multi_prompt) for all modes
    if not args.prompt and not multi_prompt_data:
        print("Error: A prompt is required (positional or via --multi-prompt).", file=sys.stderr)
        return 1

    # -----------------------------------------------------------------------
    # Resolve URLs based on mode
    # -----------------------------------------------------------------------
    try:
        image_url: str | None = resolve_image_url(args.image) if args.image else None
        end_image_url: str | None = resolve_image_url(args.end_image) if args.end_image else None
        start_image_url: str | None = resolve_image_url(args.start_image) if args.start_image else None
        video_url: str | None = resolve_video_url(args.video) if args.video else None

        # Resolve reference images
        ref_image_urls: list[str] | None = None
        if args.ref_images:
            if len(args.ref_images) > MAX_REF_IMAGES:
                print(f"Error: At most {MAX_REF_IMAGES} reference images allowed.", file=sys.stderr)
                return 1
            ref_image_urls = [resolve_image_url(r) for r in args.ref_images]

        # Resolve elements
        elements: list[dict[str, object]] | None = None
        if args.elements_json:
            elements = parse_elements_json(args.elements_json)
        elif args.element:
            if len(args.element) > MAX_ELEMENTS:
                print(f"Error: At most {MAX_ELEMENTS} elements allowed.", file=sys.stderr)
                return 1
            elem_list: list[dict[str, object]] = []
            for i, elem_path in enumerate(args.element):
                frontal_url = resolve_image_url(elem_path)
                # Attach refs and video to the last element
                is_last = i == len(args.element) - 1
                ref_urls: list[str] | None = None
                elem_video_url: str | None = None
                if is_last and args.element_refs:
                    if len(args.element_refs) > MAX_ELEMENT_REFS:
                        print(f"Error: At most {MAX_ELEMENT_REFS} element references allowed.", file=sys.stderr)
                        return 1
                    ref_urls = [resolve_image_url(r) for r in args.element_refs]
                if is_last and args.element_video:
                    elem_video_url = resolve_video_url(args.element_video)
                elem_list.append(build_element(frontal_url, ref_urls, elem_video_url))
            elements = elem_list

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Mode-specific validation
    if mode == "image-to-video" and not image_url:
        print("Error: --image is required for image-to-video mode.", file=sys.stderr)
        return 1
    if mode == "edit-video" and not video_url:
        print("Error: --video is required for edit-video mode.", file=sys.stderr)
        return 1
    if args.end_image and mode == "text-to-video":
        print("Error: --end-image requires --image (image-to-video mode).", file=sys.stderr)
        return 1

    endpoint = get_endpoint(mode, args.quality)

    # -----------------------------------------------------------------------
    # Print summary
    # -----------------------------------------------------------------------
    print(f"Mode: {mode}")
    print(f"Quality: {args.quality}")
    print(f"Endpoint: {endpoint}")
    if args.prompt:
        print(f"Prompt: {args.prompt}")
    if multi_prompt_data:
        print(f"Multi-prompt: {len(multi_prompt_data)} shots")
    print(f"Aspect ratio: {args.aspect_ratio}")
    print(f"Duration: {args.duration}s")
    if args.audio:
        print("Audio: enabled")
    if image_url:
        print(f"Image: {args.image}")
    if start_image_url:
        print(f"Start image: {args.start_image}")
    if end_image_url:
        print(f"End image: {args.end_image}")
    if video_url:
        print(f"Video: {args.video}")
    if elements:
        print(f"Elements: {len(elements)}")
    if ref_image_urls:
        print(f"Reference images: {len(ref_image_urls)}")
    print(f"Output: {args.output}\n")

    # -----------------------------------------------------------------------
    # Build arguments and generate
    # -----------------------------------------------------------------------
    if mode == "text-to-video":
        arguments = build_text_to_video_args(
            prompt=args.prompt,
            duration=args.duration,
            aspect_ratio=args.aspect_ratio,
            generate_audio=args.audio,
            multi_prompt=multi_prompt_data,
        )
    elif mode == "image-to-video":
        assert image_url is not None
        arguments = build_image_to_video_args(
            image_url=image_url,
            prompt=args.prompt,
            end_image_url=end_image_url,
            duration=args.duration,
            generate_audio=args.audio,
            multi_prompt=multi_prompt_data,
        )
    elif mode == "reference-to-video":
        arguments = build_reference_to_video_args(
            prompt=args.prompt,
            elements=elements,
            ref_images=ref_image_urls,
            start_image_url=start_image_url,
            end_image_url=end_image_url,
            duration=args.duration,
            aspect_ratio=args.aspect_ratio,
            generate_audio=args.audio,
            multi_prompt=multi_prompt_data,
        )
    elif mode == "edit-video":
        assert video_url is not None
        assert args.prompt is not None
        arguments = build_edit_video_args(
            prompt=args.prompt,
            video_url=video_url,
            ref_images=ref_image_urls,
            elements=elements,
            keep_audio=args.keep_audio,
        )
    else:
        print(f"Error: Unknown mode: {mode}", file=sys.stderr)
        return 1

    try:
        result = generate_video(endpoint, arguments)
    except Exception as e:
        print(f"Error: API call failed: {e}", file=sys.stderr)
        return 1

    # -----------------------------------------------------------------------
    # Save output
    # -----------------------------------------------------------------------
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = args.filename or f"kling_{timestamp}.mp4"
    output_dir = Path(args.output)

    saved = save_video(result, output_dir, filename)
    if saved is None:
        print("\nNo video was generated. Try adjusting your prompt.")
        return 1

    print(f"\nDone! Video saved to {saved}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
