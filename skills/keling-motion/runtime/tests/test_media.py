"""Tests for media.py — validation and URL resolution."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from config import MAX_IMAGE_SIZE_MB, MAX_VIDEO_SIZE_MB, UploadError, ValidationError
from media import (
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

    def test_valid_webp(self, tmp_path: Path):
        img = make_test_image(tmp_path / "test.webp")
        validate_input_image(img)  # should not raise

    def test_file_not_found(self, tmp_path: Path):
        with pytest.raises(ValidationError, match="not found"):
            validate_input_image(tmp_path / "nonexistent.png")

    def test_not_a_file(self, tmp_path: Path):
        with pytest.raises(ValidationError, match="Not a file"):
            validate_input_image(tmp_path)

    def test_unsupported_extension(self, tmp_path: Path):
        path = tmp_path / "test.bmp"
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
# URL resolution
# ---------------------------------------------------------------------------


class TestResolveImageUrl:
    def test_http_url_passthrough(self):
        url = "https://example.com/img.png"
        assert resolve_image_url(url) == url

    def test_https_url_passthrough(self):
        url = "https://cdn.example.com/img.jpg"
        assert resolve_image_url(url) == url

    @patch("media.fal_client.upload_file", return_value="https://fal.ai/uploaded/img.png")
    def test_local_file_upload(self, mock_upload: MagicMock, tmp_path: Path):
        img = make_test_image(tmp_path / "local.png")
        result = resolve_image_url(str(img))
        assert result == "https://fal.ai/uploaded/img.png"
        mock_upload.assert_called_once_with(img)

    def test_invalid_local_file_raises(self, tmp_path: Path):
        with pytest.raises(ValidationError, match="not found"):
            resolve_image_url(str(tmp_path / "missing.png"))

    @patch("media.fal_client.upload_file", side_effect=RuntimeError("upload failed"))
    def test_upload_failure_raises_upload_error(self, mock_upload: MagicMock, tmp_path: Path):
        img = make_test_image(tmp_path / "local.png")
        with pytest.raises(UploadError, match="Failed to upload image"):
            resolve_image_url(str(img))


class TestResolveVideoUrl:
    def test_url_passthrough(self):
        url = "https://example.com/vid.mp4"
        assert resolve_video_url(url) == url

    @patch("media.fal_client.upload_file", return_value="https://fal.ai/uploaded/vid.mp4")
    def test_local_file_upload(self, mock_upload: MagicMock, tmp_path: Path):
        vid = make_test_video(tmp_path / "local.mp4")
        result = resolve_video_url(str(vid))
        assert result == "https://fal.ai/uploaded/vid.mp4"
        mock_upload.assert_called_once_with(vid)

    def test_invalid_local_file_raises(self, tmp_path: Path):
        with pytest.raises(ValidationError, match="not found"):
            resolve_video_url(str(tmp_path / "missing.mp4"))

    @patch("media.fal_client.upload_file", side_effect=RuntimeError("upload failed"))
    def test_upload_failure_raises_upload_error(self, mock_upload: MagicMock, tmp_path: Path):
        vid = make_test_video(tmp_path / "local.mp4")
        with pytest.raises(UploadError, match="Failed to upload video"):
            resolve_video_url(str(vid))
