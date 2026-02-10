# AnyT Notebook File Specification

> **Spec version**: `2.1`
> **Schema version**: `2.0`
> **Last updated**: 2026-02-10
> **Purpose**: Complete specification for generating valid `.anyt.md` notebook files.
> This document is designed to be consumed by AI systems as a reference for
> creating, editing, and validating AnyT notebooks.

### Spec Versions

| Spec Version | Schema Version | Date | Description |
|--------------|----------------|------|-------------|
| **2.1** | **2.0** | 2026-02-10 | Add `label` attribute. Cell IDs read-only in UI. |
| 2.0 | 2.0 | 2026-02-05 | Initial schema 2.0. Structure-only file with folder-based state. |

### Changelog

#### 2.1 (2026-02-10)
- **Added** optional `label` attribute on all cell types for human-friendly display names
- **Added** validation rules 11-12 for valid attributes and label format
- **Changed** UI behavior: label is now the primary cell name; cell ID is read-only
- **Removed** workflow inputs feature from frontmatter

#### 2.0 (2026-02-05)
- Initial schema 2.0 specification
- Structure-only `.anyt.md` file format — all runtime state stored in `.anyt/cells/` folders
- Five cell types: `task`, `shell`, `input`, `note`, `break`
- JSON-only form format for input cells
- Shell environment variable support with `env_file` and login shell

---

## File Format Overview

An `.anyt.md` file is a plain-text document with two sections:

1. **YAML Frontmatter** — Notebook metadata between `---` delimiters
2. **Body** — A markdown heading followed by ordered cell tags

The file stores **structure only**. All runtime state (execution status, outputs, duration) is stored externally in `.anyt/cells/` folders and is never written to the file.

```
---
[YAML frontmatter]
---

# [Notebook Title]

[Cell tags in execution order]
```

---

## 1. YAML Frontmatter

### Required Format

Frontmatter MUST be enclosed between two `---` lines at the very start of the file.

### Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `schema` | `"2.0"` | Yes | — | Always `"2.0"` for new files. Must be the first field. |
| `name` | string | Yes | — | Notebook identifier (used as filename stem and heading) |
| `description` | string | No | — | Human-readable summary |
| `version` | string | No | — | Semantic version (e.g. `"1.0.0"`) |
| `workdir` | string | No | `"anyt_workspace"` | Execution directory (relative to `.anyt.md` file or absolute) |

### Working Directory

The `workdir` field sets the current working directory for all cell execution. All file paths in shell scripts and task descriptions should be **relative to workdir**, not include the workdir name.

```yaml
workdir: my-project
```

**Correct usage** (paths relative to workdir):
```bash
mkdir -p src docs        # Creates my-project/src, my-project/docs
cat config.json          # Reads my-project/config.json
```

**Incorrect usage** (creates nested folders):
```bash
mkdir -p my-project/src  # Wrong! Creates my-project/my-project/src
cat my-project/config.json  # Wrong! Looks for my-project/my-project/config.json
```
| `env_file` | string | No | `".env"` | Path to .env file (relative to notebook or absolute) |
| `dependencies` | object | No | — | Skill dependencies as `name: version` pairs |

### Minimal Valid Frontmatter

```yaml
---
schema: "2.0"
name: my-notebook
workdir: output
---
```

### Environment Variables

The `env_file` field specifies a path to an environment file containing secrets and configuration:

```yaml
env_file: ".env"              # Default - looks for .env in notebook directory
env_file: "secrets/prod.env"  # Relative path from notebook directory
env_file: "/etc/app/.env"     # Absolute path
```

> **Security Note:** Never put API keys or secrets directly in the notebook file. Always use `env_file` to reference an external `.env` file that is excluded from version control via `.gitignore`.

**Environment variable priority (highest to lowest):**
1. `.env` file (from `env_file` or default `.env` in notebook directory)
2. Shell profile (`~/.zshrc`, `~/.bash_profile`) - loaded via login shell

**Example `.env` file** (create in notebook directory, add to `.gitignore`):
```
# API keys and secrets - DO NOT COMMIT
GEMINI_API_KEY=your-api-key-here
OPENAI_API_KEY=sk-...

# Configuration
DEBUG=true
```

Shell cells run as login shells by default, which sources your shell profile files.

### Full Frontmatter Example

```yaml
---
schema: "2.0"
name: web-scraper
description: Scrape and process website data
version: 1.0.0
workdir: scraper_output
env_file: ".env"  # Optional - defaults to .env in notebook directory
dependencies:
  scraping-tools: "1.0.0"
---
```

