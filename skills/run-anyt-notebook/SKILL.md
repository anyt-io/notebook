---
name: run-anyt-notebook
description: Run and execute AnyT Notebook (.anyt.md) files. Use when the user wants to run a notebook, execute notebook cells, resume a paused notebook, check notebook execution status, parse or update .anyt files programmatically, or manage notebook workspace state.
---

# Run AnyT Notebook

Execute `.anyt.md` notebook files by parsing cells and running them sequentially. This skill teaches you how to handle workspaces, load environment variables, execute each cell type, and track execution state.

For the complete file format specification, see [references/anyt-notebook-spec.md](references/anyt-notebook-spec.md).

## Prerequisites

- `uv` (Python package manager) — for running the parser and state management scripts

## Overview

An AnyT Notebook (`.anyt.md`) contains YAML frontmatter and ordered cell tags. You — the coding agent — are the runtime. You parse the notebook, set up the workspace, and execute each cell in order.

**Cell types and how you handle them:**

| Cell Type | What You Do |
|-----------|-------------|
| `task` | Execute the natural language instructions yourself (you are the AI agent) |
| `shell` | Run the bash script via the Bash tool |
| `input` | Ask the user for the requested information, or read from saved response |
| `note` | Display the content to the user, then continue |
| `break` | Pause and ask the user if they want to continue |

## Step-by-Step Execution

### 1. Parse the Notebook

Use the parser to get structured JSON:

```bash
uv run --project runtime runtime/parse_notebook.py path/to/notebook.anyt.md
```

This outputs JSON with `schema`, `name`, `workdir`, `env_file`, `cells`, etc.

To validate before running:

```bash
uv run --project runtime runtime/parse_notebook.py path/to/notebook.anyt.md --validate
```

To inspect a single cell:

```bash
uv run --project runtime runtime/parse_notebook.py path/to/notebook.anyt.md --cell setup-env
```

### 2. Set Up the Workspace

The `workdir` field (from frontmatter) is the working directory for all execution. It is relative to the notebook file's location.

```bash
# Resolve workdir relative to the notebook file
NOTEBOOK_DIR=$(dirname path/to/notebook.anyt.md)
WORKDIR="$NOTEBOOK_DIR/<workdir-value>"

# Create the workspace
mkdir -p "$WORKDIR"

# Create state directory
mkdir -p "$WORKDIR/.anyt/cells"
```

**Important:** All file paths in cells are relative to `workdir`. When running shell cells or executing task instructions, `cd` into the workdir first.

### 3. Load Environment Variables

If `env_file` is specified (defaults to `.env`), load it before executing cells:

```bash
# Resolve env file path relative to notebook directory
ENV_FILE="$NOTEBOOK_DIR/<env_file-value>"

# Load if it exists
if [ -f "$ENV_FILE" ]; then
  set -a
  source "$ENV_FILE"
  set +a
fi
```

The `.env` file contains secrets like API keys. Never display the contents to the user. If the `.env` file doesn't exist, continue without it — it's optional.

**Priority (highest to lowest):**
1. `.env` file
2. Shell profile (`~/.zshrc`, `~/.bash_profile`)

### 4. Execute Cells Sequentially

Process cells in order. Stop on failure.

#### Task Cells

You ARE the AI agent. Execute the task instructions yourself:

1. Read the cell content — it contains natural language instructions
2. `cd` to the workdir
3. Execute the instructions (create files, write code, etc.)
4. Save state:
   ```bash
   uv run --project runtime runtime/manage_state.py "$WORKDIR" mark-done --cell <cell-id>
   ```
5. If a task references a previous input cell, read the input response first:
   ```bash
   uv run --project runtime runtime/manage_state.py "$WORKDIR" read-input --cell <input-cell-id>
   ```

**Task cell conventions:**
- `**Output:** file1, file2` declares expected output files
- Reference previous cells' output files by their paths relative to workdir
- If the cell has an `agent` attribute, note it but you still execute it (you are the agent)

#### Shell Cells

Run the script content directly:

1. `cd` to the workdir
2. Execute the bash script using the Bash tool
3. Save script and output:
   ```bash
   uv run --project runtime runtime/manage_state.py "$WORKDIR" mark-done --cell <cell-id>
   ```
