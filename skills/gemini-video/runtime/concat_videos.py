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

from config import DEFAULT_OUTPUT_DIR, SUPPORTED_VIDEO_EXTENSIONS, ConfigError, GeminiVideoError, ValidationError

_ERROR_PREFIXES: dict[type[GeminiVideoError], str] = {
    ConfigError: "Configuration error",
    ValidationError: "Validation error",
}


def check_ffmpeg() -> None:
    """Check if ffmpeg is available. Raises ConfigError if not."""
    if shutil.which("ffmpeg") is None:
        raise ConfigError("ffmpeg is not installed or not on PATH. Install from https://ffmpeg.org/")


def find_videos_in_directory(directory: Path, pattern: str = "*.mp4") -> list[Path]:
    """Find all matching video files in a directory, sorted by name."""
    if not directory.is_dir():
        return []
    return sorted(directory.glob(pattern))


def validate_video_files(paths: list[Path]) -> None:
    """Validate video file list. Raises ValidationError if any file is invalid."""
    if not paths:
        raise ValidationError("No video files provided.")
    for path in paths:
        if not path.exists():
            raise ValidationError(f"File not found: {path}")
        if not path.is_file():
            raise ValidationError(f"Not a file: {path}")
        if path.suffix.lower() not in SUPPORTED_VIDEO_EXTENSIONS:
            raise ValidationError(
                f"Unsupported format '{path.suffix}': {path} "
                f"(supported: {', '.join(sorted(SUPPORTED_VIDEO_EXTENSIONS))})"
            )


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

    try:
        # Stage 1: Check ffmpeg
        check_ffmpeg()

        # Stage 2: Resolve input files
        if args.dir and args.files:
            raise ConfigError("Use either positional files or --dir, not both.")

        if args.dir:
            video_dir = Path(args.dir)
            if not video_dir.is_dir():
                raise ValidationError(f"Directory not found: {video_dir}")
            video_paths = find_videos_in_directory(video_dir, args.pattern)
            if not video_paths:
                raise ValidationError(f"No files matching '{args.pattern}' in {video_dir}")
        elif args.files:
            video_paths = [Path(f) for f in args.files]
        else:
            raise ConfigError("Provide video files as arguments or use --dir.")

        # Stage 3: Validate
        validate_video_files(video_paths)

        # Stage 4: Print summary and concat
        output_path = Path(args.output)
        print(f"Concatenating {len(video_paths)} video(s):")
        for p in video_paths:
            print(f"  {p}")
        print(f"Output: {output_path}\n")

        exit_code = concat_videos(video_paths, output_path)
        if exit_code == 0:
            print(f"\nDone! Video saved to {output_path}")
        else:
            print("\nError: ffmpeg failed.", file=sys.stderr)
        return exit_code

    except GeminiVideoError as e:
        prefix = _ERROR_PREFIXES.get(type(e), "Error")
        print(f"\n{prefix}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
