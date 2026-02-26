"""Tests for config.py — constants, API key, and endpoint."""

from unittest.mock import patch

from config import (
    DEFAULT_ORIENTATION,
    ENDPOINT,
    MAX_IMAGE_SIZE_MB,
    MAX_VIDEO_SIZE_MB,
    SUPPORTED_INPUT_EXTENSIONS,
    SUPPORTED_ORIENTATIONS,
    SUPPORTED_VIDEO_EXTENSIONS,
    get_api_key,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


class TestConstants:
    def test_endpoint(self):
        assert ENDPOINT == "fal-ai/kling-video/v2.6/standard/motion-control"

    def test_supported_orientations(self):
        assert "image" in SUPPORTED_ORIENTATIONS
        assert "video" in SUPPORTED_ORIENTATIONS
        assert len(SUPPORTED_ORIENTATIONS) == 2

    def test_default_orientation(self):
        assert DEFAULT_ORIENTATION == "image"
        assert DEFAULT_ORIENTATION in SUPPORTED_ORIENTATIONS

    def test_supported_image_extensions(self):
        assert ".png" in SUPPORTED_INPUT_EXTENSIONS
        assert ".jpg" in SUPPORTED_INPUT_EXTENSIONS
        assert ".jpeg" in SUPPORTED_INPUT_EXTENSIONS
        assert ".webp" in SUPPORTED_INPUT_EXTENSIONS
        assert ".gif" in SUPPORTED_INPUT_EXTENSIONS

    def test_supported_video_extensions(self):
        assert ".mp4" in SUPPORTED_VIDEO_EXTENSIONS
        assert ".mov" in SUPPORTED_VIDEO_EXTENSIONS

    def test_limits(self):
        assert MAX_IMAGE_SIZE_MB == 10
        assert MAX_VIDEO_SIZE_MB == 200


# ---------------------------------------------------------------------------
# API key
# ---------------------------------------------------------------------------


class TestGetApiKey:
    def test_returns_key_when_set(self):
        with patch.dict("os.environ", {"FAL_KEY": "test-key-123"}):
            assert get_api_key() == "test-key-123"

    def test_returns_none_when_not_set(self):
        with patch.dict("os.environ", {}, clear=True):
            assert get_api_key() is None
