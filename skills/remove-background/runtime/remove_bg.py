#!/usr/bin/env python3
"""
Remove background from images using rembg.
Run with: uv run --project runtime runtime/remove_bg.py <image> [<image> ...]
"""

import argparse
import sys
from pathlib import Path

from PIL import Image
from rembg import new_session, remove
from rembg.sessions import BaseSession

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = SKILL_DIR / "output"

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif"}

AVAILABLE_MODELS = [
    "u2net",
    "u2netp",
    "u2net_human_seg",
    "u2net_cloth_seg",
    "silueta",
    "isnet-general-use",
    "isnet-anime",
    "birefnet-general",
    "birefnet-general-lite",
    "birefnet-portrait",
    "birefnet-dis",
    "birefnet-hrsod",
    "birefnet-cod",
    "birefnet-massive",
    "bria-rmbg",
]


def remove_background(
    input_path: Path,
    output_dir: Path,
    session: BaseSession,
    mask_only: bool = False,
) -> Path:
    """Remove background from a single image and save the result."""
    img = Image.open(input_path)
    result: Image.Image = remove(img, session=session, only_mask=mask_only)  # type: ignore[assignment]

    suffix = "_mask" if mask_only else "_nobg"
    output_path = output_dir / f"{input_path.stem}{suffix}.png"
    result.save(output_path)
    return output_path


def validate_input(path: Path) -> str | None:
    """Return an error message if the input path is invalid, else None."""
    if not path.exists():
        return f"File not found: {path}"
    if not path.is_file():
        return f"Not a file: {path}"
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return f"Unsupported format '{path.suffix}': {path} (supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))})"
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Remove background from images using AI models")
    parser.add_argument("images", nargs="+", help="Input image path(s)")
    parser.add_argument(
        "-o",
        "--output",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "-m",
        "--model",
        default="u2net",
        choices=AVAILABLE_MODELS,
        help="Model to use for background removal (default: u2net)",
    )
    parser.add_argument(
        "--mask-only",
        action="store_true",
        help="Output grayscale mask instead of transparent image",
    )
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Validate all inputs before processing
    input_paths: list[Path] = []
    for img_str in args.images:
        p = Path(img_str)
        error = validate_input(p)
        if error:
            print(f"Error: {error}", file=sys.stderr)
            return 1
        input_paths.append(p)

    print(f"Model: {args.model}")
    print(f"Output: {output_dir}")
    print(f"Mode: {'mask only' if args.mask_only else 'transparent background'}")
    print(f"Images: {len(input_paths)}\n")

    session = new_session(args.model)

    for input_path in input_paths:
        print(f"Processing: {input_path.name} ... ", end="", flush=True)
        try:
            output_path = remove_background(input_path, output_dir, session, mask_only=args.mask_only)
            print(f"-> {output_path}")
        except Exception as e:
            print(f"FAILED: {e}", file=sys.stderr)
            return 1

    print(f"\nDone! {len(input_paths)} image(s) processed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
