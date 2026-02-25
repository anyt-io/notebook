"""Tests for config.py — constants and API key."""

from unittest.mock import patch

from config import (
    AVAILABLE_MODELS,
    DEFAULT_MODEL,
    DEFAULT_POLL_INTERVAL,
    MAX_REFERENCE_IMAGES,
    MIME_TYPES,
    PERSON_GENERATION_OPTIONS,
    SUPPORTED_ASPECT_RATIOS,
    SUPPORTED_DURATIONS,
    SUPPORTED_INPUT_EXTENSIONS,
    SUPPORTED_RESOLUTIONS,
    get_api_key,
)


class TestConstants:
    def test_default_model_is_veo_3_1(self):
        assert DEFAULT_MODEL == "veo-3.1-generate-preview"

    def test_default_model_in_available(self):
        assert DEFAULT_MODEL in AVAILABLE_MODELS

    def test_available_models_only_veo_3_1(self):
        assert "veo-3.1-generate-preview" in AVAILABLE_MODELS
        assert "veo-3.1-fast-generate-preview" in AVAILABLE_MODELS
        assert len(AVAILABLE_MODELS) == 2
        for model in AVAILABLE_MODELS:
            assert model.startswith("veo-3.1")

    def test_aspect_ratios(self):
        assert "16:9" in SUPPORTED_ASPECT_RATIOS
        assert "9:16" in SUPPORTED_ASPECT_RATIOS
        for ratio in SUPPORTED_ASPECT_RATIOS:
            parts = ratio.split(":")
            assert len(parts) == 2
            assert int(parts[0]) > 0
            assert int(parts[1]) > 0

    def test_resolutions(self):
        assert SUPPORTED_RESOLUTIONS == ["720p", "1080p", "4k"]

    def test_durations(self):
        assert SUPPORTED_DURATIONS == [4, 6, 8]

    def test_person_generation_options(self):
        assert "allow_all" in PERSON_GENERATION_OPTIONS
        assert "allow_adult" in PERSON_GENERATION_OPTIONS
        assert "dont_allow" in PERSON_GENERATION_OPTIONS

    def test_mime_types_cover_extensions(self):
        for ext in SUPPORTED_INPUT_EXTENSIONS:
            assert ext in MIME_TYPES

    def test_default_poll_interval(self):
        assert DEFAULT_POLL_INTERVAL == 10

    def test_max_reference_images(self):
        assert MAX_REFERENCE_IMAGES == 3


class TestGetApiKey:
    def test_returns_key_when_set(self):
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key-123"}):
            assert get_api_key() == "test-key-123"

    def test_returns_none_when_not_set(self):
        with patch.dict("os.environ", {}, clear=True):
            assert get_api_key() is None
