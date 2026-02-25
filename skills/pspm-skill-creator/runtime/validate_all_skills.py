#!/usr/bin/env python3
"""
Validate all PSPM skills in a directory.
Iterates over each subdirectory in the given path and runs skill validation.
Run with: uv run --project runtime runtime/validate_all_skills.py <skills-dir>
"""

import sys
from pathlib import Path

from config import ValidationError
from validate_skill import validate_skill


def validate_all_skills(skills_dir: Path) -> bool:
    """
    Validate all skill directories under the given path.

    Returns True if all skills are valid, False otherwise.
    """
    skills_dir = Path(skills_dir).resolve()

    if not skills_dir.is_dir():
        print(f"Error: Not a directory: {skills_dir}")
        return False

    skill_dirs = sorted(d for d in skills_dir.iterdir() if d.is_dir() and (d / "SKILL.md").exists())

    if not skill_dirs:
        print(f"No skills found in {skills_dir}")
        return False

    print(f"Validating {len(skill_dirs)} skill(s) in {skills_dir}\n")

    all_valid = True
    results: list[tuple[str, bool, str]] = []

    for skill_path in skill_dirs:
        try:
            name = validate_skill(skill_path)
            results.append((skill_path.name, True, f"Skill '{name}' is valid"))
        except ValidationError as e:
            results.append((skill_path.name, False, str(e)))
            all_valid = False

    # Print results
    for name, valid, message in results:
        status = "PASS" if valid else "FAIL"
        print(f"  [{status}] {name}: {message}")

    print()
    if all_valid:
        print(f"All {len(results)} skill(s) are valid.")
    else:
        failed = sum(1 for _, v, _ in results if not v)
        print(f"{failed} of {len(results)} skill(s) failed validation.")

    return all_valid


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: uv run --project runtime runtime/validate_all_skills.py <skills-directory>")
        return 1

    skills_dir = Path(sys.argv[1])
    success = validate_all_skills(skills_dir)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
