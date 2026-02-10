# AnyT Notebook -- Product Overview

**The workflow development environment for AI agents.**

## Why This Exists

AI agents are the most powerful coding tools ever created. Claude Code, Codex, and others can generate entire applications, refactor complex systems, and solve problems that would take humans hours. But they all share the same fundamental limitation: **they work like chatbots.**

You give an AI agent a prompt. It tries to do everything in one shot. Maybe it works. Maybe it breaks halfway through and leaves your project in an inconsistent state. Maybe it goes in the wrong direction for 20 steps before you notice. There's no way to see the plan before it runs, no way to pause and redirect, no way to recover when things go wrong.

This is fine for small tasks -- "fix this bug", "write this function." But software development is full of complex, multi-step work: setting up projects, running migration pipelines, building features with dependencies, deploying systems. For these tasks, the chatbot model falls apart.

**AnyT Notebook exists to bridge this gap.** It gives AI agents something they've never had: a workflow layer -- visible steps, human checkpoints, recoverable state, and a development lifecycle.

## The Core Idea

The insight behind AnyT Notebook is simple:

> Complex AI work needs the same things complex human work needs: a plan you can see, steps you can control, and checkpoints where you verify before moving forward.

AnyT Notebook is a VS Code extension that provides a Jupyter-style notebook interface for AI agent workflows. Instead of a single prompt, you write a sequence of **cells** -- each one a discrete step that can be an AI task, a shell script, a user input form, a documentation note, or a pause point. The notebook executes cells in order, and you control where the human gets involved.

## The Problem in Detail

### AI Agents Today: Powerful but Uncontrollable

Every AI coding agent today -- Claude Code, Codex, Cursor, Copilot -- operates in fundamentally the same way:

1. User writes a prompt (or selects code and asks a question)
2. AI generates a response (code, explanation, or action)
3. User reviews and accepts or rejects
4. Repeat

This conversational loop works well for individual actions. But when the task is "set up a new microservice with authentication, database migrations, API routes, tests, and deployment config" -- a single prompt either produces a monolithic output that's hard to review, or the agent takes dozens of autonomous actions that you can't inspect until it's done.

The problems:

**No visibility.** You can't see the plan. The agent decides what to do internally, and you only see results after the fact. If the agent misunderstands step 1, every subsequent step compounds the error.

**No control.** You can't say "do steps 1-3, then stop so I can check before you do step 4." The agent runs until it's done or it fails. Human-in-the-loop means "approve or reject the whole thing," not "guide the process step by step."

**No recovery.** If the agent fails at step 6 of 10, there's no concept of "re-run from step 6." You start a new conversation, re-explain the context, and hope it gets further this time. Partial results from the first run may or may not still be valid.

**No separation of concerns.** The agent uses AI for everything -- including tasks that don't need AI at all. Running `npm install` through an AI agent is slower, more expensive, and less reliable than running it directly. But in a chatbot model, there's no way to mix AI and non-AI steps.

### What's Missing: A Workflow Tool

Software engineering has solved these exact problems before -- just in different domains:

- **Jupyter Notebook** solved it for data science: break computation into cells, run step by step, inspect intermediate results, iterate on individual cells.
- **CI/CD pipelines** solved it for deployment: break deployment into stages, add approval gates, retry failed stages without restarting the whole pipeline.
- **Makefiles** solved it for builds: declare steps with dependencies, run only what's needed, mix different tools in a single pipeline.

AI agent workflows need the same thing. Not a chatbot. A **workflow tool**.

## How AnyT Notebook Works

### The Notebook

An AnyT notebook is a `.anyt.md` file -- a plain-text, version-controllable document that defines a sequence of cells. Each cell has a type, an ID, and content:

