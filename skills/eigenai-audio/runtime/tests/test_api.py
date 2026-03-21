"""Tests for API interaction functions."""

from pathlib import Path

import pytest

from api import validate_audio_file, validate_voice_file
from config import ValidationError


def test_validate_audio_file_not_found(tmp_path: Path) -> None:
    with pytest.raises(ValidationError, match="Audio file not found"):
        validate_audio_file(tmp_path / "nonexistent.mp3")


def test_validate_audio_file_not_a_file(tmp_path: Path) -> None:
    with pytest.raises(ValidationError, match="Not a file"):
        validate_audio_file(tmp_path)


def test_validate_audio_file_unsupported_format(tmp_path: Path) -> None:
    bad_file = tmp_path / "test.txt"
    bad_file.write_text("not audio")
    with pytest.raises(ValidationError, match="Unsupported format"):
        validate_audio_file(bad_file)


def test_validate_audio_file_valid(tmp_path: Path) -> None:
    for ext in [".mp3", ".wav", ".m4a", ".ogg", ".webm"]:
        audio_file = tmp_path / f"test{ext}"
        audio_file.write_bytes(b"\x00" * 100)
        validate_audio_file(audio_file)  # Should not raise


def test_validate_voice_file_not_found(tmp_path: Path) -> None:
    with pytest.raises(ValidationError, match="Voice reference file not found"):
        validate_voice_file(tmp_path / "nonexistent.wav")


def test_validate_voice_file_unsupported_format(tmp_path: Path) -> None:
    bad_file = tmp_path / "test.txt"
    bad_file.write_text("not audio")
    with pytest.raises(ValidationError, match="Unsupported voice file format"):
        validate_voice_file(bad_file)


def test_validate_voice_file_valid(tmp_path: Path) -> None:
    for ext in [".wav", ".mp3", ".m4a", ".ogg"]:
        voice_file = tmp_path / f"voice{ext}"
        voice_file.write_bytes(b"\x00" * 100)
        validate_voice_file(voice_file)  # Should not raise
