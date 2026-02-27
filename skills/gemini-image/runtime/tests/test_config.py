"""Tests for config.py — constants and API key."""

from unittest.mock import patch

from config import (
    AVAILABLE_MODELS,
    DEFAULT_MODEL,
    MIME_TYPES,
    PERSON_GENERATION_OPTIONS,
    SUPPORTED_ASPECT_RATIOS,
    SUPPORTED_IMAGE_SIZES,
    SUPPORTED_INPUT_EXTENSIONS,
    get_api_key,
)


class TestConstants:
    def test_default_model_is_nano_banana(self):
        assert DEFAULT_MODEL == "gemini-2.5-flash-image"

    def test_default_model_in_available(self):
        assert DEFAULT_MODEL in AVAILABLE_MODELS

    def test_available_models_are_current(self):
        assert "gemini-2.5-flash-image" in AVAILABLE_MODELS
        assert "gemini-3.1-flash-image-preview" in AVAILABLE_MODELS
        assert "gemini-3-pro-image-preview" in AVAILABLE_MODELS
        for model in AVAILABLE_MODELS:
            assert not model.startswith("gemini-2.0-")
            assert not model.startswith("gemini-1.5-")

    def test_aspect_ratios_format(self):
        for ratio in SUPPORTED_ASPECT_RATIOS:
            parts = ratio.split(":")
            assert len(parts) == 2
            assert int(parts[0]) > 0
            assert int(parts[1]) > 0

    def test_image_sizes(self):
        assert SUPPORTED_IMAGE_SIZES == ["0.5K", "1K", "2K", "4K"]

    def test_person_generation_options(self):
        assert "DONT_ALLOW" in PERSON_GENERATION_OPTIONS
        assert "ALLOW_ADULT" in PERSON_GENERATION_OPTIONS
        assert "ALLOW_ALL" in PERSON_GENERATION_OPTIONS

    def test_mime_types_cover_extensions(self):
        for ext in SUPPORTED_INPUT_EXTENSIONS:
            assert ext in MIME_TYPES


class TestGetApiKey:
    def test_returns_key_when_set(self):
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key-123"}):
            assert get_api_key() == "test-key-123"

    def test_returns_none_when_not_set(self):
        with patch.dict("os.environ", {}, clear=True):
            assert get_api_key() is None
