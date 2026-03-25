"""Pytest configuration to add runtime directory to sys.path."""

import sys
from pathlib import Path

# Add runtime directory to path so tests can import modules directly
runtime_dir = str(Path(__file__).parent.parent)
if runtime_dir not in sys.path:
    sys.path.insert(0, runtime_dir)
