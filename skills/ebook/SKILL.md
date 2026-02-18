---
name: ebook
description: Convert markdown files to EPUB and PDF ebooks. Use when user wants to create ebooks, convert markdown to epub or pdf, generate multi-chapter books, or produce formatted digital publications from markdown content.
---

# Ebook

## Prerequisites

- `uv` (Python package manager)

## Usage

Run from the skill folder (`skills/ebook/`):

### Convert markdown to EPUB

```bash
uv run --project runtime runtime/convert_ebook.py path/to/document.md
```

### Convert markdown to PDF

```bash
uv run --project runtime runtime/convert_ebook.py document.md -f pdf
```

### Generate both EPUB and PDF

```bash
uv run --project runtime runtime/convert_ebook.py document.md -f both
```

### Multi-chapter book

```bash
uv run --project runtime runtime/convert_ebook.py ch1.md ch2.md ch3.md -t "My Book" -a "Author Name"
```

### Add a cover image (EPUB)

```bash
uv run --project runtime runtime/convert_ebook.py document.md --cover cover.png
```

### Apply custom CSS styling

```bash
uv run --project runtime runtime/convert_ebook.py document.md --css style.css
```

### Specify output directory

```bash
uv run --project runtime runtime/convert_ebook.py document.md -o path/to/output/
```

## Output

- Default output directory: `output/` inside the skill folder.
- Single input file: output filename matches the input stem (e.g., `chapter.md` → `chapter.epub`).
- Multiple input files with `--title`: output filename is a slugified title (e.g., `"My Book"` → `my-book.epub`).
- Multiple input files without title: output filename is `ebook.epub` / `ebook.pdf`.

## Limitations

- Input files must be markdown (`.md` or `.markdown`).
- PDF generation uses WeasyPrint (HTML-based rendering), not LaTeX.
- Cover images are supported for EPUB only.
- Images referenced in markdown must use relative paths from the markdown file's directory.
