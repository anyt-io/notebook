---
name: run-anyt-notebook
description: Run and execute AnyT Notebook (.anyt.md) files. Use when the user wants to run a notebook, execute notebook cells, resume a paused notebook, check notebook execution status, parse or update .anyt files programmatically, or manage notebook workspace state.
---

# Run AnyT Notebook

Execute `.anyt.md` notebook files using the `notebook-cli` command-line tool. This skill teaches you how to install the CLI, run notebooks, handle each cell type, manage workspaces, fill in input forms, handle errors, and resume interrupted runs.

For the complete file format specification, see [references/anyt-notebook-spec.md](references/anyt-notebook-spec.md).

## Prerequisites

Install the CLI globally via npm:

```bash
npm install -g @anytio/notebook-cli
```

Verify installation:

```bash
notebook-cli --help
```

**Requirements:** Node.js >= 22

## Quick Start

Run a notebook end-to-end:

```bash
notebook-cli run path/to/notebook.anyt.md
```

That's it. The CLI parses the file, creates the workspace, and executes all cells sequentially. It handles input prompts interactively, pauses at break cells, and stops on failure.

## How Notebooks Work

An AnyT Notebook (`.anyt.md`) is a markdown file with YAML frontmatter and ordered cell tags. The file stores **structure only** — all execution state lives in a `.anyt/cells/` folder inside the workspace directory.

### File Structure

```yaml
---
schema: "2.1"
name: my-notebook
workdir: anyt_workspace_my_notebook
---

# my-notebook

<note id="note-intro" label="Overview">
This notebook does XYZ.
</note>

<input id="input-config" label="Configuration">
Configure settings before running.

<form type="json">
{"fields": [{"name": "apiKey", "type": "text", "label": "API Key", "required": true}]}
</form>
</input>

<shell id="shell-setup" label="Setup">
mkdir -p src && echo "Ready"
</shell>

<task id="task-main" label="Main Task">
Build the application based on the user's configuration from the input cell.
**Output:** src/app.ts
</task>

<break id="break-review" label="Review">
Check the generated code before continuing.
</break>
```

### Cell Types

| Cell Type | What Happens | Executable |
|-----------|-------------|------------|
| `task` | AI agent (Claude/Codex/Gemini) executes natural language instructions | Yes |
| `shell` | Bash script runs directly | Yes |
| `input` | Pauses for user input (interactive form or JSON values) | Yes |
| `note` | Auto-completes immediately (documentation only) | No |
| `break` | Pauses and waits for user to continue | Yes |

### Cell Attributes

All cells require an `id` (slug format: lowercase, alphanumeric, hyphens). Optional attributes:

- `label` — Human-friendly display name
- `agent` — Override the default agent (`claude`, `codex`, or `gemini`)
- `skip` — Only for break cells; set to `"true"` to auto-skip

### Workspace and State

The `workdir` field in frontmatter sets the workspace directory (relative to the notebook file). All execution state is stored in `{workdir}/.anyt/cells/{cell-id}/`:

```
{workdir}/.anyt/cells/
├── {task-id}/
│   ├── task.md          # Enriched task description
│   ├── summary.md       # Agent-written summary
│   ├── output.log       # Formatted output
│   └── .done            # Completion marker (JSON with outputs, duration)
├── {shell-id}/
│   ├── script.sh        # Shell script content
│   ├── output.log       # stdout/stderr
│   └── .done            # Completion marker
├── {input-id}/
│   ├── response.json    # User's form values
│   └── .done
├── {note-id}/
│   └── .done
└── {break-id}/
    └── .done
```

## CLI Commands Reference

### `run` — Run All Cells

Run all pending cells sequentially:

```bash
notebook-cli run notebook.anyt.md
```

**Key flags:**

