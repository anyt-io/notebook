"""Tests for config.py — constants and exception hierarchy."""

from config import DEFAULT_OUTPUT_DIR, SKILL_DIR, ConversionError, EbookError, ValidationError


class TestDefaultOutputDir:
    def test_output_dir_under_skill_dir(self):
        assert DEFAULT_OUTPUT_DIR == SKILL_DIR / "output"

    def test_skill_dir_is_ebook(self):
        assert SKILL_DIR.name == "ebook"


class TestExceptionHierarchy:
    def test_validation_error_is_ebook_error(self):
        assert issubclass(ValidationError, EbookError)

    def test_conversion_error_is_ebook_error(self):
        assert issubclass(ConversionError, EbookError)

    def test_ebook_error_is_exception(self):
        assert issubclass(EbookError, Exception)