---

## 2. Body Structure

After the closing `---` of the frontmatter, the body contains:

1. A markdown heading: `# {name}` (matching the frontmatter `name`)
2. Optional markdown prose (ignored by parser, visible in raw view)
3. Cell tags in execution order

Cells execute sequentially from top to bottom.

---

## 3. Cell Tags

### General Syntax

All cells use XML-like tags with a required `id` attribute and an optional `label` attribute:

```xml
<{type} id="{unique-id}">
{content}
</{type}>

<{type} id="{unique-id}" label="{display name}">
{content}
</{type}>
```

### Attributes

| Attribute | Required | Description |
|-----------|----------|-------------|
| `id` | Yes | Unique technical identifier (slug format). Used for file paths, cross-references, and folder names. Not editable from the UI. |
| `label` | No | Human-friendly display name. Shown as the primary cell name in the UI. Can contain spaces and mixed case. |

When a `label` is set, the UI shows it as the primary name with the `id` displayed as a subtle suffix. When no label is set, the `id` is shown as the cell name.

### Rules

- **Tag names**: Must be one of: `task`, `shell`, `input`, `note`, `break`
- **`id` attribute**: Required on every cell. Must be unique across the entire notebook.
- **ID format**: Use lowercase alphanumeric characters, hyphens, and underscores (slug format). Examples: `setup-env`, `generate-report`, `review-data`
- **`label` attribute**: Optional on every cell. Free-form text for human display. Examples: `"Setup Environment"`, `"Generate API Report"`
- **Content**: Everything between the opening and closing tags (trimmed of leading/trailing whitespace)
- **No nesting**: Cell tags cannot be nested inside other cell tags
- **No runtime attributes**: Do NOT include `status`, `duration`, `error`, or other runtime attributes on cell tags.
- **Ordering**: Cells run top-to-bottom. Place dependencies before dependents.
- **Spacing**: Leave a blank line between cell tags for readability

---

## 4. Cell Types

### 4.1 Task Cell

An AI-executable unit. The content is a natural language instruction for an AI agent.

```xml
<task id="unique-id">
Natural language description of what the AI should do.
Can span multiple lines. Markdown formatting is supported.

**Output:** path/to/file1, path/to/file2
</task>

<task id="unique-id" label="Human-Friendly Name">
Same content, but displayed with a readable label in the UI.
</task>
```

**Content guidelines:**
- Write clear, specific instructions
- Reference input variables from frontmatter where relevant
- Reference files created by previous cells where relevant
- Use `**Output:** file1, file2` to declare expected output files (parsed by the system)
- Markdown formatting is preserved and passed to the AI agent

**Examples:**
```xml
<task id="create-api" label="Create REST API">
Create a REST API with the following endpoints:
- GET /users - List all users
- POST /users - Create a new user
- GET /users/:id - Get user by ID

Use Express.js with TypeScript. Include proper error handling
and input validation.

**Output:** src/app.ts, src/routes/users.ts
</task>
```

### 4.2 Shell Cell

Executes a shell script directly (no AI involvement). The content is a bash script.

```xml
<shell id="unique-id">
#!/bin/bash
command1
command2
</shell>
```

**Content guidelines:**
- Write valid bash scripts
- The `#!/bin/bash` shebang is optional but recommended
- stdout and stderr are captured to `output.log`
- Exit code 0 = success, non-zero = failure
- Use for deterministic operations: installing dependencies, running builds, creating directories

**Example:**
```xml
<shell id="setup-env" label="Install Dependencies">
mkdir -p src tests docs
npm init -y
npm install express typescript @types/express
npx tsc --init
</shell>
```

### 4.3 Input Cell

Pauses execution and displays a form to the user. Execution resumes when the user submits.

```xml
<input id="unique-id">
Markdown description of what input is needed.

<form type="json">
{
  "fields": [
    { "name": "fieldName", "type": "text", "label": "Label" }
  ]
}
</form>
</input>

<input id="unique-id" label="Display Name">
Same content, but displayed with a readable label in the UI.
</input>
```

**Content structure:**
1. Markdown text explaining what the user should provide (displayed above the form)
2. A `<form type="json">` block defining form fields as a JSON object

**Form JSON format:**

