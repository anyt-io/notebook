"""Tests for media.py — image validation, loading, and reference building."""

from pathlib import Path

import pytest
from google.genai import types
from PIL import Image

from config import MAX_INPUT_SIZE_MB, ValidationError
from media import build_reference_images, load_image, validate_input_image


def make_test_image(path: Path, size: tuple[int, int] = (10, 10), fmt: str = "PNG") -> Path:
    """Create a small test image file."""
    img = Image.new("RGB", size, color="red")
    img.save(path, format=fmt)
    return path


class TestValidateInputImage:
    def test_valid_png(self, tmp_path: Path):
        img_path = make_test_image(tmp_path / "test.png")
        validate_input_image(img_path)  # should not raise

    def test_valid_jpeg(self, tmp_path: Path):
        img_path = make_test_image(tmp_path / "test.jpg", fmt="JPEG")
        validate_input_image(img_path)  # should not raise

    def test_valid_webp(self, tmp_path: Path):
        img_path = make_test_image(tmp_path / "test.webp", fmt="WEBP")
        validate_input_image(img_path)  # should not raise

    def test_file_not_found(self, tmp_path: Path):
        with pytest.raises(ValidationError, match="not found"):
            validate_input_image(tmp_path / "nonexistent.png")

    def test_not_a_file(self, tmp_path: Path):
        with pytest.raises(ValidationError, match="Not a file"):
            validate_input_image(tmp_path)

    def test_unsupported_extension(self, tmp_path: Path):
        path = tmp_path / "test.bmp"
        path.write_bytes(b"fake")
        with pytest.raises(ValidationError, match="Unsupported format"):
            validate_input_image(path)

    def test_file_too_large(self, tmp_path: Path):
        path = tmp_path / "huge.png"
        path.write_bytes(b"\x00" * (MAX_INPUT_SIZE_MB * 1024 * 1024 + 1))
        with pytest.raises(ValidationError, match="too large"):
            validate_input_image(path)


class TestLoadImage:
    def test_returns_image_with_data(self, tmp_path: Path):
        img_path = make_test_image(tmp_path / "test.png")
        image = load_image(img_path)
        assert image.image_bytes is not None
        assert image.mime_type == "image/png"

    def test_jpeg_mime_type(self, tmp_path: Path):
        img_path = make_test_image(tmp_path / "test.jpg", fmt="JPEG")
        image = load_image(img_path)
        assert image.mime_type == "image/jpeg"


class TestBuildReferenceImages:
    def test_builds_references(self, tmp_path: Path):
        paths = [make_test_image(tmp_path / f"ref{i}.png") for i in range(3)]
        refs = build_reference_images(paths)
        assert len(refs) == 3
        for ref in refs:
            assert ref.reference_type == types.VideoGenerationReferenceType.ASSET
            assert ref.image is not None
            assert ref.image.mime_type == "image/png"

    def test_single_reference(self, tmp_path: Path):
        path = make_test_image(tmp_path / "ref.png")
        refs = build_reference_images([path])
        assert len(refs) == 1
        assert refs[0].reference_type == types.VideoGenerationReferenceType.ASSET

    def test_empty_list(self):
        refs = build_reference_images([])
        assert refs == []
