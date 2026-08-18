#!/usr/bin/env python3
"""Verify the R5-B5 positive-measure nonconstancy record."""

from __future__ import annotations

import argparse
import copy
import json
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import certify_r5_positive_measure_nonconstancy as builder
import certify_r5_first_leaf_preflight as preflight


HERE = Path(__file__).resolve().parent
CERT_PATH = HERE / "certificates" / "r5_positive_measure_nonconstancy_v1_0.json"
DIAG_PATH = HERE / "diagnostics" / "r5_positive_measure_nonconstancy_v1_0.json"
RECORD_PATH = CERT_PATH if CERT_PATH.exists() else DIAG_PATH

ARB_RE = re.compile(r"^\[(?P<mid>[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?) \+/- (?P<rad>(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\]$")
ZERO_ARB_RE = re.compile(r"^\[\+/- (?P<rad>(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\]$")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def decimal_bounds(value: Any) -> tuple[Decimal, Decimal] | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = Decimal(value)
    except (InvalidOperation, ValueError, OverflowError):
        match = ARB_RE.match(value)
        if match:
            mid = Decimal(match.group("mid"))
            rad = Decimal(match.group("rad"))
        else:
            zero = ZERO_ARB_RE.match(value)
            if not zero:
                return None
            mid = Decimal("0")
            rad = Decimal(zero.group("rad"))
        lower = mid - rad
        upper = mid + rad
    else:
        lower = upper = parsed
    if not lower.is_finite() or not upper.is_finite() or lower > upper:
        return None
    return lower, upper


def lower(value: Any) -> Decimal:
    bounds = decimal_bounds(value)
    if bounds is None:
        raise ValueError(value)
    return bounds[0]


