"""Tests for config.py — shared constants, validation, and exception hierarchy."""

import pytest

from config import (
    ALLOWED_FRONTMATTER_KEYS,
    EXCLUDE_PATTERNS,
    MAX_COMPATIBILITY_LENGTH,
    MAX_DESCRIPTION_LENGTH,
    MAX_NAME_LENGTH,
    InitError,
    PackagingError,
    SkillCreatorError,
    ValidationError,
    validate_name,
)


class TestConstants:
    def test_max_name_length(self):
        assert MAX_NAME_LENGTH == 64

    def test_max_description_length(self):
        assert MAX_DESCRIPTION_LENGTH == 1024

    def test_max_compatibility_length(self):
        assert MAX_COMPATIBILITY_LENGTH == 500

    def test_allowed_frontmatter_keys(self):
        assert "name" in ALLOWED_FRONTMATTER_KEYS
        assert "description" in ALLOWED_FRONTMATTER_KEYS

    def test_exclude_patterns_has_common_dev_artifacts(self):
        for pattern in [".venv", "__pycache__", "node_modules", "uv.lock"]:
            assert pattern in EXCLUDE_PATTERNS


class TestExceptionHierarchy:
    def test_validation_error_is_skill_creator_error(self):
        assert issubclass(ValidationError, SkillCreatorError)

    def test_init_error_is_skill_creator_error(self):
        assert issubclass(InitError, SkillCreatorError)

    def test_packaging_error_is_skill_creator_error(self):
        assert issubclass(PackagingError, SkillCreatorError)

    def test_base_is_exception(self):
        assert issubclass(SkillCreatorError, Exception)


class TestValidateName:
    def test_valid_kebab_case(self):
        validate_name("my-skill")  # should not raise

    def test_valid_single_word(self):
        validate_name("skill")  # should not raise

    def test_valid_with_digits(self):
        validate_name("my-skill-2")  # should not raise

    def test_accepts_max_length(self):
        validate_name("a" * 64)  # should not raise

    def test_rejects_uppercase(self):
        with pytest.raises(ValidationError, match="kebab-case"):
            validate_name("My-Skill")

    def test_rejects_underscores(self):
        with pytest.raises(ValidationError, match="kebab-case"):
            validate_name("my_skill")

    def test_rejects_leading_hyphen(self):
        with pytest.raises(ValidationError, match="kebab-case"):
            validate_name("-my-skill")

    def test_rejects_trailing_hyphen(self):
        with pytest.raises(ValidationError, match="kebab-case"):
            validate_name("my-skill-")

    def test_rejects_consecutive_hyphens(self):
        with pytest.raises(ValidationError, match="kebab-case"):
            validate_name("my--skill")

    def test_rejects_too_long(self):
        with pytest.raises(ValidationError, match="64 characters"):
            validate_name("a" * 65)
