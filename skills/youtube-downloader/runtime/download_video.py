#!/usr/bin/env python3
"""
YouTube Video Downloader
Downloads videos from YouTube with customizable quality and format options.
Run with: uv run --project runtime runtime/download_video.py <url>
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = SKILL_DIR / "output"


def get_video_info(url: str) -> dict:
    """Get information about the video without downloading."""
    result = subprocess.run(
        ["yt-dlp", "--dump-json", "--no-playlist", url],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def download_video(
    url: str,
    output_path: str | Path = DEFAULT_OUTPUT_DIR,
    quality: str = "best",
    format_type: str = "mp4",
    audio_only: bool = False,
) -> bool:
    """
    Download a YouTube video.

    Args:
        url: YouTube video URL
        output_path: Directory to save the video
        quality: Quality setting (best, 1080p, 720p, 480p, 360p, worst)
        format_type: Output format (mp4, webm, mkv)
        audio_only: Download only audio (mp3)
    """
    Path(output_path).mkdir(parents=True, exist_ok=True)
    cmd = ["yt-dlp"]

    if audio_only:
        cmd.extend(
            [
                "-x",
                "--audio-format",
                "mp3",
                "--audio-quality",
                "0",
            ]
        )
    else:
        if quality == "best":
            format_string = "bestvideo+bestaudio/best"
        elif quality == "worst":
            format_string = "worstvideo+worstaudio/worst"
        else:
            height = quality.replace("p", "")
            format_string = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"

        cmd.extend(
            [
                "-f",
                format_string,
                "--merge-output-format",
                format_type,
            ]
        )

    cmd.extend(
        [
            "-o",
            f"{output_path}/%(title)s.%(ext)s",
            "--no-playlist",
        ]
    )

    cmd.append(url)

    print(f"Downloading from: {url}")
    print(f"Quality: {quality}")
    print(f"Format: {'mp3 (audio only)' if audio_only else format_type}")
    print(f"Output: {output_path}\n")

    try:
        info = get_video_info(url)
        print(f"Title: {info.get('title', 'Unknown')}")
        duration = info.get("duration", 0) or 0
        print(f"Duration: {int(duration) // 60}:{int(duration) % 60:02d}")
        print(f"Uploader: {info.get('uploader', 'Unknown')}\n")

        subprocess.run(cmd, check=True)
        print("\nDownload complete!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nError downloading video: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Download YouTube videos with customizable quality and format")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument(
        "-o",
        "--output",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "-q",
        "--quality",
        default="best",
        choices=["best", "1080p", "720p", "480p", "360p", "worst"],
        help="Video quality (default: best)",
    )
    parser.add_argument(
        "-f",
        "--format",
        default="mp4",
        choices=["mp4", "webm", "mkv"],
        help="Video format (default: mp4)",
    )
    parser.add_argument(
        "-a",
        "--audio-only",
        action="store_true",
        help="Download only audio as MP3",
    )

    args = parser.parse_args()

    success = download_video(
        url=args.url,
        output_path=args.output,
        quality=args.quality,
        format_type=args.format,
        audio_only=args.audio_only,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