4. If the script exits with non-zero, mark as failed:
   ```bash
   uv run --project runtime runtime/manage_state.py "$WORKDIR" mark-failed --cell <cell-id> --error "Exit code: N"
   ```

**Important:** Shell cells run in the workdir. Do NOT prefix paths with the workdir name inside the script.

#### Input Cells

Input cells pause execution and collect information from the user. In VS Code this renders as a GUI form; when you run a notebook as a coding agent, you present the fields conversationally and collect answers.

**Step-by-step procedure:**

1. **Check for a saved response first.** A previous run may have already collected this input:
   ```bash
   uv run --project runtime runtime/manage_state.py "$WORKDIR" read-input --cell <cell-id>
   ```
   If a response exists (exit code 0), use those values and skip to step 6.

2. **Extract the form fields** from the cell content:
   ```bash
   # Get structured JSON of all fields (type, label, options, defaults, validation)
   uv run --project runtime runtime/parse_notebook.py path/to/notebook.anyt.md --form <cell-id>

   # Or get a human-readable prompt to present to the user
   uv run --project runtime runtime/parse_notebook.py path/to/notebook.anyt.md --form-prompt <cell-id>
   ```

   The `--form` output is structured JSON:
   ```json
   [
     {"name": "projectName", "field_type": "text", "label": "Project Name", "required": true, "default": null, ...},
     {"name": "database", "field_type": "select", "label": "Database", "options": [{"value": "sqlite", "label": "SQLite"}, ...], "default": "sqlite", ...}
   ]
   ```

   The `--form-prompt` output is a human-readable summary:
   ```
   ## Configure Your Project

   - **Project Name** (required)
   - **Database** — Choose one: SQLite, PostgreSQL [default: sqlite]
   - **Features** — Choose one or more: Auth, API, Database
   - **Dev Port** — Number (min: 1024, max: 65535) [default: 3000]
   - **Public Repository** — Yes/No
   ```

3. **Present fields to the user.** Show the `--form-prompt` output and ask the user to provide values. For each field type:
   - **text / textarea**: Ask for free-form text input
   - **number**: Ask for a numeric value
   - **checkbox**: Ask Yes/No
   - **select / radio**: Present the options and ask the user to pick one
   - **multiselect**: Present the options and ask the user to pick one or more
   - **file**: Ask for a file path on their local system

   If a field has a `default`, tell the user they can skip it to use the default. If a field is `required`, ensure the user provides a value.

4. **Validate responses.** Check against the field's `validation` rules:
   - `minLength` / `maxLength` for text fields
   - `pattern` (regex) for text fields
   - `min` / `max` for number fields
   - `minItems` / `maxItems` for multiselect fields
   - `minFiles` / `maxFiles` for file fields with `multiple`

   If validation fails, tell the user what's wrong and ask again.

5. **Save the response.** Write a `response.json` file to the state directory:
   ```bash
   mkdir -p "$WORKDIR/.anyt/cells/<cell-id>"
   ```
   Then write `$WORKDIR/.anyt/cells/<cell-id>/response.json` with this format:
   ```json
   {
     "values": {
       "projectName": "my-app",
       "database": "postgres",
       "features": ["auth", "api"],
       "port": 3000,
       "isPublic": true
     },
     "timestamp": "2026-03-10T12:00:00Z"
   }
   ```

   **Value formats by field type:**
   | Field Type | JSON Value Format |
   |------------|-------------------|
   | `text` / `textarea` | `"string"` |
   | `number` | `123` |
   | `checkbox` | `true` / `false` |
   | `select` / `radio` | `"value"` (the `value` from the selected option) |
   | `multiselect` | `["value1", "value2"]` |
   | `file` (single) | `{"filename": "photo.jpg", "path": "/abs/path/photo.jpg"}` |
   | `file` (multiple) | `[{"filename": "a.pdf", "path": "/abs/a.pdf"}, ...]` |

6. **Mark done:**
   ```bash
   uv run --project runtime runtime/manage_state.py "$WORKDIR" mark-done --cell <cell-id>
   ```

