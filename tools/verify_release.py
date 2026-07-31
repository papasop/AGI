#!/usr/bin/env python3
"""Fail-closed structural verification for the migration package."""

from __future__ import annotations

import hashlib
import json
import py_compile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PARAMETERIZATION_HASH = (
    "e8ad8a6fbcab626b726082b570f59df6854d4a28259177783e1f5e3274b1cb84"
)
REQUIRED = [
    "CITATION.cff",
    "LICENSE",
    "README.md",
    "README_RECOVERY.md",
    "docs/MIGRATION_RECORD.md",
    "docs/CLAIM_SCOPE.md",
    "docs/STEP_REFINEMENT.md",
    "docs/FORMAL_ROADMAP.md",
    "requirements.txt",
    "rebuild_all_artifacts.py",
    "results/reference/step_refinement_summary.json",
    "scripts/response_fibre_exact_root_descent_v1_3_1.py",
    "scripts/response_fibre_geometric_flow_preflight_v0_1.py",
    "scripts/response_fibre_projected_gradient_reconstruction_v0_2_2_oneclick.py",
    "scripts/response_fibre_projected_gradient_reconstruction_v0_2_3_steps160_oneclick.py",
]


def canonical_json(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    missing = [relative for relative in REQUIRED if not (ROOT / relative).is_file()]
    if missing:
        raise SystemExit(f"FAIL missing required files: {missing}")

    for relative in REQUIRED:
        if relative.endswith(".py"):
            py_compile.compile(str(ROOT / relative), doraise=True)

    summary_path = ROOT / "results/reference/step_refinement_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if summary["source_parameterization_sha256"] != EXPECTED_PARAMETERIZATION_HASH:
        raise SystemExit("FAIL frozen parameterization hash mismatch")
    runs = summary["runs"]
    if not all(runs[key]["all_gates_pass"] for key in ("80", "160")):
        raise SystemExit("FAIL one reference run is not marked as passing")
    if not all(
        runs[key]["scientific_status"]
        == "PROJECTED_GRADIENT_CURVE_RECONSTRUCTION_SUPPORTED"
        for key in ("80", "160")
    ):
        raise SystemExit("FAIL unexpected scientific status")

    observed = abs(runs["80"]["total_L6_change"] - runs["160"]["total_L6_change"])
    declared = summary["step_refinement"][
        "absolute_total_L6_change_difference"
    ]
    if abs(observed - declared) > 1.0e-15:
        raise SystemExit("FAIL inconsistent step-refinement difference")

    print("PASS: migration package structure and reference summary are consistent")
    print(f"summary_sha256 = {sha256(summary_path)}")


if __name__ == "__main__":
    main()
