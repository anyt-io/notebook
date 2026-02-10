#!/usr/bin/env python3
"""
PSPM Skill Validator
Validates a skill directory's SKILL.md frontmatter and structure.
Run with: uv run --project runtime runtime/validate_skill.py <skill-dir>
"""

import json
import re
import sys
from pathlib import Path

import yaml

ALLOWED_FRONTMATTER_KEYS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}


def validate_skill(skill_path: Path) -> tuple[bool, str]:
    """
    Validate a PSPM skill directory.

    Checks:
    - SKILL.md exists and has valid YAML frontmatter
    - Required fields: name, description
    - Name is kebab-case, max 64 chars
    - Description max 1024 chars, no angle brackets
    - Only allowed frontmatter keys
    - pspm.json exists and is valid JSON

    Returns:
        (valid, message) tuple
    """
    skill_path = Path(skill_path).resolve()

    if not skill_path.is_dir():
        return False, f"Not a directory: {skill_path}"

    # Check SKILL.md
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md not found"

    content = skill_md.read_text()

    # Parse frontmatter
    if not content.startswith("---"):
        return False, "SKILL.md must start with YAML frontmatter (---)"

    parts = content.split("---", 2)
    if len(parts) < 3:
        return False, "SKILL.md must have closing --- for YAML frontmatter"

    try:
        frontmatter = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        return False, f"Invalid YAML frontmatter: {e}"

    if not isinstance(frontmatter, dict):
        return False, "YAML frontmatter must be a mapping"

    # Check for unknown keys
    unknown_keys = set(frontmatter.keys()) - ALLOWED_FRONTMATTER_KEYS
    if unknown_keys:
        return False, f"Unknown frontmatter keys: {', '.join(sorted(unknown_keys))}"

    # Required: name
    name = frontmatter.get("name")
    if not name:
        return False, "Missing 'name' in frontmatter"
    if not isinstance(name, str):
        return False, "'name' must be a string"
    if len(name) > 64:
        return False, "Skill name must be 64 characters or fewer"
    if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name):
        return False, "Skill name must be kebab-case (lowercase, digits, single hyphens)"

    # Required: description
    desc = frontmatter.get("description")
    if not desc:
        return False, "Missing 'description' in frontmatter"
    if not isinstance(desc, str):
        return False, "'description' must be a string"
    if len(desc) > 1024:
        return False, "Description must be 1024 characters or fewer"
    if re.search(r"[<>]", desc):
        return False, "Description must not contain angle brackets"

    # Optional: compatibility
    compat = frontmatter.get("compatibility")
    if compat is not None:
        if not isinstance(compat, str):
            return False, "'compatibility' must be a string"
        if len(compat) > 500:
            return False, "Compatibility must be 500 characters or fewer"

    # Check pspm.json
    pspm_json = skill_path / "pspm.json"
    if pspm_json.exists():
        try:
            json.loads(pspm_json.read_text())
        except json.JSONDecodeError as e:
            return False, f"Invalid pspm.json: {e}"

    return True, f"Skill '{name}' is valid"


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: uv run --project runtime runtime/validate_skill.py <skill-directory>")
        sys.exit(1)

    skill_path = Path(sys.argv[1])
    valid, message = validate_skill(skill_path)

    if valid:
        print(f"Valid: {message}")
        sys.exit(0)
    else:
        print(f"Invalid: {message}")
        sys.exit(1)


if __name__ == "__main__":
    main()
