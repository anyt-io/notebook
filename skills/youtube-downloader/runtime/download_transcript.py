#!/usr/bin/env python3
"""
YouTube Transcript Downloader
Downloads transcripts/subtitles from YouTube videos.
Run with: uv run --project runtime runtime/download_transcript.py <url>
"""

import argparse
import re
import sys
from pathlib import Path

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter, SRTFormatter, TextFormatter

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = SKILL_DIR / "output"

FORMATTERS = {
    "text": TextFormatter(),
    "json": JSONFormatter(),
    "srt": SRTFormatter(),
}

FORMAT_EXTENSIONS = {
    "text": ".txt",
    "json": ".json",
    "srt": ".srt",
}


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


def download_transcript(
    url: str,
    output_path: Path = DEFAULT_OUTPUT_DIR,
    fmt: str = "text",
    lang: str = "en",
) -> bool:
    video_id = extract_video_id(url)
    Path(output_path).mkdir(parents=True, exist_ok=True)

    print(f"Fetching transcript for: {video_id}")
    print(f"Language: {lang}")
    print(f"Format: {fmt}\n")

    ytt = YouTubeTranscriptApi()

    try:
        transcript = ytt.fetch(video_id, languages=[lang])
    except Exception as e:
        print(f"Error fetching transcript: {e}", file=sys.stderr)

        try:
            transcript_list = ytt.list(video_id)
            available = [t.language_code for t in transcript_list]
            print(f"Available languages: {', '.join(available)}", file=sys.stderr)
        except Exception:
            pass

        return False

    formatter = FORMATTERS[fmt]
    formatted: str = formatter.format_transcript(transcript)  # type: ignore[assignment]

    ext = FORMAT_EXTENSIONS[fmt]
    output_file = Path(output_path) / f"{video_id}{ext}"
    output_file.write_text(formatted, encoding="utf-8")

    print(f"Saved to: {output_file}")
    print(f"Language: {transcript.language} ({transcript.language_code})")

    snippets = transcript.snippets
    if snippets:
        duration = snippets[-1].start + snippets[-1].duration
        print(f"Segments: {len(snippets)}")
        print(f"Duration: {int(duration) // 60}:{int(duration) % 60:02d}")

    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Download YouTube video transcripts")
    parser.add_argument("url", help="YouTube video URL or video ID")
    parser.add_argument(
        "-o",
        "--output",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "-f",
        "--format",
        default="text",
        choices=["text", "json", "srt"],
        help="Output format (default: text)",
    )
    parser.add_argument(
        "-l",
        "--lang",
        default="en",
        help="Language code (default: en)",
    )

    args = parser.parse_args()

    success = download_transcript(
        url=args.url,
        output_path=Path(args.output),
        fmt=args.format,
        lang=args.lang,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