```yaml
---
schema: "2.0"
name: project-setup
workdir: my-project
---

# Project Setup

<task id="scaffold">
Create a new Next.js project with TypeScript, Tailwind CSS, and ESLint.
</task>

<break id="review-scaffold">
Review the project structure. Check package.json, tsconfig, and folder layout.
</break>

<task id="auth">
Add NextAuth.js with GitHub OAuth provider. Create login/logout pages.
</task>

<input id="db-choice">
Which database do you want to use?

<form type="json">
{
  "fields": [
    {
      "name": "database",
      "type": "select",
      "label": "Database",
      "options": ["PostgreSQL", "MySQL", "SQLite"],
      "default": "PostgreSQL"
    }
  ]
}
</form>
</input>

<task id="database">
Set up Prisma ORM with the selected database. Create User and Session models.
</task>

<shell id="migrate">
cd my-project && npx prisma migrate dev --name init
</shell>

<shell id="test">
cd my-project && npm test
</shell>
```

This notebook tells you exactly what will happen, in what order, and where the human gets involved -- before anything runs.

### Five Cell Types

AnyT Notebook provides five cell types, each serving a distinct role in the workflow:

**Task Cells** -- The AI does the work. You write a natural language instruction, and the AI agent (Claude Code, Codex) executes it. The agent can read files, write code, run commands -- whatever's needed to fulfill the instruction. Output is streamed in real-time so you can watch progress.

**Shell Cells** -- Deterministic execution. You write a shell script, and it runs directly -- no AI involved. Fast, predictable, and cheap. Use these for installation, building, testing, deployment, or any step where you know exactly what command to run.

**Input Cells** -- The human provides information. The workflow pauses and presents a form (text fields, dropdowns, checkboxes, etc.). The user fills it in, and subsequent cells can reference the values. Use these for configuration choices, approval workflows, or any point where human judgment is needed.

**Note Cells** -- Documentation and progress markers. Markdown content that auto-completes when reached during execution. Use these to document sections of the workflow, provide context for the next steps, or mark milestones.

**Break Cells** -- Human review gates. The workflow pauses and waits for the user to click "Continue." Use these after critical steps where the human should inspect outputs before the workflow proceeds. Think of them as breakpoints in a debugger.

### Execution Model

Cells execute sequentially from top to bottom:

1. The user clicks "Run" (whole notebook) or runs a single cell
2. Each cell runs in order based on its type
3. Break and input cells **pause** execution and wait for the human
4. After the human continues, execution resumes with the next cell
5. If a cell fails, execution stops -- the user can fix and retry from that point

All execution state is stored in folders (`{workdir}/.anyt/cells/{cell-id}/`), separate from the notebook file. This means:
- The notebook file stays clean (just structure, no runtime data)
- State persists across VS Code sessions
- You can reset all state by deleting the `.anyt/` folder
- State is inspectable -- just look at the files

## The Workflow Development Lifecycle

This is where AnyT Notebook fundamentally differs from every other AI tool. It treats AI workflows as artifacts that go through a **development lifecycle** -- just like code.

### Phase 1: Create

You start by writing cells. Think about what needs to happen, in what order. What should the AI do? What can a shell script handle? Where does the human need to make a decision?

You don't need to get it perfect. Just write the rough sequence.

### Phase 2: Debug

Add break cells liberally -- after every AI task if you want. Run the notebook. At each breakpoint, inspect the output. Did the AI do what you expected? Is the output what the next step needs?

This is exactly like stepping through code with a debugger. You're building confidence in each step.

### Phase 3: Iterate

Some steps will fail. Some outputs won't match what you need. Now you iterate:

- Edit the task description to be clearer
- Add a shell cell to install a dependency the AI missed
- Insert an input cell where you realize you need human choice
- Split a task cell that's trying to do too much into two cells
- Remove a step that turned out to be unnecessary

Run again. Check again. The workflow improves with each iteration.

### Phase 4: Harden

The workflow is working. Now remove the unnecessary breakpoints. Keep only the ones at truly critical review points. The workflow should run with minimal human intervention -- pausing only where human judgment genuinely adds value.

### Phase 5: Share

The `.anyt.md` file is a portable, versionable artifact. Check it into git. Share it with teammates. Someone else can take your debugged workflow, understand what it does by reading it, and run it in their environment.

