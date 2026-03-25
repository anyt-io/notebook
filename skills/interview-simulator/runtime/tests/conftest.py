"""Shared fixtures for interview simulator tests."""

from __future__ import annotations

import sys
from pathlib import Path

# Add runtime directory to path so tests can import modules
sys.path.insert(0, str(Path(__file__).parent.parent))
