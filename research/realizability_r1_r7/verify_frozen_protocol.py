#!/usr/bin/env python3
"""Verify the frozen prospective Principle R protocol scaffold.

This verifier is intentionally structural. It checks schema, required fields,
declared file hashes, R1--R5/R7 declarations, absence of R6 result fields, and
the exact no-search status. It does not run or import any R6 search.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "frozen_protocol_v1_0.json"
EXPECTED_STATUS = "PROTOCOL_FROZEN_NO_R6_SEARCH_PERFORMED"
REQUIRED_TOP_LEVEL = {
    "schema_version",
    "protocol_id",
    "title",
    "status",
    "boundary",
    "dependencies",
    "input_files",
    "R1",
    "R2",
    "R3",
    "R4",
    "R5",
    "R6",
    "R7",
}
REQUIRED_R_SECTIONS = ("R1", "R2", "R3", "R4", "R5", "R7")
FORBIDDEN_R6_RESULT_KEYS = {
    "result",
    "results",
    "certificate",
    "certificate_sha256",
    "report",
    "report_sha256",
    "all_gates_pass",
    "r6_success",
    "r6_failure",
    "scientific_status",
    "computed_bounds",
    "search_output",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def has_forbidden_key(value: Any, forbidden: set[str]) -> list[str]:
    findings: list[str] = []

    def walk(node: Any, prefix: str) -> None:
        if isinstance(node, dict):
            for key, child in node.items():
                path = f"{prefix}.{key}" if prefix else str(key)
                if key in forbidden:
                    findings.append(path)
                walk(child, path)
        elif isinstance(node, list):
            for index, child in enumerate(node):
                walk(child, f"{prefix}[{index}]")

    walk(value, "")
    return findings


def main() -> int:
    checks: dict[str, bool] = {}
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))

    checks["schema_version"] = protocol.get("schema_version") == "1.0"
    checks["required_top_level_fields"] = REQUIRED_TOP_LEVEL.issubset(protocol)
    checks["status_exact"] = protocol.get("status") == EXPECTED_STATUS

    boundary = protocol.get("boundary", {})
    checks["boundary_is_prospective_only"] = (
        boundary.get("kind") == "prospective_protocol_only"
        and boundary.get("published_theorem_modified") is False
        and boundary.get("r6_search_performed") is False
        and boundary.get("r6_certificate_present") is False
        and boundary.get("global_flow_claimed") is False
        and boundary.get("v0_9_3_used_as_new_r6_result") is False
    )

    deps = protocol.get("dependencies", {})
    checks["dependencies_declared"] = (
        deps.get("python_flint") == "0.8.0"
        and deps.get("arb_precision_bits") == 192
    )

    input_files = protocol.get("input_files", [])
    checks["input_files_schema"] = isinstance(input_files, list) and bool(input_files)
    for item in input_files:
        rel = item.get("path")
        expected = item.get("sha256")
        path = ROOT / rel if isinstance(rel, str) else ROOT / "__invalid__"
        label = str(rel).replace("/", "_")
        checks[f"input_{label}_exists"] = path.is_file()
        checks[f"input_{label}_sha256"] = (
            path.is_file()
            and isinstance(expected, str)
            and sha256_file(path) == expected
        )

    for section in REQUIRED_R_SECTIONS:
        body = protocol.get(section, {})
        checks[f"{section}_declared"] = isinstance(body, dict) and body.get("declared") is True

    r3 = protocol.get("R3", {})
    w_pi = r3.get("W_Pi", {})
    checks["R3_metric_declared_as_protocol_relative"] = (
        r3.get("interpretation") == "protocol-relative response cost"
        and w_pi.get("frozen") is True
        and w_pi.get("matrix") == "identity_8x8"
        and "physical time" in r3.get("not_interpreted_as", [])
        and "physical energy" in r3.get("not_interpreted_as", [])
        and "physical action" in r3.get("not_interpreted_as", [])
    )
    identity_8 = [[1 if i == j else 0 for j in range(8)] for i in range(8)]
    checks["R3_W_Pi_hash"] = (
        hashlib.sha256(canonical_json(identity_8)).hexdigest()
        == w_pi.get("sha256_of_canonical_json")
    )

    r5 = protocol.get("R5", {})
    checks["R5_candidate_family_frozen_no_certificate"] = (
        r5.get("candidate_family") == "a_epsilon(s)=epsilon*sin(2*pi*s)*v"
        and r5.get("certificate_run") is False
        and isinstance(r5.get("epsilon_sequence"), list)
        and bool(r5.get("epsilon_sequence"))
    )

    r6 = protocol.get("R6", {})
    checks["R6_future_gates_only"] = (
        r6.get("declared") is True
        and r6.get("search_allowed_in_this_repository_state") is False
        and r6.get("certificate_run") is False
        and set(r6.get("future_gates_only", []))
        == {
            "existence",
            "uniqueness",
            "chart_residence",
            "exact_response_preservation",
            "zero_total_cost",
            "positive_measure_nonconstancy",
            "strict_independent_L6_change",
        }
    )
    checks["R6_result_fields_absent"] = not has_forbidden_key(r6, FORBIDDEN_R6_RESULT_KEYS)

    r7 = protocol.get("R7", {})
    checks["R7_positive_control_declared_no_certificate"] = (
        r7.get("control_family") == "eta_delta(s)=theta_0+s*delta*n"
        and r7.get("uses_same_response_cost_as_R3") is True
        and r7.get("certificate_run") is False
        and isinstance(r7.get("delta_sequence"), list)
        and bool(r7.get("delta_sequence"))
    )

    print(json.dumps(checks, indent=2, sort_keys=True))
    passed = bool(checks) and all(checks.values())
    print("PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
