---
name: create-anyt-notebook
description: Create AnyT Notebook (.anyt) files for AI agent workflows. Use when the user wants to create, scaffold, or generate an AnyT notebook, design an AI workflow with cells, or build a step-by-step notebook for tasks like project setup, data pipelines, or content generation.
---

# Create AnyT Notebook

Create `.anyt` notebook files — workflow documents for AI agents that combine task cells (AI execution), shell cells (scripts), input cells (user forms), note cells (documentation), and break cells (review gates).

For the complete specification, see [references/anyt-notebook-spec.md](references/anyt-notebook-spec.md).
For product context, see [references/product.md](references/product.md).
For real-world examples, see files in [references/examples/](references/examples/).

## File Format

An `.anyt` file has two sections: YAML frontmatter and a body with cell tags.

```
---
[YAML frontmatter]
---

# [Notebook Title]

[Cell tags in execution order]
```

## Frontmatter

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `schema` | `"2.0"` | Yes | — | Must be first field, always `"2.0"` |
| `name` | string | Yes | — | Notebook identifier (used as heading) |
| `description` | string | No | — | Human-readable summary |
| `version` | string | No | — | Semantic version |
| `workdir` | string | No | `"anyt_workspace"` | Working directory for execution (relative to notebook file). Use `anyt_workspace_` prefix (e.g., `anyt_workspace_yt_summarizer`). |
| `env_file` | string | No | `".env"` | Path to .env file for secrets |
| `dependencies` | object | No | — | Skill dependencies as `name: version` pairs |
| `agents` | array | No | — | Agent profiles for configuring AI runtime engines (see below) |

Minimal valid frontmatter:

```yaml
---
schema: "2.0"
name: my-notebook
workdir: anyt_workspace_my_notebook
---
```

### Working Directory

`workdir` sets the current working directory for all cell execution. All file paths in shell scripts and task descriptions should be **relative to workdir**, not include the workdir name.

**Convention:** Always use the `anyt_workspace_` prefix for workdir names (e.g., `anyt_workspace_yt_summarizer`, `anyt_workspace_rednote`). This ensures all workspace folders are gitignored by the `anyt_workspace_*/` pattern.

```yaml
workdir: anyt_workspace_my_project
```

Correct: `mkdir -p src docs` (creates `anyt_workspace_my_project/src`, `anyt_workspace_my_project/docs`)
Wrong: `mkdir -p anyt_workspace_my_project/src` (creates nested path)

### Environment Variables

Never put secrets directly in the notebook. Use `env_file` to reference an external `.env` file (excluded from version control):

```yaml
env_file: ".env"              # Default
env_file: "secrets/prod.env"  # Relative path
```

Priority (highest to lowest): .env file > shell profile.

### Agent Profiles

The `agents` field defines named, reusable agent configurations for AI runtime engines:

```yaml
agents:
  - id: claude-default
    name: Claude Code
    type: claude
    default: true
    permissionMode: bypassPermissions
    model: ""
  - id: codex-fast
    name: Codex
    type: codex
    permissionMode: dangerously-bypass
    model: ""
```

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `id` | string | Yes | Unique identifier for this profile |
| `name` | string | Yes | Display name for the profile |
| `type` | `"claude" \| "codex"` | Yes | Runtime type |
| `default` | boolean | No | Whether this is the default profile |
| `permissionMode` | string | No | Permission mode for execution |
| `model` | string | No | Model to use |
| `additionalArgs` | string[] | No | Additional CLI arguments |

Cells can reference an agent profile by its `id` using the `agent` attribute.

## Cell Types

All cells use XML-like tags with a required `id` attribute and optional `label`, `agent`, and `skip` attributes:

```xml
<{type} id="{unique-id}">
{content}
</{type}>

<{type} id="{unique-id}" label="{display name}">
{content}
</{type}>

<{type} id="{unique-id}" agent="{profile-id}">
{content}
</{type}>
```

