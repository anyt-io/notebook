# AnyT Notebook

**The workflow development environment for AI agents.**

AI agents are powerful, but they work like chatbots -- you give them a prompt, hope they get everything right in one shot, and when things break halfway through, you start over. AnyT Notebook changes this. It gives AI agents a **workflow layer**: visible steps, human checkpoints, and recoverable state.

![AnyT Notebook Demo](media/demo.gif)

## Why AnyT Notebook

When you ask an AI agent to do something complex, the one-shot chatbot model falls apart:

- **No visibility** -- You can't see the plan before it runs
- **No control** -- You can't pause, review, or redirect mid-execution
- **No recovery** -- If step 4 of 8 fails, you redo everything
- **No separation** -- AI handles things a simple shell command could do faster

AnyT Notebook solves this with a Jupyter-style notebook for AI agent workflows. Break tasks into cells, add human checkpoints, mix AI and shell scripts, and run with full control. Edit cells with a rich text editor featuring code blocks with syntax highlighting, or toggle to raw markdown. Give cells human-friendly labels so your notebook reads like a plan. Configure agent profiles per-notebook or per-cell to use different runtimes and settings where they matter most.

## Supported Runtimes

AnyT Notebook works with multiple AI runtimes:

| Runtime | Status | Notes |
|---------|--------|-------|
| **Claude Code** | Primary | Full support with streaming output |
| **Codex** | Supported | Full support with JSON output |

Select your runtime from the dropdown in the notebook toolbar. Switch between runtimes at any time. Use **agent profiles** to configure different runtimes per-notebook or per-cell -- for example, use Claude Code for complex reasoning tasks and a faster runtime for simpler ones.

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

**1. Try a Sample** -- `Cmd+Shift+P` -> "AnyT: Open Sample Notebook" -> pick one -> click Run

**2. Or Create Your Own:**
- `Cmd+Shift+P` -> "AnyT: New Notebook"
- Click **+ Task**, **+ Shell**, **+ Input**, **+ Break**, or **+ Note** to add cells
- Edit cells with the rich text editor (or switch to the Markdown tab for raw editing)
- Click **Run** to execute the notebook step by step

---

## Cell Types

AnyT Notebook provides five cell types. Mix and match them to build workflows that combine AI execution, automation, and human oversight.

### Task

Task cells are executed by your AI agent (Claude Code or Codex). Write a natural language instruction and the agent carries it out. Use tasks for anything that requires reasoning, code generation, or multi-file changes.

> *Example: "Create a REST API with Express.js and TypeScript, including user authentication routes."*

### Shell

Shell cells run scripts directly -- no AI involved. They're fast, deterministic, and ideal for commands you already know. Use them for installs, builds, tests, linting, or any CLI operation.

> *Example: `npm install && npm run build && npm test`*

### Input

Input cells pause execution and present a form to the user. Use them to collect configuration values, choose between options, or supply information that downstream cells need. Form responses are available to subsequent cells.

> *Example: "Choose deployment target" with a dropdown for staging vs. production.*

### Note

Note cells are markdown documentation checkpoints. They auto-complete instantly when reached and serve as section headers, context annotations, or progress markers in your workflow.

> *Example: A section header like "Phase 2: Testing and Validation" to organize your notebook.*

### Break

Break cells pause execution so you can review what's happened so far. Inspect outputs, verify results, then click Continue when ready. Add breaks liberally while developing a workflow; remove them once you're confident it runs end-to-end.

> *Example: "Review the generated project structure before adding API routes."*

---

## Workflow Development Lifecycle

AnyT Notebook treats AI workflows like code -- build, test, and refine them iteratively:

1. **Create** -- Add cells visually: tasks for AI work, shell for scripts, inputs for user decisions, notes for documentation
2. **Debug** -- Insert break cells as checkpoints and run step by step to inspect each output
3. **Iterate** -- Review results, fix failing steps, reorder or add cells as needed
4. **Harden** -- Remove breakpoints once confident and run the full workflow end-to-end
5. **Share** -- Version the `.anyt.md` file and share with your team

This is the same cycle as software development: write code, add breakpoints, step through, fix bugs, remove breakpoints, deploy. **AnyT Notebook brings this discipline to AI agent workflows.**

---

## Sample Notebooks

| Sample | What it does |
|--------|--------------|
| **Hello World** | Simplest notebook -- one task, instant result |
| **Web Scraper** | Scrape, review, parse, validate -- with human checkpoints |
| **Form Demo** | All form field types for user input |
| **Product Video** | Full video pipeline with Remotion, voiceover, and subtitles |

Open Command Palette -> **"AnyT: Open Sample Notebook"** -> pick one -> click Run.

---

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `anyt.agent` | `"claude"` | AI agent (`claude` or `codex`) |
| `anyt.autoVersion` | `true` | Auto-version on changes |

---

## Commands

| Command | What it does |
|---------|--------------|
| `AnyT: New Notebook` | Create a fresh `.anyt.md` file |
| `AnyT: Open Sample Notebook` | Browse and open built-in sample notebooks |

All other actions (run, stop, reset, add cells) are available directly from the notebook toolbar.

---

## Requirements

- **Claude Code CLI** installed and authenticated ([install guide](https://docs.anthropic.com/en/docs/claude-code)) or **Codex CLI** installed
- VS Code 1.85+

---

## Skills

AnyT Notebook supports [PSPM](https://github.com/anyt-io/pspm-cli) skills — reusable prompt skill packages that extend AI coding agents with additional capabilities. This repo includes example skills in the [`skills/`](skills/) directory:

| Skill | Description |
|-------|-------------|
| [youtube-downloader](skills/youtube-downloader/) | Download YouTube videos and transcripts in various formats and qualities |
| [pspm-skill-creator](skills/pspm-skill-creator/) | Scaffold, validate, and package PSPM skills with isolated runtime environments |
| [create-anyt-notebook](skills/create-anyt-notebook/) | Create new AnyT Notebook files from templates |

Install a skill with PSPM:

```bash
pspm install youtube-downloader
```

See [docs/skill-development-guide.md](docs/skill-development-guide.md) for full conventions on creating new skills.

---

## Documentation

- [Product Overview](docs/PRODUCT.md) -- Detailed introduction to AnyT Notebook
- [User Guide](docs/USER_GUIDE.md) -- Complete guide to using AnyT Notebook
- [File Format Specification](docs/anyt-notebook-spec.md) -- Complete `.anyt.md` format reference
- [Changelog](CHANGELOG.md) -- Release history and changes
- [Examples](examples/) -- Sample notebooks to get you started

## Links

- [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=AnyT.anyt-notebook)
- [GitHub Issues](https://github.com/anyt-io/notebook/issues)

## License

Copyright (c) 2026 AnyTransformer Inc. All rights reserved.

See the [LICENSE](LICENSE) file for details.
