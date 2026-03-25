---
name: document-intake
description: Parse domain-specific documents (legal codes, regulations, procedures, immigration rules) into structured question banks for interview simulation systems. Use when user wants to extract structured data from regulatory or procedural documents, generate interview questions from domain documents, or build question banks for assessment systems.
---

# Document Intake

## Prerequisites

- `uv` (Python package manager)

## Usage

Run from the skill folder (`skills/document-intake/`):

### Parse a PDF document

```bash
uv run --project runtime runtime/intake.py --input path/to/document.pdf
```

### Parse a text or markdown file

```bash
uv run --project runtime runtime/intake.py --input path/to/rules.txt
uv run --project runtime runtime/intake.py --input path/to/regulations.md
```

### Specify output directory

```bash
uv run --project runtime runtime/intake.py --input document.pdf --output path/to/output/
```

### Specify domain context

```bash
uv run --project runtime runtime/intake.py --input document.pdf --domain immigration
```

## Supported Formats

- **PDF** (`.pdf`) — extracted via pdfplumber
- **Plain text** (`.txt`)
- **Markdown** (`.md`, `.markdown`)

## Output

Default output directory: `output/` inside the skill folder.

Two JSON files are produced:

### parsed_document.json

```json
{
  "source_file": "document.pdf",
  "sections": [
    {"heading": "Section 1", "content": "..."}
  ],
  "key_terms": [
    {"term": "...", "definition": "..."}
  ],
  "rules": [
    {"id": "R1", "text": "...", "source_section": "Section 1"}
  ],
  "raw_text": "..."
}
```

### question_bank.json

```json
{
  "metadata": {
    "source_file": "document.pdf",
    "domain": "immigration",
    "total_questions": 15
  },
  "questions": [
    {
      "id": "Q001",
      "text": "What is the definition of ...?",
      "category": "definition",
      "difficulty": 2,
      "expected_answer_keywords": ["keyword1", "keyword2"],
      "source_section": "Section 1",
      "domain": "immigration"
    }
  ]
}
```

## Question Categories

- **definition** — questions about key terms and definitions
- **rule** — questions about specific rules and requirements
- **procedure** — questions about procedural steps
- **eligibility** — questions about eligibility criteria
- **exception** — questions about exceptions and special cases

## Difficulty Levels

1. Basic recall
2. Understanding
3. Application
4. Analysis
5. Evaluation

## Limitations

- PDF extraction quality depends on the document structure (scanned images are not supported).
- Question generation uses heuristic extraction; complex nested regulations may require manual review.
- Best results with well-structured documents that have clear headings and numbered sections.