| Attribute | Required | Description |
|-----------|----------|-------------|
| `id` | Yes | Unique technical identifier (slug format). Used for file paths and folder names. |
| `label` | No | Human-friendly display name. Shown as the primary cell name in the UI. Can contain spaces and mixed case. |
| `agent` | No | Agent profile ID to use for this cell. Overrides the notebook's default agent profile. Must reference a profile defined in the `agents` frontmatter field. |
| `skip` | No | Set to `"true"` to skip this break cell during execution. Only valid on `break` cells. |

Rules:
- Valid types: `task`, `shell`, `input`, `note`, `break`
- `id` is required, must be unique across the notebook
- ID format: lowercase alphanumeric + hyphens (e.g., `setup-env`, `create-api`)
- `label` is optional, free-form text (e.g., `"Setup Environment"`, `"Create API"`)
- No nesting of cell tags
- Valid attributes are `id`, `label`, `agent`, and `skip` only — never include `status`, `duration`, `error`
- Leave a blank line between cell tags

### Task Cell

AI agent executes natural language instructions. Markdown formatting is preserved.

```xml
<task id="create-api" label="Create REST API">
Create a REST API with the following endpoints:
- GET /users - List all users
- POST /users - Create a new user

Use Express.js with TypeScript and proper error handling.

**Output:** src/app.ts, src/routes/users.ts
</task>
```

- Reference files created by previous cells (paths relative to workdir)
- Reference input cell responses
- Use `**Output:** file1, file2` to declare expected output files
- **Do NOT include explicit CLI commands** for installed skills — just describe what to do (inputs/outputs) and name the skill. The AI agent reads the skill's SKILL.md and determines the correct commands itself.
- Use the `agent` attribute to override the default agent profile for this cell

### Shell Cell

Executes bash scripts directly — no AI involvement. Fast, deterministic.

```xml
<shell id="setup-env" label="Install Dependencies">
mkdir -p src tests docs
npm init -y
npm install express typescript @types/express
</shell>
```

- `#!/bin/bash` shebang is optional but recommended
- Exit code 0 = success, non-zero = failure
- Use for installation, building, testing, deployment

**Skill installation:** Use `npx @anytio/pspm@latest add @user/<username>/<skillname> -y` to install skills. Skills are installed to `.pspm/skills/` and symlinked into agent skill directories (`.claude/skills/`, `.codex/skills/`, etc.). Verify with `ls -la .pspm/skills/anyt/<skill-name>/`.

### Input Cell

Pauses execution and displays a form. Resumes when user submits.

```xml
<input id="project-config" label="Project Configuration">
## Configure Your Project

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
      "name": "database",
      "type": "select",
      "label": "Database",
      "default": "sqlite",
      "options": [
        { "value": "sqlite", "label": "SQLite" },
        { "value": "postgres", "label": "PostgreSQL" }
      ]
    },
    {
      "name": "features",
      "type": "multiselect",
      "label": "Features",
      "options": [
        { "value": "auth", "label": "Auth" },
        { "value": "api", "label": "API" }
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

**Field types:** `text`, `textarea`, `number`, `checkbox`, `select`, `radio`, `multiselect`

**Field properties:**

| Property | Required | Description |
|----------|----------|-------------|
| `name` | Yes | Unique field identifier |
| `type` | Yes | Field type |
| `label` | Yes | Display label |
| `description` | No | Help text |
| `required` | No | Whether field must be filled |
| `default` | No | Default value |
| `placeholder` | No | Placeholder text |
| `options` | Conditional | Options array for select/radio/multiselect: `[{ "value": "v", "label": "L" }]` |
| `rows` | No | Textarea rows (default: 3) |
| `validation` | No | Rules: `minLength`, `maxLength`, `pattern`, `min`, `max`, `step`, `minItems`, `maxItems` |

**Input without form** (action buttons only):

```xml
<input id="review">
## Review Output

Check the generated files and choose how to proceed.
</input>
```

### Note Cell

Markdown documentation checkpoint. Auto-completes instantly during execution.

```xml
<note id="phase-1-complete" label="Phase 1 Complete">
## Phase 1 Complete

Generated files:
- `src/app.ts` - Express server
- `src/routes/` - API routes

