#!/usr/bin/env python3
"""Verify hashes, Python syntax, JSON syntax, and milestone claim boundaries."""
from __future__ import annotations

import hashlib
import json
import py_compile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


expected = {}
for line in (ROOT / "SHA256SUMS.txt").read_text().splitlines():
    if line.strip():
        value, name = line.split(None, 1)
        expected[name.strip()] = value

for name, value in expected.items():
    path = ROOT / name
    assert path.is_file(), f"missing: {name}"
    assert digest(path) == value, f"hash mismatch: {name}"

with tempfile.TemporaryDirectory(prefix="geometric_flow_verify_update_") as tmp:
    cache = Path(tmp)
    for path in (ROOT / "src").glob("*.py"):
        py_compile.compile(str(path), cfile=str(cache / f"{path.name}.pyc"), doraise=True)
for path in (ROOT / "results").rglob("*.json"):
    json.loads(path.read_text())

summary = json.loads((ROOT / "results/v0_10_5/run_summary.json").read_text())
assert summary["same_expression_X_ready"] is True
assert summary["same_expression_DX_ready"] is True
assert summary["qr_lohner_flowpipe_certified"] is False
assert summary["global_flow_claimed"] is False
print("v0.10.5 update verification: PASS")