| Flag | Description |
|------|-------------|
| `--rerun` | Reset all cells and start fresh |
| `--skip-breaks` | Auto-continue all break cells |
| `--from <cellId>` | Start from a specific cell (skip earlier ones) |
| `--auto-input <path>` | JSON file with pre-filled input values |
| `--agent <type>` | Override agent (`claude`, `codex`, `gemini`) |
| `--model <name>` | Override the model name |
| `--permission-mode <mode>` | Override the agent's permission mode |
| `--verbose` | Show agent tool call names in output |

**Examples:**

```bash
# Re-run entire notebook from scratch
notebook-cli run notebook.anyt.md --rerun

# Resume from a specific cell
notebook-cli run notebook.anyt.md --from task-main

# Skip all break points for unattended execution
notebook-cli run notebook.anyt.md --skip-breaks

# Pre-fill all input cells from a JSON file
notebook-cli run notebook.anyt.md --auto-input values.json

# Use a specific agent and model
notebook-cli run notebook.anyt.md --agent claude --model claude-sonnet-4-5-20250514
```

### `continue` — Resume Execution

Alias for `run` — resumes from the first uncompleted cell:

```bash
notebook-cli continue notebook.anyt.md
```

### `status` — Check Execution Status

Show all cells and their current status:

```bash
notebook-cli status notebook.anyt.md
```

Output:

```
Notebook: my-notebook
Workdir:  anyt_workspace_my_notebook

ID              TYPE   STATUS   LABEL
──────────────  ─────  ───────  ────────────────────
note-intro      note   done     Overview
input-config    input  done     Configuration
shell-setup     shell  done     Setup
task-main       task   FAIL     Main Task
break-review    break           Review

Total: 5 | Done: 3 | Pending: 1 | Failed: 1 | Skipped: 0
```

### `run-cell` — Execute a Single Cell

Run one specific cell:

```bash
notebook-cli run-cell notebook.anyt.md task-main
```

Flags: `--agent`, `--model`, `--permission-mode`, `--env-file <path>`, `--verbose`

**Note:** Input cells cannot be run with `run-cell` — use `submit-input` instead.

### `mark-done` — Mark Cell Complete (External Agents)

Mark a cell as done or failed without executing it via the CLI. For external agents that execute task cells directly:

```bash
# Mark as done with summary and output files
notebook-cli mark-done notebook.anyt.md task-main \
  --summary "Created the application" \
  --outputs "src/app.ts,src/db.ts"

# Mark as failed
notebook-cli mark-done notebook.anyt.md task-main \
  --failed --error "Build failed: missing dependency"
```

**Flags:**

| Flag | Description |
|------|-------------|
| `--summary <text>` | Summary of what was accomplished |
| `--outputs <files>` | Comma-separated list of output files |
| `--failed` | Mark as failed instead of done |
| `--error <message>` | Error message (used with `--failed`) |

### `reset` — Reset Cell State

```bash
# Reset a single cell (remove markers, allow re-run)
notebook-cli reset notebook.anyt.md task-main

# Reset all cells
notebook-cli reset notebook.anyt.md

# Reset and delete all cell data (output logs, summaries, etc.)
notebook-cli reset notebook.anyt.md --all
```

### Global Flags

These work with all commands:

| Flag | Description |
|------|-------------|
| `--workspace-dir <path>` | Override the notebook's workspace directory |
| `--json` | Output machine-readable JSON (for agent consumption) |
| `--verbose` | Show agent tool call details during execution |
| `--help` | Show help (use after a command for command-specific help) |

## Handling Input Cells

Input cells pause execution and collect user data. There are three ways to provide values:

### 1. Interactive Prompt (Default)

When running in a terminal, the CLI prompts interactively:

```
Select the stock to review

Stock (Which Stock to review):
  1) Nvidia (default)
  2) Google
  3) Salesforce
Choose [1]: 2
Last days [30]: 12
```

### 2. Pre-filled Values with `--auto-input`

Create a JSON file mapping cell IDs to their values:

