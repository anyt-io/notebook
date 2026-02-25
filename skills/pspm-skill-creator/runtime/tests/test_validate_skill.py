"""Tests for validate_skill.py."""

from pathlib import Path

import pytest

from config import ValidationError
from validate_skill import validate_skill


def _create_skill_md(skill_path: Path, frontmatter: str, body: str = "# Test\n") -> None:
    """Helper to create a SKILL.md with given frontmatter."""
    skill_path.mkdir(parents=True, exist_ok=True)
    (skill_path / "SKILL.md").write_text(f"---\n{frontmatter}---\n\n{body}")


class TestValidateSkill:
    def test_valid_skill(self, tmp_path: Path):
        _create_skill_md(tmp_path, "name: test-skill\ndescription: A test skill\n")
        name = validate_skill(tmp_path)
        assert name == "test-skill"

    def test_missing_skill_md(self, tmp_path: Path):
        with pytest.raises(ValidationError, match=r"SKILL\.md"):
            validate_skill(tmp_path)

    def test_missing_frontmatter(self, tmp_path: Path):
        tmp_path.mkdir(parents=True, exist_ok=True)
        (tmp_path / "SKILL.md").write_text("# No frontmatter\n")
        with pytest.raises(ValidationError, match="frontmatter"):
            validate_skill(tmp_path)

    def test_missing_name(self, tmp_path: Path):
        _create_skill_md(tmp_path, "description: A test skill\n")
        with pytest.raises(ValidationError, match="name"):
            validate_skill(tmp_path)

    def test_missing_description(self, tmp_path: Path):
        _create_skill_md(tmp_path, "name: test-skill\n")
        with pytest.raises(ValidationError, match="description"):
            validate_skill(tmp_path)

    def test_invalid_name_uppercase(self, tmp_path: Path):
        _create_skill_md(tmp_path, "name: Test-Skill\ndescription: A test skill\n")
        with pytest.raises(ValidationError, match="kebab-case"):
            validate_skill(tmp_path)

    def test_name_too_long(self, tmp_path: Path):
        long_name = "a" * 65
        _create_skill_md(tmp_path, f"name: {long_name}\ndescription: A test skill\n")
        with pytest.raises(ValidationError, match="64 characters"):
            validate_skill(tmp_path)

    def test_description_too_long(self, tmp_path: Path):
        long_desc = "a" * 1025
        _create_skill_md(tmp_path, f"name: test-skill\ndescription: {long_desc}\n")
        with pytest.raises(ValidationError, match="1024 characters"):
            validate_skill(tmp_path)

    def test_description_with_angle_brackets(self, tmp_path: Path):
        _create_skill_md(tmp_path, "name: test-skill\ndescription: Use <html> tags\n")
        with pytest.raises(ValidationError, match="angle brackets"):
            validate_skill(tmp_path)

    def test_unknown_frontmatter_key(self, tmp_path: Path):
        _create_skill_md(tmp_path, "name: test-skill\ndescription: A test skill\nunknown-key: value\n")
        with pytest.raises(ValidationError, match=r"[Uu]nknown"):
            validate_skill(tmp_path)

    def test_valid_with_optional_fields(self, tmp_path: Path):
        _create_skill_md(tmp_path, "name: test-skill\ndescription: A test skill\nlicense: MIT\ncompatibility: macOS\n")
        name = validate_skill(tmp_path)
        assert name == "test-skill"

    def test_compatibility_too_long(self, tmp_path: Path):
        long_compat = "a" * 501
        _create_skill_md(tmp_path, f"name: test-skill\ndescription: A test skill\ncompatibility: {long_compat}\n")
        with pytest.raises(ValidationError, match="500 characters"):
            validate_skill(tmp_path)

    def test_valid_pspm_json(self, tmp_path: Path):
        _create_skill_md(tmp_path, "name: test-skill\ndescription: A test skill\n")
        (tmp_path / "pspm.json").write_text('{"name": "test-skill"}')
        name = validate_skill(tmp_path)
        assert name == "test-skill"

    def test_invalid_pspm_json(self, tmp_path: Path):
        _create_skill_md(tmp_path, "name: test-skill\ndescription: A test skill\n")
        (tmp_path / "pspm.json").write_text("{invalid json}")
        with pytest.raises(ValidationError, match=r"pspm\.json"):
            validate_skill(tmp_path)

    def test_not_a_directory(self, tmp_path: Path):
        file_path = tmp_path / "not-a-dir"
        file_path.write_text("hello")
        with pytest.raises(ValidationError, match="Not a directory"):
            validate_skill(file_path)