def bound_record(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    required = {"enclosure", "lower", "upper", "abs_lower", "abs_upper", "contains_zero"}
    return set(value) == required and isinstance(value["contains_zero"], bool) and all(
        decimal_bounds(value[key]) is not None for key in ["enclosure", "lower", "upper", "abs_lower", "abs_upper"]
    )


def bound_vector(value: Any, size: int) -> bool:
    return isinstance(value, list) and len(value) == size and all(bound_record(item) for item in value)


def comparable(value: dict[str, Any]) -> dict[str, Any]:
    return builder.digest_payload(value)


def epsilon_gates_valid(gates: Any) -> bool:
    required = {
        "epsilon_positive",
        "epsilon_in_frozen_sequence",
        "s_interval_matches_protocol",
        "cosine_lower_bound_positive",
        "intrinsic_speed_positive_on_I",
        "environment_direction_projection_positive",
        "environment_speed_positive_on_I",
        "positive_measure_interval",
        "endpoint_comparison_used",
        "binary64_theorem_decision_used",
        "nonconstant_positive_measure",
    }
    if not isinstance(gates, dict) or set(gates) != required or not all(isinstance(v, bool) for v in gates.values()):
        return False
    expected = all(gates[k] for k in required - {"endpoint_comparison_used", "binary64_theorem_decision_used", "nonconstant_positive_measure"}) and gates["endpoint_comparison_used"] is False and gates["binary64_theorem_decision_used"] is False
    return gates["nonconstant_positive_measure"] == expected


def epsilon_records_valid(records: Any, status: str) -> bool:
    if not isinstance(records, list) or [r.get("epsilon") for r in records] != builder.EPSILONS:
        return False
    certified = 0
    for record in records:
        if record.get("positive_measure_interval") != builder.S_INTERVAL:
            return False
        for key in ["positive_measure_interval_length", "cosine_lower_bound", "intrinsic_speed_lower", "environment_direction_component_abs_lower", "environment_speed_lower_on_I"]:
            if not bound_record(record.get(key)):
                return False
        if not epsilon_gates_valid(record.get("gates")):
            return False
        if record["gates"]["epsilon_positive"] != (lower(record["epsilon"]) > 0):
            return False
        if record["gates"]["cosine_lower_bound_positive"] != (lower(record["cosine_lower_bound"]["lower"]) > 0):
            return False
        if record["gates"]["intrinsic_speed_positive_on_I"] != (lower(record["intrinsic_speed_lower"]["lower"]) > 0):
            return False
        if record["gates"]["environment_speed_positive_on_I"] != (lower(record["environment_speed_lower_on_I"]["lower"]) > 0):
            return False
        if (record.get("epsilon_status") == "EPSILON_NONCONSTANT_CERTIFIED") != record["gates"]["nonconstant_positive_measure"]:
            return False
        certified += int(record["gates"]["nonconstant_positive_measure"])
    return (certified == len(builder.EPSILONS)) == (status == builder.CERTIFIED)


def verify(record: dict[str, Any], expected: dict[str, Any] | None = None) -> dict[str, bool]:
    if expected is None:
        expected = builder.build_record()
    status = record.get("scientific_status")
    inputs = record.get("inputs", {})
    protocol = record.get("frozen_protocol", {})
    method = record.get("method", {})
    scope = record.get("scope", {})
    summary = record.get("summary", {})
    eps = record.get("epsilon_records")
    certified = sum(1 for item in eps if isinstance(item, dict) and item.get("gates", {}).get("nonconstant_positive_measure") is True) if isinstance(eps, list) else -1
    return {
        "record_matches_recomputed_arb_record": comparable(record) == comparable(expected),
        "record_sha256": record.get("record_sha256") == builder.sha256_bytes(builder.canonical_json(comparable(record))),
        "schema_version": record.get("schema_version") == "1.0",
        "record_id": record.get("record_id") == "r5_positive_measure_nonconstancy_v1_0",
        "record_kind": record.get("record_kind") == "prospective_r5_b5_positive_measure_nonconstancy_certificate",
        "stage": record.get("stage") == "R5-B5",
        "scientific_status_allowed": status in builder.ALLOWED_STATUSES,
        "scientific_status_consistent": (status == builder.CERTIFIED and certified == len(builder.EPSILONS)) or (status == builder.NOT_CERTIFIED and certified < len(builder.EPSILONS)) or status in {builder.INCONCLUSIVE, builder.BOUNDARY_MISMATCH, builder.IMPLEMENTATION_ERROR},
        "arb_precision": record.get("arb_precision_bits") == 192,
        "base_commit": record.get("base_commit") == builder.EXPECTED_BASE_COMMIT,
        "input_hashes": inputs.get("protocol_sha256") == preflight.EXPECTED_PROTOCOL_SHA256 and inputs.get("auxiliary_sha256") == preflight.EXPECTED_AUXILIARY_SHA256 and inputs.get("b4_certificate_artifact_sha256") == builder.EXPECTED_B4_CERT_SHA256 and inputs.get("b4_internal_record_sha256") == builder.EXPECTED_B4_RECORD_SHA256 and inputs.get("object_sha256") == preflight.EXPECTED_OBJECT_SHA256,
        "frozen_protocol": protocol.get("epsilon_sequence") == builder.EPSILONS and protocol.get("s_interval") == builder.S_INTERVAL and protocol.get("fixed_v") == ["1", "0", "0", "0", "0", "0"] and protocol.get("result_adaptive_changes_allowed") is False,
        "method": method.get("source_branch") == "R5-B4 C1 implicit branch" and method.get("environment_projection_gate") == "single frozen phase-coordinate projection lower bound" and method.get("endpoint_comparison_used") is False and method.get("sampling_used") is False and method.get("binary64_theorem_decision_used") is False and method.get("new_observable_introduced") is False and method.get("zero_cost_checked") is False and method.get("r6_search_performed") is False and method.get("normal_K1_residual_recovery_performed") is False,
        "environment_direction": bound_vector(record.get("environment_direction", {}).get("T_v"), 14) and bound_record(record.get("environment_direction", {}).get("b_prime_inf_norm_upper_from_B4")) and isinstance(record.get("environment_direction", {}).get("coordinate_projection_bounds"), list) and len(record["environment_direction"]["coordinate_projection_bounds"]) == 14 and bound_record(record.get("environment_direction", {}).get("selected_coordinate_abs_lower")) and lower(record["environment_direction"]["selected_coordinate_abs_lower"]["lower"]) > 0,
        "epsilon_records": epsilon_records_valid(eps, status),
        "summary": summary.get("epsilon_count") == len(builder.EPSILONS) and summary.get("certified_epsilon_count") == certified and summary.get("positive_measure_interval") == builder.S_INTERVAL and bound_record(summary.get("minimum_environment_speed_lower")) and lower(summary["minimum_environment_speed_lower"]["lower"]) > 0 and bound_record(summary.get("environment_direction_lower")) and summary.get("can_enter_b6") == (status == builder.CERTIFIED),
        "scope": scope.get("b4_global_c1_branch_certified") is True and scope.get("positive_measure_nonconstancy_certified") == (status == builder.CERTIFIED) and scope.get("full_path_zero_cost_certified") is False and scope.get("full_r5_certificate_generated") is False and scope.get("r5_certified") is False and scope.get("principle_r_pr_r5_certified") is False and scope.get("principle_r_pr_r6_supplied") is False and scope.get("principle_r_fully_witnessed") is False and scope.get("global_ode_flow_certified") is False and scope.get("r6_search_performed") is False and scope.get("normal_K1_residual_recovery_performed") is False,
        "all_gates_pass": record.get("all_gates_pass") == (status == builder.CERTIFIED),
    }


def mutation_cases(record: dict[str, Any]) -> dict[str, dict[str, Any]]:
    cases = {}
    m = copy.deepcopy(record); m["inputs"]["b4_certificate_artifact_sha256"] = "0" * 64; cases["b4_sha_fails"] = m
    m = copy.deepcopy(record); m["inputs"]["b4_internal_record_sha256"] = "0" * 64; cases["b4_record_sha_fails"] = m
    m = copy.deepcopy(record); m["frozen_protocol"]["epsilon_sequence"] = m["frozen_protocol"]["epsilon_sequence"][:-1]; cases["epsilon_missing_fails"] = m
    m = copy.deepcopy(record); m["frozen_protocol"]["epsilon_sequence"][0] = "2e-14"; cases["epsilon_changed_fails"] = m
    m = copy.deepcopy(record); m["frozen_protocol"]["s_interval"] = ["0", "1"]; cases["interval_changed_fails"] = m
    m = copy.deepcopy(record); m["frozen_protocol"]["fixed_v"] = ["0", "1", "0", "0", "0", "0"]; cases["v_changed_fails"] = m
    m = copy.deepcopy(record); m["epsilon_records"][0]["cosine_lower_bound"]["lower"] = "-1e-30"; cases["cosine_bound_fails"] = m
    m = copy.deepcopy(record); m["epsilon_records"][0]["intrinsic_speed_lower"]["lower"] = "0"; cases["intrinsic_speed_zero_fails"] = m
    m = copy.deepcopy(record); m["environment_direction"]["selected_coordinate_abs_lower"]["lower"] = "-1e-9"; cases["environment_projection_fails"] = m
    m = copy.deepcopy(record); m["epsilon_records"][0]["environment_speed_lower_on_I"]["lower"] = "0"; cases["environment_speed_zero_fails"] = m
    m = copy.deepcopy(record); m["method"]["endpoint_comparison_used"] = True; cases["endpoint_comparison_fails"] = m
    m = copy.deepcopy(record); m["method"]["sampling_used"] = True; cases["sampling_fails"] = m
    m = copy.deepcopy(record); m["method"]["new_observable_introduced"] = True; cases["new_observable_fails"] = m
    m = copy.deepcopy(record); m["method"]["zero_cost_checked"] = True; cases["zero_cost_checked_fails"] = m
    m = copy.deepcopy(record); m["scope"]["full_path_zero_cost_certified"] = True; cases["zero_cost_forged_fails"] = m
    m = copy.deepcopy(record); m["scope"]["r5_certified"] = True; cases["r5_forged_fails"] = m
    m = copy.deepcopy(record); m["scope"]["principle_r_pr_r5_certified"] = True; cases["pr_r5_forged_fails"] = m
    m = copy.deepcopy(record); m["scope"]["principle_r_pr_r6_supplied"] = True; cases["pr_r6_forged_fails"] = m
    m = copy.deepcopy(record); m["scope"]["r6_search_performed"] = True; cases["r6_forged_fails"] = m
    m = copy.deepcopy(record); m["scope"]["normal_K1_residual_recovery_performed"] = True; cases["normal_k1_forged_fails"] = m
    m = copy.deepcopy(record); m["record_sha256"] = "0" * 64; cases["record_sha_fails"] = m
    m = copy.deepcopy(record); m["summary"]["minimum_environment_speed_lower"]["enclosure"] = "NaN"; cases["nan_bound_fails"] = m
    return cases


def run_mutation_tests(record: dict[str, Any], expected: dict[str, Any]) -> dict[str, bool]:
    return {name: not all(verify(case, expected).values()) for name, case in mutation_cases(record).items()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mutation-tests", action="store_true")
    args = parser.parse_args()
    record = read_json(RECORD_PATH)
    expected = builder.build_record()
    checks = verify(record, expected)
    if args.mutation_tests:
        checks.update(run_mutation_tests(record, expected))
    print(json.dumps(checks, indent=2, sort_keys=True))
    if not all(checks.values()):
        print("FAIL")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
