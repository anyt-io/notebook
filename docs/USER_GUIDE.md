# AnyT Notebook User Guide

This guide covers everything you need to know to create and run AI-powered notebooks with AnyT Notebook.

## Table of Contents

- [Getting Started](#getting-started)
- [Understanding the Interface](#understanding-the-interface)
- [Working with Cells](#working-with-cells)
- [Notebook Inputs](#notebook-inputs)
- [Execution Modes](#execution-modes)
- [Form-Based Inputs](#form-based-inputs)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Getting Started

### Prerequisites

- VS Code 1.85.0 or later (or Cursor)
- An AI runtime installed:
  - **Claude Code** (recommended): Install from [claude.ai/code](https://claude.ai/code)
  - **Codex**: Install via `npm install -g @openai/codex`

### Creating Your First Notebook

1. **Create a new file** with `.anyt.md` extension
2. **Add frontmatter** to configure your notebook:

```yaml
---
schema: "2.0"
name: my-notebook
workdir: output
---
```

3. **Add a title** matching the `name` field:

```markdown
# my-notebook
```

4. **Add cells** to define your notebook steps

### Understanding the Workdir

The `workdir` setting specifies where AI-generated files will be created. This keeps your project organized:

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
- **Add Cell**: Insert a new cell (dropdown with cell types)

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

Task cells are executed by AI agents. Write clear, specific instructions:

```xml
<task id="create-api">
Create a REST API endpoint for user authentication.

Requirements:
- POST /api/auth/login accepts email and password
- Returns JWT token on success
- Validates input and returns appropriate errors

**Output:** src/api/auth.ts
</task>
```

**Tips for effective tasks:**

- Be specific about what you want
- Include acceptance criteria
- Specify expected output files with `**Output:**`
- Break complex tasks into smaller steps

### Shell Cells

Shell cells execute scripts directly without AI interpretation:

```xml
<shell id="install-deps">
#!/bin/bash
npm install express jsonwebtoken bcrypt
npm run build
</shell>
```

**Use cases:**

- Installing dependencies
- Running build commands
- Setting up directory structures
- Executing existing scripts

### Input Cells

Input cells pause the notebook and wait for user interaction:

```xml
<input id="review-code">
## Code Review Checkpoint

Please review the generated authentication code in `src/api/auth.ts`.

**Checklist:**
- [ ] Security best practices followed
- [ ] Error handling is comprehensive
- [ ] Code is well-documented
</input>
```

Input cells can also include structured forms. See [Form-Based Inputs](#form-based-inputs).

### Note Cells

Note cells provide documentation and auto-complete when reached:

```xml
<note id="phase-1-complete">
## Phase 1: Setup Complete

The following has been accomplished:
- Project structure created
- Dependencies installed
- Basic configuration set up

Proceeding to Phase 2: Implementation
</note>
```

### Break Cells

Break cells pause execution until you explicitly continue:

```xml
<break id="manual-verification">
Please manually verify the deployment at https://staging.example.com
before proceeding to production deployment.
</break>
```

## Notebook Inputs

Define variables in frontmatter that can be referenced in tasks:

```yaml
---
schema: "2.0"
name: deploy-notebook
workdir: deployment
inputs:
  environment: staging
  version: 1.2.3
  enableDebug: true
  maxRetries: 3
---
```

Tasks can reference these values, and the AI will have access to them as context.

**Supported types:**

- **string**: `environment: staging`
- **number**: `maxRetries: 3`
- **boolean**: `enableDebug: true`

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

Input cells can include a `<form type="dsl">` block for structured data collection:

```xml
<input id="config-form">
## Configuration

Please configure the deployment settings:

<form type="dsl">
environment: select[dev,staging,prod] | Target Environment | required
replicas: number | Number of Replicas | default=3, min=1, max=10
enableMonitoring: checkbox | Enable Monitoring | default=true
</form>
</input>
```

### Form DSL Syntax

Each line defines a form field:

```
fieldName: fieldType[options] | Label Text | modifier1, modifier2
```

### Field Types

| Type | Aliases | Description |
|------|---------|-------------|
| `text` | `string`, `str` | Single-line text input |
| `textarea` | — | Multi-line text input |
| `number` | `int`, `integer` | Numeric input |
| `checkbox` | `bool`, `boolean` | Boolean toggle |
| `select` | `enum` | Dropdown (single selection) |
| `radio` | — | Radio button group |
| `multiselect` | `multi` | Checkbox group (multiple selection) |

### Modifiers

| Modifier | Applies to | Example |
|----------|-----------|---------|
| `required` | All | `required` |
| `default=value` | All | `default=react` |
| `placeholder="text"` | text, textarea, number | `placeholder="Enter name"` |
| `description="text"` | All | `description="Help text"` |
| `minLength=N` | text, textarea | `minLength=3` |
| `maxLength=N` | text, textarea | `maxLength=100` |
| `pattern="regex"` | text | `pattern="^[a-z]+$"` |
| `min=N` | number | `min=0` |
| `max=N` | number | `max=65535` |
| `rows=N` | textarea | `rows=5` |
| `minItems=N` | multiselect | `minItems=1` |
| `maxItems=N` | multiselect | `maxItems=3` |

### Options

For select, radio, and multiselect fields, use square brackets:

```
database: select[sqlite,postgres,mysql] | Database | default=sqlite
```

### Comments

Lines starting with `#` inside `<form>` are ignored:

```xml
<form type="dsl">
# Basic info
name: text | Name | required
# Settings
debug: checkbox | Debug Mode
</form>
```

### Complete Form Example

```xml
<input id="project-config">
## Configure Your Project

<form type="dsl">
# Basic info
projectName: text | Project Name | required, minLength=3, pattern="^[a-z][a-z0-9-]*$"
description: textarea | Description | rows=3, placeholder="Describe your project..."
# Tech stack
framework: select[react,vue,svelte] | Framework | default=react, required
features: multiselect[auth,api,database,testing] | Features | minItems=1
port: int | Dev Port | min=1024, max=65535, default=3000
isPublic: bool | Public Repository
</form>
</input>
```

## Best Practices

### Writing Effective Tasks

1. **Be specific**: Include all requirements and constraints
2. **Specify outputs**: Use `**Output:** path/to/file` to declare expected files
3. **Break down complexity**: Split large tasks into smaller, focused cells
4. **Provide context**: Reference notebook inputs and previous outputs

### Organizing Notebooks

1. **Use notes as section headers**: Group related tasks with note cells
2. **Add checkpoints**: Use input/break cells at critical points
3. **Name cells meaningfully**: Use descriptive IDs like `create-user-api` not `task-1`

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

- Ensure the `<form type="dsl">` block is properly formatted
- Check that field types are valid
- Verify required properties are present

### Execution state not persisting

- State is stored in `{workdir}/.anyt/cells/`
- Ensure the workdir is writable
- Check that VS Code has permission to create folders

### Runtime not available

- Verify the runtime is installed: `claude --version` or `codex --version`
- Check PATH environment variable
- Restart VS Code after installing runtimes
