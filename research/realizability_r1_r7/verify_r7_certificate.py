#!/usr/bin/env python3
"""Verify the R7 positive-control certificate without recomputing R7."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PROTOCOL_PATH = HERE / "frozen_protocol_v1_0.json"
CERT_PATH = HERE / "certificates" / "r7_positive_control_v1_1.json"

EXPECTED_STATUS = "R7_CERTIFIED"
EXPECTED_SCOPE = "prospective_r7_certificate"
EXPECTED_CERTIFICATE_ID = "principle_r_r7_positive_control_v1_1"
SUPERSEDED_CERTIFICATE_ID = "principle_r_r7_positive_control_v1_0"
EXPECTED_PROTOCOL_STATUS = "PROTOCOL_FROZEN_NO_R6_SEARCH_PERFORMED"
EXPECTED_BASELINE = "b9796c9ffb203bfbf3d0e230fe624ca85c0e75b9"
EXPECTED_PROTOCOL_SHA256 = "e8519a644ab50a9989eb40bc34499055f83760563167d88da21d17b3c7539e1c"
EXPECTED_W_PI_SHA256 = "0111dea7a4444ff1449da5ffcc98beb2eae423e7e8e3a290626d377896aa82dc"
EXPECTED_DELTAS = ["1e-14", "3e-14", "1e-13", "3e-13", "1e-12"]
EXPECTED_N = [1.0] + [0.0] * 13


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def positive_decimal_string(value: Any) -> bool:
    parsed = parse_finite_decimal(value)
    return parsed is not None and parsed > 0


def parse_finite_decimal(value: Any) -> Decimal | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = Decimal(value)
        if not parsed.is_finite():
            return None
        return parsed
    except (InvalidOperation, ValueError, OverflowError):
        return None


def full_path_enclosure(record: dict[str, Any]) -> bool:
    delta = parse_finite_decimal(record.get("delta"))
    lower = parse_finite_decimal(record.get("displacement_interval_lower"))
    upper = parse_finite_decimal(record.get("displacement_interval_upper"))
    if delta is None or lower is None or upper is None:
        return False
    return (
        delta > 0
        and lower <= 0
        and upper >= delta
        and lower <= upper
    )


def verify(certificate: dict[str, Any]) -> dict[str, bool]:
    protocol = read_json(PROTOCOL_PATH)
    protocol_inputs = {item["path"]: item["sha256"] for item in protocol["input_files"]}
    cert_inputs = certificate.get("input_sha256", {})
    protocol_gates = certificate.get("protocol_identity_gates", {})
    input_gates = certificate.get("input_identity_gates", {})
    gates = certificate.get("gates", {})
    records = certificate.get("delta_records", [])
    w_pi = certificate.get("W_Pi", {})
    n = certificate.get("R7_fixed_normal_control_n", {}).get("components")

    checks = {
        "certificate_id": certificate.get("certificate_id") == EXPECTED_CERTIFICATE_ID,
        "supersedes_v1_0": (
            certificate.get("corrects_certificate_id") == SUPERSEDED_CERTIFICATE_ID
            and "PR #53" in certificate.get("supersession_note", "")
            and "[0, delta]" in certificate.get("supersession_note", "")
        ),
        "certificate_file_scope": certificate.get("scientific_scope") == EXPECTED_SCOPE,
        "scientific_status": certificate.get("scientific_status") == EXPECTED_STATUS,
        "all_gates_pass": certificate.get("all_gates_pass") is True,
        "R7_CERTIFIED": certificate.get("R7_CERTIFIED") is True,
        "protocol_status": certificate.get("protocol_status") == EXPECTED_PROTOCOL_STATUS,
        "protocol_sha256": certificate.get("protocol_sha256") == EXPECTED_PROTOCOL_SHA256,
        "live_protocol_sha256": sha256_file(PROTOCOL_PATH) == EXPECTED_PROTOCOL_SHA256,
        "baseline_commit": certificate.get("required_main_baseline_commit") == EXPECTED_BASELINE,
        "arb_precision": certificate.get("arb_precision_bits") == 192,
        "python_flint_version": certificate.get("versions", {}).get("python_flint") == "0.8.0",
        "input_hashes_match_protocol": cert_inputs == protocol_inputs,
        "all_protocol_identity_gates_pass": bool(protocol_gates) and all(protocol_gates.values()),
        "all_input_identity_gates_pass": bool(input_gates) and all(input_gates.values()),
        "all_certificate_gates_pass": bool(gates) and all(gates.values()),
        "normal_control_n_matches": n == EXPECTED_N,
        "delta_sequence_matches": certificate.get("R7_delta_sequence") == EXPECTED_DELTAS,
        "W_Pi_identity_hash_matches": (
            w_pi.get("frozen") is True
            and w_pi.get("matrix") == "identity_8x8"
            and w_pi.get("sha256_of_canonical_json") == EXPECTED_W_PI_SHA256
        ),
        "R5_not_run": certificate.get("R5_certificate_run") is False,
        "R6_not_run": (
            certificate.get("R6_search_performed") is False
            and certificate.get("R6_certificate_run") is False
        ),
        "no_physical_or_global_claim": (
            certificate.get("global_flow_claimed") is False
            and certificate.get("empirical_physical_validation_claimed") is False
            and certificate.get("physical_time_energy_or_action_claimed") is False
            and certificate.get("lorentzian_spacetime_or_gr_claimed") is False
        ),
        "all_delta_records_present": [r.get("delta") for r in records] == EXPECTED_DELTAS,
    }

    for record in records:
        delta = record.get("delta", "__missing__")
        prefix = f"delta_{delta}"
        checks[f"{prefix}_status"] = record.get("status") == "R7_DELTA_CERTIFIED"
        checks[f"{prefix}_chart"] = record.get("chart_residence_gate") is True
        checks[f"{prefix}_no_wrap"] = record.get("no_phase_wrap_gate") is True
        checks[f"{prefix}_nonconstant"] = record.get("nonconstant_gate") is True
        checks[f"{prefix}_same_meter"] = record.get("same_meter_gate") is True
        checks[f"{prefix}_full_path_enclosure"] = (
            record.get("path_enclosure")
            == "theta0[0] + arb(delta/2, delta/2), enclosing s*delta for s in [0,1]"
            and record.get("endpoint_theta0_contained_gate") is True
            and record.get("endpoint_theta0_plus_delta_contained_gate") is True
            and full_path_enclosure(record)
        )
        checks[f"{prefix}_pointwise_positive"] = (
            record.get("strict_positive_pointwise_response_gate") is True
            and positive_decimal_string(record.get("pointwise_cost_lower"))
            and positive_decimal_string(record.get("response_speed_square_interval_lower"))
        )
        checks[f"{prefix}_total_cost_positive"] = (
            record.get("strict_positive_total_cost_gate") is True
            and positive_decimal_string(record.get("total_cost_lower"))
        )

    return checks


def run_mutation_tests(certificate: dict[str, Any]) -> dict[str, bool]:
    cases: dict[str, dict[str, Any]] = {}

    mutated = copy.deepcopy(certificate)
    mutated["delta_records"][0]["pointwise_cost_lower"] = "0"
    cases["zero_positive_lower_bound_fails"] = mutated

    malformed_values = {
        "negative_positive_lower_bound_fails": "-1e-30",
        "nan_positive_lower_bound_fails": "NaN",
        "snan_positive_lower_bound_fails": "sNaN",
        "infinity_positive_lower_bound_fails": "Infinity",
        "plus_infinity_positive_lower_bound_fails": "+Infinity",
        "minus_infinity_positive_lower_bound_fails": "-Infinity",
        "malformed_positive_lower_bound_fails": "not-a-decimal",
        "non_string_positive_lower_bound_fails": 1,
    }
    for name, value in malformed_values.items():
        mutated = copy.deepcopy(certificate)
        mutated["delta_records"][0]["pointwise_cost_lower"] = value
        cases[name] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["delta_records"][0]["endpoint_theta0_plus_delta_contained_gate"] = False
    cases["theta0_plus_delta_endpoint_gate_false_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["delta_records"][0]["endpoint_theta0_contained_gate"] = False
    cases["theta0_endpoint_gate_false_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["delta_records"][0]["displacement_interval_lower"] = "1e-30"
    cases["positive_displacement_lower_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["delta_records"][0]["displacement_interval_upper"] = "1e-30"
    cases["displacement_upper_smaller_than_delta_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["delta_records"][0]["displacement_interval_lower"] = "2"
    mutated["delta_records"][0]["displacement_interval_upper"] = "1"
    cases["displacement_lower_greater_than_upper_fails"] = mutated

    endpoint_bad_values = {
        "displacement_lower_nan_fails": ("displacement_interval_lower", "NaN"),
        "displacement_lower_infinity_fails": ("displacement_interval_lower", "Infinity"),
        "displacement_upper_nan_fails": ("displacement_interval_upper", "NaN"),
        "displacement_upper_infinity_fails": ("displacement_interval_upper", "Infinity"),
    }
    for name, (field, value) in endpoint_bad_values.items():
        mutated = copy.deepcopy(certificate)
        mutated["delta_records"][0][field] = value
        cases[name] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["R7_fixed_normal_control_n"]["components"][0] = 0.0
    cases["changed_n_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["R7_delta_sequence"][0] = "2e-14"
    cases["changed_delta_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["W_Pi"]["matrix"] = "scaled_identity_8x8"
    cases["changed_W_Pi_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["R5_certificate_run"] = True
    cases["R5_marked_run_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["R6_search_performed"] = True
    cases["R6_marked_run_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["input_sha256"].pop(next(iter(mutated["input_sha256"])))
    cases["deleted_dependency_hash_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["scientific_status"] = "R7_INCONCLUSIVE"
    mutated["all_gates_pass"] = True
    cases["forged_all_gates_pass_fails"] = mutated

    return {name: not all(verify(case).values()) for name, case in cases.items()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mutation-tests", action="store_true")
    args = parser.parse_args()

    certificate = read_json(CERT_PATH)
    checks = verify(certificate)
    if args.mutation_tests:
        checks.update(run_mutation_tests(certificate))
    print(json.dumps(checks, indent=2, sort_keys=True))
    passed = bool(checks) and all(checks.values())
    print("PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
