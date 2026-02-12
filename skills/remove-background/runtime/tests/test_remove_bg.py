"""Tests for remove_bg.py."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from remove_bg import SUPPORTED_EXTENSIONS, remove_background, validate_input


@pytest.fixture
def sample_image(tmp_path: Path) -> Path:
    """Create a small test image."""
    img = Image.new("RGB", (10, 10), color="red")
    path = tmp_path / "test.png"
    img.save(path)
    return path


@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    d = tmp_path / "output"
    d.mkdir()
    return d


class TestValidateInput:
    def test_valid_png(self, sample_image: Path):
        assert validate_input(sample_image) is None

    def test_valid_extensions(self, tmp_path: Path):
        for ext in SUPPORTED_EXTENSIONS:
            img = Image.new("RGB", (1, 1))
            path = tmp_path / f"test{ext}"
            if ext in {".png"}:
                fmt = "PNG"
            elif ext in {".jpg", ".jpeg"}:
                fmt = "JPEG"
            elif ext in {".bmp"}:
                fmt = "BMP"
            elif ext in {".tiff", ".tif"}:
                fmt = "TIFF"
            else:
                fmt = "WEBP"
            img.save(path, format=fmt)
            assert validate_input(path) is None

    def test_file_not_found(self, tmp_path: Path):
        result = validate_input(tmp_path / "nonexistent.png")
        assert result is not None
        assert "not found" in result.lower()

    def test_not_a_file(self, tmp_path: Path):
        result = validate_input(tmp_path)
        assert result is not None
        assert "Not a file" in result

    def test_unsupported_format(self, tmp_path: Path):
        path = tmp_path / "test.txt"
        path.write_text("not an image")
        result = validate_input(path)
        assert result is not None
        assert "Unsupported format" in result


class TestRemoveBackground:
    @patch("remove_bg.remove")
    def test_saves_transparent_output(self, mock_remove: MagicMock, sample_image: Path, output_dir: Path):
        mock_output = Image.new("RGBA", (10, 10))
        mock_remove.return_value = mock_output
        session = MagicMock()

        result = remove_background(sample_image, output_dir, session, mask_only=False)

        assert result == output_dir / "test_nobg.png"
        assert result.exists()
        mock_remove.assert_called_once()
        call_kwargs = mock_remove.call_args
        assert call_kwargs[1]["session"] is session
        assert call_kwargs[1]["only_mask"] is False

    @patch("remove_bg.remove")
    def test_saves_mask_output(self, mock_remove: MagicMock, sample_image: Path, output_dir: Path):
        mock_output = Image.new("L", (10, 10))
        mock_remove.return_value = mock_output
        session = MagicMock()

        result = remove_background(sample_image, output_dir, session, mask_only=True)

        assert result == output_dir / "test_mask.png"
        assert result.exists()
        call_kwargs = mock_remove.call_args
        assert call_kwargs[1]["only_mask"] is True

    @patch("remove_bg.remove")
    def test_output_filename_preserves_stem(self, mock_remove: MagicMock, tmp_path: Path, output_dir: Path):
        img = Image.new("RGB", (10, 10))
        path = tmp_path / "my-photo.jpg"
        img.save(path, format="JPEG")

        mock_remove.return_value = Image.new("RGBA", (10, 10))
        session = MagicMock()

        result = remove_background(path, output_dir, session)
        assert result.name == "my-photo_nobg.png"
