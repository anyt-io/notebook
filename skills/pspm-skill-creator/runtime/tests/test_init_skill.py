"""Tests for init_skill.py."""

import json
from pathlib import Path

import pytest

from config import InitError
from init_skill import init_skill


class TestInitSkill:
    def test_creates_skill_directory(self, tmp_path: Path):
        result = init_skill("test-skill", tmp_path)
        assert result == tmp_path / "test-skill"
        assert (tmp_path / "test-skill").is_dir()

    def test_creates_skill_md(self, tmp_path: Path):
        init_skill("test-skill", tmp_path)
        skill_md = tmp_path / "test-skill" / "SKILL.md"
        assert skill_md.exists()
        content = skill_md.read_text()
        assert "name: test-skill" in content
        assert "---" in content

    def test_creates_pspm_json(self, tmp_path: Path):
        init_skill("test-skill", tmp_path)
        pspm_json = tmp_path / "test-skill" / "pspm.json"
        assert pspm_json.exists()
        data = json.loads(pspm_json.read_text())
        assert data["name"] == "test-skill"

    def test_creates_pspmignore(self, tmp_path: Path):
        init_skill("test-skill", tmp_path)
        assert (tmp_path / "test-skill" / ".pspmignore").exists()

    def test_creates_runtime_directory(self, tmp_path: Path):
        init_skill("test-skill", tmp_path)
        assert (tmp_path / "test-skill" / "runtime").is_dir()

    def test_creates_pyproject_toml_for_python(self, tmp_path: Path):
        init_skill("test-skill", tmp_path, skill_type="py")
        toml = tmp_path / "test-skill" / "runtime" / "pyproject.toml"
        assert toml.exists()
        assert "test-skill" in toml.read_text()

    def test_creates_config_py_for_python(self, tmp_path: Path):
        init_skill("test-skill", tmp_path, skill_type="py")
        config = tmp_path / "test-skill" / "runtime" / "config.py"
        assert config.exists()
        content = config.read_text()
        assert "SKILL_DIR" in content
        assert "DEFAULT_OUTPUT_DIR" in content
        assert "TestSkillError" in content

    def test_creates_package_json_for_typescript(self, tmp_path: Path):
        init_skill("ts-skill", tmp_path, skill_type="ts")
        pkg = tmp_path / "ts-skill" / "runtime" / "package.json"
        assert pkg.exists()
        data = json.loads(pkg.read_text())
        assert data["name"] == "ts-skill"

    def test_creates_tests_directory_for_python(self, tmp_path: Path):
        init_skill("test-skill", tmp_path, skill_type="py")
        assert (tmp_path / "test-skill" / "runtime" / "tests" / "__init__.py").exists()
        assert (tmp_path / "test-skill" / "runtime" / "tests" / "test_example.py").exists()
        assert (tmp_path / "test-skill" / "runtime" / "tests" / "test_config.py").exists()

    def test_raises_if_directory_exists(self, tmp_path: Path):
        (tmp_path / "test-skill").mkdir()
        with pytest.raises(InitError, match="already exists"):
            init_skill("test-skill", tmp_path)

    def test_raises_for_invalid_name(self, tmp_path: Path):
        with pytest.raises(Exception, match="kebab-case"):
            init_skill("Invalid_Name", tmp_path)

    def test_creates_example_script_py(self, tmp_path: Path):
        init_skill("test-skill", tmp_path, skill_type="py")
        script = tmp_path / "test-skill" / "runtime" / "example.py"
        assert script.exists()
        content = script.read_text()
        assert "from config import" in content
        assert "TestSkillError" in content

    def test_creates_example_script_ts(self, tmp_path: Path):
        init_skill("ts-skill", tmp_path, skill_type="ts")
        script = tmp_path / "ts-skill" / "runtime" / "example.ts"
        assert script.exists()

    def test_no_config_py_for_typescript(self, tmp_path: Path):
        init_skill("ts-skill", tmp_path, skill_type="ts")
        assert not (tmp_path / "ts-skill" / "runtime" / "config.py").exists()
