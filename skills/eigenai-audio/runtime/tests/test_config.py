"""Tests for configuration constants and utilities."""

from pathlib import Path

from config import (
    API_URL,
    AUDIO_MIME_TYPES,
    AVAILABLE_TTS_MODELS,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_TTS_MODEL,
    QWEN3_LANGUAGES,
    QWEN3_RESPONSE_FORMATS,
    SUPPORTED_AUDIO_EXTENSIONS,
    ApiError,
    ConfigError,
    EigenAIAudioError,
    OutputError,
    ValidationError,
)


def test_api_url() -> None:
    assert API_URL == "https://api-web.eigenai.com/api/v1/generate"


def test_default_model_in_available() -> None:
    assert DEFAULT_TTS_MODEL in AVAILABLE_TTS_MODELS


def test_available_models() -> None:
    assert "higgs2p5" in AVAILABLE_TTS_MODELS
    assert "chatterbox" in AVAILABLE_TTS_MODELS
    assert "qwen3-tts" in AVAILABLE_TTS_MODELS


def test_supported_audio_extensions() -> None:
    for ext in [".mp3", ".wav", ".m4a", ".ogg", ".webm"]:
        assert ext in SUPPORTED_AUDIO_EXTENSIONS


def test_audio_mime_types() -> None:
    assert AUDIO_MIME_TYPES[".mp3"] == "audio/mpeg"
    assert AUDIO_MIME_TYPES[".wav"] == "audio/wav"


def test_qwen3_languages() -> None:
    assert "English" in QWEN3_LANGUAGES
    assert "Chinese" in QWEN3_LANGUAGES
    assert "Auto" in QWEN3_LANGUAGES


def test_qwen3_response_formats() -> None:
    assert "wav" in QWEN3_RESPONSE_FORMATS
    assert "mp3" in QWEN3_RESPONSE_FORMATS
    assert "flac" in QWEN3_RESPONSE_FORMATS


def test_default_output_dir() -> None:
    assert isinstance(DEFAULT_OUTPUT_DIR, Path)
    assert DEFAULT_OUTPUT_DIR.name == "output"


def test_exception_hierarchy() -> None:
    assert issubclass(ConfigError, EigenAIAudioError)
    assert issubclass(ValidationError, EigenAIAudioError)
    assert issubclass(ApiError, EigenAIAudioError)
    assert issubclass(OutputError, EigenAIAudioError)


def test_get_api_key_unset(monkeypatch: "pytest.MonkeyPatch") -> None:  # type: ignore[name-defined]  # noqa: F821
    import config

    monkeypatch.delenv("EIGENAI_API_KEY", raising=False)
    assert config.get_api_key() is None


def test_get_api_key_set(monkeypatch: "pytest.MonkeyPatch") -> None:  # type: ignore[name-defined]  # noqa: F821
    import config

    monkeypatch.setenv("EIGENAI_API_KEY", "test-key-123")
    assert config.get_api_key() == "test-key-123"
