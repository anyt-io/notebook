import zipfile
from pathlib import Path

from package_skill import package_skill, should_exclude


class TestShouldExclude:
    def test_excludes_venv(self):
        assert should_exclude(Path(".venv/lib/something.py")) is True

    def test_excludes_pycache(self):
        assert should_exclude(Path("__pycache__/module.pyc")) is True

    def test_excludes_pyc_files(self):
        assert should_exclude(Path("module.pyc")) is True

    def test_excludes_ruff_cache(self):
        assert should_exclude(Path(".ruff_cache/data")) is True

    def test_excludes_uv_lock(self):
        assert should_exclude(Path("uv.lock")) is True

    def test_includes_normal_files(self):
        assert should_exclude(Path("SKILL.md")) is False
        assert should_exclude(Path("runtime/script.py")) is False
        assert should_exclude(Path("pspm.json")) is False


class TestPackageSkill:
    def _create_valid_skill(self, path: Path) -> Path:
        """Create a minimal valid skill directory."""
        skill_path = path / "test-skill"
        skill_path.mkdir()
        (skill_path / "SKILL.md").write_text("---\nname: test-skill\ndescription: A test skill\n---\n\n# Test\n")
        (skill_path / "pspm.json").write_text('{"name": "test-skill"}')
        runtime = skill_path / "runtime"
        runtime.mkdir()
        (runtime / "script.py").write_text("print('hello')")
        return skill_path

    def test_packages_valid_skill(self, tmp_path: Path):
        skill_path = self._create_valid_skill(tmp_path)
        output_dir = tmp_path / "dist"
        result = package_skill(skill_path, output_dir)
        assert result is not None
        assert result.exists()
        assert result.suffix == ".skill"

    def test_skill_file_is_valid_zip(self, tmp_path: Path):
        skill_path = self._create_valid_skill(tmp_path)
        output_dir = tmp_path / "dist"
        result = package_skill(skill_path, output_dir)
        assert result is not None
        assert zipfile.is_zipfile(result)

    def test_skill_file_contains_expected_files(self, tmp_path: Path):
        skill_path = self._create_valid_skill(tmp_path)
        output_dir = tmp_path / "dist"
        result = package_skill(skill_path, output_dir)
        assert result is not None
        with zipfile.ZipFile(result) as zf:
            names = zf.namelist()
            assert any("SKILL.md" in n for n in names)
            assert any("pspm.json" in n for n in names)
            assert any("script.py" in n for n in names)

    def test_excludes_dev_artifacts(self, tmp_path: Path):
        skill_path = self._create_valid_skill(tmp_path)
        # Add dev artifacts
        cache = skill_path / "runtime" / "__pycache__"
        cache.mkdir()
        (cache / "module.pyc").write_text("bytecode")
        (skill_path / "runtime" / "uv.lock").write_text("lock")

        output_dir = tmp_path / "dist"
        result = package_skill(skill_path, output_dir)
        assert result is not None
        with zipfile.ZipFile(result) as zf:
            names = zf.namelist()
            assert not any("__pycache__" in n for n in names)
            assert not any("uv.lock" in n for n in names)

    def test_fails_for_missing_directory(self, tmp_path: Path):
        result = package_skill(tmp_path / "nonexistent")
        assert result is None

    def test_fails_for_missing_skill_md(self, tmp_path: Path):
        skill_path = tmp_path / "bad-skill"
        skill_path.mkdir()
        result = package_skill(skill_path)
        assert result is None

    def test_fails_for_invalid_skill(self, tmp_path: Path):
        skill_path = tmp_path / "bad-skill"
        skill_path.mkdir()
        # Missing required description
        (skill_path / "SKILL.md").write_text("---\nname: bad-skill\n---\n\n# Bad\n")
        result = package_skill(skill_path)
        assert result is None
