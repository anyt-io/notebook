"""Tests for config.py — constants, API key, and URL generation."""

from unittest.mock import patch

from config import (
    API_BASE_URL,
    DEFAULT_ORIENTATION,
    DEFAULT_POLL_INTERVAL,
    MAX_IMAGE_SIZE_MB,
    MAX_POLL_ATTEMPTS,
    MAX_VIDEO_SIZE_MB,
    MIN_DIMENSION_PX,
    MOTION_CONTROL_ENDPOINT,
    SUPPORTED_IMAGE_EXTENSIONS,
    SUPPORTED_ORIENTATIONS,
    SUPPORTED_VIDEO_EXTENSIONS,
    get_api_key,
    get_motion_control_url,
    get_result_url,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


class TestConstants:
    def test_api_base_url(self):
        assert API_BASE_URL == "https://api.wavespeed.ai/api/v3"

    def test_motion_control_endpoint(self):
        assert MOTION_CONTROL_ENDPOINT == "/kwaivgi/kling-v2.6-std/motion-control"

    def test_supported_orientations(self):
        assert "image" in SUPPORTED_ORIENTATIONS
        assert "video" in SUPPORTED_ORIENTATIONS
        assert len(SUPPORTED_ORIENTATIONS) == 2

    def test_default_orientation(self):
        assert DEFAULT_ORIENTATION == "image"
        assert DEFAULT_ORIENTATION in SUPPORTED_ORIENTATIONS

    def test_supported_image_extensions(self):
        assert ".png" in SUPPORTED_IMAGE_EXTENSIONS
        assert ".jpg" in SUPPORTED_IMAGE_EXTENSIONS
        assert ".jpeg" in SUPPORTED_IMAGE_EXTENSIONS

    def test_supported_video_extensions(self):
        assert ".mp4" in SUPPORTED_VIDEO_EXTENSIONS
        assert ".mov" in SUPPORTED_VIDEO_EXTENSIONS

    def test_limits(self):
        assert MAX_IMAGE_SIZE_MB == 10
        assert MAX_VIDEO_SIZE_MB == 10
        assert MIN_DIMENSION_PX == 300

    def test_polling_defaults(self):
        assert DEFAULT_POLL_INTERVAL == 5.0
        assert MAX_POLL_ATTEMPTS == 120


# ---------------------------------------------------------------------------
# API key
# ---------------------------------------------------------------------------


class TestGetApiKey:
    def test_returns_key_when_set(self):
        with patch.dict("os.environ", {"WAVESPEED_API_KEY": "test-key-123"}):
            assert get_api_key() == "test-key-123"

    def test_returns_none_when_not_set(self):
        with patch.dict("os.environ", {}, clear=True):
            assert get_api_key() is None


# ---------------------------------------------------------------------------
# URL generation
# ---------------------------------------------------------------------------


class TestGetMotionControlUrl:
    def test_returns_full_url(self):
        url = get_motion_control_url()
        assert url == "https://api.wavespeed.ai/api/v3/kwaivgi/kling-v2.6-std/motion-control"


class TestGetResultUrl:
    def test_returns_full_url_with_request_id(self):
        url = get_result_url("abc-123")
        assert url == "https://api.wavespeed.ai/api/v3/predictions/abc-123/result"

    def test_handles_different_request_ids(self):
        url = get_result_url("xyz-789-test")
        assert "xyz-789-test" in url
