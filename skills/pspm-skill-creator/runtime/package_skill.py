#!/usr/bin/env python3
"""
PSPM Skill Packager
Creates a distributable .skill file (ZIP archive) from a skill folder.
Run with: uv run --project runtime runtime/package_skill.py <skill-dir> [output-dir]
"""

import sys
import zipfile
from pathlib import Path

from validate_skill import validate_skill

# Patterns to exclude from packaging (dev artifacts)
EXCLUDE_PATTERNS = {
    ".venv",
    "__pycache__",
    ".ruff_cache",
    ".pytest_cache",
    ".pyc",
    "uv.lock",
    ".python-version",
    "node_modules",
    "bun.lock",
}


def should_exclude(file_path: Path) -> bool:
    """Check if a file should be excluded from the package."""
    parts = file_path.parts
    for part in parts:
        if part in EXCLUDE_PATTERNS:
            return True
    return file_path.suffix == ".pyc"


def package_skill(skill_path: Path, output_dir: Path | None = None) -> Path | None:
    """
    Package a skill folder into a .skill file.

    Args:
        skill_path: Path to the skill folder
        output_dir: Optional output directory (defaults to current directory)

    Returns:
        Path to the created .skill file, or None on error
    """
    skill_path = Path(skill_path).resolve()

    if not skill_path.exists():
        print(f"Error: Skill folder not found: {skill_path}")
        return None

    if not skill_path.is_dir():
        print(f"Error: Path is not a directory: {skill_path}")
        return None

    if not (skill_path / "SKILL.md").exists():
        print(f"Error: SKILL.md not found in {skill_path}")
        return None

    # Validate before packaging
    print("Validating skill...")
    valid, message = validate_skill(skill_path)
    if not valid:
        print(f"Validation failed: {message}")
        return None
    print(f"Validation passed: {message}\n")

    # Determine output location
    skill_name = skill_path.name
    if output_dir:
        out = Path(output_dir).resolve()
        out.mkdir(parents=True, exist_ok=True)
    else:
        out = Path.cwd()

    skill_filename = out / f"{skill_name}.skill"

    try:
        with zipfile.ZipFile(skill_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in sorted(skill_path.rglob("*")):
                if not file_path.is_file():
                    continue
                rel_path = file_path.relative_to(skill_path)
                if should_exclude(rel_path):
                    continue
                arcname = Path(skill_name) / rel_path
                zipf.write(file_path, arcname)
                print(f"  Added: {arcname}")

        print(f"\nPackaged skill to: {skill_filename}")
        return skill_filename

    except Exception as e:
        print(f"Error creating .skill file: {e}")
        return None


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: uv run --project runtime runtime/package_skill.py <skill-directory> [output-directory]")
        sys.exit(1)

    skill_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    print(f"Packaging skill: {skill_path}")
    if output_dir:
        print(f"Output directory: {output_dir}")
    print()

    result = package_skill(skill_path, output_dir)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
