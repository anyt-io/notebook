# AnyT Notebook User Guide

This guide covers everything you need to know to create and run AI-powered workflows with AnyT Notebook.

## Table of Contents

- [Getting Started](#getting-started)
- [Understanding the Interface](#understanding-the-interface)
- [Working with Cells](#working-with-cells)
- [Cell Labels](#cell-labels)
- [Agent Profiles](#agent-profiles)
- [Execution Modes](#execution-modes)
- [Form-Based Inputs](#form-based-inputs)
- [Workflow Development Lifecycle](#workflow-development-lifecycle)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Getting Started

### Prerequisites

- VS Code 1.85.0 or later (or Cursor)
- An AI runtime installed:
  - **Claude Code** (recommended): Install from [claude.ai/code](https://claude.ai/code)
  - **Codex**: Install via `npm install -g @openai/codex`

### Creating Your First Notebook

**Option A: Start from a sample**

1. Open Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`)
2. Run **"AnyT: Open Sample Notebook"**
3. Pick a sample (Hello World is a good start)
4. Click **Run** to execute

**Option B: Create from scratch**

1. Open Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`)
2. Run **"AnyT: New Notebook"**
3. The notebook editor opens with an empty canvas
4. Click **+ Task**, **+ Shell**, **+ Input**, **+ Break**, or **+ Note** in the toolbar to add cells
5. Edit cells with the rich text editor (supports bold, italic, headings, lists, and code blocks with syntax highlighting) or switch to the Markdown tab for raw editing
6. Select your AI runtime from the toolbar dropdown (Claude Code or Codex)
7. Click **Run** to execute the notebook step by step

### Understanding the Workdir

The `workdir` setting in the notebook frontmatter specifies where AI-generated files will be created. This keeps your project organized:

- **Relative path**: `workdir: output` creates `./output/` relative to your `.anyt.md` file
- **Absolute path**: `workdir: /tmp/my-project` uses an absolute location

All cell state (execution logs, progress) is stored in `{workdir}/.anyt/cells/`.

## Understanding the Interface

### Toolbar

The top toolbar provides quick actions:

- **Run All**: Execute the entire notebook from the beginning
- **Run Selected**: Run only the currently selected cell
- **Stop**: Pause execution
- **Reset**: Clear all execution state and start fresh
- **Add Cell**: Insert a new cell (dropdown with all five cell types)

### Runtime Selector

Choose your AI runtime from the dropdown:

- **Claude Code**: Anthropic's AI coding assistant (recommended)
- **Codex**: OpenAI's code generation model

### Permission Mode

Control how the AI interacts with your system:

- **Default**: AI asks for confirmation before making changes
- **Plan**: AI creates a plan before executing
- **Auto Accept Edits**: Automatically accept file edits
- **Full Auto**: Run without confirmations (use with caution)

### Cell Indicators

Each cell shows:

- **Execution number**: `[1]`, `[2]`, etc. showing run order
- **Status indicator**: Pending (gray), Running (blue), Done (green), Failed (red)
- **Duration**: Time taken to execute

## Working with Cells

### Task Cells

Task cells are executed by your AI agent (Claude Code or Codex). Write clear, specific instructions describing what you want the agent to accomplish.

**Tips for effective tasks:**

- Be specific about what you want
- Include acceptance criteria
- Specify expected output files with `**Output:**`
- Break complex tasks into smaller steps

> *Example: "Create a REST API endpoint for user authentication. POST /api/auth/login accepts email and password, returns JWT token on success, validates input and returns appropriate errors. **Output:** src/api/auth.ts"*

### Shell Cells

Shell cells run scripts directly -- no AI involved. They're fast, deterministic, and ideal for commands you already know.

**Use cases:**

- Installing dependencies
- Running build commands
- Setting up directory structures
- Executing tests and linters

> *Example: `npm install express jsonwebtoken bcrypt && npm run build`*

### Input Cells

Input cells pause the notebook and present a form to the user. Use them to collect configuration values, choose between options, or supply information that downstream cells need.

Input cells can include structured forms for richer interaction. See [Form-Based Inputs](#form-based-inputs).

> *Example: "Choose deployment target" with a dropdown for staging vs. production.*

### Note Cells

Note cells are markdown documentation checkpoints. They auto-complete instantly when reached and serve as section headers, context annotations, or progress markers.

> *Example: A section header like "Phase 2: Testing and Validation" to organize your notebook into logical sections.*

### Break Cells

Break cells pause execution so you can review what's happened so far. Inspect outputs, verify results, then click Continue when ready.

> *Example: "Review the generated project structure before adding API routes."*

## Cell Labels

Cells have a technical `id` (slug format, used for file paths and references) and an optional human-friendly `label` for display:

```xml
<task id="setup-env" label="Setup Environment">
Install dependencies and configure the project.
</task>
```

- When a **label** is set, it's shown as the primary cell name with the ID displayed as a subtle suffix
- When **no label** is set, the cell ID is shown as the name
- Click a cell name to edit the label; cell IDs are read-only

**Tips:**
- Use descriptive labels so your notebook reads like a plan: "Install Dependencies", "Create API Routes", "Review Output"
- Labels appear in both expanded and collapsed cell views
- Labels are optional — cells work fine with just an ID

## Agent Profiles

Agent profiles let you configure different AI runtimes and settings at the notebook or cell level.

### Notebook-Level Profile

Set a default agent profile for the entire notebook. All task cells will use this profile unless overridden.

### Per-Cell Profile

Override the notebook default on individual task cells. This is useful when different tasks benefit from different runtimes or settings -- for example, using a more capable model for complex reasoning tasks and a faster one for straightforward code generation.

### Runtime Health Checks

The toolbar shows the health status of your configured runtimes. If a runtime is not installed, you'll see setup links to get started quickly.

## Execution Modes

### Run All

Executes all cells from the beginning, clearing previous state.

### Run Single Cell

Executes only the selected cell, useful for:

- Testing a specific task
- Re-running a failed cell
- Iterating on task descriptions

### Continue from Cell

When a notebook pauses (at input or break cells), click "Continue" to proceed.

## Form-Based Inputs

Input cells can include a `<form type="json">` block for structured data collection. When the notebook reaches an input cell with a form, it renders interactive fields and waits for the user to submit.

### Field Types

| Type | Description |
|------|-------------|
| `text` | Single-line text input |
| `textarea` | Multi-line text input |
| `number` | Numeric input |
| `checkbox` | Boolean toggle |
| `select` | Dropdown (single selection) |
| `radio` | Radio button group |
| `multiselect` | Checkbox group (multiple selection) |

### Field Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `name` | string | Yes | Unique field identifier |
| `type` | string | Yes | Field type |
| `label` | string | Yes | Display label |
| `description` | string | No | Help text below field |
| `required` | boolean | No | Whether field must be filled |
| `default` | varies | No | Default value |
| `placeholder` | string | No | Placeholder text |
| `options` | array | Conditional | Options for select/radio/multiselect |
| `rows` | number | No | Rows for textarea |
| `validation` | object | No | Validation rules |

### Validation Rules

| Rule | Applies to | Example |
|------|-----------|---------|
| `minLength` | text, textarea | `{ "minLength": 3 }` |
| `maxLength` | text, textarea | `{ "maxLength": 100 }` |
| `pattern` | text | `{ "pattern": "^[a-z]+$" }` |
| `min` | number | `{ "min": 0 }` |
| `max` | number | `{ "max": 65535 }` |
| `minItems` | multiselect | `{ "minItems": 1 }` |
| `maxItems` | multiselect | `{ "maxItems": 3 }` |

### Form Syntax Reference

Forms are defined inside input cells using a `<form type="json">` block. Here's the file-format syntax for reference:

```xml
<input id="config-form">
## Configuration

Please configure the deployment settings:

<form type="json">
{
  "fields": [
    {
      "name": "environment",
      "type": "select",
      "label": "Target Environment",
      "required": true,
      "options": [
        { "value": "dev", "label": "Development" },
        { "value": "staging", "label": "Staging" },
        { "value": "prod", "label": "Production" }
      ]
    },
    {
      "name": "replicas",
      "type": "number",
      "label": "Number of Replicas",
      "default": 3,
      "validation": { "min": 1, "max": 10 }
    },
    {
      "name": "enableMonitoring",
      "type": "checkbox",
      "label": "Enable Monitoring",
      "default": true
    }
  ]
}
</form>
</input>
```

### Complete Form Example

```xml
<input id="project-config">
## Configure Your Project

<form type="json">
{
  "fields": [
    {
      "name": "projectName",
      "type": "text",
      "label": "Project Name",
      "required": true,
      "placeholder": "my-app",
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
      "label": "Features to Enable",
      "description": "Select all features you want to use",
      "options": [
        { "value": "analytics", "label": "Analytics" },
        { "value": "reports", "label": "Reports" },
        { "value": "api", "label": "API" },
        { "value": "webhooks", "label": "Webhooks" }
      ],
      "validation": { "minItems": 1, "maxItems": 3 }
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

## Workflow Development Lifecycle

AnyT Notebook treats AI workflows like code -- build, test, and refine them iteratively:

### Phase 1: Create

Add cells visually using the toolbar buttons. Think about what needs to happen, in what order. What should the AI do? What can a shell script handle? Where does the human need to decide?

### Phase 2: Debug

Add break cells liberally -- after every AI task if you want. Run the notebook. At each breakpoint, inspect the output. Did the AI do what you expected?

### Phase 3: Iterate

Some steps will fail. Edit the task description to be clearer. Add a shell cell to install a missing dependency. Insert an input cell where you need human choice. Split a task that's too big into two.

### Phase 4: Harden

The workflow works. Remove unnecessary breakpoints. Keep only the ones at critical review points. The workflow runs with minimal human intervention.

### Phase 5: Share

Check the `.anyt.md` file into git. Share it with teammates. They get a debugged, proven workflow they can understand and run.

## Best Practices

### Writing Effective Tasks

1. **Be specific**: Include all requirements and constraints
2. **Specify outputs**: Use `**Output:** path/to/file` to declare expected files
3. **Break down complexity**: Split large tasks into smaller, focused cells
4. **Provide context**: Reference notebook inputs and previous outputs

### Organizing Notebooks

1. **Use notes as section headers**: Group related tasks with note cells
2. **Add checkpoints**: Use input/break cells at critical points
3. **Name cells meaningfully**: Use descriptive IDs like `create-user-api` not `task-1`, and add labels like "Create User API" for readability
4. **Mix cell types**: Use shell for deterministic steps, tasks for creative AI work

### Managing State

1. **Reset when needed**: Use "Reset" to clear all state and start fresh
2. **Re-run single cells**: Test individual tasks without running the entire notebook
3. **Check the workdir**: All outputs and logs are in `{workdir}/.anyt/cells/`

## Troubleshooting

### Cell stuck in "Running"

- Check if the AI runtime is installed and accessible
- Look at the output panel for errors
- Try stopping and re-running the cell

### AI not finding files

- Ensure the `workdir` is correctly set
- Check that previous tasks completed successfully
- Verify file paths in task descriptions

### Form not rendering

- Ensure the `<form type="json">` block contains valid JSON
- Check that field types are valid
- Verify required properties (`name`, `type`, `label`) are present

### Execution state not persisting

- State is stored in `{workdir}/.anyt/cells/`
- Ensure the workdir is writable
- Check that VS Code has permission to create folders

### Runtime not available

- Verify the runtime is installed: `claude --version` or `codex --version`
- Check PATH environment variable
- Restart VS Code after installing runtimes
