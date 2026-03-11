#!/usr/bin/env python3
"""Emit OpenClaw MEDIA lines for an existing local file."""

import argparse
import sys
from pathlib import Path

from config import ProcessingError, TelegramMediaSkillError, ValidationError

_ERROR_PREFIXES: dict[type[TelegramMediaSkillError], str] = {
    ValidationError: "Validation error",
    ProcessingError: "Processing error",
}


def resolve_file(path_str: str) -> Path:
    path = Path(path_str).expanduser().resolve()
    if not path.exists():
        raise ValidationError(f"file not found: {path}")
    if not path.is_file():
        raise ValidationError(f"not a file: {path}")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit OpenClaw MEDIA lines for an existing local file")
    parser.add_argument("path", help="Path to an existing local file")
    parser.add_argument("--caption", help="Optional caption text to print before the MEDIA line")
    args = parser.parse_args()

    try:
        path = resolve_file(args.path)
        if args.caption:
            print(args.caption)
        print(f"MEDIA:{path}")
        return 0
    except TelegramMediaSkillError as e:
        prefix = _ERROR_PREFIXES.get(type(e), "Error")
        print(f"\n{prefix}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
