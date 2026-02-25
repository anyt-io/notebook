"""Tests for media.py — validation, URL resolution, parsing, and mode detection."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from config import MAX_IMAGE_SIZE_MB, MAX_VIDEO_SIZE_MB, UploadError, ValidationError
from media import (
    build_element,
    detect_mode,
    parse_elements_json,
    parse_multi_prompt,
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


# ---------------------------------------------------------------------------
# Mode detection
# ---------------------------------------------------------------------------


class TestDetectMode:
    def _ns(self, **kwargs: object) -> MagicMock:
        ns = MagicMock()
        ns.image = kwargs.get("image")
        ns.video = kwargs.get("video")
        ns.element = kwargs.get("element")
        ns.elements_json = kwargs.get("elements_json")
        return ns

    def test_text_to_video(self):
        assert detect_mode(self._ns()) == "text-to-video"

    def test_image_to_video(self):
        assert detect_mode(self._ns(image="start.png")) == "image-to-video"

    def test_reference_with_element(self):
        assert detect_mode(self._ns(element=["char.png"])) == "reference-to-video"

    def test_reference_with_elements_json(self):
        assert detect_mode(self._ns(elements_json="[{}]")) == "reference-to-video"

    def test_edit_video(self):
        assert detect_mode(self._ns(video="input.mp4")) == "edit-video"

    def test_video_takes_priority_over_image(self):
        assert detect_mode(self._ns(video="input.mp4", image="start.png")) == "edit-video"

    def test_element_takes_priority_over_image(self):
        assert detect_mode(self._ns(element=["char.png"], image="start.png")) == "reference-to-video"


# ---------------------------------------------------------------------------
# Element building
# ---------------------------------------------------------------------------


class TestBuildElement:
    def test_frontal_only(self):
        elem = build_element("https://front.png")
        assert elem == {"frontal_image_url": "https://front.png"}

    def test_with_refs(self):
        elem = build_element("https://front.png", ref_urls=["https://side.png", "https://back.png"])
        assert elem["reference_image_urls"] == ["https://side.png", "https://back.png"]

    def test_with_video(self):
        elem = build_element("https://front.png", video_url="https://motion.mp4")
        assert elem["video_url"] == "https://motion.mp4"

    def test_with_all(self):
        elem = build_element(
            "https://front.png",
            ref_urls=["https://side.png"],
            video_url="https://motion.mp4",
        )
        assert elem["frontal_image_url"] == "https://front.png"
        assert elem["reference_image_urls"] == ["https://side.png"]
        assert elem["video_url"] == "https://motion.mp4"


# ---------------------------------------------------------------------------
# Multi-prompt parsing
# ---------------------------------------------------------------------------


class TestParseMultiPrompt:
    def test_json_string(self):
        data = parse_multi_prompt('[{"prompt":"Scene 1","duration":"5"},{"prompt":"Scene 2"}]')
        assert len(data) == 2
        assert data[0]["prompt"] == "Scene 1"
        assert data[0]["duration"] == "5"

    def test_json_file(self, tmp_path: Path):
        f = tmp_path / "prompts.json"
        f.write_text(json.dumps([{"prompt": "A"}, {"prompt": "B"}]))
        data = parse_multi_prompt(str(f))
        assert len(data) == 2

    def test_invalid_not_array(self):
        with pytest.raises(ValidationError, match="JSON array"):
            parse_multi_prompt('{"prompt":"test"}')

    def test_invalid_missing_prompt(self):
        with pytest.raises(ValidationError, match="prompt"):
            parse_multi_prompt('[{"duration":"5"}]')

    def test_invalid_json(self):
        with pytest.raises(json.JSONDecodeError):
            parse_multi_prompt("not json")


class TestParseElementsJson:
    def test_json_string(self):
        data = parse_elements_json('[{"frontal_image_url":"https://x.png"}]')
        assert len(data) == 1

    def test_json_file(self, tmp_path: Path):
        f = tmp_path / "elements.json"
        f.write_text(json.dumps([{"frontal_image_url": "https://a.png"}, {"frontal_image_url": "https://b.png"}]))
        data = parse_elements_json(str(f))
        assert len(data) == 2

    def test_invalid_not_array(self):
        with pytest.raises(ValidationError, match="JSON array"):
            parse_elements_json('{"frontal_image_url":"x"}')
