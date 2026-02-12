# Changelog

All notable changes to AnyT Notebook will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.9.0] - 2026-02-11

### Added

- Agent profile system for per-notebook and per-cell agent configuration
- Runtime health checks with setup links and agent display in collapsed cells

### Fixed

- Agent config default selector and badge dropdown UX
- Agent label now shows only on task cells; fixed config panel profiles
- Auto-discover runtimes on editor open; fixed NOT INSTALLED display

## [0.8.0] - 2026-02-10

### Added

- Cell label attribute for human-friendly display names (e.g., `label="Setup Project"`)
- Spec v2.1 documentation with label support

### Changed

- Promoted label as primary cell name, made cell ID read-only
- Renamed spec file to `anyt-notebook-spec.md`
- Removed workflow inputs feature from codebase
- Removed v1.0 schema support and cleaned up stale docs

### Fixed

- Race condition where done marker is missed on process exit

## [0.7.0] - 2026-02-09

### Added

- TipTap 3.x rich text editor for cell editing with code block syntax highlighting, language selector, and copy button
- Markdown editor tab for switching between rich text and raw markdown

### Changed

- Migrated cell editors (task, note, break, input) from textarea to TipTap-based MarkdownEditor
- Extracted TipTap editor into `@anyt/editor` shared package
- Unified cell UI interactions and allowed editing completed cells
- Improved schema preview text wrapping

### Fixed

- Removed false selection highlight on cells

## [0.6.3] - 2026-02-09

### Added

- Telemetry hooks for execution event tracking
- Codex runtime suggestion support

### Changed

- Refactored ExecutionService into focused sub-services (state machine, number manager, interaction state, workdir validator)
- Decomposed large files into focused modules with unit tests
- Updated documentation for execution refactor and type split

### Fixed

- Webview build errors and font loading issues
- Improved cancellation handling

## [0.6.2] - 2026-02-06

### Added

- Environment variable support with `env_file` for task and shell cells
- Login shell option for shell cells to source profile files
- Responsive toolbar with compact mode
- Markdown link handling in cell output

### Fixed

- Stop notebook execution on any cell failure
- Breakpoint reset behavior

## [0.6.1] - 2026-02-06

### Added

- Collapsible cell cards for notebook overview

### Changed

- Rewrote README for visual-first UX and reduced command palette commands
- Synced documentation with v0.6.0 code changes

## [0.6.0] - 2026-02-05

### Added

- Schema versioning for `.anyt.md` file format
- CurrentCellIndicator component with state-aware navigation and actions
- Running cell indicator in toolbar with improved execution state handling
- Relative image path support in markdown cells
- `<form>` tag architecture for input cells
- Comprehensive tests for break, shell executors, and watcher service
- Project-scaffolder sample notebook

### Changed

- Switched form format to JSON-only with silent DSL/YAML migration
- Rewrote product positioning as "The workflow development environment for AI agents"
- Updated extension README with new positioning and correct demo GIF URL
- Renamed workflow terminology to notebook throughout codebase
- Removed legacy YAML code block support for input schemas
- Optimized extension package size
- Added biome linting rules and reduced cognitive complexity

### Fixed

- Shell cell editor not saving changes
- Restored 100ms timer interval for execution time display
- Removed Cancel and Skip buttons from input form

## [0.5.2] - 2026-02-05

### Added

- **Schema versioning** for `.anyt.md` file format (`schema: "2.0"` required in frontmatter)
- **Versioned specs** and consolidated documentation under `docs/`

### Changed

- **Optimized extension package size** by excluding unnecessary files from `.vsix`
- **Renamed "workflow" to "notebook"** terminology throughout codebase
- **Removed legacy YAML code block support** for input schemas (use `<form>` tags instead)
- Moved CHANGELOG.md into extension package for VS Code Marketplace visibility

## [0.5.1] - 2026-02-05

### Added

- **CurrentCellIndicator component** - Always-visible status indicator showing current cell state
  - Color-coded by cell type with state icons (running/waiting/pending/complete)
  - Click to navigate to current cell
  - Action buttons: stop (running), run (pending), continue (break)
- **Improved execution state handling** - Better recovery from stuck states
  - `forceResetState()` method for state recovery
  - Try-finally wrapper to ensure cleanup on errors
  - Enhanced warning messages showing which cell is blocking

