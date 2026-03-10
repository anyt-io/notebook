#!/usr/bin/env python3
"""
Manage AnyT Notebook execution state.

Run with: uv run --project runtime runtime/manage_state.py <workdir> <command> [options]

Commands:
  status              Show execution status of all cells
  mark-done           Mark a cell as done
  mark-failed         Mark a cell as failed
  reset               Reset state for a cell or all cells
  read-input          Read input cell response
"""

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from config import (
    CELLS_DIR_NAME,
    MARKER_DONE,
    MARKER_FAILED,
    MARKER_SKIPPED,
    STATE_DIR_NAME,
    ExecutionError,
    NotebookError,
)

_ERROR_PREFIXES: dict[type[NotebookError], str] = {
    ExecutionError: "Execution error",
}


def _cells_dir(workdir: Path) -> Path:
    return workdir / STATE_DIR_NAME / CELLS_DIR_NAME


def _cell_dir(workdir: Path, cell_id: str) -> Path:
    return _cells_dir(workdir) / cell_id


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_cell_status(workdir: Path, cell_id: str) -> str:
    """Get the status of a cell: 'done', 'failed', 'skipped', or 'pending'."""
    cell_dir = _cell_dir(workdir, cell_id)
    if (cell_dir / MARKER_DONE).exists():
        return "done"
    if (cell_dir / MARKER_FAILED).exists():
        return "failed"
    if (cell_dir / MARKER_SKIPPED).exists():
        return "skipped"
    return "pending"


def get_all_status(workdir: Path, cell_ids: list[str]) -> list[dict[str, str]]:
    """Get status for all cells."""
    return [{"id": cid, "status": get_cell_status(workdir, cid)} for cid in cell_ids]


def mark_done(workdir: Path, cell_id: str, duration: float | None = None,
              extra: dict[str, object] | None = None) -> None:
    """Mark a cell as completed successfully."""
    cell_dir = _cell_dir(workdir, cell_id)
    cell_dir.mkdir(parents=True, exist_ok=True)

    # Remove any existing markers
    for marker in [MARKER_DONE, MARKER_FAILED, MARKER_SKIPPED]:
        (cell_dir / marker).unlink(missing_ok=True)

    data: dict[str, object] = {"status": "done", "timestamp": _now_iso()}
    if duration is not None:
        data["duration"] = duration
    if extra:
        data.update(extra)

    (cell_dir / MARKER_DONE).write_text(json.dumps(data, indent=2), encoding="utf-8")


def mark_failed(workdir: Path, cell_id: str, error: str, duration: float | None = None) -> None:
    """Mark a cell as failed."""
    cell_dir = _cell_dir(workdir, cell_id)
    cell_dir.mkdir(parents=True, exist_ok=True)

    for marker in [MARKER_DONE, MARKER_FAILED, MARKER_SKIPPED]:
        (cell_dir / marker).unlink(missing_ok=True)

    data: dict[str, object] = {"status": "failed", "error": error, "timestamp": _now_iso()}
    if duration is not None:
        data["duration"] = duration

    (cell_dir / MARKER_FAILED).write_text(json.dumps(data, indent=2), encoding="utf-8")


def mark_skipped(workdir: Path, cell_id: str) -> None:
    """Mark a cell as skipped."""
    cell_dir = _cell_dir(workdir, cell_id)
    cell_dir.mkdir(parents=True, exist_ok=True)

    for marker in [MARKER_DONE, MARKER_FAILED, MARKER_SKIPPED]:
        (cell_dir / marker).unlink(missing_ok=True)

    data = {"status": "skipped", "timestamp": _now_iso()}
    (cell_dir / MARKER_SKIPPED).write_text(json.dumps(data, indent=2), encoding="utf-8")


def save_shell_script(workdir: Path, cell_id: str, script: str) -> None:
    """Save shell cell script content."""
    cell_dir = _cell_dir(workdir, cell_id)
    cell_dir.mkdir(parents=True, exist_ok=True)
    (cell_dir / "script.sh").write_text(script, encoding="utf-8")


def save_shell_output(workdir: Path, cell_id: str, output: str) -> None:
    """Save shell cell output."""
    cell_dir = _cell_dir(workdir, cell_id)
    cell_dir.mkdir(parents=True, exist_ok=True)
    (cell_dir / "output.log").write_text(output, encoding="utf-8")


