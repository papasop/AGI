#!/usr/bin/env python3
"""Reproduce Layer II: stored finite continuation reference checks."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


if __name__ == "__main__":
    sys.path.insert(0, str(SCRIPTS))
    runpy.run_path(
        str(ROOT / "scripts" / "reproduce_lohner_flowpipe.py"),
        run_name="__main__",
    )