This lifecycle doesn't exist with chatbot-style AI agents. Every conversation is ephemeral. Every complex task starts from scratch. AnyT Notebook makes AI workflows **durable, improvable, and shareable**.

## Use Cases

### Project Scaffolding
Set up new projects with a predefined sequence: scaffold, configure, add dependencies, set up testing, create initial routes. Break cells let you verify the structure before the AI builds on top of it.

### Migration Pipelines
Database migrations, API version upgrades, framework migrations. Each step is explicit. Shell cells handle the mechanical parts (backup, migrate, test). AI handles the creative parts (rewrite code for new API). Break cells gate destructive operations.

### Content Generation Pipelines
Generate documentation, video scripts, marketing copy, or translations. Input cells collect requirements. AI generates content. Break cells let you review before the pipeline moves to the next stage (e.g., generating audio from approved scripts).

### CI/CD-Style Automation
Build, test, lint, deploy -- but with AI steps mixed in. The AI generates release notes while the shell runs tests. A break cell gates the actual deployment.

### Onboarding & Training
Create step-by-step guides that new team members run as notebooks. Notes provide context. Tasks set up their environment. Input cells collect their preferences. Break cells are natural stopping points for reading documentation.

### Prototyping & Experimentation
Rapidly prototype features. Each cell is one experiment. Run them independently. When something works, keep it. When it doesn't, modify just that cell. Build up a working solution incrementally instead of hoping a single prompt nails it.

## Comparison with Existing Tools

| | Chatbot AI (Claude Code, Codex CLI) | CI/CD (GitHub Actions, etc.) | Jupyter Notebook | AnyT Notebook |
|---|---|---|---|---|
| **Steps visible before run** | No | Yes | Yes | Yes |
| **Human review gates** | Approve/reject entire output | Manual approval stages | Run cells manually | Break & input cells |
| **Recovery on failure** | Start over | Retry failed stage | Re-run failed cell | Re-run from failed cell |
| **AI + deterministic mix** | Everything is AI | Everything is scripted | Code cells only | Task + shell cells |
| **Modify plan mid-run** | New conversation | Edit YAML, re-run | Add/edit cells | Add/edit cells |
| **State persistence** | Conversation history | Pipeline artifacts | Notebook file | Folder-based (.anyt/cells/) |
| **Shareable workflow** | Copy-paste prompts | YAML config file | .ipynb file | .anyt.md file |
| **Primary domain** | Ad-hoc coding tasks | Deployment & CI | Data science | AI agent workflows |

## Technical Design

### Separation of Structure and State

The notebook file (`.anyt.md`) stores only the **structure**: cell IDs, types, and content. All execution state -- outputs, status, duration, errors -- is stored in the filesystem under `.anyt/cells/{cell-id}/`. This separation means:

- Notebook files are clean and diffable
- Multiple people can share the same notebook without state conflicts
- Resetting is as simple as deleting folders
- State is transparent -- every output is a readable file on disk

### AI Runtime Abstraction

AnyT Notebook doesn't implement its own AI. It orchestrates existing AI agents (Claude Code, Codex) as runtimes. When a task cell runs, AnyT sends the prompt to the selected runtime and streams the output back. This means:

- You use the AI agent you already have installed
- New runtimes can be added without changing the notebook format
- Permission modes and model selection are configurable per execution

### Plain-Text, Version-Controlled Format

`.anyt.md` files are plain text with YAML frontmatter and XML-like cell syntax. They work with git, code review tools, and any text editor. No binary format, no proprietary database.

## Getting Started

1. Install AnyT Notebook from the VS Code Marketplace
2. Create a `.anyt.md` file
3. Write a few task and shell cells
4. Add break cells between steps
5. Select an AI runtime (Claude Code recommended)
6. Hit Run and step through your workflow
7. Iterate until it works
8. Remove unnecessary breakpoints
9. Share the notebook with your team

For the file format reference, see [anyt-notebook-spec.md](anyt-notebook-spec.md).
