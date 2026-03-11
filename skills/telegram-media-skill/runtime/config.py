"""Configuration constants and exception hierarchy for the telegram-media-skill skill."""

from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = SKILL_DIR / "output"


class TelegramMediaSkillError(Exception):
    """Base exception for telegram-media-skill skill errors."""


class ValidationError(TelegramMediaSkillError):
    """Input validation errors."""


class ProcessingError(TelegramMediaSkillError):
    """Processing or conversion failures."""
