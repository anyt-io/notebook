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

from config import (
    ALLOWED_FRONTMATTER_KEYS,
    MAX_COMPATIBILITY_LENGTH,
    MAX_DESCRIPTION_LENGTH,
    SkillCreatorError,
    ValidationError,
    validate_name,
)


def validate_skill(skill_path: Path) -> str:
    """
    Validate a PSPM skill directory.

    Returns the skill name on success. Raises ValidationError on failure.
    """
    skill_path = Path(skill_path).resolve()

    if not skill_path.is_dir():
        raise ValidationError(f"Not a directory: {skill_path}")

    # Check SKILL.md
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        raise ValidationError("SKILL.md not found")

    content = skill_md.read_text()

    # Parse frontmatter
    if not content.startswith("---"):
        raise ValidationError("SKILL.md must start with YAML frontmatter (---)")

    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValidationError("SKILL.md must have closing --- for YAML frontmatter")

    try:
        frontmatter = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        raise ValidationError(f"Invalid YAML frontmatter: {e}") from e

    if not isinstance(frontmatter, dict):
        raise ValidationError("YAML frontmatter must be a mapping")

    # Check for unknown keys
    unknown_keys = set(frontmatter.keys()) - ALLOWED_FRONTMATTER_KEYS
    if unknown_keys:
        raise ValidationError(f"Unknown frontmatter keys: {', '.join(sorted(unknown_keys))}")

    # Required: name
    name = frontmatter.get("name")
    if not name:
        raise ValidationError("Missing 'name' in frontmatter")
    if not isinstance(name, str):
        raise ValidationError("'name' must be a string")
    validate_name(name)

    # Required: description
    desc = frontmatter.get("description")
    if not desc:
        raise ValidationError("Missing 'description' in frontmatter")
    if not isinstance(desc, str):
        raise ValidationError("'description' must be a string")
    if len(desc) > MAX_DESCRIPTION_LENGTH:
        raise ValidationError(f"Description must be {MAX_DESCRIPTION_LENGTH} characters or fewer")
    if re.search(r"[<>]", desc):
        raise ValidationError("Description must not contain angle brackets")

    # Optional: compatibility
    compat = frontmatter.get("compatibility")
    if compat is not None:
        if not isinstance(compat, str):
            raise ValidationError("'compatibility' must be a string")
        if len(compat) > MAX_COMPATIBILITY_LENGTH:
            raise ValidationError(f"Compatibility must be {MAX_COMPATIBILITY_LENGTH} characters or fewer")

    # Check pspm.json
    pspm_json = skill_path / "pspm.json"
    if pspm_json.exists():
        try:
            json.loads(pspm_json.read_text())
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid pspm.json: {e}") from e

    return name


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: uv run --project runtime runtime/validate_skill.py <skill-directory>")
        return 1

    skill_path = Path(sys.argv[1])

    try:
        name = validate_skill(skill_path)
        print(f"Valid: Skill '{name}' is valid")
        return 0
    except SkillCreatorError as e:
        print(f"Invalid: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
