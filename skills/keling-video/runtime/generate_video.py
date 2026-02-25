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
import sys
from datetime import datetime
from pathlib import Path

from api import (
    build_edit_video_args,
    build_image_to_video_args,
    build_reference_to_video_args,
    build_text_to_video_args,
    generate_video,
    save_video,
)
from config import (
    DEFAULT_ASPECT_RATIO,
    DEFAULT_DURATION,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_QUALITY,
    MAX_ELEMENT_REFS,
    MAX_ELEMENTS,
    MAX_REF_IMAGES,
    SUPPORTED_ASPECT_RATIOS,
    SUPPORTED_DURATIONS,
    SUPPORTED_QUALITY,
    ApiError,
    ConfigError,
    KelingError,
    OutputError,
    UploadError,
    ValidationError,
    get_api_key,
    get_endpoint,
)
from media import (
    build_element,
    detect_mode,
    parse_elements_json,
    parse_multi_prompt,
    resolve_image_url,
    resolve_video_url,
)

# Maps exception types to human-readable pipeline stage prefixes
_ERROR_PREFIXES: dict[type[KelingError], str] = {
    ConfigError: "Configuration error",
    ValidationError: "Validation error",
    UploadError: "Upload error",
    ApiError: "API error",
    OutputError: "Output error",
}


def _print_summary(
    mode: str,
    args: argparse.Namespace,
    multi_prompt_data: list[dict[str, str]] | None,
    image_url: str | None,
    start_image_url: str | None,
    end_image_url: str | None,
    video_url: str | None,
    elements: list[dict[str, object]] | None,
    ref_image_urls: list[str] | None,
) -> None:
    """Print a summary of the generation request."""
    print(f"Mode: {mode}")
    print(f"Quality: {args.quality}")
    print(f"Endpoint: {get_endpoint(mode, args.quality)}")
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


def _resolve_urls(
    args: argparse.Namespace,
) -> tuple[
    str | None,  # image_url
    str | None,  # end_image_url
    str | None,  # start_image_url
    str | None,  # video_url
    list[str] | None,  # ref_image_urls
    list[dict[str, object]] | None,  # elements
]:
    """Resolve all input URLs from CLI arguments. Validates and uploads local files."""
    image_url = resolve_image_url(args.image) if args.image else None
    end_image_url = resolve_image_url(args.end_image) if args.end_image else None
    start_image_url = resolve_image_url(args.start_image) if args.start_image else None
    video_url = resolve_video_url(args.video) if args.video else None

    # Resolve reference images
    ref_image_urls: list[str] | None = None
    if args.ref_images:
        if len(args.ref_images) > MAX_REF_IMAGES:
            raise ValidationError(f"At most {MAX_REF_IMAGES} reference images allowed.")
        ref_image_urls = [resolve_image_url(r) for r in args.ref_images]

    # Resolve elements
    elements: list[dict[str, object]] | None = None
    if args.elements_json:
        elements = parse_elements_json(args.elements_json)
    elif args.element:
        if len(args.element) > MAX_ELEMENTS:
            raise ValidationError(f"At most {MAX_ELEMENTS} elements allowed.")
        elem_list: list[dict[str, object]] = []
        for i, elem_path in enumerate(args.element):
            frontal_url = resolve_image_url(elem_path)
            is_last = i == len(args.element) - 1
            ref_urls: list[str] | None = None
            elem_video_url: str | None = None
            if is_last and args.element_refs:
                if len(args.element_refs) > MAX_ELEMENT_REFS:
                    raise ValidationError(f"At most {MAX_ELEMENT_REFS} element references allowed.")
                ref_urls = [resolve_image_url(r) for r in args.element_refs]
            if is_last and args.element_video:
                elem_video_url = resolve_video_url(args.element_video)
            elem_list.append(build_element(frontal_url, ref_urls, elem_video_url))
        elements = elem_list

    return image_url, end_image_url, start_image_url, video_url, ref_image_urls, elements


def _build_arguments(
    mode: str,
    args: argparse.Namespace,
    multi_prompt_data: list[dict[str, str]] | None,
    image_url: str | None,
    end_image_url: str | None,
    start_image_url: str | None,
    video_url: str | None,
    ref_image_urls: list[str] | None,
    elements: list[dict[str, object]] | None,
) -> dict[str, object]:
    """Build the API arguments dict based on the detected mode."""
    if mode == "text-to-video":
        return build_text_to_video_args(
            prompt=args.prompt,
            duration=args.duration,
            aspect_ratio=args.aspect_ratio,
            generate_audio=args.audio,
            multi_prompt=multi_prompt_data,
        )
    elif mode == "image-to-video":
        assert image_url is not None
        return build_image_to_video_args(
            image_url=image_url,
            prompt=args.prompt,
            end_image_url=end_image_url,
            duration=args.duration,
            generate_audio=args.audio,
            multi_prompt=multi_prompt_data,
        )
    elif mode == "reference-to-video":
        return build_reference_to_video_args(
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
        return build_edit_video_args(
            prompt=args.prompt,
            video_url=video_url,
            ref_images=ref_image_urls,
            elements=elements,
            keep_audio=args.keep_audio,
        )
    else:
        raise ConfigError(f"Unknown mode: {mode}")


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

    try:
        # Stage 1: Check configuration
        api_key = get_api_key()
        if not api_key:
            raise ConfigError(
                "FAL_KEY environment variable is not set.\n  Get an API key at: https://fal.ai/dashboard/keys"
            )

        # Stage 2: Parse structured inputs
        multi_prompt_data: list[dict[str, str]] | None = None
        if args.multi_prompt:
            multi_prompt_data = parse_multi_prompt(args.multi_prompt)

        mode = detect_mode(args)

        if not args.prompt and not multi_prompt_data:
            raise ConfigError("A prompt is required (positional or via --multi-prompt).")

        # Stage 3: Resolve URLs (validates + uploads local files)
        image_url, end_image_url, start_image_url, video_url, ref_image_urls, elements = _resolve_urls(args)

        # Stage 4: Mode-specific validation
        if mode == "image-to-video" and not image_url:
            raise ValidationError("--image is required for image-to-video mode.")
        if mode == "edit-video" and not video_url:
            raise ValidationError("--video is required for edit-video mode.")
        if args.end_image and mode == "text-to-video":
            raise ValidationError("--end-image requires --image (image-to-video mode).")

        # Stage 5: Print summary
        _print_summary(
            mode,
            args,
            multi_prompt_data,
            image_url,
            start_image_url,
            end_image_url,
            video_url,
            elements,
            ref_image_urls,
        )

        # Stage 6: Build arguments and call API
        endpoint = get_endpoint(mode, args.quality)
        arguments = _build_arguments(
            mode,
            args,
            multi_prompt_data,
            image_url,
            end_image_url,
            start_image_url,
            video_url,
            ref_image_urls,
            elements,
        )
        result = generate_video(endpoint, arguments)

        # Stage 7: Save output
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = args.filename or f"kling_{timestamp}.mp4"
        output_dir = Path(args.output)
        saved = save_video(result, output_dir, filename)
        print(f"\nDone! Video saved to {saved}")
        return 0

    except KelingError as e:
        prefix = _ERROR_PREFIXES.get(type(e), "Error")
        print(f"\n{prefix}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
