#!/usr/bin/env python3
"""Verify or reproduce the published local-paper theorem boundary.

Default mode is a fast fail-closed check of the stored v0.7.4 and v0.9.3
reference artifacts, SHA-256 manifest, citation metadata, and published-paper
boundary document. Use --run to recompute the two theorem components locally.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
V074_OUT = ROOT / "results" / "published_paper_v074"
V093_OUT = ROOT / "results" / "published_paper_v093"
SUMMARY = ROOT / "results" / "published_paper_summary.json"


def run(command: list[str]) -> int:
    return subprocess.call(command, cwd=ROOT)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def joint_gate(stage_a: dict, stage_b: dict) -> dict:
    stage_a_checks = {
        "stage_a_rank_descent_cover_certified": stage_a.get("stage_a_rank_descent_cover_certified") is True,
        "formal_response_rank_cover_certified": stage_a.get("formal_response_rank_cover_certified") is True,
        "formal_response_tangency_cover_certified": stage_a.get("formal_response_tangency_cover_certified") is True,
        "formal_projected_gradient_nonstationary_cover_certified": (
            stage_a.get("formal_projected_gradient_nonstationary_cover_certified") is True
        ),
        "uniform_single_box_L6_descent_certified": stage_a.get("uniform_single_box_L6_descent_certified") is True,
        "child_box_cover": (
            stage_a.get("child_boxes_declared") == 16
            and stage_a.get("child_boxes_passing_stage_a") == 16
        ),
        "not_ode_claim": stage_a.get("validated_ODE_claimed") is False,
        "not_global_flow": stage_a.get("global_flow_claimed") is False,
    }
    stage_b_checks = {
        "all_gates_pass": stage_b.get("all_gates_pass") is True,
        "validated_ODE_claimed": stage_b.get("validated_ODE_claimed") is True,
        "ODE_existence_certified": stage_b.get("ODE_existence_certified") is True,
        "ODE_uniqueness_certified": stage_b.get("ODE_uniqueness_certified") is True,
        "exact_response_preservation_certified": stage_b.get("exact_response_preservation_certified") is True,
        "uniform_L6_descent_certified_for_validated_solution": (
            stage_b.get("uniform_L6_descent_certified_for_validated_solution") is True
        ),
        "protocol_hash": (
            stage_b.get("protocol_sha256")
            == "6d0aaefabd71f1d2986515ed84673f0083ae90d0344b9a1e92d7697ac08d061a"
        ),
        "generator_hash": (
            stage_b.get("generator_source_sha256")
            == "3be3e07146ff0e505f08bae7bd0ec7f2895955f2540647fea3278fdba51db79c"
        ),
        "not_global_flow": stage_b.get("global_flow_claimed") is False,
    }
    summary = {
        "STAGE_A_PARENT_BOX_GEOMETRY_CERTIFIED": all(stage_a_checks.values()),
        "STAGE_B_LOCAL_ODE_MICROSTEP_CERTIFIED": all(stage_b_checks.values()),
        "GLOBAL_FLOW_CLAIMED": False,
    }
    summary["PUBLISHED_LOCAL_PAPER_RELEASE_GATE"] = (
        summary["STAGE_A_PARENT_BOX_GEOMETRY_CERTIFIED"]
        and summary["STAGE_B_LOCAL_ODE_MICROSTEP_CERTIFIED"]
        and summary["GLOBAL_FLOW_CLAIMED"] is False
    )
    return {
        "stage_a_checks": stage_a_checks,
        "stage_b_checks": stage_b_checks,
        "summary": summary,
    }


def verify_stored_boundary() -> int:
    code = run([sys.executable, "scripts/verify_reference_results.py"])
    if code:
        return code
    code = run([sys.executable, "tools/verify_certificate_semantics.py"])
    if code:
        return code
    stage_a = load_json(ROOT / "results" / "reference_run_summary.json")
    stage_b = load_json(ROOT / "results" / "v0_9_3_reference" / "report.json")
    result = joint_gate(stage_a, stage_b)
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    if not result["summary"]["PUBLISHED_LOCAL_PAPER_RELEASE_GATE"]:
        print("FAIL-CLOSED: stored published-paper boundary did not verify", file=sys.stderr)
        return 1
    print("PASS: published paper boundary verified")
    return 0


def reproduce_boundary() -> int:
    commands = [
        [
            sys.executable,
            "src/response_fibre_arb_kkt_witness_alignment_v0_7_4.py",
            "--inputs-zip",
            "inputs/response_fibre_v0_6_2_backend_inputs.zip",
            "--chart",
            "9",
            "--subdivision",
            "32",
            "--output",
            str(V074_OUT.relative_to(ROOT)),
        ],
        [
            sys.executable,
            "src/response_fibre_intrinsic_picard_microstep_v0_9_3.py",
            "--inputs-zip",
            "inputs/response_fibre_v0_6_2_backend_inputs.zip",
            "--v074-source",
            "src/response_fibre_arb_kkt_witness_alignment_v0_7_4.py",
            "--no-download",
            "--output",
            str(V093_OUT.relative_to(ROOT)),
        ],
    ]
    for command in commands:
        code = run(command)
        if code:
            return code
    result = joint_gate(load_json(V074_OUT / "report.json"), load_json(V093_OUT / "report.json"))
    SUMMARY.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    if not result["summary"]["PUBLISHED_LOCAL_PAPER_RELEASE_GATE"]:
        print("FAIL-CLOSED: recomputed published-paper boundary did not verify", file=sys.stderr)
        return 1
    print("PASS: published paper boundary reproduced")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run",
        action="store_true",
        help="recompute v0.7.4 and v0.9.3 instead of checking stored artifacts",
    )
    args = parser.parse_args(argv)
    if args.run:
        return reproduce_boundary()
    return verify_stored_boundary()


if __name__ == "__main__":
    raise SystemExit(main())
