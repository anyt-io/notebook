#!/usr/bin/env python3
"""Generate and serve a review page for eval results.

Reads the workspace directory, discovers runs (directories with outputs/),
embeds all output data into a self-contained HTML page, and serves it via
a tiny HTTP server. Feedback auto-saves to feedback.json in the workspace.

Usage:
    uv run --project runtime runtime/generate_review.py <workspace-path> [--port PORT] [--skill-name NAME]
    uv run --project runtime runtime/generate_review.py <workspace-path> --previous-workspace /path/to/old/
    uv run --project runtime runtime/generate_review.py <workspace-path> --static output.html

No dependencies beyond the Python stdlib are required.
"""

import argparse
import base64
import json
import mimetypes
import os
import re
import signal
import subprocess
import sys
import time
import webbrowser
from functools import partial
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# Files to exclude from output listings
METADATA_FILES = {"transcript.md", "user_notes.md", "metrics.json"}

# Extensions we render as inline text
TEXT_EXTENSIONS = {
    ".txt",
    ".md",
    ".json",
    ".csv",
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".yaml",
    ".yml",
    ".xml",
    ".html",
    ".css",
    ".sh",
    ".rb",
    ".go",
    ".rs",
    ".java",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".sql",
    ".r",
    ".toml",
}

# Extensions we render as inline images
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}

# MIME type overrides for common types
MIME_OVERRIDES = {
    ".svg": "image/svg+xml",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}


