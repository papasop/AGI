#!/usr/bin/env python3
"""Reproduce Layer I: the frozen v0.9.3 local ODE theorem."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


if __name__ == "__main__":
    sys.path.insert(0, str(SCRIPTS))
    runpy.run_path(str(ROOT / "scripts" / "reproduce_local_ode.py"), run_name="__main__")
