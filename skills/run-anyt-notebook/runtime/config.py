"""Configuration constants and exception hierarchy for the run-anyt-notebook skill."""

from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = SKILL_DIR / "output"

SCHEMA_VERSION = "2.0"
VALID_CELL_TYPES = {"task", "shell", "input", "note", "break"}
VALID_CELL_ATTRIBUTES = {"id", "label", "agent", "skip"}
VALID_AGENT_TYPES = {"claude", "codex", "gemini"}
ID_PATTERN = r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$"

STATE_DIR_NAME = ".anyt"
CELLS_DIR_NAME = "cells"

# Completion marker filenames
MARKER_DONE = ".done"
MARKER_FAILED = ".failed"
MARKER_SKIPPED = ".skipped"


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------


class NotebookError(Exception):
    """Base exception for notebook skill errors."""


class ParseError(NotebookError):
    """Errors parsing the .anyt.md file."""


class ValidationError(NotebookError):
    """Validation errors (invalid structure, missing fields)."""


class ExecutionError(NotebookError):
    """Errors during cell execution."""
