#!/usr/bin/env python3
"""
PSPM Skill Initializer
Scaffolds a new PSPM skill with the standard directory structure and template files.
Run with: uv run --project runtime runtime/init_skill.py <skill-name> --path <output-dir>
"""

import argparse
import sys
from pathlib import Path

from config import InitError, SkillCreatorError, validate_name
from templates import (
    CONFIG_PY_TEMPLATE,
    EXAMPLE_SCRIPT_PY,
    EXAMPLE_SCRIPT_TS,
    PACKAGE_JSON_TEMPLATE,
    PSPM_JSON_TEMPLATE,
    PSPMIGNORE_TEMPLATE,
    PYPROJECT_TEMPLATE,
    SKILL_MD_TEMPLATE,
    TEST_CONFIG_PY,
    TEST_EXAMPLE,
    TEST_INIT,
)


def _error_base_name(name: str) -> str:
    """Derive the base error class name from the skill name, e.g. 'my-tool' -> 'MyToolError'."""
    return name.replace("-", " ").title().replace(" ", "") + "Error"


def init_skill(name: str, base_path: Path, skill_type: str = "py") -> Path:
    """
    Initialize a new PSPM skill directory.

    Returns the path to the created skill directory.
    Raises InitError on failure.
    """
    validate_name(name)

    skill_path = base_path / name
    if skill_path.exists():
        raise InitError(f"Directory already exists: {skill_path}")

    title = name.replace("-", " ").title()
    error_base = _error_base_name(name)
    underscored_name = name.replace("-", "_")

    # Create directories
    runtime_path = skill_path / "runtime"
    tests_path = runtime_path / "tests"
    tests_path.mkdir(parents=True, exist_ok=True)

    # SKILL.md
    (skill_path / "SKILL.md").write_text(SKILL_MD_TEMPLATE.format(name=name, title=title))

    # pspm.json
    (skill_path / "pspm.json").write_text(PSPM_JSON_TEMPLATE.format(name=name))

    # .pspmignore
    (skill_path / ".pspmignore").write_text(PSPMIGNORE_TEMPLATE)

    # .gitignore
    (skill_path / ".gitignore").write_text("runtime/__pycache__/\n")

    # Runtime files
    if skill_type == "py":
        (runtime_path / "pyproject.toml").write_text(PYPROJECT_TEMPLATE.format(name=name))
        (runtime_path / "config.py").write_text(CONFIG_PY_TEMPLATE.format(name=name, error_base=error_base))
        (runtime_path / "example.py").write_text(EXAMPLE_SCRIPT_PY.format(name=name, error_base=error_base))
        (tests_path / "__init__.py").write_text(TEST_INIT)
        (tests_path / "test_config.py").write_text(
            TEST_CONFIG_PY.format(name=name, error_base=error_base, underscored_name=underscored_name)
        )
        (tests_path / "test_example.py").write_text(TEST_EXAMPLE)
    else:
        (runtime_path / "package.json").write_text(PACKAGE_JSON_TEMPLATE.format(name=name))
        (runtime_path / "example.ts").write_text(EXAMPLE_SCRIPT_TS.format(name=name))

    print(f"Initialized PSPM skill: {skill_path}")
    print("  SKILL.md          — usage documentation")
    print("  pspm.json         — PSPM manifest")
    print("  .pspmignore       — publishing exclusions")
    print(f"  runtime/          — isolated {skill_type} environment")
    if skill_type == "py":
        print("  runtime/config.py — constants and exception hierarchy")
        print("  runtime/tests/    — pytest tests")
    print("\nNext steps:")
    if skill_type == "py":
        print(f"  cd {skill_path}/runtime && uv sync")
        print("  uv add <your-dependencies>")
    else:
        print(f"  cd {skill_path}/runtime && bun install")
        print("  bun add <your-dependencies>")
    return skill_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a new PSPM skill")
    parser.add_argument("name", help="Skill name (kebab-case, e.g. my-cool-skill)")
    parser.add_argument("--path", default=".", help="Parent directory for the skill folder (default: current dir)")
    parser.add_argument(
        "--type",
        choices=["py", "ts"],
        default="py",
        help="Runtime type: py (Python/uv) or ts (TypeScript/bun). Default: py",
    )

    args = parser.parse_args()

    try:
        init_skill(args.name, Path(args.path), args.type)
        return 0
    except SkillCreatorError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
