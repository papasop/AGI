#!/usr/bin/env python3
"""Verify stored reference-result structure and SHA-256 manifest."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHA256SUMS = ROOT / "SHA256SUMS.txt"


def run(command: list[str]) -> int:
    return subprocess.call(command, cwd=ROOT)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_manifest() -> int:
    for lineno, line in enumerate(SHA256SUMS.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            expected, name = line.split(None, 1)
        except ValueError:
            print(f"Malformed SHA256SUMS.txt line {lineno}", file=sys.stderr)
            return 1
        path = ROOT / name
        if not path.is_file():
            print(f"{name}: FAILED open or read", file=sys.stderr)
            return 1
        actual = sha256(path)
        if actual != expected:
            print(f"{name}: FAILED", file=sys.stderr)
            return 1
        print(f"{name}: OK")
    return 0


def main() -> int:
    code = run([sys.executable, "tools/verify_release.py"])
    if code:
        return code
    return verify_manifest()


if __name__ == "__main__":
    raise SystemExit(main())
