#!/usr/bin/env python3
"""
Convert markdown files to EPUB and PDF ebooks using pandoc.
Run with: uv run --project runtime runtime/convert_ebook.py <markdown> [<markdown> ...]
"""

import argparse
import re
import sys
from pathlib import Path

import pypandoc

from config import (
    DEFAULT_OUTPUT_DIR,
    IMAGE_EXTENSIONS,
    OUTPUT_FORMATS,
    SUPPORTED_EXTENSIONS,
    ConversionError,
    EbookError,
    ValidationError,
)

_ERROR_PREFIXES: dict[type[EbookError], str] = {
    ValidationError: "Validation error",
    ConversionError: "Conversion error",
}


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_input(path: Path) -> None:
    """Validate input markdown file. Raises ValidationError if invalid."""
    if not path.exists():
        raise ValidationError(f"File not found: {path}")
    if not path.is_file():
        raise ValidationError(f"Not a file: {path}")
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValidationError(
            f"Unsupported format '{path.suffix}': {path} (supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))})"
        )


def validate_cover_image(path: Path) -> None:
    """Validate cover image file. Raises ValidationError if invalid."""
    if not path.exists():
        raise ValidationError(f"Cover image not found: {path}")
    if not path.is_file():
        raise ValidationError(f"Cover image is not a file: {path}")
    if path.suffix.lower() not in IMAGE_EXTENSIONS:
        raise ValidationError(
            f"Unsupported cover image format '{path.suffix}': {path} (supported: {', '.join(sorted(IMAGE_EXTENSIONS))})"
        )


def validate_css_file(path: Path) -> None:
    """Validate CSS stylesheet file. Raises ValidationError if invalid."""
    if not path.exists():
        raise ValidationError(f"CSS file not found: {path}")
    if not path.is_file():
        raise ValidationError(f"CSS path is not a file: {path}")
    if path.suffix.lower() != ".css":
        raise ValidationError(f"Not a CSS file: {path}")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def resolve_resource_path(input_files: list[Path]) -> str:
    """Build a pandoc --resource-path value from input file directories."""
    seen: set[str] = set()
    dirs: list[str] = []
    for f in input_files:
        d = str(f.resolve().parent)
        if d not in seen:
            seen.add(d)
            dirs.append(d)
    return ":".join(dirs)


def _build_extra_args(
    title: str | None,
    author: str | None,
    cover: Path | None,
    css: Path | None,
    resource_path: str,
    output_format: str,
) -> list[str]:
    """Construct pandoc extra arguments for the given format and options."""
    args: list[str] = []

    if title:
        args.extend(["--metadata", f"title={title}"])
    if author:
        args.extend(["--metadata", f"author={author}"])
    if cover:
        args.extend(["--epub-cover-image", str(cover)])
    if css:
        args.extend(["--css", str(css)])

    args.extend(["--resource-path", resource_path])

    if output_format == "pdf":
        args.extend(["--pdf-engine=weasyprint", "-t", "html"])

    return args


def _output_filename(input_files: list[Path], title: str | None, ext: str) -> str:
    """Determine the output filename."""
    if len(input_files) == 1:
        return f"{input_files[0].stem}.{ext}"
    if title:
        slug = re.sub(r"[^\w\s-]", "", title.lower())
        slug = re.sub(r"[\s_]+", "-", slug).strip("-")
        return f"{slug}.{ext}"
    return f"ebook.{ext}"


# ---------------------------------------------------------------------------
# Core conversion
# ---------------------------------------------------------------------------


def convert_ebook(
    input_files: list[Path],
    output_format: str,
    output_dir: Path,
    title: str | None = None,
    author: str | None = None,
    cover: Path | None = None,
    css: Path | None = None,
) -> list[Path]:
    """Convert markdown files to ebook format(s).

    Returns list of output paths. Raises ConversionError on failure.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    resource_path = resolve_resource_path(input_files)

    formats = ["epub", "pdf"] if output_format == "both" else [output_format]
    source_files = [str(f) for f in input_files]
    results: list[Path] = []

    for fmt in formats:
        filename = _output_filename(input_files, title, fmt)
        output_path = output_dir / filename
        extra_args = _build_extra_args(title, author, cover, css, resource_path, fmt)

        try:
            pypandoc.convert_file(
                source_files,
                fmt if fmt == "pdf" else "epub3",
                outputfile=str(output_path),
                extra_args=extra_args,
            )
        except Exception as e:
            raise ConversionError(f"Pandoc conversion to {fmt} failed: {e}") from e

        results.append(output_path)

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert markdown files to EPUB and PDF ebooks")
    parser.add_argument("markdown", nargs="+", help="Input markdown file(s)")
    parser.add_argument(
        "-f",
        "--format",
        default="epub",
        choices=OUTPUT_FORMATS,
        help="Output format (default: epub)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument("-t", "--title", help="Book title metadata")
    parser.add_argument("-a", "--author", help="Book author metadata")
    parser.add_argument("--cover", help="Cover image path (EPUB only)")
    parser.add_argument("--css", help="Custom CSS stylesheet path")
    args = parser.parse_args()

    try:
        # Stage 1: Validate all inputs
        input_paths: list[Path] = []
        for md_str in args.markdown:
            p = Path(md_str)
            validate_input(p)
            input_paths.append(p)

        cover_path: Path | None = None
        if args.cover:
            cover_path = Path(args.cover)
            validate_cover_image(cover_path)

        css_path: Path | None = None
        if args.css:
            css_path = Path(args.css)
            validate_css_file(css_path)

        # Stage 2: Print summary
        output_dir = Path(args.output)
        print(f"Format: {args.format}")
        print(f"Output: {output_dir}")
        print(f"Files: {len(input_paths)}\n")

        # Stage 3: Convert
        results = convert_ebook(
            input_files=input_paths,
            output_format=args.format,
            output_dir=output_dir,
            title=args.title,
            author=args.author,
            cover=cover_path,
            css=css_path,
        )
        for path in results:
            print(f"Created: {path}")

        print(f"\nDone! {len(input_paths)} file(s) converted.")
        return 0

    except EbookError as e:
        prefix = _ERROR_PREFIXES.get(type(e), "Error")
        print(f"\n{prefix}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
