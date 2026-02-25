"""Shared constants, validation helpers, and exception hierarchy for pspm-skill-creator."""

import re

# ---------------------------------------------------------------------------
# Name validation
# ---------------------------------------------------------------------------

NAME_REGEX = r"^[a-z0-9]+(-[a-z0-9]+)*$"
MAX_NAME_LENGTH = 64

# ---------------------------------------------------------------------------
# Frontmatter validation
# ---------------------------------------------------------------------------

MAX_DESCRIPTION_LENGTH = 1024
MAX_COMPATIBILITY_LENGTH = 500
ALLOWED_FRONTMATTER_KEYS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}

# ---------------------------------------------------------------------------
# Packaging exclusions
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------


class SkillCreatorError(Exception):
    """Base exception for pspm-skill-creator errors."""


class ValidationError(SkillCreatorError):
    """Skill validation failures (bad frontmatter, invalid name, etc.)."""


class InitError(SkillCreatorError):
    """Skill initialization failures (directory exists, invalid name)."""


class PackagingError(SkillCreatorError):
    """Skill packaging failures (missing files, zip errors)."""


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def validate_name(name: str) -> None:
    """Validate skill name is kebab-case, max 64 chars. Raises ValidationError."""
    if len(name) > MAX_NAME_LENGTH:
        raise ValidationError(f"Skill name must be {MAX_NAME_LENGTH} characters or fewer")
    if not re.match(NAME_REGEX, name):
        raise ValidationError(
            "Skill name must be kebab-case (lowercase letters, digits, single hyphens, no leading/trailing hyphens)"
        )
