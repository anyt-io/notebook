#!/usr/bin/env python3
"""
Parse an AnyT Notebook (.anyt.md) file into structured JSON.

Run with: uv run --project runtime runtime/parse_notebook.py <notebook.anyt.md>

Outputs JSON with frontmatter metadata and an ordered list of cells.
"""

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

from config import (
    SCHEMA_VERSION,
    VALID_AGENT_TYPES,
    VALID_CELL_TYPES,
    NotebookError,
    ParseError,
    ValidationError,
)

_ERROR_PREFIXES: dict[type[NotebookError], str] = {
    ParseError: "Parse error",
    ValidationError: "Validation error",
}


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class FormField:
    name: str
    field_type: str
    label: str
    description: str | None = None
    required: bool = False
    default: object = None
    placeholder: str | None = None
    options: list[dict[str, str]] | None = None
    rows: int | None = None
    accept: str | None = None
    multiple: bool = False
    validation: dict[str, object] | None = None


@dataclass
class Cell:
    cell_type: str
    id: str
    label: str | None = None
    agent: str | None = None
    skip: bool = False
    content: str = ""


@dataclass
class Notebook:
    schema: str = SCHEMA_VERSION
    name: str = ""
    description: str | None = None
    version: str | None = None
    workdir: str = "anyt_workspace"
    env_file: str = ".env"
    dependencies: dict[str, str] = field(default_factory=dict)
    cells: list[Cell] = field(default_factory=list)
    source_path: str | None = None


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

# Match opening cell tags: <type id="..." ...>
_OPEN_TAG_RE = re.compile(
    r"^<(task|shell|input|note|break)\s+((?:[a-z]+=(?:\"[^\"]*\"|\'[^\']*\')[\s]*)+)>\s*$",
    re.IGNORECASE,
)

# Match closing cell tags: </type>
_CLOSE_TAG_RE = re.compile(r"^</(task|shell|input|note|break)>\s*$", re.IGNORECASE)

# Extract individual attributes: key="value"
_ATTR_RE = re.compile(r'([a-z]+)=["\']([^"\']*)["\']')

# YAML frontmatter boundaries
_FRONTMATTER_DELIM = "---"


def _parse_frontmatter(lines: list[str]) -> tuple[dict[str, object], int]:
    """Parse YAML frontmatter from lines. Returns (metadata dict, end line index)."""
    if not lines or lines[0].strip() != _FRONTMATTER_DELIM:
        raise ParseError("File must start with YAML frontmatter (---)")

    end_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == _FRONTMATTER_DELIM:
            end_idx = i
            break

    if end_idx == -1:
        raise ParseError("Unclosed YAML frontmatter (missing closing ---)")

    # Simple YAML key-value parser for flat frontmatter
    metadata: dict[str, object] = {}
    current_key: str | None = None
    current_indent: int = 0
    nested: dict[str, str] = {}

    for line in lines[1:end_idx]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip())

        # Check if this is a nested value under a mapping key
        if current_key and indent > current_indent and ":" in stripped:
            k, _, v = stripped.partition(":")
            nested[k.strip()] = v.strip().strip('"').strip("'")
            continue

        # Save any accumulated nested mapping
        if current_key and nested:
            metadata[current_key] = dict(nested)
            nested = {}

        if ":" in stripped:
            k, _, v = stripped.partition(":")
            k = k.strip()
            v = v.strip()
            current_key = k
            current_indent = indent

            if not v:
                # Could be a mapping key — accumulate nested values
                nested = {}
                continue

            # Strip quotes
            if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                v = v[1:-1]

            metadata[k] = v

    # Handle final nested mapping
    if current_key and nested:
        metadata[current_key] = dict(nested)

    return metadata, end_idx


def _parse_cells(lines: list[str], start_idx: int) -> list[Cell]:
    """Parse cell tags from body lines."""
    cells: list[Cell] = []
    i = start_idx
    current_cell: Cell | None = None
    content_lines: list[str] = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Try to match a closing tag
        close_match = _CLOSE_TAG_RE.match(stripped)
        if close_match and current_cell:
            close_type = close_match.group(1).lower()
            if close_type != current_cell.cell_type:
                raise ParseError(
                    f"Mismatched closing tag: expected </{current_cell.cell_type}>, got </{close_type}> (line {i + 1})"
                )
            current_cell.content = "\n".join(content_lines).strip()
            cells.append(current_cell)
            current_cell = None
            content_lines = []
            i += 1
            continue

        # Try to match an opening tag
        open_match = _OPEN_TAG_RE.match(stripped)
        if open_match and current_cell is None:
            cell_type = open_match.group(1).lower()
            attrs_str = open_match.group(2)
            attrs = dict(_ATTR_RE.findall(attrs_str))

            if "id" not in attrs:
                raise ParseError(f"Cell tag missing required 'id' attribute (line {i + 1})")

            current_cell = Cell(
                cell_type=cell_type,
                id=attrs["id"],
                label=attrs.get("label"),
                agent=attrs.get("agent"),
                skip=attrs.get("skip", "").lower() == "true",
            )
            i += 1
            continue

        # Accumulate content inside a cell
        if current_cell is not None:
            content_lines.append(line)
        i += 1

    if current_cell is not None:
        raise ParseError(f"Unclosed cell tag: <{current_cell.cell_type} id=\"{current_cell.id}\"> has no closing tag")

    return cells


