#!/usr/bin/env python3
"""
YouTube Cover/Thumbnail Downloader
Downloads the cover (thumbnail) image of a YouTube video.
Run with: uv run --project runtime runtime/download_cover.py <url>
"""

import argparse
import re
import sys
import urllib.request
from pathlib import Path

from download_video import get_video_info

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = SKILL_DIR / "output"


def extract_video_id(url: str) -> str:
    """Extract video ID from a YouTube URL or return as-is if already an ID."""
    patterns = [
        r"(?:v=|/v/|youtu\.be/)([a-zA-Z0-9_-]{11})",
        r"^([a-zA-Z0-9_-]{11})$",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    print(f"Error: could not extract video ID from '{url}'", file=sys.stderr)
    sys.exit(1)


def download_cover(
    url: str,
    output_path: str | Path = DEFAULT_OUTPUT_DIR,
    filename: str | None = None,
) -> bool:
    """
    Download the cover/thumbnail image of a YouTube video.

    Args:
        url: YouTube video URL
        output_path: Directory to save the cover image
        filename: Custom filename (without extension). Defaults to video ID.
    """
    Path(output_path).mkdir(parents=True, exist_ok=True)

    print(f"Fetching cover for: {url}")

    try:
        info = get_video_info(url)
        title = info.get("title", "Unknown")
        thumbnail_url = info.get("thumbnail", "")

        if not thumbnail_url:
            print("Error: no thumbnail URL found in video metadata", file=sys.stderr)
            return False

        print(f"Title: {title}")
        print(f"Thumbnail URL: {thumbnail_url}\n")

        video_id = extract_video_id(url)
        base_name = filename or video_id

        # Determine extension from URL, default to .jpg
        ext = ".jpg"
        if ".png" in thumbnail_url:
            ext = ".png"
        elif ".webp" in thumbnail_url:
            ext = ".webp"

        output_file = Path(output_path) / f"{base_name}{ext}"

        urllib.request.urlretrieve(thumbnail_url, output_file)

        print(f"Saved to: {output_file}")
        return True
    except Exception as e:
        print(f"\nError downloading cover: {e}", file=sys.stderr)
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Download YouTube video cover/thumbnail image")
    parser.add_argument("url", help="YouTube video URL or video ID")
    parser.add_argument(
        "-o",
        "--output",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "-n",
        "--name",
        default=None,
        help="Custom filename without extension (default: video ID)",
    )

    args = parser.parse_args()

    success = download_cover(
        url=args.url,
        output_path=args.output,
        filename=args.name,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
