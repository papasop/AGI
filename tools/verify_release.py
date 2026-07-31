#!/usr/bin/env python3
"""Fail-closed structural and hash verification for the frozen v0.7.4 release."""

from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "response_fibre_arb_kkt_witness_alignment_v0_7_4.py"
INPUTS = ROOT / "inputs" / "response_fibre_v0_6_2_backend_inputs.zip"
SUMMARY = ROOT / "results" / "reference_run_summary.json"

EXPECTED_SOURCE_SHA256 = (
    "1f71c4918d1cd1d6c45dc0da4a7358e176baac9116c8f71f4a949a6d657520f8"
)
EXPECTED_INPUTS_SHA256 = (
    "2efd863f5ff26da1067594f068bfe265678e6ebac480574ff0574ccc55f98666"
)
EXPECTED_ATLAS_SHA256 = (
    "c02acc1c76e0b670793340150d1a875fdc373e0ac7c46d3360a7824b66a3a5ef"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(value) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def main() -> int:
    checks = {
        "source_exists": SOURCE.is_file(),
        "inputs_exist": INPUTS.is_file(),
        "summary_exists": SUMMARY.is_file(),
    }
    if not all(checks.values()):
        print(json.dumps(checks, indent=2))
        return 1

    checks["source_sha256"] = sha256(SOURCE) == EXPECTED_SOURCE_SHA256
    checks["inputs_sha256"] = sha256(INPUTS) == EXPECTED_INPUTS_SHA256

    with zipfile.ZipFile(INPUTS) as archive:
        atlas_names = [
            name for name in archive.namelist()
            if name.endswith("/corrected_atlas.json")
            or name == "corrected_atlas.json"
        ]
        checks["one_corrected_atlas"] = len(atlas_names) == 1
        if atlas_names:
            atlas = json.loads(archive.read(atlas_names[0]))
            checks["canonical_atlas_sha256"] = (
                hashlib.sha256(canonical_json(atlas)).hexdigest()
                == EXPECTED_ATLAS_SHA256
            )

    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    checks["stage_a_certified"] = (
        summary.get("stage_a_rank_descent_cover_certified") is True
    )
    checks["alignment_fail_closed"] = (
        summary.get("kkt_witness_alignment_cover_certified") is False
        and summary.get("all_gates_pass") is False
    )
    checks["validated_ode_not_claimed"] = (
        summary.get("validated_ODE_claimed") is False
    )

    print(json.dumps(checks, indent=2, sort_keys=True))
    passed = all(checks.values())
    print("PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())

