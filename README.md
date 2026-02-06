# AnyT Notebook

**The workflow development environment for AI agents.**

AI agents are powerful, but they work like chatbots -- you give them a prompt, hope they get everything right in one shot, and when things break halfway through, you start over. AnyT Notebook changes this. It gives AI agents a **workflow layer**: visible steps, human checkpoints, and recoverable state -- so complex, multi-step tasks actually work.

## The Problem

When you ask an AI agent to do something complex -- set up a project, run a migration pipeline, build a feature with multiple dependencies -- the one-shot chatbot model falls apart:

- **No visibility** -- You can't see what the agent plans to do before it runs
- **No control** -- You can't pause, review, or redirect mid-execution
- **No recovery** -- If step 4 of 8 fails, you redo everything from scratch
- **No separation** -- AI handles things that a simple shell command could do faster and more reliably

## The Solution

AnyT Notebook is a VS Code extension that brings a Jupyter-style notebook interface for AI agent workflows. You break complex tasks into discrete cells, add human review checkpoints where they matter, mix AI and deterministic steps, and run the whole thing with full visibility and control.

```yaml
---
schema: "2.0"
name: deploy-pipeline
workdir: output
---

# Deploy Pipeline

<shell id="install">
npm install && npm run build
</shell>

<task id="generate-config">
Generate deployment configuration based on the project structure.
</task>

<break id="review">
Review the generated config before deploying.
</break>

<task id="deploy">
Deploy the application using the generated configuration.
</task>
```

**This is not a prompt.** It's a workflow program -- visible, controllable, debuggable, shareable.

## Why AnyT Notebook

### Visibility -- See the Full Plan Before Anything Runs
A notebook is an ordered list of steps. Before you hit "Run", you can see exactly what will happen: step 1, step 2, step 3. No more hoping the AI figures out the right sequence.

### Controllability -- Human Decides Where to Intervene
Break cells and input cells let you insert **human review gates** at exactly the right points. Not every step needs review -- but the critical ones should have a human checkpoint.

### Recoverability -- When Things Break, You Don't Start Over
If step 4 fails, you fix step 4 and re-run from there. Steps 1-3's results are intact. Folder-based state persistence means no work is lost.

### Composability -- Mix AI and Deterministic Steps
Not everything needs an AI agent. `npm install` doesn't need AI. Shell cells let you use the **right tool for each step**: AI for creative/complex tasks, shell scripts for deterministic/efficient ones.

### Adaptability -- Modify the Plan Mid-Execution
After reviewing step 3's output, you realize you need an extra step. Add a cell in the middle. Remove one that's no longer needed. The workflow evolves as you learn.

## Workflow Development Lifecycle

AnyT Notebook treats AI workflows like code -- they go through a development lifecycle:

| Phase | What You Do |
|-------|-------------|
| **Create** | Write cells: tasks for AI, shell for scripts, notes for documentation |
| **Debug** | Add break cells and input cells as checkpoints, run step by step |
| **Iterate** | Review outputs, fix failing steps, add/remove cells as needed |
| **Harden** | Remove breakpoints when confident, let the workflow run end-to-end |
| **Share** | Version the `.anyt.md` file, share a debugged workflow with your team |

This is the same cycle as software development: write code, add breakpoints, step through, fix bugs, remove breakpoints, deploy. **AnyT Notebook brings this discipline to AI agent workflows.**

## Cell Types

Five cell types for complete workflow control:

| Cell | Purpose | Example |
|------|---------|---------|
| **Task** | AI agent executes a natural language instruction | "Generate API endpoints based on the database schema" |
| **Shell** | Run shell scripts directly -- fast, deterministic, no AI overhead | `npm install && npm run build` |
| **Input** | Pause for user input with forms (text, select, checkbox) | "Choose deployment target: staging or production" |
| **Note** | Markdown documentation that marks progress checkpoints | Section headers, context for the next steps |
| **Break** | Pause execution for human review before continuing | "Review generated files before deploying" |

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

1. Create a new file with `.anyt.md` extension
2. The AnyT Notebook editor opens automatically
3. Write your workflow:

```yaml
---
schema: "2.0"
name: my-first-notebook
workdir: output
---

# My First Notebook

<task id="scaffold">
Create a new Express.js project with TypeScript configuration.
</task>

<break id="review-scaffold">
Review the project structure before continuing.
</break>

<task id="add-routes">
Add REST API routes for user CRUD operations.
</task>

<shell id="test">
npm test
</shell>
```

4. Select your AI runtime (Claude Code recommended)
5. Click "Run" to execute the notebook

During development, add break cells between steps to inspect outputs. Once the workflow is proven, remove them and let it run end-to-end.

## Supported AI Runtimes

| Runtime | Status | Notes |
|---------|--------|-------|
| Claude Code | Primary | Full support with streaming output |
| Codex | Supported | Full support with JSON output |

## Documentation

- [Product Overview](docs/PRODUCT.md) -- Detailed introduction to AnyT Notebook
- [User Guide](docs/USER_GUIDE.md) -- Complete guide to using AnyT Notebook
- [File Format Specification](docs/FILE_FORMAT.md) -- Detailed `.anyt.md` format reference
- [Examples](examples/) -- Sample notebooks to get you started

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `anyt.agent` | `"claude"` | AI agent to use (`claude`, `codex`) |
| `anyt.autoVersion` | `true` | Automatically create versions on changes |

## Commands

| Command | Description |
|---------|-------------|
| `AnyT: New Notebook` | Create a new .anyt.md notebook |
| `AnyT: Run Notebook` | Run all cells from beginning |
| `AnyT: Run Task` | Run a single cell |
| `AnyT: Add Task` | Add a new task cell |
| `AnyT: Add Shell Cell` | Add a new shell cell |
| `AnyT: Add Input Cell` | Add a new input cell |
| `AnyT: Add Note Cell` | Add a new note cell |
| `AnyT: Pause Execution` | Stop current execution |
| `AnyT: Reset Notebook` | Clear all cell execution state |
| `AnyT: Export to Script` | Export notebook as shell script |

## Links

- [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=AnyT.anyt-notebook)
- [GitHub Issues](https://github.com/anyt-io/notebook/issues)

## License

Copyright (c) 2026 AnyTransformer Inc. All rights reserved.

See the [LICENSE](LICENSE) file for details.
