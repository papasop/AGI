#!/usr/bin/env python3
"""Shared helpers for stable user-facing reproduction entry points."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHA256SUMS = ROOT / "SHA256SUMS.txt"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_manifest() -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in SHA256SUMS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, name = line.split(None, 1)
        entries[name] = digest
    return entries


def fail_closed_sha256(relative_paths: list[str]) -> None:
    manifest = read_manifest()
    for name in relative_paths:
        path = ROOT / name
        expected = manifest.get(name)
        if expected is None:
            raise SystemExit(f"fail closed: {name} is absent from SHA256SUMS.txt")
        if not path.is_file():
            raise SystemExit(f"fail closed: {name} is missing")
        actual = sha256(path)
        if actual != expected:
            raise SystemExit(
                f"fail closed: {name} SHA-256 mismatch\n"
                f"expected {expected}\n"
                f"actual   {actual}"
            )


def run_python_script(relative_path: str, args: list[str]) -> int:
    return subprocess.call([sys.executable, relative_path, *args], cwd=ROOT)


def stable_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="verify frozen SHA-256 bindings without running the underlying script",
    )
    return parser