The `<form>` block contains a JSON object with a `fields` array. Each field object has the following properties:

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `name` | string | Yes | Unique field identifier (used in response JSON) |
| `type` | string | Yes | Field type (see below) |
| `label` | string | Yes | Display label shown to user |
| `description` | string | No | Help text shown below field |
| `required` | boolean | No | Whether field must be filled |
| `default` | varies | No | Default value |
| `placeholder` | string | No | Placeholder text (text, textarea, number) |
| `options` | array | Conditional | Options for select, radio, multiselect |
| `rows` | number | No | Number of rows for textarea (default: 3) |
| `validation` | object | No | Validation rules (see below) |

**Supported field types:**

| Type | Description |
|------|-------------|
| `text` | Single-line text input |
| `textarea` | Multi-line text input |
| `number` | Numeric input |
| `checkbox` | Boolean toggle |
| `select` | Dropdown (single selection) |
| `radio` | Radio button group |
| `multiselect` | Checkbox group (multiple selection) |

**Options** (for select, radio, multiselect): array of objects with `value` and `label`:
```json
"options": [
  { "value": "sqlite", "label": "SQLite" },
  { "value": "postgres", "label": "PostgreSQL" }
]
```

**Validation rules:**

| Rule | Applies to | Type |
|------|-----------|------|
| `minLength` | text, textarea | number |
| `maxLength` | text, textarea | number |
| `pattern` | text | string (regex) |
| `min` | number | number |
| `max` | number | number |
| `step` | number | number |
| `minItems` | multiselect | number |
| `maxItems` | multiselect | number |

**Example:**
```xml
<input id="project-config" label="Project Configuration">
## Configure Your Project

Set up the initial project parameters:

<form type="json">
{
  "fields": [
    {
      "name": "projectName",
      "type": "text",
      "label": "Project Name",
      "required": true,
      "validation": { "minLength": 3, "pattern": "^[a-z][a-z0-9-]*$" }
    },
    {
      "name": "description",
      "type": "textarea",
      "label": "Description",
      "rows": 3,
      "placeholder": "Describe your project..."
    },
    {
      "name": "framework",
      "type": "select",
      "label": "Framework",
      "required": true,
      "default": "react",
      "options": [
        { "value": "react", "label": "React" },
        { "value": "vue", "label": "Vue" },
        { "value": "svelte", "label": "Svelte" }
      ]
    },
    {
      "name": "features",
      "type": "multiselect",
      "label": "Features",
      "options": [
        { "value": "auth", "label": "Auth" },
        { "value": "api", "label": "API" },
        { "value": "database", "label": "Database" },
        { "value": "testing", "label": "Testing" }
      ],
      "validation": { "minItems": 1 }
    },
    {
      "name": "port",
      "type": "number",
      "label": "Dev Port",
      "default": 3000,
      "validation": { "min": 1024, "max": 65535 }
    },
    {
      "name": "isPublic",
      "type": "checkbox",
      "label": "Public Repository"
    }
  ]
}
</form>
</input>
```

**Input cells without forms**: If no `<form>` block is present, the cell displays action buttons instead:

```xml
<input id="review">
## Review Output

Check the generated files and choose how to proceed.

**Actions:**
- `continue` - Proceed to next step
- `edit` - Make manual changes first
- `skip` - Skip this step
</input>
```

**Legacy format support**: Forms written in the older DSL or YAML formats are still parsed correctly on load but are always saved as JSON.

### 4.4 Note Cell

A markdown documentation checkpoint. Auto-completes instantly when reached during execution.

```xml
<note id="unique-id">
Markdown content. Used for documentation, progress markers,
or section headers within the notebook.
</note>

<note id="unique-id" label="Display Name">
Same content, but displayed with a readable label in the UI.
</note>
```

**Use cases:**
- Section dividers between phases of work
- Summary checkpoints listing what's been accomplished
- Instructions or context for the human reader

**Example:**
```xml
<note id="phase-1-complete" label="Phase 1 Complete">
## Phase 1 Complete

Generated files:
- `src/app.ts` - Express server
- `src/routes/` - API routes
- `tests/` - Test suite

Next: Configure database and add authentication.
</note>
```

### 4.5 Break Cell

Pauses execution and waits for the user to click "Continue". Used for manual verification points.

```xml
<break id="unique-id">
Description of what the user should review before continuing.
</break>

<break id="unique-id" label="Display Name">
Same content, but displayed with a readable label in the UI.
</break>
```

**Example:**
```xml
<break id="verify-setup" label="Verify Setup">
Review the project structure and configuration files before
proceeding to add the database layer.
</break>
```

---

## 5. State Storage

Schema 2.0 uses **folder-based state storage**. The `.anyt.md` file contains structure only — all execution state lives in `.anyt/cells/` folders.