```json
{
  "input-config": {
    "apiKey": "sk-test-123",
    "model": "gpt-4"
  },
  "input-settings": {
    "port": 3000,
    "debug": true
  }
}
```

Then run:

```bash
notebook-cli run notebook.anyt.md --auto-input values.json
```

### 3. Submit Values via CLI (for Agents)

When running non-interactively (e.g., from another agent), use `submit-input`:

```bash
# Inline JSON
notebook-cli submit-input notebook.anyt.md input-config \
  --values '{"apiKey": "sk-test-123", "model": "gpt-4"}'

# From a file
notebook-cli submit-input notebook.anyt.md input-config \
  --values-file config.json
```

Then re-run to continue past the input cell:

```bash
notebook-cli continue notebook.anyt.md
```

### Input Field Types

Input cells define forms with these field types:

| Field Type | Value Format | Example |
|------------|-------------|---------|
| `text` / `textarea` | `"string"` | `"hello world"` |
| `number` | `123` | `3000` |
| `checkbox` | `true` / `false` | `true` |
| `select` / `radio` | `"value"` | `"postgres"` |
| `multiselect` | `["v1", "v2"]` | `["auth", "api"]` |
| `file` | `{"filename": "f.jpg", "path": "/abs/path"}` | — |

### Reading Input Values from Previous Cells

Task cells automatically receive context about previous input cells. The CLI enriches each task description with instructions to read responses from `.anyt/cells/{input-id}/response.json`.

## Handling Break Cells

Break cells pause execution for manual review:

- **Interactive terminal:** Prompts "press Enter to continue..."
- **Non-interactive / agent mode:** CLI exits with code `11`, signaling a break. Use `continue-break` to proceed:

```bash
# Mark break as done so execution can continue
notebook-cli continue-break notebook.anyt.md break-review

# Then resume
notebook-cli continue notebook.anyt.md
```

To skip all breaks automatically:

```bash
notebook-cli run notebook.anyt.md --skip-breaks
```

## Using `--workspace-dir`

By default, the workspace is resolved from the notebook's `workdir` frontmatter field, relative to the notebook file. Use `--workspace-dir` to override this:

```bash
# Run with a custom workspace location
notebook-cli run notebook.anyt.md --workspace-dir /tmp/my-workspace

# Check status of a specific workspace
notebook-cli status notebook.anyt.md --workspace-dir /tmp/my-workspace

# Multiple independent runs of the same notebook
notebook-cli run notebook.anyt.md --workspace-dir run-1
notebook-cli run notebook.anyt.md --workspace-dir run-2
```

This is useful for:
- Running the same notebook multiple times with different workspaces
- Pointing to an existing workspace with pre-populated data
- Testing in isolated directories

## Error Handling

### Exit Codes

| Code | Meaning | What to Do |
|------|---------|-----------|
| `0` | Success | All cells completed |
| `1` | Cell failed | Check error output, fix the issue, then `notebook-cli continue` |
| `2` | Usage error | Check flags and arguments — run `notebook-cli <command> --help` |
| `10` | Waiting for input | Use `submit-input` to provide values, then `continue` |
| `11` | Waiting at break | Use `continue-break` to proceed, then `continue` |

### Common Errors and Fixes

**Unknown flag:**
```
Error: Unknown flag '--workspace' for command 'run'. Did you mean '--workspace-dir'?
```
Fix: Use the correct flag name. The CLI suggests alternatives for typos.

**Invalid agent value:**
```
Error: Invalid value 'gpt4' for flag '--agent'. Valid values: claude, codex, gemini
```
Fix: Use one of the three supported agent types.

**File not found:**
```
Error: File not found: notebook.anyt.md
```
Fix: Check the file path. The CLI validates file existence before running.

**Cell execution failure:**
When a task or shell cell fails, the CLI stops and reports the error:
```
[3/5] task: task-main (Main Task)
  Agent: claude
  ✗ Failed (15.2s): Agent exited with code 1
Failed at cell: task-main — Agent exited with code 1
```

