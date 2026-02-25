#!/usr/bin/env python3
"""
Concatenate multiple video files into one using ffmpeg.
Run with: uv run --project runtime runtime/concat_videos.py video1.mp4 video2.mp4 ... [options]

Requires ffmpeg to be installed and available on PATH.
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = SKILL_DIR / "output"

SUPPORTED_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}


def check_ffmpeg() -> str | None:
    """Return an error message if ffmpeg is not available, else None."""
    if shutil.which("ffmpeg") is None:
        return "ffmpeg is not installed or not on PATH. Install from https://ffmpeg.org/"
    return None


def find_videos_in_directory(directory: Path, pattern: str = "*.mp4") -> list[Path]:
    """Find all matching video files in a directory, sorted by name."""
    if not directory.is_dir():
        return []
    return sorted(directory.glob(pattern))


def validate_video_files(paths: list[Path]) -> str | None:
    """Return an error message if any video file is invalid, else None."""
    if not paths:
        return "No video files provided."
    for path in paths:
        if not path.exists():
            return f"File not found: {path}"
        if not path.is_file():
            return f"Not a file: {path}"
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            return f"Unsupported format '{path.suffix}': {path} (supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))})"
    return None


def build_concat_file(video_paths: list[Path], concat_file: Path) -> None:
    """Write the ffmpeg concat demuxer file listing all videos."""
    lines = [f"file '{path.resolve()}'" for path in video_paths]
    concat_file.write_text("\n".join(lines) + "\n")


def concat_videos(video_paths: list[Path], output_path: Path) -> int:
    """Concatenate videos using ffmpeg concat demuxer. Returns ffmpeg exit code."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp_dir:
        concat_file = Path(tmp_dir) / "concat_list.txt"
        build_concat_file(video_paths, concat_file)

        result = subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_file),
                "-c",
                "copy",
                str(output_path),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"ffmpeg error: {result.stderr}", file=sys.stderr)
        return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Concatenate multiple video files into one using ffmpeg",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""examples:
  # Concatenate specific files
  %(prog)s scene_01.mp4 scene_02.mp4 scene_03.mp4

  # Concatenate all mp4 files in a directory
  %(prog)s --dir video/

  # Custom output path
  %(prog)s --dir video/ -o final_video.mp4

  # Custom glob pattern
  %(prog)s --dir video/ --pattern "scene_*.mp4"
""",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Video files to concatenate (in order)",
    )
    parser.add_argument(
        "--dir",
        help="Directory containing video files to concatenate",
    )
    parser.add_argument(
        "--pattern",
        default="*.mp4",
        help="Glob pattern when using --dir (default: *.mp4)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=str(DEFAULT_OUTPUT_DIR / "concat.mp4"),
        help=f"Output file path (default: {DEFAULT_OUTPUT_DIR / 'concat.mp4'})",
    )
    args = parser.parse_args()

    # --- Check ffmpeg ---
    error = check_ffmpeg()
    if error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    # --- Resolve input files ---
    if args.dir and args.files:
        print("Error: Use either positional files or --dir, not both.", file=sys.stderr)
        return 1

    if args.dir:
        video_dir = Path(args.dir)
        if not video_dir.is_dir():
            print(f"Error: Directory not found: {video_dir}", file=sys.stderr)
            return 1
        video_paths = find_videos_in_directory(video_dir, args.pattern)
        if not video_paths:
            print(f"Error: No files matching '{args.pattern}' in {video_dir}", file=sys.stderr)
            return 1
    elif args.files:
        video_paths = [Path(f) for f in args.files]
    else:
        print("Error: Provide video files as arguments or use --dir.", file=sys.stderr)
        return 1

    # --- Validate ---
    error = validate_video_files(video_paths)
    if error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    # --- Print summary ---
    output_path = Path(args.output)
    print(f"Concatenating {len(video_paths)} video(s):")
    for p in video_paths:
        print(f"  {p}")
    print(f"Output: {output_path}\n")

    # --- Concat ---
    exit_code = concat_videos(video_paths, output_path)
    if exit_code == 0:
        print(f"\nDone! Video saved to {output_path}")
    else:
        print("\nError: ffmpeg failed.", file=sys.stderr)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
