"""Shared test helpers for keling-video tests."""

from pathlib import Path


def make_test_image(path: Path, size_bytes: int = 100) -> Path:
    """Create a small fake image file."""
    path.write_bytes(b"\x89PNG" + b"\x00" * max(0, size_bytes - 4))
    return path


def make_test_video(path: Path, size_bytes: int = 100) -> Path:
    """Create a small fake video file."""
    path.write_bytes(b"\x00\x00\x00\x1cftyp" + b"\x00" * max(0, size_bytes - 8))
    return path