### Changed

- Removed "Go To Next" button from toolbar (replaced by CurrentCellIndicator)
- Improved state detection with fallback to cell status when IDs are stale

### Fixed

- Execution state getting stuck after errors or interruptions
- Warning messages now show specific cell ID instead of generic message

## [0.5.0] - 2026-02-04

### Added

- **Sample notebooks** - 6 pre-built example workflows demonstrating various capabilities:
  - Hello World (beginner)
  - Express API (beginner)
  - Project Scaffolder with user input forms (intermediate)
  - React Component with tests and Storybook (intermediate)
  - Full-Stack Next.js app with auth and database (advanced)
  - Data Pipeline mixing shell and AI tasks (intermediate)
- **"Open Sample Notebook" command** - QuickPick UI with complexity badges to try samples
- **VS Code walkthrough** - Getting started guide in VS Code's Welcome tab
- **Product-focused README** - Updated with use cases, quick start, and samples section

### Changed

- **Renamed "Workflow" to "Notebook"** throughout codebase for clarity
- **Auto-switch to Output tab** when task starts running
- **Redesigned toolbar layout** with social links

### Fixed

- UI stability improvements preventing flickering and layout shift during cell execution

## [0.4.1] - 2026-02-03

### Fixed

- Add `--verbose` flag to Claude Code runtime for proper output
- Add `--skip-git-repo-check` flag to Codex runtime for non-git directories

## [0.4.0] - 2026-02-03

### Added

- **New notebook command** - `anyt.newNotebook` command to create new notebooks
- **Break cell type** - new cell type for workflow pause points
- **Form-based input system** - improved input cells with form-based UI
- **GitHub Actions CI/CD** - automated workflows for CI and release
- **Jupyter-style execution numbers** - execution counts with workspace persistence
- **Shell cell type** - direct shell script execution with stdout/stderr capture
- **Codex CLI support** - alternative runtime with JSON output parsing
- **Unified cell styling** - consistent status indicators and Jupyter-style execution counts

### Changed

- Simplified top bar UI with editable workflow title
- Improved cell insertion and deletion behavior
- Added reset buttons and improved toolbar workflow controls
- Improved cell ID generation with auto-focus rename
- Simplified input cells to form-only design
- Made workflow version optional in frontmatter

## [0.3.0] - 2026-02-02

### Added

- **Drag-and-drop cell reordering** - reorder workflow cells by dragging with smooth animations
- **@dnd-kit integration** - using industry-standard React drag-and-drop library for accessibility and touch support
- **Drag handle UI** - grip icon visible on cell hover for intuitive reordering
- **Drag overlay** - visual preview of cell being dragged

### Changed

- Removed cell dependency system (cells execute in order, top to bottom)
- Updated to Tailwind CSS v4

### Fixed

- Replace non-null assertion with nullish coalescing for safer code

## [0.2.0] - 2026-02-02

### Added

- **Unified cell architecture** with three cell types: task, input, and note
- **Folder-based state persistence** - all cell state stored in `.anyt/cells/{id}/` directories
- **Input cells** - human-in-the-loop checkpoints that pause workflow for user interaction
- **Note cells** - markdown documentation cells that auto-complete as checkpoints
- **Real-time progress tracking** via file watchers on cell directories
- **Clickable file paths** in task output for easy navigation
- **Inputs editor UI** for managing workflow-level input variables
- **Dependency management** - cells can depend on other cells of any type
- **Streaming output** - real-time AI agent output displayed in notebook UI
- **Pre-commit hooks** with Biome for consistent code formatting

### Changed

- Renamed extension from PSPM to AnyT Notebook
- Moved from task-centric to unified cell-based architecture
- Workflow files now store only structure (id, type, description, depends)
- All runtime state (status, outputs, duration) stored in cell folders instead of workflow file
- Improved process execution by spawning directly without shell

### Fixed

- Process execution reliability improvements
- Input cell response handling with folder-based storage

## [0.1.0] - 2026-01-29

### Added

- Initial VS Code extension setup
- Custom editor for `.anyt.md` files
- Jupyter-style notebook UI with React and Tailwind CSS
- Task cell execution with Claude Code runtime support
- Basic workflow parsing and execution
- YAML frontmatter for workflow metadata
- XML-like cell syntax for task definitions
