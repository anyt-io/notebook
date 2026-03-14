---
name: run-anyt-notebook-openclaw
description: Run AnyT Notebook (.anyt.md) files as the coding agent. For agents like OpenClaw that execute task cells directly instead of spawning sub-agents. Use when the user wants to run a notebook and you need to act as both the orchestrator and the coding agent.
---

# Run AnyT Notebook (Agent-as-Executor)

Execute `.anyt.md` notebook files where **you are the coding agent**. Unlike the standard workflow that spawns sub-agents (Claude/Codex/Gemini) for task cells, you execute task cells directly — reading the task description, doing the work in the workspace, and marking completion via the CLI.

The CLI handles orchestration (cell ordering, state tracking, shell execution, completion markers), while you handle the actual coding work for task cells.

For the complete file format specification, see [references/anyt-notebook-spec.md](references/anyt-notebook-spec.md).

## Prerequisites

Install the CLI globally via npm:

```bash
npm install -g @anytio/notebook-cli
```

**Requirements:** Node.js >= 22

## Execution Loop

Run notebooks one cell at a time using this loop:

```
1. Get next cell:     notebook-cli next {file} --json
2. Handle by type:    (see Cell Type Handlers below)
3. Repeat until:      next returns null (all cells complete)
```

### Step-by-Step

**1. Get the next pending cell:**

```bash
notebook-cli next notebook.anyt.md --json 2>/dev/null
```

Response when a cell is pending:
```json
{
  "ok": true,
  "command": "next",
  "data": {
    "id": "task-build",
    "type": "task",
    "label": "Build App",
    "description": "Create the application using user config...",
    "agent": "claude",
    "workdir": "/absolute/path/to/workspace"
  }
}
```

Response when all cells are complete:
```json
{
  "ok": true,
  "command": "next",
  "data": null
}
```

The `workdir` field is the absolute path to the workspace directory where you should do your work.

**2. Handle the cell based on its type** (see handlers below).

**3. Repeat** — call `next` again to get the next pending cell. Continue until `data` is `null`.

## Cell Type Handlers

### `shell` — Run via CLI

Shell cells are executed by the CLI directly:

```bash
notebook-cli run-cell notebook.anyt.md {cell-id} --json 2>/dev/null
```

The CLI runs the bash script in the workspace and writes all markers automatically.

### `note` — Skip

Note cells are non-executable documentation. The `next` command skips them automatically — you never see them.

### `input` — Submit Values via CLI

Input cells require form values. Read the `description` from the `next` output to understand what fields are needed.

```bash
notebook-cli submit-input notebook.anyt.md {cell-id} \
  --values '{"fieldName": "value", "port": 3000}'
```

The description contains the form schema as a `<form type="json">` block with field definitions (name, type, label, default, options).

### `break` — Continue via CLI

Break cells pause for review. To proceed:

```bash
notebook-cli continue-break notebook.anyt.md {cell-id}
```

### `task` — Execute Directly (You Are the Agent)

This is the key difference. For task cells, **you do the work yourself** instead of spawning a sub-agent.

**Step 1: Understand the task**

The `description` field from the `next` output contains the task instructions. The `workdir` field tells you where to work.

To get richer context (previous cell outputs, input values), check the `.anyt/cells/` directory in the workspace:

- **Previous task summaries:** `{workdir}/.anyt/cells/{prev-cell-id}/summary.md`
- **Previous task outputs:** `{workdir}/.anyt/cells/{prev-cell-id}/.done` — contains `{"outputs": ["file1", "file2"]}`
- **Input cell responses:** `{workdir}/.anyt/cells/{input-cell-id}/response.json` — contains `{"values": {...}}`

**Step 2: Do the work**

Change to the workspace directory and execute the task — write code, run commands, create files, etc. This is where you act as the coding agent.

**Step 3: Mark completion via CLI**

Use the `mark-done` command to record what you did:

**On success:**

```bash
notebook-cli mark-done notebook.anyt.md {cell-id} \
  --summary "Created Express server with auth middleware" \
  --outputs "src/index.ts,src/routes.ts,src/middleware/auth.ts"
```

- `--summary` — Brief description of what was accomplished
- `--outputs` — Comma-separated list of key files created or modified

**On failure:**

```bash
notebook-cli mark-done notebook.anyt.md {cell-id} \
  --failed --error "Could not connect to database: ECONNREFUSED"
```

