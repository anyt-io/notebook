# AnyT Notebook

**Define workflows in natural language, let AI execute them.**

AnyT Notebook is a VS Code extension that brings a Jupyter-style notebook experience for creating, editing, and running AI-powered workflows. Write your tasks in plain English, and let AI agents like Claude Code execute them step by step.

## Features

- **Natural Language Workflows**: Define tasks in plain English using `.anyt.md` files
- **Jupyter-Style Interface**: Familiar notebook UI with cells, execution numbers, and drag-and-drop reordering
- **AI-Powered Execution**: Integrates with Claude Code and Codex to execute tasks
- **Five Cell Types**: Tasks (AI), Shell (scripts), Input (forms), Note (markdown), Break (pause points)
- **Human-in-the-Loop**: Add input cells with forms or break points for manual intervention
- **Persistent State**: Workflow execution state persists across VS Code sessions
- **Real-time Progress**: Watch AI agents work with streaming output updates

## Installation

### From VS Code Marketplace

1. Open VS Code or Cursor
2. Go to Extensions (Ctrl+Shift+X / Cmd+Shift+X)
3. Search for "AnyT Notebook"
4. Click Install

### From VSIX

1. Download the latest `.vsix` file from the releases
2. In VS Code, open Command Palette (Ctrl+Shift+P / Cmd+Shift+P)
3. Run "Extensions: Install from VSIX..."
4. Select the downloaded file

## Quick Start

1. Create a new file with `.anyt.md` extension (e.g., `workflow.anyt.md`)
2. The AnyT Notebook editor will open automatically
3. Add tasks using the "+" button or write them directly:

```yaml
---
name: my-first-workflow
workdir: output
---

# My First Workflow

<task id="hello">
Create a file called hello.txt with a friendly greeting message.
</task>

<task id="goodbye">
Create a file called goodbye.txt with a farewell message.
</task>
```

4. Select your AI runtime (Claude Code recommended)
5. Click "Run" to execute the workflow

## Documentation

- [User Guide](docs/USER_GUIDE.md) - Complete guide to using AnyT Notebook
- [File Format Specification](docs/FILE_FORMAT.md) - Detailed `.anyt.md` format reference
- [Examples](examples/) - Sample workflows to get you started

## Cell Types

### Task Cells

Executable by AI agents - describe what you want in natural language:

```xml
<task id="unique-id">
Task description in natural language.

**Output:** expected/output/file
</task>
```

### Shell Cells

Direct script execution without AI:

```xml
<shell id="setup">
#!/bin/bash
npm install
npm run build
</shell>
```

### Input Cells

Form-based user interaction with validation:

```xml
<input id="review">
Please review the generated files.

```yaml
fields:
  - name: approved
    type: checkbox
    label: Approve changes
    required: true
```
</input>
```

### Note Cells

Documentation and checkpoints:

```xml
<note id="docs">
## Section Header

Markdown documentation that auto-completes when reached.
</note>
```

### Break Cells

Workflow pause points:

```xml
<break id="checkpoint">
Pause here to verify everything is correct before continuing.
</break>
```

## Supported AI Runtimes

| Runtime | Status | Notes |
|---------|--------|-------|
| Claude Code | Primary | Full support with streaming output |
| Codex | Supported | Full support with JSON output |

## Configuration

Configure AnyT Notebook in VS Code settings:

| Setting | Default | Description |
|---------|---------|-------------|
| `anyt.agent` | `"claude"` | AI agent to use (`claude`, `codex`) |
| `anyt.autoVersion` | `true` | Automatically create versions on changes |

## Commands

| Command | Description |
|---------|-------------|
| `AnyT: New Notebook` | Create a new .anyt.md notebook |
| `AnyT: Run Workflow` | Run all cells from beginning |
| `AnyT: Run Task` | Run a single cell |
| `AnyT: Add Task` | Add a new task cell |
| `AnyT: Add Shell Cell` | Add a new shell cell |
| `AnyT: Add Input Cell` | Add a new input cell |
| `AnyT: Add Note Cell` | Add a new note cell |
| `AnyT: Pause Execution` | Stop current execution |
| `AnyT: Reset Workflow` | Clear all cell execution state |
| `AnyT: Export to Script` | Export workflow as shell script |

## Links

- [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=AnyT.anyt-notebook)
- [GitHub Issues](https://github.com/anyt-io/notebook/issues)

## License

Copyright (c) 2026 AnyTransformer Inc. All rights reserved.

See the [LICENSE](LICENSE) file for details.
