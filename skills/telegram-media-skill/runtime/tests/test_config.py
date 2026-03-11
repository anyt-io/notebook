"""Tests for config.py."""

from config import (
    DEFAULT_OUTPUT_DIR,
    SKILL_DIR,
    ProcessingError,
    TelegramMediaSkillError,
    ValidationError,
)


class TestDefaultOutputDir:
    def test_output_dir_under_skill_dir(self):
        assert DEFAULT_OUTPUT_DIR == SKILL_DIR / "output"

    def test_skill_dir_is_telegram_media_skill(self):
        assert SKILL_DIR.name == "telegram-media-skill"


class TestExceptionHierarchy:
    def test_validation_error_is_base_error(self):
        assert issubclass(ValidationError, TelegramMediaSkillError)

    def test_processing_error_is_base_error(self):
        assert issubclass(ProcessingError, TelegramMediaSkillError)

    def test_base_error_is_exception(self):
        assert issubclass(TelegramMediaSkillError, Exception)
