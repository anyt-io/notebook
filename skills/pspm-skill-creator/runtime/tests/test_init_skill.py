from pathlib import Path

from init_skill import init_skill, validate_name


class TestValidateName:
    def test_valid_kebab_case(self):
        assert validate_name("my-skill")[0] is True

    def test_valid_single_word(self):
        assert validate_name("skill")[0] is True

    def test_valid_with_digits(self):
        assert validate_name("my-skill-2")[0] is True

    def test_rejects_uppercase(self):
        assert validate_name("My-Skill")[0] is False

    def test_rejects_underscores(self):
        assert validate_name("my_skill")[0] is False

    def test_rejects_leading_hyphen(self):
        assert validate_name("-my-skill")[0] is False

    def test_rejects_trailing_hyphen(self):
        assert validate_name("my-skill-")[0] is False

    def test_rejects_consecutive_hyphens(self):
        assert validate_name("my--skill")[0] is False

    def test_rejects_too_long(self):
        assert validate_name("a" * 65)[0] is False

    def test_accepts_max_length(self):
        assert validate_name("a" * 64)[0] is True


class TestInitSkill:
    def test_creates_skill_directory(self, tmp_path: Path):
        result = init_skill("test-skill", tmp_path)
        assert result is True
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
        import json

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

    def test_creates_package_json_for_typescript(self, tmp_path: Path):
        init_skill("ts-skill", tmp_path, skill_type="ts")
        pkg = tmp_path / "ts-skill" / "runtime" / "package.json"
        assert pkg.exists()
        import json

        data = json.loads(pkg.read_text())
        assert data["name"] == "ts-skill"

    def test_creates_tests_directory_for_python(self, tmp_path: Path):
        init_skill("test-skill", tmp_path, skill_type="py")
        assert (tmp_path / "test-skill" / "runtime" / "tests" / "__init__.py").exists()
        assert (tmp_path / "test-skill" / "runtime" / "tests" / "test_example.py").exists()

    def test_fails_if_directory_exists(self, tmp_path: Path):
        (tmp_path / "test-skill").mkdir()
        result = init_skill("test-skill", tmp_path)
        assert result is False

    def test_fails_for_invalid_name(self, tmp_path: Path):
        result = init_skill("Invalid_Name", tmp_path)
        assert result is False

    def test_creates_example_script_py(self, tmp_path: Path):
        init_skill("test-skill", tmp_path, skill_type="py")
        script = tmp_path / "test-skill" / "runtime" / "example.py"
        assert script.exists()
        assert "SKILL_DIR" in script.read_text()

    def test_creates_example_script_ts(self, tmp_path: Path):
        init_skill("ts-skill", tmp_path, skill_type="ts")
        script = tmp_path / "ts-skill" / "runtime" / "example.ts"
        assert script.exists()
