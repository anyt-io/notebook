from pathlib import Path

from validate_all_skills import validate_all_skills


def _create_skill(skill_path: Path, name: str, description: str = "A valid skill") -> None:
    """Helper to create a minimal valid skill."""
    skill_path.mkdir(parents=True, exist_ok=True)
    (skill_path / "SKILL.md").write_text(f"---\nname: {name}\ndescription: {description}\n---\n\n# {name}\n")
    (skill_path / "pspm.json").write_text(f'{{"name": "{name}"}}')


class TestValidateAllSkills:
    def test_all_valid(self, tmp_path: Path):
        _create_skill(tmp_path / "skill-a", "skill-a")
        _create_skill(tmp_path / "skill-b", "skill-b")
        assert validate_all_skills(tmp_path) is True

    def test_one_invalid(self, tmp_path: Path):
        _create_skill(tmp_path / "skill-a", "skill-a")
        # Missing description
        bad = tmp_path / "skill-b"
        bad.mkdir()
        (bad / "SKILL.md").write_text("---\nname: skill-b\n---\n\n# Bad\n")
        assert validate_all_skills(tmp_path) is False

    def test_all_invalid(self, tmp_path: Path):
        bad1 = tmp_path / "skill-a"
        bad1.mkdir()
        (bad1 / "SKILL.md").write_text("---\nname: skill-a\n---\n\n# Bad\n")
        bad2 = tmp_path / "skill-b"
        bad2.mkdir()
        (bad2 / "SKILL.md").write_text("---\nname: skill-b\n---\n\n# Bad\n")
        assert validate_all_skills(tmp_path) is False

    def test_no_skills_found(self, tmp_path: Path):
        assert validate_all_skills(tmp_path) is False

    def test_not_a_directory(self, tmp_path: Path):
        file_path = tmp_path / "not-a-dir"
        file_path.write_text("hello")
        assert validate_all_skills(file_path) is False

    def test_skips_non_skill_directories(self, tmp_path: Path):
        _create_skill(tmp_path / "skill-a", "skill-a")
        # Directory without SKILL.md — should be skipped, not cause failure
        (tmp_path / "not-a-skill").mkdir()
        (tmp_path / "not-a-skill" / "random.txt").write_text("hello")
        assert validate_all_skills(tmp_path) is True
