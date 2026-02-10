# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

This is the AnyT Notebook repository — a VS Code extension that provides a workflow development environment for AI agents. It also includes PSPM (Prompt Skill Package Manager) skills. See the [PSPM CLI](https://github.com/anyt-io/pspm-cli) for more information on skills.

## Repository Structure

```
skills/
└── <skill-name>/
    ├── SKILL.md          # Usage documentation (loaded by AI agents)
    ├── pspm.json         # PSPM manifest
    ├── .pspmignore       # Excludes dev files from PSPM publishing
    └── runtime/          # Isolated execution environment (uv or bun project)
```

Each skill is self-contained. Standalone files (SKILL.md, pspm.json) live at the skill root. All code and dependencies live in `runtime/` — each skill has its own isolated environment.

## Commands

### Running a skill (from `skills/<skill-name>/`)

```bash
uv run --project runtime runtime/<script>.py [args]     # Python
bun run runtime/<script>.ts [args]                       # TypeScript
```

### Dev checks (from `skills/<skill-name>/runtime/`)

```bash
uv run ruff check .          # Lint
uv run ruff format .         # Format
uv run python -m pyright .   # Type check
uv run pytest tests/ -v      # Test
```

### Validate skills (from `skills/pspm-skill-creator/`)

```bash
uv run --project runtime runtime/validate_skill.py ../<skill-name>    # Single skill
uv run --project runtime runtime/validate_all_skills.py ../           # All skills
```

## Conventions

- **Python skills**: Use `uv` for everything. Never use `pip` directly.
- **TypeScript skills**: Use `bun` for everything. Never use `npm` directly.
- **SKILL.md**: Must have YAML frontmatter with `name` and `description`. Body contains usage instructions only — no development docs. Follow [Anthropic skill guidelines](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md).
- **Output**: Skills that produce files should default to `output/` inside the skill folder (auto-created, gitignored).
- **Testing**: Python skills include pytest tests in `runtime/tests/`.

### Python tool config

All Python skills should include ruff and pyright as dev dependencies with this baseline config in `pyproject.toml`:

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
```

## CI

GitHub Actions (`.github/workflows/validate-skills.yml`) runs on pushes/PRs to `main` that touch `skills/`:
1. Validates all skills via `validate_all_skills.py`
2. Auto-discovers Python skills with `runtime/pyproject.toml`
3. Runs lint (ruff), type check (pyright), and tests (pytest) for each discovered skill

## Skill Guide

See [docs/skill-development-guide.md](docs/skill-development-guide.md) for the full skill development conventions.
