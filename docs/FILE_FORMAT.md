# AnyT File Format Specification

The `.anyt.md` file format defines AI-executable workflows using a combination of YAML frontmatter and XML-like cell syntax.

## File Structure

A `.anyt.md` file consists of two parts:
1. **YAML Frontmatter** - Workflow metadata enclosed in `---` delimiters
2. **Body** - Cells defining tasks, inputs, and notes

```
---
[YAML frontmatter]
---

[Body with cells]
```

**Important:** The `.anyt.md` file stores only the workflow **structure** (cell definitions). All runtime **state** (status, outputs, duration) is stored in the `.anyt/cells/` folder within the workdir.

## YAML Frontmatter

The frontmatter contains workflow-level configuration:

```yaml
---
name: my-workflow
version: 1.0.0
workdir: output_directory
created: 2025-01-29T10:00:00Z
updated: 2025-01-29T12:00:00Z
inputs:
  projectName: My Project
  maxRetries: 3
  verbose: true
---
```

### Frontmatter Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name` | string | No | "Untitled Workflow" | Workflow display name |
| `version` | string | No | "1.0.0" | Semantic version |
| `workdir` | string | No | "anyt_workspace" | Working directory for execution (relative to .anyt.md file or absolute). All cell state is stored here. |
| `created` | string | No | Current time | ISO 8601 timestamp |
| `updated` | string | No | Current time | ISO 8601 timestamp (auto-updated on save) |
| `inputs` | object | No | `{}` | Key-value pairs passed to tasks as context |

### Input Types

Inputs support three value types:
- **string**: `projectName: "My Project"`
- **number**: `maxRetries: 3`
- **boolean**: `verbose: true`

## Cell Syntax

Cells are defined using XML-like tags. There are five cell types:

### Task Cells

Tasks are executable units that AI agents process.

```xml
<task id="unique-id">
Task description in natural language.
This can span multiple lines.

**Output:** path/to/file1, path/to/file2
</task>
```

#### Task Attributes

| Attribute | Required | Values | Description |
|-----------|----------|--------|-------------|
| `id` | Yes | string | Unique identifier (slug format recommended) |

**Note:** Status, duration, and error are NOT stored in the file - they are read from `.anyt/cells/{id}/` markers.

#### Task Content

The content between `<task>` tags is the task description - natural language instructions for the AI agent.

Special syntax in content:
- `**Output:** file1, file2` - Declares expected output files

### Input Cells

Input cells are user interaction points that pause workflow execution and wait for user input before continuing. They enable human-in-the-loop workflows.

```xml
<input id="review-storyboard">
## Review Generated Storyboard

Please review the files in `working/scenes.json` and verify:
- Scene order makes sense
- Durations are appropriate
- All key features covered

**Actions:**
- `continue` - Proceed with current storyboard
- `edit` - Modify files manually, then continue
</input>
```

#### Input Attributes

| Attribute | Required | Values | Description |
|-----------|----------|--------|-------------|
| `id` | Yes | string | Unique identifier |

#### Action Syntax

Actions are parsed from the description using this format:
```markdown
**Actions:**
- `actionName` - Description of the action
- `anotherAction` - Another action description
```

If no actions are specified, default actions are provided:
- `continue` - Proceed to next step
- `skip` - Skip this prompt

#### Special Actions

| Action | Behavior |
|--------|----------|
| `continue` | Mark input as done, continue workflow |
| `skip` | Mark input as skipped, continue workflow |
| `edit` | Mark input as done, indicates manual editing before continuing |
| `cancel` | Stop entire workflow (always available) |

#### Form-Based Inputs

Input cells can include YAML form definitions for structured data collection:

```xml
<input id="config">
## Configuration

```yaml
fields:
  - name: environment
    type: select
    label: Environment
    required: true
    options:
      - value: dev
        label: Development
      - value: prod
        label: Production

  - name: replicas
    type: number
    label: Replicas
    default: 3
    validation:
      min: 1
      max: 10