### Folder Structure

```
{workdir}/
├── .anyt/
│   └── cells/
│       ├── {task-id}/
│       │   ├── task.md            # Task description + context
│       │   ├── summary.md         # Agent-written summary
│       │   ├── output.log         # Formatted output
│       │   ├── raw-output.log     # Raw JSON output
│       │   └── .done              # {"status":"done","duration":30,"outputs":[...]}
│       ├── {shell-id}/
│       │   ├── script.sh          # Shell script content
│       │   ├── output.log         # stdout/stderr output
│       │   └── .done              # {"status":"done","duration":5,"exitCode":0}
│       ├── {input-id}/
│       │   ├── response.json      # {"values":{...},"timestamp":"..."}
│       │   └── .done              # {"status":"done","response":"..."}
│       ├── {note-id}/
│       │   └── .done              # {"status":"done","timestamp":"..."}
│       └── {break-id}/
│           └── .done              # {"status":"done","timestamp":"..."}
```

### Completion Markers

Each cell folder uses one of these markers:
- `.done` — Cell completed successfully
- `.failed` — Cell failed (contains error details)
- `.skipped` — Cell was skipped

All markers are JSON files.

---

## 6. Execution Model

Cells execute sequentially, top to bottom:

```
task    → AI agent executes, writes results to workdir
shell   → Bash script runs, captures stdout/stderr
input   → PAUSES — waits for user form submission, then resumes
note    → Auto-completes instantly, continues to next cell
break   → PAUSES — waits for user to click Continue, then resumes
```

If any cell **fails** (task error, non-zero shell exit code), execution stops.

Input cell responses are available to subsequent task cells as context.

---

## 7. Design Patterns

### Linear Pipeline
Simple sequential execution:
```
shell (setup) → task (generate) → task (process) → note (summary)
```

### Human-in-the-Loop
Collect input, generate, review, iterate:
```
input (config) → task (generate) → break (review) → task (refine)
```

### Mixed Automation
Combine deterministic shell steps with AI tasks:
```
shell (mkdir, npm install) → task (generate code) → shell (build) → task (write tests)
```

### Phased Execution
Group work into phases with notes and breaks:
```
note (Phase 1) → task → task → break (review)
note (Phase 2) → input → task → shell → note (done)
```

---

## 8. Referencing Previous Cells

Task cells can reference output from earlier cells:

- **Files from previous tasks/shells**: Refer to paths relative to `workdir`
- **Input cell responses**: Reference by input cell ID — the runtime makes form values available as context to subsequent tasks

Example of a task referencing prior context:
```xml
<task id="implement">
Based on the user's input from the "config" step:
- Use the selected framework to scaffold the project
- Apply the chosen features
- Write to the paths under the workdir
</task>
```

---

## 9. Complete Examples

### Minimal Notebook

```yaml
---
schema: "2.0"
name: hello-world
workdir: hello-output
---

# hello-world

<task id="hello">
Create a file called hello.txt with the text "Hello from AnyT!"
</task>
```

### Multi-Cell Notebook

```yaml
---
schema: "2.0"
name: express-api
workdir: express-api
---

# express-api

<shell id="init" label="Initialize Project">
mkdir -p express-api
cd express-api && npm init -y && npm install express typescript @types/express
</shell>

<task id="create-server" label="Create Express Server">
Create an Express.js server with TypeScript:
- src/app.ts with a basic Express setup
- src/routes/health.ts with a GET /health endpoint
- tsconfig.json configured for Node.js

**Output:** src/app.ts, src/routes/health.ts, tsconfig.json
</task>

<shell id="build" label="Build TypeScript">
cd express-api && npx tsc
</shell>

<task id="add-tests" label="Add Tests">
Add Vitest tests for the health endpoint:
- Install vitest and supertest as dev dependencies
- Create tests/health.test.ts
- Add a "test" script to package.json
</task>

<note id="complete" label="API Ready">
## API Ready

- Server: `src/app.ts`
- Routes: `src/routes/health.ts`
- Tests: `tests/health.test.ts`

Run: `cd express-api && npx tsc && node dist/app.js`
</note>
```

### Interactive Notebook with Forms