def parse_notebook(file_path: Path) -> Notebook:
    """Parse an .anyt.md file into a Notebook object."""
    if not file_path.exists():
        raise ParseError(f"File not found: {file_path}")

    text = file_path.read_text(encoding="utf-8")
    lines = text.split("\n")

    # Parse frontmatter
    metadata, fm_end = _parse_frontmatter(lines)

    # Build notebook from frontmatter
    notebook = Notebook(source_path=str(file_path.resolve()))

    if "schema" in metadata:
        notebook.schema = str(metadata["schema"])
    if "name" in metadata:
        notebook.name = str(metadata["name"])
    if "description" in metadata:
        notebook.description = str(metadata["description"])
    if "version" in metadata:
        notebook.version = str(metadata["version"])
    if "workdir" in metadata:
        notebook.workdir = str(metadata["workdir"])
    if "env_file" in metadata:
        notebook.env_file = str(metadata["env_file"])
    if "dependencies" in metadata and isinstance(metadata["dependencies"], dict):
        notebook.dependencies = {str(k): str(v) for k, v in metadata["dependencies"].items()}

    # Parse cells from body
    notebook.cells = _parse_cells(lines, fm_end + 1)

    return notebook


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_notebook(notebook: Notebook) -> list[str]:
    """Validate a parsed notebook. Returns a list of error messages (empty = valid)."""
    errors: list[str] = []

    if notebook.schema != SCHEMA_VERSION:
        errors.append(f"Schema must be '{SCHEMA_VERSION}', got '{notebook.schema}'")

    if not notebook.name:
        errors.append("Missing required 'name' field in frontmatter")

    seen_ids: set[str] = set()
    id_pattern = re.compile(r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")

    for cell in notebook.cells:
        if cell.cell_type not in VALID_CELL_TYPES:
            errors.append(f"Invalid cell type '{cell.cell_type}' on cell '{cell.id}'")

        if not id_pattern.match(cell.id):
            errors.append(f"Invalid cell ID format '{cell.id}' (must be slug-format: lowercase, alphanumeric, hyphens)")

        if cell.id in seen_ids:
            errors.append(f"Duplicate cell ID: '{cell.id}'")
        seen_ids.add(cell.id)

        if cell.agent and cell.agent not in VALID_AGENT_TYPES:
            errors.append(f"Invalid agent type '{cell.agent}' on cell '{cell.id}' (valid: {VALID_AGENT_TYPES})")

        if cell.skip and cell.cell_type != "break":
            errors.append(f"'skip' attribute only valid on break cells, found on '{cell.cell_type}' cell '{cell.id}'")

    return errors


# ---------------------------------------------------------------------------
# Form extraction
# ---------------------------------------------------------------------------

_FORM_RE = re.compile(r"<form\s+type=[\"']json[\"']>\s*(.*?)\s*</form>", re.DOTALL)


def extract_form_fields(cell: Cell) -> list[FormField] | None:
    """Extract form field definitions from an input cell's content.

    Returns a list of FormField objects, or None if the cell has no <form> block.
    """
    if cell.cell_type != "input":
        return None

    match = _FORM_RE.search(cell.content)
    if not match:
        return None

    try:
        form_data = json.loads(match.group(1))
    except json.JSONDecodeError as e:
        raise ParseError(f"Invalid JSON in form block of input cell '{cell.id}': {e}") from e

    raw_fields = form_data.get("fields", [])
    fields: list[FormField] = []

    for f in raw_fields:
        fields.append(
            FormField(
                name=f["name"],
                field_type=f["type"],
                label=f["label"],
                description=f.get("description"),
                required=f.get("required", False),
                default=f.get("default"),
                placeholder=f.get("placeholder"),
                options=f.get("options"),
                rows=f.get("rows"),
                accept=f.get("accept"),
                multiple=f.get("multiple", False),
                validation=f.get("validation"),
            )
        )

    return fields


def extract_form_description(cell: Cell) -> str | None:
    """Extract the markdown description above the <form> block in an input cell.

    Returns the description text, or None if the cell has no content above the form.
    """
    if cell.cell_type != "input":
        return None

    # Everything before the <form> tag
    form_start = cell.content.find("<form")
    if form_start == -1:
        # No form — entire content is the description
        return cell.content.strip() or None

    desc = cell.content[:form_start].strip()
    return desc or None


def format_form_prompt(cell: Cell) -> str | None:
    """Generate a human-readable text prompt for an input cell's form fields.

    Returns a formatted string the agent can present to the user, or None if no form.
    """
    fields = extract_form_fields(cell)
    if fields is None:
        return None

    desc = extract_form_description(cell)
    parts: list[str] = []

    if desc:
        parts.append(desc)
        parts.append("")

    for f in fields:
        req = " (required)" if f.required else ""
        line = f"- **{f.label}**{req}"

        if f.field_type in ("select", "radio") and f.options:
            opts = ", ".join(o["label"] for o in f.options)
            line += f" — Choose one: {opts}"
        elif f.field_type == "multiselect" and f.options:
            opts = ", ".join(o["label"] for o in f.options)
            line += f" — Choose one or more: {opts}"
        elif f.field_type == "checkbox":
            line += " — Yes/No"
        elif f.field_type == "number":
            constraints: list[str] = []
            if f.validation:
                if "min" in f.validation:
                    constraints.append(f"min: {f.validation['min']}")
                if "max" in f.validation:
                    constraints.append(f"max: {f.validation['max']}")
            if constraints:
                line += f" — Number ({', '.join(constraints)})"
            else:
                line += " — Number"
        elif f.field_type == "textarea":
            line += " — Multi-line text"
        elif f.field_type == "file":
            if f.accept:
                line += f" — File ({f.accept})"
            else:
                line += " — File"
            if f.multiple:
                line += ", multiple allowed"
        else:
            if f.placeholder:
                line += f" — e.g. {f.placeholder}"

        if f.default is not None:
            line += f" [default: {f.default}]"

        if f.description:
            line += f"\n  {f.description}"

        parts.append(line)

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse an AnyT Notebook (.anyt.md) file into JSON")
    parser.add_argument("notebook", help="Path to .anyt.md file")
    parser.add_argument("--validate", action="store_true", help="Validate the notebook and report errors")
    parser.add_argument("--cells-only", action="store_true", help="Output only the cells array")
    parser.add_argument("--cell", help="Output a single cell by ID")
    parser.add_argument("--form", help="Extract form fields from an input cell by ID (outputs JSON)")
    parser.add_argument("--form-prompt", help="Generate a human-readable prompt for an input cell by ID")
    parser.add_argument("--pretty", action="store_true", default=True, help="Pretty-print JSON output (default: true)")
    parser.add_argument("--compact", action="store_true", help="Compact JSON output")
    args = parser.parse_args()

    try:
        notebook_path = Path(args.notebook)
        notebook = parse_notebook(notebook_path)

        if args.validate:
            errors = validate_notebook(notebook)
            if errors:
                print("Validation errors:", file=sys.stderr)
                for err in errors:
                    print(f"  - {err}", file=sys.stderr)
                return 1
            print("Notebook is valid.")
            return 0

        indent = None if args.compact else 2

        if args.form:
            for cell in notebook.cells:
                if cell.id == args.form:
                    fields = extract_form_fields(cell)
                    if fields is None:
                        print(f"No form found in cell '{args.form}'", file=sys.stderr)
                        return 1
                    print(json.dumps([asdict(f) for f in fields], indent=indent))
                    return 0
            print(f"Cell not found: {args.form}", file=sys.stderr)
            return 1

        if args.form_prompt:
            for cell in notebook.cells:
                if cell.id == args.form_prompt:
                    prompt = format_form_prompt(cell)
                    if prompt is None:
                        print(f"No form found in cell '{args.form_prompt}'", file=sys.stderr)
                        return 1
                    print(prompt)
                    return 0
            print(f"Cell not found: {args.form_prompt}", file=sys.stderr)
            return 1

        if args.cell:
            for cell in notebook.cells:
                if cell.id == args.cell:
                    print(json.dumps(asdict(cell), indent=indent))
                    return 0
            print(f"Cell not found: {args.cell}", file=sys.stderr)
            return 1

        if args.cells_only:
            print(json.dumps([asdict(c) for c in notebook.cells], indent=indent))
        else:
            print(json.dumps(asdict(notebook), indent=indent))

        return 0

    except NotebookError as e:
        prefix = _ERROR_PREFIXES.get(type(e), "Error")
        print(f"\n{prefix}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
