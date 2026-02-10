#!/usr/bin/env python3
"""
YouTube Video Screenshot Capture
Extracts frame images from YouTube videos at specific timestamps without downloading the full video.
Uses yt-dlp to get the direct stream URL and ffmpeg to seek and capture individual frames.
Run with: uv run --project runtime runtime/screenshot_video.py <url> -t <seconds> [...]
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = SKILL_DIR / "output"


def get_stream_url(url: str) -> str:
    """Get the direct video stream URL using yt-dlp without downloading."""
    result = subprocess.run(
        ["yt-dlp", "-f", "bestvideo[ext=mp4]/bestvideo/best", "-g", "--no-playlist", url],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip().split("\n")[0]


def get_video_info(url: str) -> dict:
    """Get information about the video without downloading."""
    result = subprocess.run(
        ["yt-dlp", "--dump-json", "--no-playlist", url],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def format_timestamp(seconds: float) -> str:
    """Format seconds as H:MM:SS or M:SS."""
    total = int(seconds)
    h, remainder = divmod(total, 3600)
    m, s = divmod(remainder, 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def capture_screenshot(
    stream_url: str,
    timestamp: float,
    output_file: Path,
    quality: int = 2,
) -> bool:
    """
    Capture a single frame from the video stream at the given timestamp.

    Args:
        stream_url: Direct video stream URL from yt-dlp
        timestamp: Time in seconds to capture the frame
        output_file: Path to save the screenshot
        quality: JPEG quality (1=best, 31=worst, default 2)
    """
    cmd = [
        "ffmpeg",
        "-ss",
        str(timestamp),
        "-i",
        stream_url,
        "-frames:v",
        "1",
        "-q:v",
        str(quality),
        "-y",
        str(output_file),
    ]

    try:
        subprocess.run(cmd, capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def screenshot_video(
    url: str,
    timestamps: list[float],
    output_path: str | Path = DEFAULT_OUTPUT_DIR,
    prefix: str = "frame",
    quality: int = 2,
) -> list[dict]:
    """
    Capture screenshots from a YouTube video at specified timestamps.

    Args:
        url: YouTube video URL
        timestamps: List of timestamps in seconds to capture
        output_path: Directory to save screenshots
        prefix: Filename prefix for screenshots
        quality: JPEG quality (1=best, 31=worst)

    Returns:
        List of result dicts with timestamp, file, and success status
    """
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Video URL: {url}")
    print(f"Timestamps: {len(timestamps)} frames to capture")
    print(f"Output: {output_dir}\n")

    try:
        info = get_video_info(url)
        print(f"Title: {info.get('title', 'Unknown')}")
        duration = info.get("duration", 0) or 0
        print(f"Duration: {format_timestamp(duration)}")
        print(f"Uploader: {info.get('uploader', 'Unknown')}\n")
    except subprocess.CalledProcessError as e:
        print(f"Error getting video info: {e}", file=sys.stderr)
        return []

    print("Getting stream URL...")
    try:
        stream_url = get_stream_url(url)
        print("Stream URL obtained.\n")
    except subprocess.CalledProcessError as e:
        print(f"Error getting stream URL: {e}", file=sys.stderr)
        return []

    results: list[dict] = []
    for i, ts in enumerate(timestamps, 1):
        filename = f"{prefix}_{i:03d}.jpg"
        output_file = output_dir / filename
        print(f"[{i}/{len(timestamps)}] Capturing frame at {format_timestamp(ts)}...")

        success = capture_screenshot(stream_url, ts, output_file, quality)
        result = {
            "timestamp": ts,
            "formatted_time": format_timestamp(ts),
            "file": filename,
            "path": str(output_file),
            "success": success,
        }
        results.append(result)

        if success:
            print(f"  Saved: {filename}")
        else:
            print(f"  FAILED: {filename}", file=sys.stderr)

    succeeded = sum(1 for r in results if r["success"])
    print(f"\nDone: {succeeded}/{len(timestamps)} frames captured.")

    manifest_path = output_dir / "manifest.json"
    manifest = {
        "video_url": url,
        "video_title": info.get("title", "Unknown"),
        "frames": results,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Manifest: {manifest_path}")

    return results


def parse_timestamps(value: str) -> list[float]:
    """Parse a comma-separated list of timestamps (seconds or M:SS or H:MM:SS)."""
    timestamps: list[float] = []
    for part in value.split(","):
        part = part.strip()
        if ":" in part:
            segments = part.split(":")
            if len(segments) == 2:
                m, s = segments
                timestamps.append(int(m) * 60 + float(s))
            elif len(segments) == 3:
                h, m, s = segments
                timestamps.append(int(h) * 3600 + int(m) * 60 + float(s))
        else:
            timestamps.append(float(part))
    return timestamps


def main():
    parser = argparse.ArgumentParser(
        description="Capture screenshots from YouTube videos at specific timestamps without downloading"
    )
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument(
        "-t",
        "--timestamps",
        required=True,
        help="Comma-separated timestamps in seconds or M:SS or H:MM:SS (e.g., '30,1:15,2:00')",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "-p",
        "--prefix",
        default="frame",
        help="Filename prefix for screenshots (default: frame)",
    )
    parser.add_argument(
        "-q",
        "--quality",
        type=int,
        default=2,
        choices=range(1, 32),
        metavar="1-31",
        help="JPEG quality: 1=best, 31=worst (default: 2)",
    )

    args = parser.parse_args()
    timestamps = parse_timestamps(args.timestamps)

    if not timestamps:
        print("Error: no valid timestamps provided", file=sys.stderr)
        sys.exit(1)

    results = screenshot_video(
        url=args.url,
        timestamps=timestamps,
        output_path=args.output,
        prefix=args.prefix,
        quality=args.quality,
    )

    failed = sum(1 for r in results if not r["success"])
    sys.exit(1 if failed == len(results) else 0)


if __name__ == "__main__":
    main()
