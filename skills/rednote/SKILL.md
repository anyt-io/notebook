---
name: rednote
description: Generate Xiaohongshu/Rednote-style card images from markdown files. Use when user wants to create social media cards, convert markdown to card images, generate Rednote/XHS posts, or make shareable visual content from text. Supports multiple templates, custom watermarks, and batch card generation.
---

# Rednote Card Generator

Convert markdown content into beautiful Xiaohongshu (Rednote) style card images (1080x1440px PNG).

## Prerequisites

- `pnpm` (Node.js package manager)
- Chromium browser for Playwright

## Setup (first time only)

From the skill folder (`skills/rednote/`):

```bash
# Install dependencies
pnpm -C runtime install

# Build the app
pnpm -C runtime build

# Install Chromium for Playwright
pnpm -C runtime exec playwright install chromium
```

## Usage

Run from the skill folder (`skills/rednote/`):

### Generate cards from a markdown file

```bash
pnpm -C runtime generate path/to/content.md
```

### Choose a template

```bash
pnpm -C runtime generate content.md -t dark
```

Available templates: `apple-notes` (default), `swiss`, `magazine`, `aurora`, `dark`, `corporate`, `blank`.

### Set custom watermark

```bash
pnpm -C runtime generate content.md --watermark "@MyHandle"
```

### Set language

```bash
pnpm -C runtime generate content.md --lang zh
```

### Specify output directory

```bash
pnpm -C runtime generate content.md -o path/to/output/
```

### Combine options

```bash
pnpm -C runtime generate content.md -t magazine --watermark "MyBrand" --lang zh -o ./cards/
```

## Markdown Syntax

Standard GitHub Flavored Markdown plus:

| Syntax | Effect |
|--------|--------|
| `---` | Page break (splits into separate cards) |
| `==text==` | Highlighted text |
| Single newline | Line break (more lenient than standard Markdown) |

Long sections without `---` are auto-paginated based on card height.

## Output

- PNG images at 1080x1440px (@2x density for crisp rendering)
- Files named `xhs-card-1.png`, `xhs-card-2.png`, etc.
- Default output directory: `output/` inside the skill folder

## Limitations

- Chromium must be installed for Playwright (headless browser rendering)
- Images in markdown must be accessible URLs (or data URIs)