def get_mime_type(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in MIME_OVERRIDES:
        return MIME_OVERRIDES[ext]
    mime, _ = mimetypes.guess_type(str(path))
    return mime or "application/octet-stream"


def find_runs(workspace: Path) -> list[dict]:
    """Recursively find directories that contain an outputs/ subdirectory."""
    runs: list[dict] = []
    _find_runs_recursive(workspace, workspace, runs)
    runs.sort(key=lambda r: (r.get("eval_id", float("inf")), r["id"]))
    return runs


def _find_runs_recursive(root: Path, current: Path, runs: list[dict]) -> None:
    if not current.is_dir():
        return

    outputs_dir = current / "outputs"
    if outputs_dir.is_dir():
        run = build_run(root, current)
        if run:
            runs.append(run)
        return

    skip = {"node_modules", ".git", "__pycache__", "skill", "inputs"}
    for child in sorted(current.iterdir()):
        if child.is_dir() and child.name not in skip:
            _find_runs_recursive(root, child, runs)


def build_run(root: Path, run_dir: Path) -> dict | None:
    """Build a run dict with prompt, outputs, and grading data."""
    prompt = ""
    eval_id = None

    # Try eval_metadata.json
    for candidate in [run_dir / "eval_metadata.json", run_dir.parent / "eval_metadata.json"]:
        if candidate.exists():
            try:
                metadata = json.loads(candidate.read_text())
                prompt = metadata.get("prompt", "")
                eval_id = metadata.get("eval_id")
            except (json.JSONDecodeError, OSError):
                pass
            if prompt:
                break

    # Fall back to transcript.md
    if not prompt:
        for candidate in [run_dir / "transcript.md", run_dir / "outputs" / "transcript.md"]:
            if candidate.exists():
                try:
                    text = candidate.read_text()
                    match = re.search(r"## Eval Prompt\n\n([\s\S]*?)(?=\n##|$)", text)
                    if match:
                        prompt = match.group(1).strip()
                except OSError:
                    pass
                if prompt:
                    break

    if not prompt:
        prompt = "(No prompt found)"

    run_id = str(run_dir.relative_to(root)).replace("/", "-").replace("\\", "-")

    # Collect output files
    outputs_dir = run_dir / "outputs"
    output_files: list[dict] = []
    if outputs_dir.is_dir():
        for f in sorted(outputs_dir.iterdir()):
            if f.is_file() and f.name not in METADATA_FILES:
                output_files.append(embed_file(f))

    # Load grading if present
    grading = None
    for candidate in [run_dir / "grading.json", run_dir.parent / "grading.json"]:
        if candidate.exists():
            try:
                grading = json.loads(candidate.read_text())
            except (json.JSONDecodeError, OSError):
                pass
            if grading:
                break

    return {
        "id": run_id,
        "prompt": prompt,
        "eval_id": eval_id,
        "outputs": output_files,
        "grading": grading,
    }


def embed_file(path: Path) -> dict:
    """Read a file and return an embedded representation."""
    ext = path.suffix.lower()
    mime = get_mime_type(path)

    if ext in TEXT_EXTENSIONS:
        try:
            content = path.read_text(errors="replace")
        except OSError:
            content = "(Error reading file)"
        return {
            "name": path.name,
            "type": "text",
            "content": content,
        }
    elif ext in IMAGE_EXTENSIONS:
        try:
            raw = path.read_bytes()
            b64 = base64.b64encode(raw).decode("ascii")
        except OSError:
            return {"name": path.name, "type": "error", "content": "(Error reading file)"}
        return {
            "name": path.name,
            "type": "image",
            "mime": mime,
            "data_uri": f"data:{mime};base64,{b64}",
        }
    elif ext == ".pdf":
        try:
            raw = path.read_bytes()
            b64 = base64.b64encode(raw).decode("ascii")
        except OSError:
            return {"name": path.name, "type": "error", "content": "(Error reading file)"}
        return {
            "name": path.name,
            "type": "pdf",
            "data_uri": f"data:{mime};base64,{b64}",
        }
    elif ext == ".xlsx":
        try:
            raw = path.read_bytes()
            b64 = base64.b64encode(raw).decode("ascii")
        except OSError:
            return {"name": path.name, "type": "error", "content": "(Error reading file)"}
        return {
            "name": path.name,
            "type": "xlsx",
            "data_b64": b64,
        }
    else:
        # Binary / unknown — base64 download link
        try:
            raw = path.read_bytes()
            b64 = base64.b64encode(raw).decode("ascii")
        except OSError:
            return {"name": path.name, "type": "error", "content": "(Error reading file)"}
        return {
            "name": path.name,
            "type": "binary",
            "mime": mime,
            "data_uri": f"data:{mime};base64,{b64}",
        }


def load_previous_iteration(workspace: Path) -> dict[str, dict]:
    """Load previous iteration's feedback and outputs.

    Returns a map of run_id -> {"feedback": str, "outputs": list[dict]}.
    """
    result: dict[str, dict] = {}

    # Load feedback
    feedback_map: dict[str, str] = {}
    feedback_path = workspace / "feedback.json"
    if feedback_path.exists():
        try:
            data = json.loads(feedback_path.read_text())
            feedback_map = {
                r["run_id"]: r["feedback"] for r in data.get("reviews", []) if r.get("feedback", "").strip()
            }
        except (json.JSONDecodeError, OSError, KeyError):
            pass

    # Load runs (to get outputs)
    prev_runs = find_runs(workspace)
    for run in prev_runs:
        result[run["id"]] = {
            "feedback": feedback_map.get(run["id"], ""),
            "outputs": run.get("outputs", []),
        }

    # Also add feedback for run_ids that had feedback but no matching run
    for run_id, fb in feedback_map.items():
        if run_id not in result:
            result[run_id] = {"feedback": fb, "outputs": []}

    return result


# The viewer HTML template is embedded as a constant
VIEWER_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Eval Review</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@500;600&family=Lora:wght@400;500&display=swap" rel="stylesheet">
  <script src="https://cdn.sheetjs.com/xlsx-0.20.3/package/dist/xlsx.full.min.js" crossorigin="anonymous"></script>
  <style>
    :root {
      --bg: #faf9f5; --surface: #ffffff; --border: #e8e6dc;
      --text: #141413; --text-muted: #b0aea5; --accent: #d97757;
      --accent-hover: #c4613f; --green: #788c5d; --green-bg: #eef2e8;
      --red: #c44; --red-bg: #fceaea; --header-bg: #141413;
      --header-text: #faf9f5; --radius: 6px;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Lora', Georgia, serif; background: var(--bg); color: var(--text); height: 100vh; display: flex; flex-direction: column; }
    .header { background: var(--header-bg); color: var(--header-text); padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; flex-shrink: 0; }
    .header h1 { font-family: 'Poppins', sans-serif; font-size: 1.25rem; font-weight: 600; }
    .header .instructions { font-size: 0.8rem; opacity: 0.7; margin-top: 0.25rem; }
    .header .progress { font-size: 0.875rem; opacity: 0.8; text-align: right; }
    .main { flex: 1; overflow-y: auto; padding: 1.5rem 2rem; display: flex; flex-direction: column; gap: 1.25rem; }
    .section { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); flex-shrink: 0; }
    .section-header { font-family: 'Poppins', sans-serif; padding: 0.75rem 1rem; font-size: 0.75rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); border-bottom: 1px solid var(--border); background: var(--bg); }
    .section-body { padding: 1rem; }
    .config-badge { display: inline-block; padding: 0.2rem 0.625rem; border-radius: 9999px; font-family: 'Poppins', sans-serif; font-size: 0.6875rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.03em; margin-left: 0.75rem; vertical-align: middle; }
    .config-badge.config-primary { background: rgba(33, 150, 243, 0.12); color: #1976d2; }
    .config-badge.config-baseline { background: rgba(255, 193, 7, 0.15); color: #f57f17; }
    .prompt-text { white-space: pre-wrap; font-size: 0.9375rem; line-height: 1.6; }
    .output-file { border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; }
    .output-file + .output-file { margin-top: 1rem; }
    .output-file-header { padding: 0.5rem 0.75rem; font-size: 0.8rem; font-weight: 600; color: var(--text-muted); background: var(--bg); border-bottom: 1px solid var(--border); font-family: 'SF Mono', SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace; display: flex; justify-content: space-between; align-items: center; }
    .output-file-header .dl-btn { font-size: 0.7rem; color: var(--accent); text-decoration: none; cursor: pointer; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-weight: 500; opacity: 0.8; }
    .output-file-header .dl-btn:hover { opacity: 1; text-decoration: underline; }
    .output-file-content { padding: 0.75rem; overflow-x: auto; }
    .output-file-content pre { font-size: 0.8125rem; line-height: 1.5; white-space: pre-wrap; word-break: break-word; font-family: 'SF Mono', SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace; }
    .output-file-content img { max-width: 100%; height: auto; border-radius: 4px; }
    .output-file-content iframe { width: 100%; height: 600px; border: none; }
    .empty-state { color: var(--text-muted); font-style: italic; padding: 2rem; text-align: center; }
    .feedback-textarea { width: 100%; min-height: 100px; padding: 0.75rem; border: 1px solid var(--border); border-radius: 4px; font-family: inherit; font-size: 0.9375rem; line-height: 1.5; resize: vertical; color: var(--text); }
    .feedback-textarea:focus { outline: none; border-color: var(--accent); box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1); }
    .feedback-status { font-size: 0.75rem; color: var(--text-muted); margin-top: 0.5rem; min-height: 1.1em; }
    .prev-feedback { background: var(--bg); border: 1px solid var(--border); border-radius: 4px; padding: 0.625rem 0.75rem; margin-top: 0.75rem; font-size: 0.8125rem; color: var(--text-muted); line-height: 1.5; }
    .prev-feedback-label { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 0.25rem; color: var(--text-muted); }
    .grades-toggle { display: flex; align-items: center; cursor: pointer; user-select: none; }
    .grades-toggle:hover { color: var(--accent); }
    .grades-toggle .arrow { margin-right: 0.5rem; transition: transform 0.15s; font-size: 0.75rem; }
    .grades-toggle .arrow.open { transform: rotate(90deg); }
    .grades-content { display: none; margin-top: 0.75rem; }
    .grades-content.open { display: block; }
    .grade-badge { display: inline-block; padding: 0.125rem 0.5rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; }
    .grade-pass { background: var(--green-bg); color: var(--green); }
    .grade-fail { background: var(--red-bg); color: var(--red); }
    .assertion-list { list-style: none; }
    .assertion-item { padding: 0.625rem 0; border-bottom: 1px solid var(--border); font-size: 0.8125rem; }
    .assertion-item:last-child { border-bottom: none; }
    .assertion-status { font-weight: 600; margin-right: 0.5rem; }
    .assertion-status.pass { color: var(--green); }
    .assertion-status.fail { color: var(--red); }
    .assertion-evidence { color: var(--text-muted); font-size: 0.75rem; margin-top: 0.25rem; padding-left: 1.5rem; }
    .view-tabs { display: flex; gap: 0; padding: 0 2rem; background: var(--bg); border-bottom: 1px solid var(--border); flex-shrink: 0; }
    .view-tab { font-family: 'Poppins', sans-serif; padding: 0.625rem 1.25rem; font-size: 0.8125rem; font-weight: 500; cursor: pointer; border: none; background: none; color: var(--text-muted); border-bottom: 2px solid transparent; transition: all 0.15s; }
    .view-tab:hover { color: var(--text); }
    .view-tab.active { color: var(--accent); border-bottom-color: var(--accent); }
    .view-panel { display: none; }
    .view-panel.active { display: flex; flex-direction: column; flex: 1; overflow: hidden; }
    .benchmark-view { padding: 1.5rem 2rem; overflow-y: auto; flex: 1; }
    .benchmark-table { border-collapse: collapse; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); font-size: 0.8125rem; width: 100%; margin-bottom: 1.5rem; }
    .benchmark-table th, .benchmark-table td { padding: 0.625rem 0.75rem; text-align: left; border: 1px solid var(--border); }
    .benchmark-table th { font-family: 'Poppins', sans-serif; background: var(--header-bg); color: var(--header-text); font-weight: 500; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em; }
    .benchmark-delta-positive { color: var(--green); font-weight: 600; }
    .benchmark-delta-negative { color: var(--red); font-weight: 600; }
    .benchmark-notes { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem; }
    .benchmark-notes h3 { font-family: 'Poppins', sans-serif; font-size: 0.875rem; margin-bottom: 0.75rem; }
    .benchmark-notes ul { list-style: disc; padding-left: 1.25rem; }
    .benchmark-notes li { font-size: 0.8125rem; line-height: 1.6; margin-bottom: 0.375rem; }
    .benchmark-empty { color: var(--text-muted); font-style: italic; text-align: center; padding: 3rem; }
    .nav { display: flex; justify-content: space-between; align-items: center; padding: 1rem 2rem; border-top: 1px solid var(--border); background: var(--surface); flex-shrink: 0; }
    .nav-btn { font-family: 'Poppins', sans-serif; padding: 0.5rem 1.25rem; border: 1px solid var(--border); border-radius: var(--radius); background: var(--surface); cursor: pointer; font-size: 0.875rem; font-weight: 500; color: var(--text); transition: all 0.15s; }
    .nav-btn:hover:not(:disabled) { background: var(--bg); border-color: var(--text-muted); }
    .nav-btn:disabled { opacity: 0.4; cursor: not-allowed; }
    .done-btn { font-family: 'Poppins', sans-serif; padding: 0.5rem 1.5rem; border: 1px solid var(--border); border-radius: var(--radius); background: var(--surface); color: var(--text); cursor: pointer; font-size: 0.875rem; font-weight: 500; transition: all 0.15s; }
    .done-btn:hover { background: var(--bg); border-color: var(--text-muted); }
    .done-btn.ready { border: none; background: var(--accent); color: white; font-weight: 600; }
    .done-btn.ready:hover { background: var(--accent-hover); }
    .done-overlay { display: none; position: fixed; inset: 0; background: rgba(0, 0, 0, 0.5); z-index: 100; justify-content: center; align-items: center; }
    .done-overlay.visible { display: flex; }
    .done-card { background: var(--surface); border-radius: 12px; padding: 2rem 3rem; text-align: center; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3); max-width: 500px; }
    .done-card h2 { font-size: 1.5rem; margin-bottom: 0.5rem; }
    .done-card p { color: var(--text-muted); margin-bottom: 1.5rem; line-height: 1.5; }
    .done-card .btn-row { display: flex; gap: 0.5rem; justify-content: center; }
    .done-card button { padding: 0.5rem 1.25rem; border: 1px solid var(--border); border-radius: var(--radius); background: var(--surface); cursor: pointer; font-size: 0.875rem; }
    .done-card button:hover { background: var(--bg); }
    .toast { position: fixed; bottom: 5rem; left: 50%; transform: translateX(-50%); background: var(--header-bg); color: var(--header-text); padding: 0.625rem 1.25rem; border-radius: var(--radius); font-size: 0.875rem; opacity: 0; transition: opacity 0.3s; pointer-events: none; z-index: 200; }
    .toast.visible { opacity: 1; }
  </style>
