#!/usr/bin/env python3
"""Audit Layer III: the implementation-open fifth-frame target."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


if __name__ == "__main__":
    sys.path.insert(0, str(SCRIPTS))
    runpy.run_path(str(ROOT / "scripts" / "audit_fifth_frame.py"), run_name="__main__")
