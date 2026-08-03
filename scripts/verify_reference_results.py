#!/usr/bin/env python3
"""Verify stored reference-result structure and SHA-256 manifest."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str]) -> int:
    return subprocess.call(command, cwd=ROOT)


def main() -> int:
    checks = [
        [sys.executable, "tools/verify_release.py"],
        ["/sbin/sha256sum", "-c", "SHA256SUMS.txt"],
    ]
    for command in checks:
        code = run(command)
        if code:
            return code
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
