#!/usr/bin/env python3
"""
Update cells in an AnyT Notebook (.anyt.md) file.

Run with: uv run --project runtime runtime/update_notebook.py <notebook.anyt.md> --cell <id> --content <new>

Preserves the original file structure, only modifying the targeted cell content.
"""

import argparse
import re
import sys
from pathlib import Path

from config import NotebookError, ParseError

_ERROR_PREFIXES: dict[type[NotebookError], str] = {
    ParseError: "Parse error",
}

# Match opening cell tags
_OPEN_TAG_RE = re.compile(
    r"^<(task|shell|input|note|break)\s+((?:[a-z]+=(?:\"[^\"]*\"|\'[^\']*\')[\s]*)+)>\s*$",
    re.IGNORECASE,
)
_CLOSE_TAG_RE = re.compile(r"^</(task|shell|input|note|break)>\s*$", re.IGNORECASE)
_ATTR_RE = re.compile(r'([a-z]+)=["\']([^"\']*)["\']')


def update_cell_content(file_path: Path, cell_id: str, new_content: str) -> None:
    """Replace the content of a specific cell in the notebook file."""
    if not file_path.exists():
        raise ParseError(f"File not found: {file_path}")

    text = file_path.read_text(encoding="utf-8")
    lines = text.split("\n")

    # Find the cell boundaries
    cell_start: int | None = None
    cell_end: int | None = None
    cell_type: str | None = None

    for i, line in enumerate(lines):
        stripped = line.strip()

        open_match = _OPEN_TAG_RE.match(stripped)
        if open_match:
            attrs = dict(_ATTR_RE.findall(open_match.group(2)))
            if attrs.get("id") == cell_id:
                cell_start = i
                cell_type = open_match.group(1).lower()
                continue

        if cell_start is not None and cell_type is not None:
            close_match = _CLOSE_TAG_RE.match(stripped)
            if close_match and close_match.group(1).lower() == cell_type:
                cell_end = i
                break

    if cell_start is None:
        raise ParseError(f"Cell not found: {cell_id}")
    if cell_end is None:
        raise ParseError(f"Unclosed cell tag for: {cell_id}")

    # Replace the content between open and close tags
    new_lines = [*lines[: cell_start + 1], new_content, *lines[cell_end:]]
    file_path.write_text("\n".join(new_lines), encoding="utf-8")


def add_cell(
    file_path: Path, cell_type: str, cell_id: str, content: str, label: str | None = None, after: str | None = None
) -> None:
    """Add a new cell to the notebook. Inserts after the specified cell ID, or appends to the end."""
    if not file_path.exists():
        raise ParseError(f"File not found: {file_path}")

    text = file_path.read_text(encoding="utf-8")
    lines = text.split("\n")

    # Build the new cell tag
    attrs = f'id="{cell_id}"'
    if label:
        attrs += f' label="{label}"'
    new_cell = f"\n<{cell_type} {attrs}>\n{content}\n</{cell_type}>\n"

    if after:
        # Find the closing tag of the 'after' cell
        in_target = False
        target_type: str | None = None
        insert_idx: int | None = None

        for i, line in enumerate(lines):
            stripped = line.strip()
            open_match = _OPEN_TAG_RE.match(stripped)
            if open_match:
                attrs_dict = dict(_ATTR_RE.findall(open_match.group(2)))
                if attrs_dict.get("id") == after:
                    in_target = True
                    target_type = open_match.group(1).lower()
                    continue

            if in_target and target_type:
                close_match = _CLOSE_TAG_RE.match(stripped)
                if close_match and close_match.group(1).lower() == target_type:
                    insert_idx = i + 1
                    break

        if insert_idx is None:
            raise ParseError(f"Cell not found for 'after' reference: {after}")

        lines.insert(insert_idx, new_cell)
    else:
        # Append to end
        lines.append(new_cell)

    file_path.write_text("\n".join(lines), encoding="utf-8")


def remove_cell(file_path: Path, cell_id: str) -> None:
    """Remove a cell from the notebook file."""
    if not file_path.exists():
        raise ParseError(f"File not found: {file_path}")

    text = file_path.read_text(encoding="utf-8")
    lines = text.split("\n")

    cell_start: int | None = None
    cell_end: int | None = None
    cell_type: str | None = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        open_match = _OPEN_TAG_RE.match(stripped)
        if open_match:
            attrs = dict(_ATTR_RE.findall(open_match.group(2)))
            if attrs.get("id") == cell_id:
                cell_start = i
                cell_type = open_match.group(1).lower()
                continue

        if cell_start is not None and cell_type is not None:
            close_match = _CLOSE_TAG_RE.match(stripped)
            if close_match and close_match.group(1).lower() == cell_type:
                cell_end = i
                break

    if cell_start is None:
        raise ParseError(f"Cell not found: {cell_id}")
    if cell_end is None:
        raise ParseError(f"Unclosed cell tag for: {cell_id}")

    # Remove lines from start to end (inclusive), plus any blank line after
    end = cell_end + 1
    if end < len(lines) and lines[end].strip() == "":
        end += 1

    new_lines = lines[:cell_start] + lines[end:]
    file_path.write_text("\n".join(new_lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Update cells in an AnyT Notebook (.anyt.md) file")
    parser.add_argument("notebook", help="Path to .anyt.md file")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # update command
    update_parser = subparsers.add_parser("update", help="Update a cell's content")
    update_parser.add_argument("--cell", required=True, help="Cell ID to update")
    update_parser.add_argument("--content", required=True, help="New cell content")

    # add command
    add_parser = subparsers.add_parser("add", help="Add a new cell")
    add_parser.add_argument(
        "--type", required=True, choices=["task", "shell", "input", "note", "break"], help="Cell type"
    )
    add_parser.add_argument("--id", required=True, help="Cell ID")
    add_parser.add_argument("--content", required=True, help="Cell content")
    add_parser.add_argument("--label", help="Cell label")
    add_parser.add_argument("--after", help="Insert after this cell ID")

    # remove command
    remove_parser = subparsers.add_parser("remove", help="Remove a cell")
    remove_parser.add_argument("--cell", required=True, help="Cell ID to remove")

    args = parser.parse_args()

    try:
        notebook_path = Path(args.notebook)

        if args.command == "update":
            update_cell_content(notebook_path, args.cell, args.content)
            print(f"Updated cell '{args.cell}'")
        elif args.command == "add":
            add_cell(notebook_path, args.type, args.id, args.content, args.label, getattr(args, "after", None))
            print(f"Added {args.type} cell '{args.id}'")
        elif args.command == "remove":
            remove_cell(notebook_path, args.cell)
            print(f"Removed cell '{args.cell}'")

        return 0

    except NotebookError as e:
        prefix = _ERROR_PREFIXES.get(type(e), "Error")
        print(f"\n{prefix}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