**Input cells without forms:** Some input cells have no `<form>` block — just markdown text with action buttons. In this case, display the content to the user and ask how they want to proceed (e.g., continue, edit, skip).

**Making input responses available to later task cells:** When a subsequent task cell references a previous input cell (e.g., "Based on the user's input from the config step"), read the saved response before executing:
```bash
uv run --project runtime runtime/manage_state.py "$WORKDIR" read-input --cell <input-cell-id>
```
Use the returned JSON values as context when executing the task instructions. For example, if the response has `"database": "postgres"`, use that to guide your code generation.

#### Note Cells

Display the markdown content to the user and continue immediately:

```bash
uv run --project runtime runtime/manage_state.py "$WORKDIR" mark-done --cell <cell-id>
```

#### Break Cells

Pause and ask the user whether to continue:

1. If the cell has `skip="true"`, auto-continue:
   ```bash
   uv run --project runtime runtime/manage_state.py "$WORKDIR" mark-done --cell <cell-id>
   ```
2. Otherwise, display the cell content and ask: "Ready to continue?"
3. Wait for user confirmation before proceeding.

### 5. Handle Failures

If any cell fails, stop execution. Report what failed and why. The user can fix the issue and ask you to resume from the failed cell.

To resume from a specific cell, re-run the execution loop starting at that cell. Previous cells with `.done` markers are skipped.

### 6. Check Execution Status

```bash
uv run --project runtime runtime/manage_state.py "$WORKDIR" status --cells cell-1 cell-2 cell-3
```

### 7. Reset State

Reset a single cell:
```bash
uv run --project runtime runtime/manage_state.py "$WORKDIR" reset --cell <cell-id>
```

Reset all cells:
```bash
uv run --project runtime runtime/manage_state.py "$WORKDIR" reset
```

## Updating Notebooks

To modify a notebook's cell content:

```bash
uv run --project runtime runtime/update_notebook.py path/to/notebook.anyt.md update --cell <cell-id> --content "New content here"
```

To add a new cell:

```bash
uv run --project runtime runtime/update_notebook.py path/to/notebook.anyt.md add --type task --id new-task --content "Do something" --label "New Task" --after existing-cell-id
```

To remove a cell:

```bash
uv run --project runtime runtime/update_notebook.py path/to/notebook.anyt.md remove --cell <cell-id>
```

## State Storage Layout

All execution state lives in `{workdir}/.anyt/cells/`:

```
{workdir}/.anyt/cells/
├── {task-id}/
│   ├── task.md          # Task description
│   ├── summary.md       # Summary of what was done
│   ├── output.log       # Output log
│   └── .done/.failed    # Completion marker (JSON)
├── {shell-id}/
│   ├── script.sh        # Script content
│   ├── output.log       # stdout/stderr
│   └── .done/.failed
├── {input-id}/
│   ├── response.json    # {"values": {...}, "timestamp": "..."}
│   └── .done
├── {note-id}/
│   └── .done
└── {break-id}/
    └── .done
```

## .anyt File Format Quick Reference

```yaml
---
schema: "2.0"
name: notebook-name
workdir: anyt_workspace_name
env_file: ".env"
---

# notebook-name

<shell id="setup" label="Setup">
mkdir -p src
</shell>

<task id="create-api" label="Create API">
Create a REST API with Express.js.
**Output:** src/app.ts
</task>

<input id="config" label="Config">
<form type="json">
{"fields": [{"name": "port", "type": "number", "label": "Port", "default": 3000}]}
</form>
</input>

<break id="review" label="Review">
Check the output before continuing.
</break>

<note id="done" label="Complete">
All done.
</note>
```

**Cell attributes:** `id` (required), `label` (optional), `agent` (optional: `claude`/`codex`/`gemini`), `skip` (break cells only, value `"true"`).

## Limitations

- Input cells with `file` type fields reference local filesystem paths — verify files exist before using them.
- The `agent` attribute is informational when you are the sole executing agent.
- Shell cells assume bash. Scripts with `#!/bin/bash` shebang are recommended.
- Environment variables from `.env` must be loaded before each shell cell execution if running cells individually.
