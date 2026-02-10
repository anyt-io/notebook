---
name: pspm-skill-creator
description: Guide for creating PSPM skills with isolated runtime environments. Use when users want to create a new PSPM skill, scaffold a skill project, initialize a skill with uv or bun, validate a skill's SKILL.md frontmatter, or package a skill into a distributable .skill file.
---

# PSPM Skill Creator

This skill provides guidance and tooling for creating PSPM skills — self-contained prompt skill packages for AI coding agents.

Reference: [Anthropic skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator) for upstream design principles.

## About PSPM Skills

PSPM skills are modular packages that extend AI coding agents (Claude Code, Cursor, Windsurf, Gemini CLI) with specialized capabilities. Each skill is a self-contained folder with documentation, metadata, and an isolated runtime environment.

### Skill Structure

```
skills/<skill-name>/
├── SKILL.md              # Usage documentation (loaded by AI agents)
├── pspm.json             # PSPM manifest (name, version, metadata)
├── .pspmignore           # Files excluded from PSPM publishing
└── runtime/              # Isolated execution environment
    ├── pyproject.toml    # Python: deps + tool config (uv)
    ├── uv.lock           # Python: pinned dependency versions
    ├── package.json      # TypeScript: deps + scripts (bun)
    ├── bun.lock          # TypeScript: pinned dependency versions
    ├── <scripts>.py/.ts  # Flat in runtime/, no nested folders
    └── tests/            # Test files (Python: pytest)
```

### Key Differences from Anthropic Skills

PSPM skills use **isolated runtime environments** instead of bare `scripts/` folders:

| Anthropic skills | PSPM skills |
|------------------|-------------|
| `scripts/foo.py` | `runtime/foo.py` |
| No dependency management | `runtime/pyproject.toml` or `runtime/package.json` |
| `python scripts/foo.py` | `uv run --project runtime runtime/foo.py` |
| `references/` for docs | `references/` for docs (same) |
| `assets/` for templates | Not used — runtime handles everything |

## Prerequisites

- `uv` (Python skills): https://docs.astral.sh/uv/getting-started/installation/
- `bun` (TypeScript skills): https://bun.sh/

## Skill Creation Workflow

### Step 1: Initialize the skill

```bash
uv run --project runtime runtime/init_skill.py <skill-name> --path skills/
```

This creates the full directory structure with template files. For TypeScript skills, add `--type ts`.

### Step 2: Set up the runtime

**Python:**
```bash
cd skills/<skill-name>/runtime
uv add <runtime-deps>
uv add --dev ruff pyright pytest
```

**TypeScript:**
```bash
cd skills/<skill-name>/runtime
bun add <runtime-deps>
```

### Step 3: Write scripts

Place scripts directly in `runtime/`. Use `SKILL_DIR = Path(__file__).resolve().parent.parent` for resolving paths relative to the skill root.

Execute from the skill folder:
```bash
# Python
uv run --project runtime runtime/<script>.py [args]

# TypeScript
bun run runtime/<script>.ts [args]
```

### Step 4: Write SKILL.md

Every SKILL.md must have YAML frontmatter with `name` and `description`:

```yaml
---
name: my-skill
description: What this skill does. Use when the user wants to [triggers]. Supports [capabilities].
---
```

The `description` is the primary triggering mechanism — it determines when the AI agent loads the skill. Be specific about use cases.

Body contains usage instructions in imperative form. Include prerequisites, commands, flags, and limitations. Keep it concise — only include what the AI agent cannot infer.

For design patterns, see [references/output-patterns.md](references/output-patterns.md) and [references/workflows.md](references/workflows.md).

### Step 5: Write pspm.json

```json
{
  "$schema": "https://pspm.dev/schema/v1/pspm.json",
  "name": "<skill-name>",
  "version": "0.1.0",
  "description": "Brief description",
  "author": "Name <email>",
  "license": "Apache-2.0",
  "type": "skill",
  "main": "SKILL.md",
  "files": ["SKILL.md", "runtime"],
  "dependencies": {},
  "private": false
}
```

### Step 6: Add .pspmignore

Exclude dev artifacts from PSPM publishing:

```
runtime/.venv/
runtime/.ruff_cache/
runtime/__pycache__/
runtime/.pytest_cache/
runtime/tests/
runtime/.python-version
runtime/uv.lock
output/
```

### Step 7: Validate

```bash
uv run --project runtime runtime/validate_skill.py skills/<skill-name>
```

### Step 8: Package

```bash
uv run --project runtime runtime/package_skill.py skills/<skill-name> [output-dir]
```

Creates a `.skill` file (ZIP archive) for distribution.

## Dev Checks (Python)

```bash
cd skills/<skill-name>/runtime
uv run ruff check .
uv run ruff format .
uv run python -m pyright .
uv run pytest tests/ -v
```

### pyproject.toml baseline

```toml
[tool.ruff]
target-version = "py310"
line-length = 120

[tool.ruff.lint]
select = ["E", "W", "F", "I", "UP", "B", "SIM", "RUF"]

[tool.pyright]
pythonVersion = "3.10"
include = ["."]
typeCheckingMode = "standard"

[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
```

## Limitations

- Skill names must be kebab-case, max 64 characters
- SKILL.md description max 1024 characters
- Keep SKILL.md body under 500 lines to minimize context bloat
