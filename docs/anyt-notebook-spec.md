# AnyT Notebook File Specification

The `.anyt.md` file format is a Markdown-based notebook that defines a sequence of executable cells — shell commands, AI agent tasks, user inputs, notes, and breakpoints.

## Current Version

- **Spec version**: 2.4
- **Schema version**: 2.0

## Full Specification

The complete specification is maintained in the [anyt-io monorepo](https://github.com/anyt-io/anyt-io) at `docs/anyt-notebook-spec.md`.

For user-friendly documentation, see: **[docs.anyt.io/notebook/file-format](https://docs.anyt.io/notebook/file-format)**

## Quick Overview

An `.anyt.md` file has two sections:

1. **YAML frontmatter** — notebook metadata between `---` delimiters
2. **Body** — a markdown heading followed by ordered cell tags (`<task>`, `<shell>`, `<input>`, `<note>`, `<break>`)

For the full list of cell types, attributes, frontmatter options, and examples, refer to the documentation linked above.
