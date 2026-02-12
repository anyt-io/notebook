"""Tests for upscale.py."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from upscale import (
    AVAILABLE_MODELS,
    PLATFORM_ASSETS,
    SUPPORTED_EXTENSIONS,
    get_binary_name,
    get_image_dimensions,
    get_platform_key,
    upscale_image,
    validate_input,
)


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
            fmt = "PNG" if ext == ".png" else "WEBP" if ext == ".webp" else "JPEG"
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
        path = tmp_path / "test.bmp"
        path.write_bytes(b"fake")
        result = validate_input(path)
        assert result is not None
        assert "Unsupported format" in result


class TestPlatformDetection:
    def test_platform_key_valid(self):
        key = get_platform_key()
        assert key in PLATFORM_ASSETS

    def test_binary_name_windows(self):
        with patch("upscale.get_platform_key", return_value="windows"):
            assert get_binary_name() == "realesrgan-ncnn-vulkan.exe"

    def test_binary_name_unix(self):
        with patch("upscale.get_platform_key", return_value="linux"):
            assert get_binary_name() == "realesrgan-ncnn-vulkan"
        with patch("upscale.get_platform_key", return_value="darwin"):
            assert get_binary_name() == "realesrgan-ncnn-vulkan"

    def test_all_platforms_have_assets(self):
        for plat in ("darwin", "linux", "windows"):
            assert plat in PLATFORM_ASSETS
            assert PLATFORM_ASSETS[plat].endswith(".zip")

    def test_available_models_not_empty(self):
        assert len(AVAILABLE_MODELS) > 0
        assert "realesr-animevideov3" in AVAILABLE_MODELS


class TestGetImageDimensions:
    def test_returns_dimensions(self, sample_image: Path):
        w, h = get_image_dimensions(sample_image)
        assert w == 10
        assert h == 10


class TestUpscaleImage:
    @patch("upscale.subprocess.run")
    def test_calls_binary_correctly(self, mock_run: MagicMock, sample_image: Path, output_dir: Path):
        # Simulate the binary creating output
        output_path = output_dir / "test_upscaled.png"

        def side_effect(*args, **kwargs):
            Image.new("RGB", (20, 20)).save(output_path)
            return MagicMock(returncode=0, stderr="")

        mock_run.side_effect = side_effect

        result = upscale_image(
            sample_image,
            output_dir,
            Path("/bin/realesrgan-ncnn-vulkan"),
            Path("/models"),
            "realesr-animevideov3",
            2,
        )

        assert result == output_path
        assert result.exists()

        cmd = mock_run.call_args[0][0]
        assert cmd[0] == "/bin/realesrgan-ncnn-vulkan"
        assert "-n" in cmd
        idx = cmd.index("-n")
        assert cmd[idx + 1] == "realesr-animevideov3"
        idx = cmd.index("-s")
        assert cmd[idx + 1] == "2"

    @patch("upscale.subprocess.run")
    def test_raises_on_failure(self, mock_run: MagicMock, sample_image: Path, output_dir: Path):
        mock_run.return_value = MagicMock(returncode=1, stderr="GPU error")

        with pytest.raises(RuntimeError, match="realesrgan-ncnn-vulkan failed"):
            upscale_image(
                sample_image,
                output_dir,
                Path("/bin/realesrgan-ncnn-vulkan"),
                Path("/models"),
                "realesr-animevideov3",
                2,
            )