```yaml
---
schema: "2.0"
name: project-scaffolder
workdir: my-project
---

# project-scaffolder

<input id="config" label="Project Configuration">
## Project Setup

Configure your new project:

<form type="json">
{
  "fields": [
    {
      "name": "projectName",
      "type": "text",
      "label": "Project Name",
      "required": true,
      "validation": { "minLength": 3, "pattern": "^[a-z][a-z0-9-]*$" }
    },
    {
      "name": "description",
      "type": "textarea",
      "label": "Description",
      "rows": 3
    },
    {
      "name": "database",
      "type": "select",
      "label": "Database",
      "default": "sqlite",
      "options": [
        { "value": "sqlite", "label": "SQLite" },
        { "value": "postgres", "label": "PostgreSQL" },
        { "value": "mysql", "label": "MySQL" }
      ]
    },
    {
      "name": "includeAuth",
      "type": "checkbox",
      "label": "Include Authentication?"
    },
    {
      "name": "features",
      "type": "multiselect",
      "label": "Features",
      "options": [
        { "value": "api", "label": "API" },
        { "value": "websocket", "label": "WebSocket" },
        { "value": "cron", "label": "Cron" },
        { "value": "queue", "label": "Queue" }
      ],
      "validation": { "minItems": 1 }
    }
  ]
}
</form>
</input>

<task id="scaffold" label="Scaffold Project">
Based on the user's input from the config step, create a project:
- package.json with the project name and description
- src/index.ts entry point
- README.md explaining the project
- Database config based on the selected database type
- If includeAuth is true, add src/auth/ with JWT utilities
</task>

<shell id="install" label="Install Dependencies">
cd my-project && npm install
</shell>

<break id="review" label="Review Project">
Review the generated project structure before adding tests.
</break>

<task id="tests" label="Add Test Suite">
Add a test setup:
- Install vitest as a dev dependency
- Create src/__tests__/index.test.ts
- Add "test" script to package.json
</task>

<note id="done" label="Project Complete">
## Project Scaffolded!

Run:
1. `cd my-project`
2. `npm run dev`
3. `npm test`
</note>
```

### Data Pipeline (Mixed Shell + AI)

```yaml
---
schema: "2.0"
name: data-pipeline
workdir: pipeline-output
---

# data-pipeline

<shell id="setup-dirs" label="Create Directories">
mkdir -p pipeline-output/{raw,processed,reports}
</shell>

<task id="generate-data" label="Generate Sample Data">
Create a sample CSV file at pipeline-output/raw/sales.csv with:
- Headers: date, product, quantity, price, region
- 50 rows of realistic sales data
- Dates spanning the last 30 days
</task>

<shell id="preview">
echo "=== Preview ==="
head -10 pipeline-output/raw/sales.csv
echo "=== Row Count ==="
wc -l pipeline-output/raw/sales.csv
</shell>

<task id="transform" label="Build Transform Script">
Create pipeline-output/transform.js that:
- Reads raw/sales.csv
- Adds a 'total' column (quantity * price)
- Filters rows with quantity < 5
- Writes to processed/sales-clean.csv
</task>

<shell id="run-transform">
cd pipeline-output && node transform.js
</shell>

<task id="analyze" label="Analyze Sales Data">
Create pipeline-output/analyze.py that:
- Reads processed/sales-clean.csv
- Computes revenue by product and region
- Writes reports/summary.json and reports/summary.txt
</task>

<shell id="run-analysis">
cd pipeline-output && python analyze.py
</shell>

<note id="done" label="Pipeline Complete">
## Pipeline Complete

Files: `raw/sales.csv`, `processed/sales-clean.csv`, `reports/summary.*`
</note>
```

---

## 10. Validation Rules

When generating a notebook, ensure:

1. **Frontmatter**: Must start with `---` and end with `---`
2. **`schema: "2.0"`**: Must be present as the first field in frontmatter
3. **`name`**: Required. Used in the `# heading` after frontmatter
4. **`workdir`**: Should be set to a meaningful directory name
5. **Unique IDs**: Every cell `id` must be unique within the file
6. **Valid cell types**: Only `task`, `shell`, `input`, `note`, `break`
7. **Closed tags**: Every `<type id="...">` must have a matching `</type>`
8. **No inline state**: Do NOT include `status`, `duration`, `error`, or `exitCode` attributes on cell tags
9. **ID format**: Use slug-format IDs: lowercase, alphanumeric, hyphens (e.g., `setup-env`, `create-api`)
10. **Heading**: Include `# {name}` after the frontmatter, matching the `name` field
11. **Valid attributes**: Cell tags only accept `id` and `label` attributes. No other attributes are allowed.
12. **Label format**: Labels are free-form text. Use human-readable names (e.g., `"Setup Environment"`, `"Generate Report"`). Labels are optional — when omitted, the cell ID is displayed as the name.

