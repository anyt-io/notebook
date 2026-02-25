"""Template strings for scaffolding new PSPM skills."""

# ---------------------------------------------------------------------------
# Skill root files
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Python runtime files
# ---------------------------------------------------------------------------

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

CONFIG_PY_TEMPLATE = """\
\"\"\"Configuration constants and exception hierarchy for the {name} skill.\"\"\"

from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = SKILL_DIR / "output"


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------


class {error_base}(Exception):
    \"\"\"Base exception for {name} skill errors.\"\"\"


class ValidationError({error_base}):
    \"\"\"Input validation errors.\"\"\"


class ProcessingError({error_base}):
    \"\"\"Processing or conversion failures.\"\"\"
"""

EXAMPLE_SCRIPT_PY = """\
#!/usr/bin/env python3
\"\"\"
Example script for {name}.
Run with: uv run --project runtime runtime/example.py [args]
\"\"\"

import argparse
import sys
from pathlib import Path

from config import (
    DEFAULT_OUTPUT_DIR,
    {error_base},
    ProcessingError,
    ValidationError,
)

_ERROR_PREFIXES: dict[type[{error_base}], str] = {{
    ValidationError: "Validation error",
    ProcessingError: "Processing error",
}}


def main() -> int:
    parser = argparse.ArgumentParser(description="TODO — describe this script")
    parser.add_argument("-o", "--output", default=str(DEFAULT_OUTPUT_DIR), help="Output directory")
    args = parser.parse_args()

    try:
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        print("TODO — implement this script")
        return 0

    except {error_base} as e:
        prefix = _ERROR_PREFIXES.get(type(e), "Error")
        print(f"\\n{{prefix}}: {{e}}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
"""

TEST_INIT = ""

TEST_CONFIG_PY = """\
\"\"\"Tests for config.py.\"\"\"

from config import (
    DEFAULT_OUTPUT_DIR,
    SKILL_DIR,
    {error_base},
    ProcessingError,
    ValidationError,
)


class TestDefaultOutputDir:
    def test_output_dir_under_skill_dir(self):
        assert DEFAULT_OUTPUT_DIR == SKILL_DIR / "output"

    def test_skill_dir_is_{underscored_name}(self):
        assert SKILL_DIR.name == "{name}"


class TestExceptionHierarchy:
    def test_validation_error_is_base_error(self):
        assert issubclass(ValidationError, {error_base})

    def test_processing_error_is_base_error(self):
        assert issubclass(ProcessingError, {error_base})

    def test_base_error_is_exception(self):
        assert issubclass({error_base}, Exception)
"""

TEST_EXAMPLE = """\
from pathlib import Path


class TestExample:
    def test_placeholder(self):
        # TODO — replace with real tests
        assert True
"""

# ---------------------------------------------------------------------------
# TypeScript runtime files
# ---------------------------------------------------------------------------

PACKAGE_JSON_TEMPLATE = """\
{{
  "name": "{name}",
  "version": "0.1.0",
  "description": "TODO — brief description",
  "type": "module"
}}
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
