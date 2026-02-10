#!/usr/bin/env python3
"""
PSPM Skill Initializer
Scaffolds a new PSPM skill with the standard directory structure and template files.
Run with: uv run --project runtime runtime/init_skill.py <skill-name> --path <output-dir>
"""

import argparse
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent

SKILL_MD_TEMPLATE = """\
---
name: {name}
description: TODO — describe what this skill does and when to use it. Include specific triggers and capabilities.
---

# {title}

## Prerequisites

TODO — list required tools (e.g. uv, ffmpeg, bun).

## Usage

Run from the skill folder (`skills/{name}/`):

```bash
uv run --project runtime runtime/<script>.py [args]
```

## Limitations

TODO — note any constraints or known limitations.
"""

PSPM_JSON_TEMPLATE = """\
{{
  "$schema": "https://pspm.dev/schema/v1/pspm.json",
  "name": "{name}",
  "version": "0.1.0",
  "description": "TODO — brief description",
  "author": "TODO",
  "license": "Apache-2.0",
  "type": "skill",
  "capabilities": [],
  "main": "SKILL.md",
  "requirements": {{
    "pspm": ">=0.1.0"
  }},
  "files": [
    "SKILL.md",
    "runtime"
  ],
  "dependencies": {{}},
  "private": false
}}
"""

PSPMIGNORE_TEMPLATE = """\
# Dev environment
runtime/.venv/
runtime/.ruff_cache/
runtime/__pycache__/
runtime/.pytest_cache/

# Tests
runtime/tests/

# Dev config
runtime/.python-version

# Lockfile (consumers resolve their own deps)
runtime/uv.lock

# Skill output
output/
"""

PYPROJECT_TEMPLATE = """\
[project]
name = "{name}"
version = "0.1.0"
description = "TODO — brief description"
requires-python = ">=3.10"
dependencies = []

[dependency-groups]
dev = [
    "pyright>=1.1.408",
    "pytest>=9.0.2",
    "ruff>=0.15.0",
]

[tool.ruff]
target-version = "py310"
line-length = 120

[tool.ruff.lint]
select = ["E", "W", "F", "I", "UP", "B", "SIM", "RUF"]

[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]

[tool.pyright]
pythonVersion = "3.10"
include = ["."]
typeCheckingMode = "standard"
"""

PACKAGE_JSON_TEMPLATE = """\
{{
  "name": "{name}",
  "version": "0.1.0",
  "description": "TODO — brief description",
  "type": "module"
}}
"""

EXAMPLE_SCRIPT_PY = """\
#!/usr/bin/env python3
\"\"\"
Example script for {name}.
Run with: uv run --project runtime runtime/example.py
\"\"\"

import argparse
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = SKILL_DIR / "output"


def main():
    parser = argparse.ArgumentParser(description="TODO — describe this script")
    parser.add_argument("-o", "--output", default=str(DEFAULT_OUTPUT_DIR), help="Output directory")
    args = parser.parse_args()

    Path(args.output).mkdir(parents=True, exist_ok=True)
    print("TODO — implement this script")


if __name__ == "__main__":
    main()
"""

EXAMPLE_SCRIPT_TS = """\
#!/usr/bin/env bun
/**
 * Example script for {name}.
 * Run with: bun run runtime/example.ts
 */

import {{ parseArgs }} from "util";

const {{ values }} = parseArgs({{
  args: Bun.argv.slice(2),
  options: {{
    output: {{ type: "string", short: "o", default: "output" }},
  }},
}});

console.log("TODO — implement this script");
"""

TEST_INIT = ""

TEST_EXAMPLE = """\
from pathlib import Path


class TestExample:
    def test_placeholder(self):
        # TODO — replace with real tests
        assert True
"""


def validate_name(name: str) -> tuple[bool, str]:
    """Validate skill name is kebab-case, max 64 chars."""
    if len(name) > 64:
        return False, "Skill name must be 64 characters or fewer"
    if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name):
        return False, (
            "Skill name must be kebab-case (lowercase letters, digits, single hyphens, no leading/trailing hyphens)"
        )
    return True, ""


def init_skill(name: str, base_path: Path, skill_type: str = "py") -> bool:
    """
    Initialize a new PSPM skill directory.

    Args:
        name: Skill name (kebab-case)
        base_path: Parent directory where skill folder will be created
        skill_type: "py" for Python/uv or "ts" for TypeScript/bun
    """
    valid, msg = validate_name(name)
    if not valid:
        print(f"Error: {msg}")
        return False

    skill_path = base_path / name
    if skill_path.exists():
        print(f"Error: Directory already exists: {skill_path}")
        return False

    title = name.replace("-", " ").title()

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
        (runtime_path / "example.py").write_text(EXAMPLE_SCRIPT_PY.format(name=name))
        (tests_path / "__init__.py").write_text(TEST_INIT)
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
        print("  runtime/tests/    — pytest tests")
    print("\nNext steps:")
    if skill_type == "py":
        print(f"  cd {skill_path}/runtime && uv sync")
        print("  uv add <your-dependencies>")
    else:
        print(f"  cd {skill_path}/runtime && bun install")
        print("  bun add <your-dependencies>")
    return True


def main() -> None:
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
    success = init_skill(args.name, Path(args.path), args.type)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
