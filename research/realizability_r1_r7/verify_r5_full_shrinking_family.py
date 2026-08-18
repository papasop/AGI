#!/usr/bin/env python3
"""Verify the R5-B6 full shrinking-family record."""

from __future__ import annotations

import argparse
import copy
import json
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import certify_r5_full_shrinking_family as builder
import certify_r5_first_leaf_preflight as preflight


HERE = Path(__file__).resolve().parent
CERT_PATH = HERE / "certificates" / "r5_full_shrinking_family_v1_0.json"
DIAG_PATH = HERE / "diagnostics" / "r5_full_shrinking_family_v1_0.json"
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


def upper(value: Any) -> Decimal:
    bounds = decimal_bounds(value)
    if bounds is None:
        raise ValueError(value)
    return bounds[1]


def bound_record(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    required = {"enclosure", "lower", "upper", "abs_lower", "abs_upper", "contains_zero"}
    return set(value) == required and isinstance(value["contains_zero"], bool) and all(
        decimal_bounds(value[key]) is not None for key in ["enclosure", "lower", "upper", "abs_lower", "abs_upper"]
    )


def comparable(value: dict[str, Any]) -> dict[str, Any]:
    return builder.digest_payload(value)


def zero_bound(value: Any) -> bool:
    return bound_record(value) and lower(value["lower"]) == 0 and upper(value["upper"]) == 0 and value["contains_zero"] is True


def loop_gates_valid(gates: Any) -> bool:
    required = {
        "epsilon_positive",
        "epsilon_in_frozen_sequence",
        "loop_range_inside_full_tube",
        "closed_tube_endpoint_equality_allowed",
        "b4_exact_response_identity_available",
        "b5_positive_measure_nonconstancy_available",
        "zero_cost_uses_exact_identity_not_residual",
        "sampled_residual_used",
        "binary64_theorem_decision_used",
        "epsilon_full_shrinking_loop_certified",
    }
    if not isinstance(gates, dict) or set(gates) != required or not all(isinstance(value, bool) for value in gates.values()):
        return False
    expected = (
        all(gates[key] for key in required - {"closed_tube_endpoint_equality_allowed", "sampled_residual_used", "binary64_theorem_decision_used", "epsilon_full_shrinking_loop_certified"})
        and gates["sampled_residual_used"] is False
        and gates["binary64_theorem_decision_used"] is False
    )
    return gates["epsilon_full_shrinking_loop_certified"] == expected


def loop_records_valid(records: Any, status: str) -> bool:
    if not isinstance(records, list) or [item.get("epsilon") for item in records] != builder.EPSILONS:
        return False
    certified = 0
    for item in records:
        eps = Decimal(item["epsilon"])
        if not eps.is_finite() or eps <= 0:
            return False
        if item.get("full_tube") != builder.FULL_TUBE:
            return False
        if item.get("loop_t_range") != [f"-{item['epsilon']}", item["epsilon"]]:
            return False
        if not bound_record(item.get("tube_subset_margin")) or lower(item["tube_subset_margin"]["lower"]) < 0:
            return False
        if item["gates"]["closed_tube_endpoint_equality_allowed"] != (lower(item["tube_subset_margin"]["lower"]) == 0 and upper(item["tube_subset_margin"]["upper"]) == 0):
            return False
        if item.get("positive_measure_interval") != ["0", "1/12"]:
            return False
        if not bound_record(item.get("environment_speed_lower_on_I")) or lower(item["environment_speed_lower_on_I"]["lower"]) <= 0:
            return False
        if item.get("response_identity_statement") != "R3(theta_epsilon(s))=R3(theta_0) exactly on the certified B4 branch":
            return False
        if not zero_bound(item.get("response_cost_bound")) or not zero_bound(item.get("total_response_cost_bound")):
            return False
        if not loop_gates_valid(item.get("gates")):
            return False
        if (item.get("epsilon_status") == "EPSILON_ZERO_COST_NONCONSTANT_LOOP_CERTIFIED") != item["gates"]["epsilon_full_shrinking_loop_certified"]:
            return False
        certified += int(item["gates"]["epsilon_full_shrinking_loop_certified"])
    return (certified == len(builder.EPSILONS)) == (status == builder.CERTIFIED)


def verify(record: dict[str, Any], expected: dict[str, Any] | None = None) -> dict[str, bool]:
    if expected is None:
        expected = builder.build_record()
    status = record.get("scientific_status")
    inputs = record.get("inputs", {})
    protocol = record.get("frozen_protocol", {})
    logic = record.get("exact_response_identity_logic", {})
    scope = record.get("scope", {})
    summary = record.get("summary", {})
    loops = record.get("epsilon_loop_records")
    certified = sum(1 for item in loops if isinstance(item, dict) and item.get("gates", {}).get("epsilon_full_shrinking_loop_certified") is True) if isinstance(loops, list) else -1
    return {
        "record_matches_recomputed_arb_record": comparable(record) == comparable(expected),
        "record_sha256": record.get("record_sha256") == builder.sha256_bytes(builder.canonical_json(comparable(record))),
        "schema_version": record.get("schema_version") == "1.0",
        "record_id": record.get("record_id") == "r5_full_shrinking_family_v1_0",
        "record_kind": record.get("record_kind") == "prospective_gf_r5_full_shrinking_family_certificate",
        "stage": record.get("stage") == "R5-B6",
        "scientific_status_allowed": status in builder.ALLOWED_STATUSES,
        "scientific_status_consistent": (status == builder.CERTIFIED and certified == len(builder.EPSILONS)) or (status == builder.NOT_CERTIFIED and certified < len(builder.EPSILONS)) or status in {builder.INCONCLUSIVE, builder.BOUNDARY_MISMATCH, builder.IMPLEMENTATION_ERROR},
        "arb_precision": record.get("arb_precision_bits") == 192,
        "base_commit": record.get("base_commit") == builder.EXPECTED_BASE_COMMIT,
        "input_hashes": inputs.get("parent_protocol_sha256") == preflight.EXPECTED_PARENT_PROTOCOL_SHA256 and inputs.get("protocol_sha256") == preflight.EXPECTED_PROTOCOL_SHA256 and inputs.get("auxiliary_sha256") == preflight.EXPECTED_AUXILIARY_SHA256 and inputs.get("b4_certificate_artifact_sha256") == builder.EXPECTED_B4_CERT_SHA256 and inputs.get("b4_internal_record_sha256") == builder.EXPECTED_B4_RECORD_SHA256 and inputs.get("b5_certificate_artifact_sha256") == builder.EXPECTED_B5_CERT_SHA256 and inputs.get("b5_internal_record_sha256") == builder.EXPECTED_B5_RECORD_SHA256 and inputs.get("object_sha256") == preflight.EXPECTED_OBJECT_SHA256,
        "frozen_protocol": protocol.get("epsilon_sequence") == builder.EPSILONS and protocol.get("full_tube") == builder.FULL_TUBE and protocol.get("fixed_v") == ["1", "0", "0", "0", "0", "0"] and protocol.get("curve_family") == "a_epsilon(s)=epsilon*sin(2*pi*s)*v" and "W_Pi=I_8" in protocol.get("response_cost_meter", "") and protocol.get("result_adaptive_changes_allowed") is False,
        "exact_response_identity_logic": logic.get("physical_equation") == "F(t,b)=B*(R3(theta_0+T*(t*v)+N*b)-c)" and logic.get("B_strictly_invertible_source") == "R5-B0/R5-B4 Arb inverse gates" and logic.get("implicit_graph_source") == "R5-B4 global C1 implicit branch" and isinstance(logic.get("required_steps"), list) and len(logic["required_steps"]) == 5 and logic.get("forbidden_substitute") == "residual interval contains zero" and logic.get("residual_tolerance_used") is False and logic.get("sampled_residual_used") is False and logic.get("exact_response_identity_certified") == (status == builder.CERTIFIED) and logic.get("zero_response_derivative_certified") == (status == builder.CERTIFIED) and logic.get("zero_protocol_relative_response_cost_certified") == (status == builder.CERTIFIED),
        "epsilon_loop_records": loop_records_valid(loops, status),
        "summary": summary.get("epsilon_count") == len(builder.EPSILONS) and summary.get("certified_zero_cost_nonconstant_epsilon_count") == certified and summary.get("weakest_epsilon") == "1e-14" and bound_record(summary.get("minimum_environment_speed_lower")) and lower(summary["minimum_environment_speed_lower"]["lower"]) > 0 and zero_bound(summary.get("minimum_total_response_cost_upper")) and zero_bound(summary.get("maximum_total_response_cost_upper")) and summary.get("all_loops_inside_full_tube") is True and summary.get("full_path_zero_cost_certified") == (status == builder.CERTIFIED) and summary.get("positive_measure_nonconstancy_certified") is True and summary.get("gf_r5_shrinking_family_certified") == (status == builder.CERTIFIED),
        "scope": scope.get("b4_global_c1_branch_certified") is True and scope.get("b5_positive_measure_nonconstancy_certified") is True and scope.get("full_path_response_identity_certified") == (status == builder.CERTIFIED) and scope.get("zero_response_derivative_certified") == (status == builder.CERTIFIED) and scope.get("full_path_zero_response_cost_certified") == (status == builder.CERTIFIED) and scope.get("positive_measure_nonconstancy_certified") == (status == builder.CERTIFIED) and scope.get("gf_r5_shrinking_family_certified") == (status == builder.CERTIFIED) and scope.get("full_r5_certificate_generated") == (status == builder.CERTIFIED) and scope.get("r5_certified") == (status == builder.CERTIFIED) and scope.get("principle_r_pr_r5_certified") is False and scope.get("principle_r_pr_r6_supplied") is False and scope.get("principle_r_fully_witnessed") is False and scope.get("global_ode_flow_certified") is False and scope.get("r6_search_performed") is False and scope.get("normal_K1_residual_recovery_performed") is False and scope.get("published_theorem_boundary_modified") is False,
        "all_gates_pass": record.get("all_gates_pass") == (status == builder.CERTIFIED),
    }


def mutation_cases(record: dict[str, Any]) -> dict[str, dict[str, Any]]:
    cases = {}
    m = copy.deepcopy(record); m["inputs"]["b4_certificate_artifact_sha256"] = "0" * 64; cases["b4_artifact_sha_fails"] = m
    m = copy.deepcopy(record); m["inputs"]["b5_certificate_artifact_sha256"] = "0" * 64; cases["b5_artifact_sha_fails"] = m
    m = copy.deepcopy(record); m["inputs"]["b5_internal_record_sha256"] = "0" * 64; cases["b5_record_sha_fails"] = m
    m = copy.deepcopy(record); m["frozen_protocol"]["epsilon_sequence"] = m["frozen_protocol"]["epsilon_sequence"][:-1]; cases["epsilon_missing_fails"] = m
    m = copy.deepcopy(record); m["epsilon_loop_records"][0]["loop_t_range"] = ["0", "1e-14"]; cases["loop_range_tamper_fails"] = m
    m = copy.deepcopy(record); m["epsilon_loop_records"][0]["tube_subset_margin"]["lower"] = "-1e-30"; cases["tube_subset_margin_fails"] = m
    m = copy.deepcopy(record); m["exact_response_identity_logic"]["forbidden_substitute"] = "residual interval contains zero is enough"; cases["residual_zero_substitute_fails"] = m
    m = copy.deepcopy(record); m["exact_response_identity_logic"]["residual_tolerance_used"] = True; cases["residual_tolerance_fails"] = m
    m = copy.deepcopy(record); m["exact_response_identity_logic"]["sampled_residual_used"] = True; cases["sampled_residual_fails"] = m
    m = copy.deepcopy(record); m["epsilon_loop_records"][0]["response_cost_bound"]["upper"] = "1e-30"; cases["nonzero_response_cost_fails"] = m
    m = copy.deepcopy(record); m["epsilon_loop_records"][0]["total_response_cost_bound"]["upper"] = "1e-30"; cases["nonzero_total_cost_fails"] = m
    m = copy.deepcopy(record); m["epsilon_loop_records"][0]["environment_speed_lower_on_I"]["lower"] = "0"; cases["nonconstancy_lower_zero_fails"] = m
    m = copy.deepcopy(record); m["epsilon_loop_records"][0]["gates"]["b5_positive_measure_nonconstancy_available"] = False; cases["b5_nonconstancy_removed_fails"] = m
    m = copy.deepcopy(record); m["epsilon_loop_records"][0]["gates"]["zero_cost_uses_exact_identity_not_residual"] = False; cases["exact_identity_gate_removed_fails"] = m
    m = copy.deepcopy(record); m["epsilon_loop_records"][0]["gates"]["sampled_residual_used"] = True; cases["sampled_loop_gate_fails"] = m
    m = copy.deepcopy(record); m["scope"]["principle_r_pr_r5_certified"] = True; cases["pr_r5_forged_fails"] = m
    m = copy.deepcopy(record); m["scope"]["principle_r_pr_r6_supplied"] = True; cases["pr_r6_forged_fails"] = m
    m = copy.deepcopy(record); m["scope"]["global_ode_flow_certified"] = True; cases["global_flow_forged_fails"] = m
    m = copy.deepcopy(record); m["scope"]["r6_search_performed"] = True; cases["r6_forged_fails"] = m
    m = copy.deepcopy(record); m["scope"]["normal_K1_residual_recovery_performed"] = True; cases["normal_k1_forged_fails"] = m
    m = copy.deepcopy(record); m["scope"]["published_theorem_boundary_modified"] = True; cases["published_boundary_modified_fails"] = m
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