Next: Configure database and add authentication.
</note>
```

### Break Cell

Pauses execution for human review. Waits for user to click "Continue."

```xml
<break id="verify-setup" label="Verify Setup">
Review the project structure and configuration files
before proceeding to the database setup.
</break>
```

The `skip` attribute allows individual break cells to be disabled without removing them. When `skip="true"`, the break auto-continues instead of pausing:

```xml
<break id="check-output" label="Check Output" skip="true">
This break was used during development and is now skipped.
</break>
```

A global "Skip Breakpoints" toggle in the execution options can also skip all break cells at once.

## Design Patterns

### Linear Pipeline
```
shell (setup) -> task (generate) -> task (process) -> note (summary)
```

### Human-in-the-Loop
```
input (config) -> task (generate) -> break (review) -> task (refine)
```

### Mixed Automation
```
shell (mkdir, npm install) -> task (generate code) -> shell (build) -> task (write tests)
```

### Phased Execution
```
note (Phase 1) -> task -> task -> break (review)
note (Phase 2) -> input -> task -> shell -> note (done)
```

## Validation Rules

When generating a notebook, ensure:

1. Frontmatter starts with `---` and ends with `---`
2. `schema: "2.0"` is the first field in frontmatter
3. `name` is required
4. `workdir` should use the `anyt_workspace_` prefix (e.g., `anyt_workspace_my_project`)
5. Every cell `id` is unique within the file
6. Only valid cell types: `task`, `shell`, `input`, `note`, `break`
7. Every `<type id="...">` has a matching `</type>`
8. No `status`, `duration`, `error`, or `exitCode` attributes on cell tags
9. IDs are slug-format: lowercase, alphanumeric, hyphens
10. Include `# {name}` heading after frontmatter, matching `name`
11. Cell tags only accept `id`, `label`, `agent`, and `skip` attributes — no other attributes allowed
12. Labels are free-form text, optional — use human-readable names (e.g., `"Setup Environment"`)
13. The `agent` attribute must reference a valid profile `id` from the `agents` frontmatter field
14. The `skip` attribute is only valid on `break` cells. Its only valid value is `"true"`

## Complete Example

```yaml
---
schema: "2.0"
name: express-api
description: Build an Express.js API with TypeScript
workdir: anyt_workspace_express_api
---

# express-api

<shell id="init" label="Initialize Project">
mkdir -p src tests
npm init -y
npm install express typescript @types/express
npx tsc --init
</shell>

<task id="create-server" label="Create Express Server">
Create an Express.js server with TypeScript:
- src/app.ts with a basic Express setup
- src/routes/health.ts with a GET /health endpoint
- tsconfig.json configured for Node.js

**Output:** src/app.ts, src/routes/health.ts, tsconfig.json
</task>

<shell id="build" label="Build TypeScript">
npx tsc
</shell>

<break id="verify" label="Review Build">
Check that the TypeScript compiles without errors and review the generated code.
</break>

<task id="add-tests" label="Add Tests">
Add Vitest tests for the health endpoint:
- Install vitest and supertest as dev dependencies
- Create tests/health.test.ts
- Add a "test" script to package.json
</task>

<shell id="test">
npm test
</shell>

<note id="complete" label="API Ready">
## API Ready

- Server: `src/app.ts`
- Routes: `src/routes/health.ts`
- Tests: `tests/health.test.ts`

Run: `npx tsc && node dist/app.js`
</note>
```

## Workflow Tips

- **Start with a note cell** to describe the workflow overview
- **Use shell cells** for deterministic steps (install deps, build, test) — cheaper and faster than AI
- **Add break cells liberally** during development, remove once confident
- **Use `skip="true"`** on break cells to disable them without deleting (useful during workflow hardening)
- **Keep task cells focused** — one clear objective per cell
- **Declare outputs** in task cells with `**Output:** file1, file2` so the system tracks expected files
- **Reference previous cells** — task cells can reference files created by earlier cells and input responses
- **Use input cells** to collect user configuration before AI tasks that depend on choices
- **Set workdir** to keep all generated files organized in one directory
- **Add labels** to cells for readability — labels are shown as the primary name in the UI (e.g., `label="Setup Environment"`)
- **Use agent profiles** to configure different AI runtimes per cell when needed
