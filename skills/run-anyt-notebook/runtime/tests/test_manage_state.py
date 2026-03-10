"""Tests for manage_state module."""

import json
from pathlib import Path

import pytest

from manage_state import (
    get_cell_status,
    mark_done,
    mark_failed,
    mark_skipped,
    read_input_response,
    reset_all,
    reset_cell,
    save_input_response,
    save_shell_output,
    save_shell_script,
    save_task_description,
    save_task_summary,
)


@pytest.fixture
def workdir(tmp_path: Path) -> Path:
    return tmp_path / "anyt_workspace_test"


class TestCellStatus:
    def test_pending_by_default(self, workdir: Path):
        assert get_cell_status(workdir, "hello") == "pending"

    def test_mark_done(self, workdir: Path):
        mark_done(workdir, "hello", duration=5.0)
        assert get_cell_status(workdir, "hello") == "done"

        marker = workdir / ".anyt" / "cells" / "hello" / ".done"
        data = json.loads(marker.read_text())
        assert data["status"] == "done"
        assert data["duration"] == 5.0

    def test_mark_failed(self, workdir: Path):
        mark_failed(workdir, "hello", "Something went wrong", duration=2.0)
        assert get_cell_status(workdir, "hello") == "failed"

        marker = workdir / ".anyt" / "cells" / "hello" / ".failed"
        data = json.loads(marker.read_text())
        assert data["error"] == "Something went wrong"

    def test_mark_skipped(self, workdir: Path):
        mark_skipped(workdir, "hello")
        assert get_cell_status(workdir, "hello") == "skipped"

    def test_mark_replaces_previous(self, workdir: Path):
        mark_done(workdir, "hello")
        assert get_cell_status(workdir, "hello") == "done"

        mark_failed(workdir, "hello", "oops")
        assert get_cell_status(workdir, "hello") == "failed"

        # .done should be gone
        assert not (workdir / ".anyt" / "cells" / "hello" / ".done").exists()


class TestStateFiles:
    def test_save_shell_script(self, workdir: Path):
        save_shell_script(workdir, "setup", "#!/bin/bash\nmkdir -p src")
        script = workdir / ".anyt" / "cells" / "setup" / "script.sh"
        assert script.exists()
        assert "mkdir -p src" in script.read_text()

    def test_save_shell_output(self, workdir: Path):
        save_shell_output(workdir, "setup", "directory created")
        output = workdir / ".anyt" / "cells" / "setup" / "output.log"
        assert output.exists()

    def test_save_task_description(self, workdir: Path):
        save_task_description(workdir, "create-api", "Create an API with Express")
        task = workdir / ".anyt" / "cells" / "create-api" / "task.md"
        assert task.exists()

    def test_save_task_summary(self, workdir: Path):
        save_task_summary(workdir, "create-api", "Created Express API with 3 endpoints")
        summary = workdir / ".anyt" / "cells" / "create-api" / "summary.md"
        assert summary.exists()


class TestInputResponses:
    def test_save_and_read_response(self, workdir: Path):
        save_input_response(workdir, "config", {"name": "test", "port": 3000})
        response = read_input_response(workdir, "config")
        assert response == {"name": "test", "port": 3000}

    def test_read_missing_response(self, workdir: Path):
        assert read_input_response(workdir, "nonexistent") is None


class TestReset:
    def test_reset_cell(self, workdir: Path):
        mark_done(workdir, "hello")
        assert get_cell_status(workdir, "hello") == "done"

        reset_cell(workdir, "hello")
        assert get_cell_status(workdir, "hello") == "pending"

    def test_reset_all(self, workdir: Path):
        mark_done(workdir, "cell-1")
        mark_done(workdir, "cell-2")

        reset_all(workdir)
        assert get_cell_status(workdir, "cell-1") == "pending"
        assert get_cell_status(workdir, "cell-2") == "pending"