</head>
<body>
  <div id="app" style="height:100vh; display:flex; flex-direction:column;">
    <div class="header">
      <div>
        <h1>Eval Review: <span id="skill-name"></span></h1>
        <div class="instructions">Review each output and leave feedback below. Navigate with arrow keys or buttons.</div>
      </div>
      <div class="progress" id="progress"></div>
    </div>
    <div class="view-tabs" id="view-tabs" style="display:none;">
      <button class="view-tab active" onclick="switchView('outputs')">Outputs</button>
      <button class="view-tab" onclick="switchView('benchmark')">Benchmark</button>
    </div>
    <div class="view-panel active" id="panel-outputs">
      <div class="main">
        <div class="section">
          <div class="section-header">Prompt <span class="config-badge" id="config-badge" style="display:none;"></span></div>
          <div class="section-body"><div class="prompt-text" id="prompt-text"></div></div>
        </div>
        <div class="section">
          <div class="section-header">Output</div>
          <div class="section-body" id="outputs-body"><div class="empty-state">No output files found</div></div>
        </div>
        <div class="section" id="prev-outputs-section" style="display:none;">
          <div class="section-header">
            <div class="grades-toggle" onclick="togglePrevOutputs()">
              <span class="arrow" id="prev-outputs-arrow">&#9654;</span> Previous Output
            </div>
          </div>
          <div class="grades-content" id="prev-outputs-content"></div>
        </div>
        <div class="section" id="grades-section" style="display:none;">
          <div class="section-header">
            <div class="grades-toggle" onclick="toggleGrades()">
              <span class="arrow" id="grades-arrow">&#9654;</span> Formal Grades
            </div>
          </div>
          <div class="grades-content" id="grades-content"></div>
        </div>
        <div class="section">
          <div class="section-header">Your Feedback</div>
          <div class="section-body">
            <textarea class="feedback-textarea" id="feedback" placeholder="What do you think of this output? Any issues, suggestions, or things that look great?"></textarea>
            <div class="feedback-status" id="feedback-status"></div>
            <div class="prev-feedback" id="prev-feedback" style="display:none;">
              <div class="prev-feedback-label">Previous feedback</div>
              <div id="prev-feedback-text"></div>
            </div>
          </div>
        </div>
      </div>
      <div class="nav" id="outputs-nav">
        <button class="nav-btn" id="prev-btn" onclick="navigate(-1)">&#8592; Previous</button>
        <button class="done-btn" id="done-btn" onclick="showDoneDialog()">Submit All Reviews</button>
        <button class="nav-btn" id="next-btn" onclick="navigate(1)">Next &#8594;</button>
      </div>
    </div>
    <div class="view-panel" id="panel-benchmark">
      <div class="benchmark-view" id="benchmark-content">
        <div class="benchmark-empty">No benchmark data available.</div>
      </div>
    </div>
  </div>
  <div class="done-overlay" id="done-overlay">
    <div class="done-card">
      <h2>Review Complete</h2>
      <p>Your feedback has been saved. Go back to your Claude Code session and tell Claude you're done reviewing.</p>
      <div class="btn-row"><button onclick="closeDoneDialog()">OK</button></div>
    </div>
  </div>
  <div class="toast" id="toast"></div>
  <script>
    /*__EMBEDDED_DATA__*/
    let feedbackMap = {};
    let currentIndex = 0;
    let visitedRuns = new Set();

    async function init() {
      const hasPrevious = Object.keys(EMBEDDED_DATA.previous_feedback || {}).length > 0 || Object.keys(EMBEDDED_DATA.previous_outputs || {}).length > 0;
      if (!hasPrevious) {
        try {
          const resp = await fetch("/api/feedback");
          const data = await resp.json();
          if (data.reviews) { for (const r of data.reviews) feedbackMap[r.run_id] = r.feedback; }
        } catch {}
      }
      document.getElementById("skill-name").textContent = EMBEDDED_DATA.skill_name;
      showRun(0);
      const textarea = document.getElementById("feedback");
      let saveTimeout = null;
      textarea.addEventListener("input", () => {
        clearTimeout(saveTimeout);
        document.getElementById("feedback-status").textContent = "";
        saveTimeout = setTimeout(() => saveCurrentFeedback(), 800);
      });
    }

    function navigate(delta) {
      const newIndex = currentIndex + delta;
      if (newIndex >= 0 && newIndex < EMBEDDED_DATA.runs.length) {
        saveCurrentFeedback();
        showRun(newIndex);
      }
    }

    function updateNavButtons() {
      document.getElementById("prev-btn").disabled = currentIndex === 0;
      document.getElementById("next-btn").disabled = currentIndex === EMBEDDED_DATA.runs.length - 1;
    }

    function showRun(index) {
      currentIndex = index;
      const run = EMBEDDED_DATA.runs[index];
      document.getElementById("progress").textContent = `${index + 1} of ${EMBEDDED_DATA.runs.length}`;
      document.getElementById("prompt-text").textContent = run.prompt;
      const badge = document.getElementById("config-badge");
      const configMatch = run.id.match(/(with_skill|without_skill|new_skill|old_skill)/);
      if (configMatch) {
        const config = configMatch[1];
        const isBaseline = config === "without_skill" || config === "old_skill";
        badge.textContent = config.replace(/_/g, " ");
        badge.className = "config-badge " + (isBaseline ? "config-baseline" : "config-primary");
        badge.style.display = "inline-block";
      } else { badge.style.display = "none"; }
      renderOutputs(run);
      renderPrevOutputs(run);
      renderGrades(run);
      const prevFb = (EMBEDDED_DATA.previous_feedback || {})[run.id];
      const prevEl = document.getElementById("prev-feedback");
      if (prevFb) { document.getElementById("prev-feedback-text").textContent = prevFb; prevEl.style.display = "block"; }
      else { prevEl.style.display = "none"; }
      document.getElementById("feedback").value = feedbackMap[run.id] || "";
      document.getElementById("feedback-status").textContent = "";
      updateNavButtons();
      visitedRuns.add(index);
      const doneBtn = document.getElementById("done-btn");
      if (visitedRuns.size >= EMBEDDED_DATA.runs.length) { doneBtn.classList.add("ready"); }
      document.querySelector(".main").scrollTop = 0;
    }

    function renderOutputs(run) {
      const container = document.getElementById("outputs-body");
      container.innerHTML = "";
      const outputs = run.outputs || [];
      if (outputs.length === 0) { container.innerHTML = '<div class="empty-state">No output files</div>'; return; }
      for (const file of outputs) {
        const fileDiv = document.createElement("div");
        fileDiv.className = "output-file";
        const header = document.createElement("div");
        header.className = "output-file-header";
        const nameSpan = document.createElement("span");
        nameSpan.textContent = file.name;
        header.appendChild(nameSpan);
        const dlBtn = document.createElement("a");
        dlBtn.className = "dl-btn";
        dlBtn.textContent = "Download";
        dlBtn.download = file.name;
        dlBtn.href = getDownloadUri(file);
        header.appendChild(dlBtn);
        fileDiv.appendChild(header);
        const content = document.createElement("div");
        content.className = "output-file-content";
        if (file.type === "text") { const pre = document.createElement("pre"); pre.textContent = file.content; content.appendChild(pre); }
        else if (file.type === "image") { const img = document.createElement("img"); img.src = file.data_uri; img.alt = file.name; content.appendChild(img); }
        else if (file.type === "pdf") { const iframe = document.createElement("iframe"); iframe.src = file.data_uri; content.appendChild(iframe); }
        else if (file.type === "xlsx") { renderXlsx(content, file.data_b64); }
        else if (file.type === "binary") { const a = document.createElement("a"); a.className = "download-link"; a.href = file.data_uri; a.download = file.name; a.textContent = "Download " + file.name; content.appendChild(a); }
        else if (file.type === "error") { const pre = document.createElement("pre"); pre.textContent = file.content; pre.style.color = "var(--red)"; content.appendChild(pre); }
        fileDiv.appendChild(content);
        container.appendChild(fileDiv);
      }
    }

    function renderXlsx(container, b64Data) {
      try {
        const raw = Uint8Array.from(atob(b64Data), c => c.charCodeAt(0));
        const wb = XLSX.read(raw, { type: "array" });
        for (let i = 0; i < wb.SheetNames.length; i++) {
          const sheetName = wb.SheetNames[i];
          const ws = wb.Sheets[sheetName];
          if (wb.SheetNames.length > 1) {
            const sheetLabel = document.createElement("div");
            sheetLabel.style.cssText = "font-weight:600; font-size:0.8rem; color:#b0aea5; margin-top:0.5rem; margin-bottom:0.25rem;";
            sheetLabel.textContent = "Sheet: " + sheetName;
            container.appendChild(sheetLabel);
          }
          const htmlStr = XLSX.utils.sheet_to_html(ws, { editable: false });
          const wrapper = document.createElement("div");
          wrapper.innerHTML = htmlStr;
          container.appendChild(wrapper);
        }
      } catch (err) { container.textContent = "Error rendering spreadsheet: " + err.message; }
    }

    function renderGrades(run) {
      const section = document.getElementById("grades-section");
      const content = document.getElementById("grades-content");
      if (!run.grading) { section.style.display = "none"; return; }
      const grading = run.grading;
      section.style.display = "block";
      content.classList.remove("open");
      document.getElementById("grades-arrow").classList.remove("open");
      const summary = grading.summary || {};
      const expectations = grading.expectations || [];
      let html = '<div style="padding: 1rem;">';
      const passRate = summary.pass_rate != null ? Math.round(summary.pass_rate * 100) + "%" : "?";
      const badgeClass = summary.pass_rate >= 0.8 ? "grade-pass" : summary.pass_rate >= 0.5 ? "" : "grade-fail";
      html += '<div class="grades-summary"><span class="grade-badge ' + badgeClass + '">' + passRate + '</span>';
      html += '<span>' + (summary.passed || 0) + ' passed, ' + (summary.failed || 0) + ' failed of ' + (summary.total || 0) + '</span></div>';
      html += '<ul class="assertion-list">';
      for (const exp of expectations) {
        const statusClass = exp.passed ? "pass" : "fail";
        const statusIcon = exp.passed ? "\\u2713" : "\\u2717";
        html += '<li class="assertion-item"><span class="assertion-status ' + statusClass + '">' + statusIcon + '</span><span>' + escapeHtml(exp.text) + '</span>';
        if (exp.evidence) { html += '<div class="assertion-evidence">' + escapeHtml(exp.evidence) + '</div>'; }
        html += '</li>';
      }
      html += '</ul></div>';
      content.innerHTML = html;
    }

    function toggleGrades() { document.getElementById("grades-content").classList.toggle("open"); document.getElementById("grades-arrow").classList.toggle("open"); }

    function renderPrevOutputs(run) {
      const section = document.getElementById("prev-outputs-section");
      const content = document.getElementById("prev-outputs-content");
      const prevOutputs = (EMBEDDED_DATA.previous_outputs || {})[run.id];
      if (!prevOutputs || prevOutputs.length === 0) { section.style.display = "none"; return; }
      section.style.display = "block";
      content.classList.remove("open");
      document.getElementById("prev-outputs-arrow").classList.remove("open");
      content.innerHTML = "";
      const wrapper = document.createElement("div");
      wrapper.style.padding = "1rem";
      for (const file of prevOutputs) {
        const fileDiv = document.createElement("div");
        fileDiv.className = "output-file";
        const header = document.createElement("div");
        header.className = "output-file-header";
        const nameSpan = document.createElement("span");
        nameSpan.textContent = file.name;
        header.appendChild(nameSpan);
        fileDiv.appendChild(header);
        const fc = document.createElement("div");
        fc.className = "output-file-content";
        if (file.type === "text") { const pre = document.createElement("pre"); pre.textContent = file.content; fc.appendChild(pre); }
        else if (file.type === "image") { const img = document.createElement("img"); img.src = file.data_uri; img.alt = file.name; fc.appendChild(img); }
        else if (file.type === "pdf") { const iframe = document.createElement("iframe"); iframe.src = file.data_uri; fc.appendChild(iframe); }
        fileDiv.appendChild(fc);
        wrapper.appendChild(fileDiv);
      }
      content.appendChild(wrapper);
    }

    function togglePrevOutputs() { document.getElementById("prev-outputs-content").classList.toggle("open"); document.getElementById("prev-outputs-arrow").classList.toggle("open"); }

    function saveCurrentFeedback() {
      const run = EMBEDDED_DATA.runs[currentIndex];
      const text = document.getElementById("feedback").value;
      if (text.trim() === "") { delete feedbackMap[run.id]; } else { feedbackMap[run.id] = text; }
      const reviews = [];
      for (const [run_id, feedback] of Object.entries(feedbackMap)) { if (feedback.trim()) { reviews.push({ run_id, feedback, timestamp: new Date().toISOString() }); } }
      fetch("/api/feedback", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ reviews, status: "in_progress" }) })
        .then(() => { document.getElementById("feedback-status").textContent = "Saved"; })
        .catch(() => { document.getElementById("feedback-status").textContent = "Will download on submit"; });
    }

    function showDoneDialog() {
      const run = EMBEDDED_DATA.runs[currentIndex];
      const text = document.getElementById("feedback").value;
      if (text.trim() === "") { delete feedbackMap[run.id]; } else { feedbackMap[run.id] = text; }
      const reviews = [];
      const ts = new Date().toISOString();
      for (const r of EMBEDDED_DATA.runs) { reviews.push({ run_id: r.id, feedback: feedbackMap[r.id] || "", timestamp: ts }); }
      const payload = JSON.stringify({ reviews, status: "complete" }, null, 2);
      fetch("/api/feedback", { method: "POST", headers: { "Content-Type": "application/json" }, body: payload })
        .then(() => { document.getElementById("done-overlay").classList.add("visible"); })
        .catch(() => {
          const blob = new Blob([payload], { type: "application/json" });
          const url = URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url; a.download = "feedback.json"; a.click();
          URL.revokeObjectURL(url);
          document.getElementById("done-overlay").classList.add("visible");
        });
    }

    function closeDoneDialog() { saveCurrentFeedback(); document.getElementById("done-overlay").classList.remove("visible"); }

    document.addEventListener("keydown", (e) => {
      if (e.target.tagName === "TEXTAREA") return;
      if (e.key === "ArrowLeft" || e.key === "ArrowUp") { e.preventDefault(); navigate(-1); }
      else if (e.key === "ArrowRight" || e.key === "ArrowDown") { e.preventDefault(); navigate(1); }
    });

    function getDownloadUri(file) {
      if (file.data_uri) return file.data_uri;
      if (file.data_b64) return "data:application/octet-stream;base64," + file.data_b64;
      if (file.type === "text") return "data:text/plain;charset=utf-8," + encodeURIComponent(file.content);
      return "#";
    }

    function escapeHtml(text) { const div = document.createElement("div"); div.textContent = text; return div.innerHTML; }

    function switchView(view) {
      document.querySelectorAll(".view-tab").forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".view-panel").forEach(p => p.classList.remove("active"));
      document.querySelector(`[onclick="switchView('${view}')"]`).classList.add("active");
      document.getElementById("panel-" + view).classList.add("active");
    }

    function renderBenchmark() {
      const data = EMBEDDED_DATA.benchmark;
      if (!data) return;
      document.getElementById("view-tabs").style.display = "flex";
      const container = document.getElementById("benchmark-content");
      const summary = data.run_summary || {};
      const metadata = data.metadata || {};
      const notes = data.notes || [];
      let html = "";
      html += "<h2 style='font-family: Poppins, sans-serif; margin-bottom: 0.5rem;'>Benchmark Results</h2>";
      html += "<p style='color: var(--text-muted); font-size: 0.875rem; margin-bottom: 1.25rem;'>";
      if (metadata.skill_name) html += "<strong>" + escapeHtml(metadata.skill_name) + "</strong> &mdash; ";
      if (metadata.timestamp) html += metadata.timestamp + " &mdash; ";
      html += (metadata.runs_per_configuration || "?") + " runs per configuration</p>";
      html += '<table class="benchmark-table">';
      function fmtStat(stat, pct) { if (!stat) return "-"; const suffix = pct ? "%" : ""; const m = pct ? (stat.mean * 100).toFixed(0) : stat.mean.toFixed(1); const s = pct ? (stat.stddev * 100).toFixed(0) : stat.stddev.toFixed(1); return m + suffix + " +/- " + s + suffix; }
      function deltaClass(val) { if (!val) return ""; const n = parseFloat(val); if (n > 0) return "benchmark-delta-positive"; if (n < 0) return "benchmark-delta-negative"; return ""; }
      const configs = Object.keys(summary).filter(k => k !== "delta");
      const configA = configs[0] || "config_a";
      const configB = configs[1] || "config_b";
      const labelA = configA.replace(/_/g, " ").replace(/\\b\\w/g, c => c.toUpperCase());
      const labelB = configB.replace(/_/g, " ").replace(/\\b\\w/g, c => c.toUpperCase());
      const a = summary[configA] || {};
      const b = summary[configB] || {};
      const delta = summary.delta || {};
      html += "<thead><tr><th>Metric</th><th>" + escapeHtml(labelA) + "</th><th>" + escapeHtml(labelB) + "</th><th>Delta</th></tr></thead>";
      html += "<tbody>";
      html += "<tr><td><strong>Pass Rate</strong></td><td>" + fmtStat(a.pass_rate, true) + "</td><td>" + fmtStat(b.pass_rate, true) + "</td><td class='" + deltaClass(delta.pass_rate) + "'>" + (delta.pass_rate || "-") + "</td></tr>";
      if (a.time_seconds || b.time_seconds) { html += "<tr><td><strong>Time (s)</strong></td><td>" + fmtStat(a.time_seconds, false) + "</td><td>" + fmtStat(b.time_seconds, false) + "</td><td class='" + deltaClass(delta.time_seconds) + "'>" + (delta.time_seconds ? delta.time_seconds + "s" : "-") + "</td></tr>"; }
      if (a.tokens || b.tokens) { html += "<tr><td><strong>Tokens</strong></td><td>" + fmtStat(a.tokens, false) + "</td><td>" + fmtStat(b.tokens, false) + "</td><td class='" + deltaClass(delta.tokens) + "'>" + (delta.tokens || "-") + "</td></tr>"; }
      html += "</tbody></table>";
      if (notes.length > 0) { html += '<div class="benchmark-notes"><h3>Analysis Notes</h3><ul>'; for (const note of notes) { html += "<li>" + escapeHtml(note) + "</li>"; } html += "</ul></div>"; }
      container.innerHTML = html;
    }

    init();
    renderBenchmark();
  </script>
