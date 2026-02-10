# Skill Development Guide

This guide defines the conventions for building PSPM skills in this repository.

## Folder Structure

Every skill lives under `skills/<skill-name>/` and follows this layout:

```
skills/<skill-name>/
├── SKILL.md              # Skill documentation (usage only)
├── pspm.json             # PSPM manifest (name, version, metadata)
└── runtime/              # Isolated execution environment
    ├── pyproject.toml    # Python: deps + tool config (uv)
    ├── uv.lock           # Python: pinned dependency versions
    ├── .python-version   # Python: version pin
    ├── package.json      # TypeScript: deps + scripts (bun)
    ├── bun.lock          # TypeScript: pinned dependency versions
    └── <script files>    # Flat in runtime/, no nested scripts/ folder
```

The top level of each skill holds **standalone skill files** (SKILL.md, pspm.json, config).
The `runtime/` folder is a **self-contained project** with its own dependencies — fully isolated per skill.

## Runtime Environments

### Python Skills — use `uv`

Each Python skill's `runtime/` is a uv project.

**Setup:**
```bash
cd skills/<skill-name>/runtime
uv init --name <skill-name>
uv add <runtime-deps>            # e.g. yt-dlp
uv add --dev ruff pyright        # dev tooling
```

**Execution (from the skill folder):**
```bash
uv run --project runtime runtime/<script>.py [args]
```

**Dev checks (from runtime/):**
```bash
uv run ruff check .
uv run ruff format .
uv run python -m pyright .
```

**pyproject.toml conventions:**
```toml
[project]
requires-python = ">=3.10"

[tool.ruff]
target-version = "py310"
line-length = 120

[tool.ruff.lint]
select = ["E", "W", "F", "I", "UP", "B", "SIM", "RUF"]

[tool.pyright]
pythonVersion = "3.10"
include = ["."]
typeCheckingMode = "standard"
```

### TypeScript Skills — use `bun`

Each TypeScript skill's `runtime/` is a bun project.

**Setup:**
```bash
cd skills/<skill-name>/runtime
bun init
bun add <runtime-deps>
```

**Execution (from the skill folder):**
```bash
bun run runtime/<script>.ts [args]
```

## SKILL.md Conventions

Following the [Anthropic skill-creator guidelines](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md):

### YAML Frontmatter (required)

Every SKILL.md must start with YAML frontmatter containing `name` and `description`:

```yaml
---
name: skill-name
description: What this skill does. Use when the user wants to [specific triggers]. Supports [key capabilities].
---
```

- `name`: Skill identifier (matches folder name)
- `description`: Primary triggering mechanism — Claude uses this to decide when to load the skill. Include what the skill does and specific use contexts.

### Body

Write instructions for Claude on how to use the skill and its bundled scripts. Use imperative form. Keep it concise — only include what Claude cannot infer.

- Prerequisites (external tools needed)
- Usage commands with `uv run --project runtime` or `bun run runtime/`
- Options/flags reference
- Limitations

## pspm.json

Every skill has a `pspm.json` manifest for PSPM registry compatibility:

```json
{
  "name": "@user/<username>/<skill-name>",
  "version": "1.0.0",
  "description": "Brief description"
}
```

## Output Directory

Skills that produce output files should default to an `output/` directory inside the skill folder (resolved from the script's location, not cwd). The script should auto-create it.

`output/` is globally gitignored.

## .gitignore

The repo-level `.gitignore` covers all skills:

```
.venv/
.ruff_cache/
__pycache__/
*.pyc
output/
node_modules/
bun.lockb
```

Skill-specific ignores go in `skills/<skill-name>/.gitignore`.

## Testing

Python skills should include tests in `runtime/tests/` using pytest:

```bash
cd skills/<skill-name>/runtime
uv add --dev pytest
uv run pytest tests/ -v
```

Add pytest config to `pyproject.toml`:
```toml
[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
```

## .pspmignore

Each skill should have a `.pspmignore` at its root to exclude dev files from PSPM publishing (while keeping them in git):

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

## Adding a New Skill

1. Create the folder: `mkdir -p skills/<skill-name>/runtime`
2. Add `SKILL.md` with YAML frontmatter (`name`, `description`) at the skill root
3. Add `pspm.json` at the skill root
4. Add `.pspmignore` at the skill root
5. Initialize the runtime:
   - Python: `cd skills/<skill-name>/runtime && uv init --name <skill-name>`
   - TypeScript: `cd skills/<skill-name>/runtime && bun init`
6. Add dependencies and write scripts in `runtime/`
7. Add `runtime/.gitignore` for dev artifacts
8. Add tests in `runtime/tests/`
9. Test execution from the skill folder using `--project` flag
