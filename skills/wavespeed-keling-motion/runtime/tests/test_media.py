"""Tests for media.py — validation and URL resolution."""

import base64
from pathlib import Path

import pytest

from config import MAX_IMAGE_SIZE_MB, MAX_VIDEO_SIZE_MB, ValidationError
from media import (
    file_to_data_url,
    resolve_image_url,
    resolve_video_url,
    validate_input_image,
    validate_input_video,
)
from tests.helpers import make_test_image, make_test_video

# ---------------------------------------------------------------------------
# Image validation
# ---------------------------------------------------------------------------


class TestValidateInputImage:
    def test_valid_png(self, tmp_path: Path):
        img = make_test_image(tmp_path / "test.png")
        validate_input_image(img)  # should not raise

    def test_valid_jpg(self, tmp_path: Path):
        img = make_test_image(tmp_path / "test.jpg")
        validate_input_image(img)  # should not raise

    def test_valid_jpeg(self, tmp_path: Path):
        img = make_test_image(tmp_path / "test.jpeg")
        validate_input_image(img)  # should not raise

    def test_file_not_found(self, tmp_path: Path):
        with pytest.raises(ValidationError, match="not found"):
            validate_input_image(tmp_path / "nonexistent.png")

    def test_not_a_file(self, tmp_path: Path):
        with pytest.raises(ValidationError, match="Not a file"):
            validate_input_image(tmp_path)

    def test_unsupported_extension(self, tmp_path: Path):
        path = tmp_path / "test.webp"
        path.write_bytes(b"fake")
        with pytest.raises(ValidationError, match="Unsupported"):
            validate_input_image(path)

    def test_file_too_large(self, tmp_path: Path):
        path = tmp_path / "huge.png"
        path.write_bytes(b"\x89PNG" + b"\x00" * (MAX_IMAGE_SIZE_MB * 1024 * 1024))
        with pytest.raises(ValidationError, match="too large"):
            validate_input_image(path)


# ---------------------------------------------------------------------------
# Video validation
# ---------------------------------------------------------------------------


class TestValidateInputVideo:
    def test_valid_mp4(self, tmp_path: Path):
        vid = make_test_video(tmp_path / "test.mp4")
        validate_input_video(vid)  # should not raise

    def test_valid_mov(self, tmp_path: Path):
        vid = make_test_video(tmp_path / "test.mov")
        validate_input_video(vid)  # should not raise

    def test_file_not_found(self, tmp_path: Path):
        with pytest.raises(ValidationError, match="not found"):
            validate_input_video(tmp_path / "nonexistent.mp4")

    def test_not_a_file(self, tmp_path: Path):
        with pytest.raises(ValidationError, match="Not a file"):
            validate_input_video(tmp_path)

    def test_unsupported_extension(self, tmp_path: Path):
        path = tmp_path / "test.avi"
        path.write_bytes(b"fake")
        with pytest.raises(ValidationError, match="Unsupported"):
            validate_input_video(path)

    def test_file_too_large(self, tmp_path: Path):
        path = tmp_path / "huge.mp4"
        path.write_bytes(b"\x00" * (MAX_VIDEO_SIZE_MB * 1024 * 1024 + 1))
        with pytest.raises(ValidationError, match="too large"):
            validate_input_video(path)


# ---------------------------------------------------------------------------
# File to data URL
# ---------------------------------------------------------------------------


class TestFileToDataUrl:
    def test_png_file(self, tmp_path: Path):
        img = make_test_image(tmp_path / "test.png")
        data_url = file_to_data_url(img)
        assert data_url.startswith("data:image/png;base64,")

    def test_jpg_file(self, tmp_path: Path):
        img = make_test_image(tmp_path / "test.jpg")
        data_url = file_to_data_url(img)
        assert data_url.startswith("data:image/jpeg;base64,")

    def test_mp4_file(self, tmp_path: Path):
        vid = make_test_video(tmp_path / "test.mp4")
        data_url = file_to_data_url(vid)
        assert data_url.startswith("data:video/mp4;base64,")

    def test_mov_file(self, tmp_path: Path):
        vid = make_test_video(tmp_path / "test.mov")
        data_url = file_to_data_url(vid)
        assert data_url.startswith("data:video/quicktime;base64,")

    def test_content_is_base64_encoded(self, tmp_path: Path):
        content = b"\x89PNG test content"
        img = tmp_path / "test.png"
        img.write_bytes(content)
        data_url = file_to_data_url(img)
        _, encoded = data_url.split(",", 1)
        decoded = base64.b64decode(encoded)
        assert decoded == content


# ---------------------------------------------------------------------------
# URL resolution
# ---------------------------------------------------------------------------


class TestResolveImageUrl:
    def test_http_url_passthrough(self):
        url = "http://example.com/img.png"
        assert resolve_image_url(url) == url

    def test_https_url_passthrough(self):
        url = "https://cdn.example.com/img.jpg"
        assert resolve_image_url(url) == url

    def test_data_url_passthrough(self):
        url = "data:image/png;base64,abc123"
        assert resolve_image_url(url) == url

    def test_local_file_converts_to_data_url(self, tmp_path: Path):
        img = make_test_image(tmp_path / "local.png")
        result = resolve_image_url(str(img))
        assert result.startswith("data:image/png;base64,")

    def test_invalid_local_file_raises(self, tmp_path: Path):
        with pytest.raises(ValidationError, match="not found"):
            resolve_image_url(str(tmp_path / "missing.png"))


class TestResolveVideoUrl:
    def test_http_url_passthrough(self):
        url = "http://example.com/vid.mp4"
        assert resolve_video_url(url) == url

    def test_https_url_passthrough(self):
        url = "https://example.com/vid.mp4"
        assert resolve_video_url(url) == url

    def test_data_url_passthrough(self):
        url = "data:video/mp4;base64,abc123"
        assert resolve_video_url(url) == url

    def test_local_file_converts_to_data_url(self, tmp_path: Path):
        vid = make_test_video(tmp_path / "local.mp4")
        result = resolve_video_url(str(vid))
        assert result.startswith("data:video/mp4;base64,")

    def test_invalid_local_file_raises(self, tmp_path: Path):
        with pytest.raises(ValidationError, match="not found"):
            resolve_video_url(str(tmp_path / "missing.mp4"))
