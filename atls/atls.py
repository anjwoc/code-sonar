#!/usr/bin/env python3
"""Compatibility shim for local absolute-path execution."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from atls.cli import main


if __name__ == "__main__":
    main()