To recover:
1. Fix the underlying issue
2. Resume: `notebook-cli continue notebook.anyt.md`

Or reset the failed cell and retry:
1. `notebook-cli reset notebook.anyt.md task-main`
2. `notebook-cli continue notebook.anyt.md`

### JSON Mode for Agents

When running from another agent or script, use `--json` for structured output:

```bash
notebook-cli run notebook.anyt.md --json 2>/dev/null
```

Output:
```json
{
  "ok": true,
  "command": "run",
  "data": {
    "status": "complete",
    "results": [
      {"cellId": "shell-setup", "type": "shell", "status": "done", "duration": 1200},
      {"cellId": "task-main", "type": "task", "status": "done", "duration": 15000}
    ]
  }
}
```

When waiting for input:
```json
{
  "ok": true,
  "command": "run",
  "data": {
    "status": "waiting-input",
    "cellId": "input-config",
    "description": "Configure settings..."
  }
}
```

The `next` command in JSON mode also returns the `workdir` (absolute workspace path):
```json
{
  "ok": true,
  "command": "next",
  "data": {
    "id": "task-main",
    "type": "task",
    "label": "Main Task",
    "description": "...",
    "agent": "claude",
    "workdir": "/absolute/path/to/workspace"
  }
}
```

## Agent-Driven Workflow (Non-Interactive)

When another AI agent runs a notebook, follow this pattern:

```bash
# 1. Check status first
notebook-cli status notebook.anyt.md --json

# 2. Run the notebook
notebook-cli run notebook.anyt.md --json --skip-breaks

# 3. If exit code is 10 (waiting for input), submit values
notebook-cli submit-input notebook.anyt.md input-config \
  --values '{"apiKey": "sk-123"}'

# 4. Resume execution
notebook-cli continue notebook.anyt.md --json --skip-breaks

# 5. Check final status
notebook-cli status notebook.anyt.md --json
```

For fully automated runs, pre-fill all inputs:

```bash
notebook-cli run notebook.anyt.md --auto-input values.json --skip-breaks
```

## Supported Agents

The CLI can execute task cells using different AI agents:

| Agent | Flag Value | CLI Used | Default Permission Mode |
|-------|-----------|----------|------------------------|
| Claude Code | `claude` | `claude` | bypassPermissions |
| Codex | `codex` | `codex` | full-auto |
| Gemini | `gemini` | `gemini` | yolo |

Override per-run: `--agent claude --model claude-sonnet-4-5-20250514`

Agent binaries must be installed and available in PATH. Set custom paths via environment variables: `CLAUDE_BIN_PATH`, `CODEX_BIN_PATH`, `GEMINI_BIN_PATH`.

## .anyt File Format Quick Reference

```yaml
---
schema: "2.1"
name: notebook-name
workdir: anyt_workspace_name
---

# notebook-name

<note id="note-intro" label="Introduction">
Documentation content (auto-completes).
</note>

<input id="input-config" label="Config">
Description of what input is needed.

<form type="json">
{"fields": [
  {"name": "port", "type": "number", "label": "Port", "default": 3000},
  {"name": "db", "type": "select", "label": "Database", "options": [
    {"value": "sqlite", "label": "SQLite"},
    {"value": "postgres", "label": "PostgreSQL"}
  ]}
]}
</form>
</input>

<shell id="shell-setup" label="Setup">
mkdir -p src && npm init -y
</shell>

<task id="task-build" label="Build App">
Create the application using the user's configuration.
Read input from .anyt/cells/input-config/response.json.
**Output:** src/app.ts, src/db.ts
</task>

<break id="break-review" label="Review" skip="true">
Review the generated code.
</break>
```

**Cell attributes:** `id` (required), `label` (optional), `agent` (optional), `skip` (break cells only).