def save_task_description(workdir: Path, cell_id: str, description: str) -> None:
    """Save task cell description."""
    cell_dir = _cell_dir(workdir, cell_id)
    cell_dir.mkdir(parents=True, exist_ok=True)
    (cell_dir / "task.md").write_text(description, encoding="utf-8")


def save_task_summary(workdir: Path, cell_id: str, summary: str) -> None:
    """Save task cell summary."""
    cell_dir = _cell_dir(workdir, cell_id)
    cell_dir.mkdir(parents=True, exist_ok=True)
    (cell_dir / "summary.md").write_text(summary, encoding="utf-8")


def save_input_response(workdir: Path, cell_id: str, response: dict[str, object]) -> None:
    """Save input cell response."""
    cell_dir = _cell_dir(workdir, cell_id)
    cell_dir.mkdir(parents=True, exist_ok=True)
    data = {"values": response, "timestamp": _now_iso()}
    (cell_dir / "response.json").write_text(json.dumps(data, indent=2), encoding="utf-8")


def read_input_response(workdir: Path, cell_id: str) -> dict[str, object] | None:
    """Read a previously saved input cell response. Returns None if not found."""
    response_file = _cell_dir(workdir, cell_id) / "response.json"
    if not response_file.exists():
        return None
    data = json.loads(response_file.read_text(encoding="utf-8"))
    return data.get("values")


def reset_cell(workdir: Path, cell_id: str) -> None:
    """Reset state for a single cell."""
    cell_dir = _cell_dir(workdir, cell_id)
    if cell_dir.exists():
        shutil.rmtree(cell_dir)


def reset_all(workdir: Path) -> None:
    """Reset state for all cells."""
    cells_dir = _cells_dir(workdir)
    if cells_dir.exists():
        shutil.rmtree(cells_dir)


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage AnyT Notebook execution state")
    parser.add_argument("workdir", help="Notebook working directory")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # status command
    status_parser = subparsers.add_parser("status", help="Show execution status")
    status_parser.add_argument("--cells", nargs="+", help="Cell IDs to check (all if omitted)")

    # mark-done command
    done_parser = subparsers.add_parser("mark-done", help="Mark a cell as done")
    done_parser.add_argument("--cell", required=True, help="Cell ID")
    done_parser.add_argument("--duration", type=float, help="Duration in seconds")

    # mark-failed command
    failed_parser = subparsers.add_parser("mark-failed", help="Mark a cell as failed")
    failed_parser.add_argument("--cell", required=True, help="Cell ID")
    failed_parser.add_argument("--error", required=True, help="Error message")
    failed_parser.add_argument("--duration", type=float, help="Duration in seconds")

    # read-input command
    input_parser = subparsers.add_parser("read-input", help="Read input cell response")
    input_parser.add_argument("--cell", required=True, help="Input cell ID")

    # reset command
    reset_parser = subparsers.add_parser("reset", help="Reset cell state")
    reset_parser.add_argument("--cell", help="Cell ID (omit to reset all)")

    args = parser.parse_args()

    try:
        workdir = Path(args.workdir)

        if args.command == "status":
            if args.cells:
                result = get_all_status(workdir, args.cells)
            else:
                # List all cell dirs
                cells_dir = _cells_dir(workdir)
                cell_ids = sorted(d.name for d in cells_dir.iterdir() if d.is_dir()) if cells_dir.exists() else []
                result = get_all_status(workdir, cell_ids)
            print(json.dumps(result, indent=2))

        elif args.command == "mark-done":
            mark_done(workdir, args.cell, args.duration)
            print(f"Marked '{args.cell}' as done")

        elif args.command == "mark-failed":
            mark_failed(workdir, args.cell, args.error, args.duration)
            print(f"Marked '{args.cell}' as failed")

        elif args.command == "read-input":
            response = read_input_response(workdir, args.cell)
            if response is None:
                print(f"No response found for input cell '{args.cell}'", file=sys.stderr)
                return 1
            print(json.dumps(response, indent=2))

        elif args.command == "reset":
            if args.cell:
                reset_cell(workdir, args.cell)
                print(f"Reset cell '{args.cell}'")
            else:
                reset_all(workdir)
                print("Reset all cell state")

        return 0

    except NotebookError as e:
        prefix = _ERROR_PREFIXES.get(type(e), "Error")
        print(f"\n{prefix}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