```
</input>
```

See [Form Field Types](#form-field-types) for complete field documentation.

### Shell Cells

Shell cells execute scripts directly without AI involvement.

```xml
<shell id="setup-env">
#!/bin/bash
npm install
npm run build
echo "Setup complete"
</shell>
```

#### Shell Attributes

| Attribute | Required | Values | Description |
|-----------|----------|--------|-------------|
| `id` | Yes | string | Unique identifier (slug format recommended) |

**Execution behavior:** Shell cells run the content as a bash script. stdout and stderr are captured to `output.log`. The exit code is stored in the completion marker.

### Note Cells

Notes are markdown documentation cells that auto-complete when reached in workflow execution.

```xml
<note id="documentation-note">
## Section Header

This is markdown content for documentation purposes.

- Bullet point 1
- Bullet point 2
</note>
```

#### Note Attributes

| Attribute | Required | Description |
|-----------|----------|-------------|
| `id` | No | Unique identifier (auto-generated if omitted) |

**Execution behavior:** When a workflow reaches a note cell, it automatically completes and continues to the next cell. Notes create a `.done` marker in their cell folder.

### Break Cells

Break cells are pause points that stop workflow execution until the user explicitly continues.

```xml
<break id="checkpoint">
Review the output files before proceeding to the next phase.
</break>
```

#### Break Attributes

| Attribute | Required | Values | Description |
|-----------|----------|--------|-------------|
| `id` | Yes | string | Unique identifier |

**Execution behavior:** When a workflow reaches a break cell, it pauses and waits for the user to click "Continue". This allows manual verification or intervention before proceeding.

## Form Field Types

Input cells support structured forms with the following field types:

### Text Field

```yaml
- name: username
  type: text
  label: Username
  required: true
  placeholder: Enter username
  validation:
    minLength: 3
    maxLength: 50
    pattern: ^[a-z0-9_]+$
```

### Textarea Field

```yaml
- name: description
  type: textarea
  label: Description
  placeholder: Enter description...
  rows: 4
```

### Number Field

```yaml
- name: count
  type: number
  label: Count
  default: 10
  validation:
    min: 1
    max: 100
```

### Select Field

```yaml
- name: color
  type: select
  label: Color
  required: true
  options:
    - value: red
      label: Red
    - value: blue
      label: Blue
```

### Radio Field

```yaml
- name: size
  type: radio
  label: Size
  required: true
  default: medium
  options:
    - value: small
      label: Small
      description: For small projects
    - value: medium
      label: Medium
    - value: large
      label: Large
```

### Checkbox Field

```yaml
- name: agree
  type: checkbox
  label: I agree to the terms
  description: Please read the terms carefully
  default: false
```

### Multiselect Field

```yaml
- name: features
  type: multiselect
  label: Features
  options:
    - value: analytics
      label: Analytics
    - value: reporting
      label: Reporting
    - value: api
      label: API Access
  validation:
    minItems: 1
    maxItems: 3
```

## Status Lifecycle

All five cell types follow a unified lifecycle:

```
pending → active → done | failed | skipped
```

### Unified Cell Status

| Status | Storage | Description |
|--------|---------|-------------|
| `pending` | Implicit | Cell has not started. No folder or no markers exist. |
| `active` | Runtime only | Cell is currently executing (task running, input waiting). In-memory state only. |
| `done` | Folder (`.done`) | Cell completed successfully. Marker file exists in cell folder. |
| `failed` | Folder (`.failed`) | Cell failed with an error. Marker file exists in cell folder. |
| `skipped` | Folder (`.skipped`) | Cell was skipped by user (inputs only). Marker file exists. |

### Status by Cell Type

| Cell Type | Active State | Completion States |
|-----------|--------------|-------------------|
| Task | Running AI agent | `done` (outputs), `failed` (error) |
| Shell | Running script | `done` (exit code 0), `failed` (non-zero exit) |
| Input | Waiting for user | `done` (response), `skipped` |
| Note | Instant | `done` (auto-completes immediately) |
| Break | Waiting for user | `done` (user continues) |

**Key insight:** Status is determined by reading the cell folder at `{workdir}/.anyt/cells/{id}/`. The `.anyt.md` file does NOT store status.

## ID Generation

When creating new cells, IDs are auto-generated using this format:
```
{slug}-{timestamp}
```

Where:
- `slug`: First 30 characters of description, lowercased, non-alphanumeric replaced with `-`
- `timestamp`: Current time in base36

Example: `setup-the-project-directory-str-ml15kh91`

## Complete Example

```yaml
---
name: web-scraper-workflow
version: 1.0.0
workdir: scraper_output
inputs:
  targetUrl: https://example.com
  outputFormat: json
---

# web-scraper-workflow

<note id="overview">
## Web Scraper Workflow

This workflow scrapes data from a website and processes it.
</note>

<shell id="setup">
#!/bin/bash
mkdir -p data/raw data/processed logs
echo "Directory structure created"
</shell>

<task id="scrape">
Scrape the target URL and save raw HTML to data/raw/page.html

**Output:** data/raw/page.html
</task>

<input id="review-scraped">
## Review Scraped Data

Please review the raw HTML in `data/raw/page.html` and verify:
- Content is complete
- No errors or blocks
- All expected sections present

**Actions:**
- `continue` - Proceed with parsing
- `retry` - Re-scrape the page
</input>

<task id="parse">
Parse the HTML and extract structured data.
Save as JSON to data/processed/data.json
</task>

<break id="review-checkpoint">
Review the parsed data before validation.
</break>

<task id="validate">
Validate the extracted data for completeness.
Log any issues to logs/validation.log
</task>
```

## Directory Structure

AnyT stores all cell state in a unified folder structure within the workdir.

### Unified Cell Folder Structure

All cells use `{workdir}/.anyt/cells/{cell-id}/`:

```
{workdir}/
├── .anyt/
│   └── cells/
│       ├── {task-id}/
│       │   ├── prompt.md           # Full prompt sent to AI
│       │   ├── output.log          # Formatted output for display
│       │   ├── raw-output.log      # Raw JSON output from runtime
│       │   ├── progress.md         # Progress updates
│       │   └── .done | .failed     # Completion marker (JSON)
│       │
│       ├── {shell-id}/
│       │   ├── script.sh           # The shell script content
│       │   ├── output.log          # stdout/stderr output
│       │   ├── raw-output.log      # Raw output
│       │   └── .done | .failed     # Completion marker (JSON with exitCode)
│       │
│       ├── {input-id}/
│       │   ├── prompt.md           # The question/instruction to user
│       │   ├── response.json       # User's form response
│       │   └── .done | .skipped    # Completion marker (JSON)
│       │
│       ├── {note-id}/
│       │   ├── content.md          # The note's markdown content
│       │   └── .done               # Completion marker (JSON)
│       │
│       └── {break-id}/
│           └── .done               # Completion marker (JSON)
│
└── [user files created by tasks]
```

### Completion Markers

Completion markers are JSON files that indicate cell status:

**.done file** (on success):
```json
{
  "status": "done",
  "timestamp": "2025-01-29T12:30:00Z",
  "duration": 30,
  "outputs": ["path/to/output1", "path/to/output2"]
}
```

**.failed file** (on failure):
```json
{
  "status": "failed",
  "timestamp": "2025-01-29T12:30:00Z",
  "duration": 15,
  "error": "Error message describing what went wrong"
}
```

**.skipped file** (for inputs):
```json
{
  "status": "skipped",
  "timestamp": "2025-01-29T12:30:00Z",
  "response": "skipped"
}
```

### Workflow Rerun Behavior

- **Run entire workflow**: Clears all folders in `.anyt/cells/` and runs from beginning
- **Run single cell**: Clears only that cell's folder and re-executes it
- **Status recovery on reopen**: Status is read from folder markers, so state persists across sessions