## Complete Example

Given this notebook (`app.anyt.md`):

```yaml
---
schema: "2.0"
name: build-app
workdir: anyt_workspace_build_app
---

# build-app

<note id="note-intro">
This notebook builds a web application.
</note>

<input id="input-config" label="Configuration">
Choose your settings.

<form type="json">
{"fields": [
  {"name": "framework", "type": "select", "label": "Framework", "options": [
    {"value": "express", "label": "Express"},
    {"value": "hono", "label": "Hono"}
  ]},
  {"name": "port", "type": "number", "label": "Port", "default": 3000}
]}
</form>
</input>

<shell id="shell-init">
mkdir -p src && npm init -y
</shell>

<task id="task-build" label="Build Server">
Create a web server using the framework and port from input-config.
Read settings from .anyt/cells/input-config/response.json.
**Output:** src/index.ts, src/routes.ts
</task>

<break id="break-review" label="Review Code">
Check the generated code before running.
</break>

<shell id="shell-test">
npm test
</shell>
```

### Execution walkthrough:

```bash
# 1. Get first cell (notes are skipped automatically)
notebook-cli next app.anyt.md --json 2>/dev/null
# → input-config (input type), workdir: ".../anyt_workspace_build_app"

# 2. Submit input values
notebook-cli submit-input app.anyt.md input-config \
  --values '{"framework": "hono", "port": 8080}'

# 3. Get next cell
notebook-cli next app.anyt.md --json 2>/dev/null
# → shell-init (shell type)

# 4. Run shell cell
notebook-cli run-cell app.anyt.md shell-init --json 2>/dev/null

# 5. Get next cell
notebook-cli next app.anyt.md --json 2>/dev/null
# → task-build (task type) — YOU execute this!

# 6. Read input values for context
cat anyt_workspace_build_app/.anyt/cells/input-config/response.json

# 7. Do the work in workspace directory
cd anyt_workspace_build_app
# ... write src/index.ts, src/routes.ts using Hono on port 8080 ...

# 8. Mark task as done
notebook-cli mark-done app.anyt.md task-build \
  --summary "Created Hono server on port 8080 with routes" \
  --outputs "src/index.ts,src/routes.ts"

# 9. Get next cell
notebook-cli next app.anyt.md --json 2>/dev/null
# → break-review (break type)

# 10. Continue past break
notebook-cli continue-break app.anyt.md break-review

# 11. Get next cell
notebook-cli next app.anyt.md --json 2>/dev/null
# → shell-test (shell type)

# 12. Run shell cell
notebook-cli run-cell app.anyt.md shell-test --json 2>/dev/null

# 13. Get next cell
notebook-cli next app.anyt.md --json 2>/dev/null
# → null (all complete!)
```

## Checking Status

At any point, check overall notebook status:

```bash
notebook-cli status app.anyt.md --json 2>/dev/null
```

Human-readable format:
```bash
notebook-cli status app.anyt.md
```

## Resetting Cells

To re-run a specific cell:

```bash
notebook-cli reset app.anyt.md {cell-id}
```

To reset all cells:

```bash
notebook-cli reset app.anyt.md
```

To reset and delete all cell data (outputs, logs, etc.):

```bash
notebook-cli reset app.anyt.md --all
```

## Using `--workspace-dir`

Override the workspace directory for independent runs:

```bash
# All CLI commands accept this flag
notebook-cli next app.anyt.md --workspace-dir /custom/workspace --json
notebook-cli run-cell app.anyt.md shell-init --workspace-dir /custom/workspace --json
notebook-cli mark-done app.anyt.md task-build --workspace-dir /custom/workspace \
  --summary "Done" --outputs "src/app.ts"
```

## Error Recovery

If a cell fails:

1. Check what went wrong:
   ```bash
   notebook-cli status app.anyt.md
   ```

2. Fix the issue in the workspace.

3. Reset the failed cell:
   ```bash
   notebook-cli reset app.anyt.md {failed-cell-id}
   ```

4. Resume the loop — call `next` again to pick up from where you left off.

## Exit Codes Reference

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Cell failed |
| `2` | Usage error (bad flags/args) |
| `10` | Waiting for input (use `submit-input`) |
| `11` | Waiting at break (use `continue-break`) |