</body>
</html>"""


def generate_html(
    runs: list[dict],
    skill_name: str,
    previous: dict[str, dict] | None = None,
    benchmark: dict | None = None,
) -> str:
    """Generate the complete standalone HTML page with embedded data."""
    # Build previous_feedback and previous_outputs maps for the template
    previous_feedback: dict[str, str] = {}
    previous_outputs: dict[str, list[dict]] = {}
    if previous:
        for run_id, data in previous.items():
            if data.get("feedback"):
                previous_feedback[run_id] = data["feedback"]
            if data.get("outputs"):
                previous_outputs[run_id] = data["outputs"]

    embedded = {
        "skill_name": skill_name,
        "runs": runs,
        "previous_feedback": previous_feedback,
        "previous_outputs": previous_outputs,
    }
    if benchmark:
        embedded["benchmark"] = benchmark

    data_json = json.dumps(embedded)

    return VIEWER_HTML.replace("/*__EMBEDDED_DATA__*/", f"const EMBEDDED_DATA = {data_json};")


# ---------------------------------------------------------------------------
# HTTP server (stdlib only, zero dependencies)
# ---------------------------------------------------------------------------


def _kill_port(port: int) -> None:
    """Kill any process listening on the given port."""
    try:
        result = subprocess.run(
            ["lsof", "-ti", f":{port}"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        for pid_str in result.stdout.strip().split("\n"):
            if pid_str.strip():
                try:
                    os.kill(int(pid_str.strip()), signal.SIGTERM)
                except (ProcessLookupError, ValueError):
                    pass
        if result.stdout.strip():
            time.sleep(0.5)
    except subprocess.TimeoutExpired:
        pass
    except FileNotFoundError:
        print("Note: lsof not found, cannot check if port is in use", file=sys.stderr)


class ReviewHandler(BaseHTTPRequestHandler):
    """Serves the review HTML and handles feedback saves."""

    def __init__(
        self,
        workspace: Path,
        skill_name: str,
        feedback_path: Path,
        previous: dict[str, dict],
        benchmark_path: Path | None,
        *args,
        **kwargs,
    ):
        self.workspace = workspace
        self.skill_name = skill_name
        self.feedback_path = feedback_path
        self.previous = previous
        self.benchmark_path = benchmark_path
        super().__init__(*args, **kwargs)

    def do_GET(self) -> None:
        if self.path == "/" or self.path == "/index.html":
            runs = find_runs(self.workspace)
            benchmark = None
            if self.benchmark_path and self.benchmark_path.exists():
                try:
                    benchmark = json.loads(self.benchmark_path.read_text())
                except (json.JSONDecodeError, OSError):
                    pass
            html = generate_html(runs, self.skill_name, self.previous, benchmark)
            content = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == "/api/feedback":
            data = b"{}"
            if self.feedback_path.exists():
                data = self.feedback_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_error(404)

    def do_POST(self) -> None:
        if self.path == "/api/feedback":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                if not isinstance(data, dict) or "reviews" not in data:
                    raise ValueError("Expected JSON object with 'reviews' key")
                self.feedback_path.write_text(json.dumps(data, indent=2) + "\n")
                resp = b'{"ok":true}'
                self.send_response(200)
            except (json.JSONDecodeError, OSError, ValueError) as e:
                resp = json.dumps({"error": str(e)}).encode()
                self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
        else:
            self.send_error(404)

    def log_message(self, format: str, *args: object) -> None:
        _ = format, args  # Suppress request logging


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate and serve eval review")
    parser.add_argument("workspace", type=Path, help="Path to workspace directory")
    parser.add_argument("--port", "-p", type=int, default=3117, help="Server port (default: 3117)")
    parser.add_argument("--skill-name", "-n", type=str, default=None, help="Skill name for header")
    parser.add_argument(
        "--previous-workspace",
        type=Path,
        default=None,
        help="Path to previous iteration's workspace (shows old outputs and feedback as context)",
    )
    parser.add_argument(
        "--benchmark",
        type=Path,
        default=None,
        help="Path to benchmark.json to show in the Benchmark tab",
    )
    parser.add_argument(
        "--static",
        "-s",
        type=Path,
        default=None,
        help="Write standalone HTML to this path instead of starting a server",
    )
    args = parser.parse_args()

    workspace = args.workspace.resolve()
    if not workspace.is_dir():
        print(f"Error: {workspace} is not a directory", file=sys.stderr)
        sys.exit(1)

    runs = find_runs(workspace)
    if not runs:
        print(f"No runs found in {workspace}", file=sys.stderr)
        sys.exit(1)

    skill_name = args.skill_name or workspace.name.replace("-workspace", "")
    feedback_path = workspace / "feedback.json"

    previous: dict[str, dict] = {}
    if args.previous_workspace:
        previous = load_previous_iteration(args.previous_workspace.resolve())

    benchmark_path = args.benchmark.resolve() if args.benchmark else None
    benchmark = None
    if benchmark_path and benchmark_path.exists():
        try:
            benchmark = json.loads(benchmark_path.read_text())
        except (json.JSONDecodeError, OSError):
            pass

    if args.static:
        html = generate_html(runs, skill_name, previous, benchmark)
        args.static.parent.mkdir(parents=True, exist_ok=True)
        args.static.write_text(html)
        print(f"\n  Static viewer written to: {args.static}\n")
        sys.exit(0)

    # Kill any existing process on the target port
    port = args.port
    _kill_port(port)
    handler = partial(ReviewHandler, workspace, skill_name, feedback_path, previous, benchmark_path)
    try:
        server = HTTPServer(("127.0.0.1", port), handler)
    except OSError:
        server = HTTPServer(("127.0.0.1", 0), handler)
        port = server.server_address[1]

    url = f"http://localhost:{port}"
    print("\n  Eval Viewer")
    print("  ─────────────────────────────────")
    print(f"  URL:       {url}")
    print(f"  Workspace: {workspace}")
    print(f"  Feedback:  {feedback_path}")
    if previous:
        print(f"  Previous:  {args.previous_workspace} ({len(previous)} runs)")
    if benchmark_path:
        print(f"  Benchmark: {benchmark_path}")
    print("\n  Press Ctrl+C to stop.\n")

    webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        server.server_close()


if __name__ == "__main__":
    main()
