"""Tests for config.py — constants, API key, and endpoint resolution."""

from unittest.mock import patch

from config import (
    DEFAULT_ASPECT_RATIO,
    DEFAULT_DURATION,
    DEFAULT_QUALITY,
    ENDPOINTS,
    MAX_ELEMENT_REFS,
    MAX_ELEMENTS,
    MAX_IMAGE_SIZE_MB,
    MAX_REF_IMAGES,
    MAX_VIDEO_SIZE_MB,
    SUPPORTED_ASPECT_RATIOS,
    SUPPORTED_DURATIONS,
    SUPPORTED_INPUT_EXTENSIONS,
    SUPPORTED_MODES,
    SUPPORTED_QUALITY,
    SUPPORTED_VIDEO_EXTENSIONS,
    get_api_key,
    get_endpoint,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


class TestConstants:
    def test_supported_modes(self):
        assert "text-to-video" in SUPPORTED_MODES
        assert "image-to-video" in SUPPORTED_MODES
        assert "reference-to-video" in SUPPORTED_MODES
        assert "edit-video" in SUPPORTED_MODES
        assert len(SUPPORTED_MODES) == 4

    def test_endpoints_all_modes_and_qualities(self):
        for mode in SUPPORTED_MODES:
            assert mode in ENDPOINTS
            for quality in SUPPORTED_QUALITY:
                assert quality in ENDPOINTS[mode]
                assert ENDPOINTS[mode][quality].startswith("fal-ai/kling-video/o3/")

    def test_default_quality(self):
        assert DEFAULT_QUALITY == "standard"
        assert DEFAULT_QUALITY in SUPPORTED_QUALITY

    def test_aspect_ratios(self):
        assert "16:9" in SUPPORTED_ASPECT_RATIOS
        assert "9:16" in SUPPORTED_ASPECT_RATIOS
        assert "1:1" in SUPPORTED_ASPECT_RATIOS

    def test_default_aspect_ratio(self):
        assert DEFAULT_ASPECT_RATIO == "16:9"

    def test_durations_range_3_to_15(self):
        assert [str(d) for d in range(3, 16)] == SUPPORTED_DURATIONS
        assert DEFAULT_DURATION == "5"

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
        assert MAX_ELEMENTS == 2
        assert MAX_ELEMENT_REFS == 3
        assert MAX_REF_IMAGES == 4


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


# ---------------------------------------------------------------------------
# Endpoint resolution
# ---------------------------------------------------------------------------


class TestGetEndpoint:
    def test_text_to_video_standard(self):
        assert get_endpoint("text-to-video", "standard") == "fal-ai/kling-video/o3/standard/text-to-video"

    def test_text_to_video_pro(self):
        assert get_endpoint("text-to-video", "pro") == "fal-ai/kling-video/o3/pro/text-to-video"

    def test_image_to_video_standard(self):
        assert get_endpoint("image-to-video", "standard") == "fal-ai/kling-video/o3/standard/image-to-video"

    def test_image_to_video_pro(self):
        assert get_endpoint("image-to-video", "pro") == "fal-ai/kling-video/o3/pro/image-to-video"

    def test_reference_to_video_standard(self):
        assert get_endpoint("reference-to-video", "standard") == "fal-ai/kling-video/o3/standard/reference-to-video"

    def test_reference_to_video_pro(self):
        assert get_endpoint("reference-to-video", "pro") == "fal-ai/kling-video/o3/pro/reference-to-video"

    def test_edit_video_standard(self):
        assert get_endpoint("edit-video", "standard") == "fal-ai/kling-video/o3/standard/video-to-video/edit"

    def test_edit_video_pro(self):
        assert get_endpoint("edit-video", "pro") == "fal-ai/kling-video/o3/pro/video-to-video/edit"
