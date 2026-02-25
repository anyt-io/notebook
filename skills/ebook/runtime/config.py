"""Configuration constants and exception hierarchy for the ebook skill."""

from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = SKILL_DIR / "output"

SUPPORTED_EXTENSIONS = {".md", ".markdown"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp", ".tiff", ".tif"}
OUTPUT_FORMATS = ["epub", "pdf", "both"]


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------


class EbookError(Exception):
    """Base exception for ebook skill errors."""


class ValidationError(EbookError):
    """Input validation errors (bad file, unsupported format)."""


class ConversionError(EbookError):
    """Conversion failures (pandoc errors)."""
