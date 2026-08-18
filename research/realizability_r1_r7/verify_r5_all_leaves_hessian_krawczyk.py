#!/usr/bin/env python3
"""Verify the R5-B2 all-leaves Hessian Krawczyk preflight record."""

from __future__ import annotations

import argparse
import copy
import json
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import certify_r5_all_leaves_hessian_krawczyk as builder
import certify_r5_first_leaf_preflight as preflight


HERE = Path(__file__).resolve().parent
CERT_PATH = HERE / "certificates" / "r5_all_leaves_hessian_krawczyk_v1_0.json"
DIAG_PATH = HERE / "diagnostics" / "r5_all_leaves_hessian_krawczyk_v1_0.json"
RECORD_PATH = CERT_PATH if CERT_PATH.exists() else DIAG_PATH

ARB_RE = re.compile(
    r"^\[(?P<mid>[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?) "
    r"\+/- (?P<rad>(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\]$"
)
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
    return (
        set(value) == required
        and all(decimal_bounds(value[key]) is not None for key in ["enclosure", "lower", "upper", "abs_lower", "abs_upper"])
        and isinstance(value["contains_zero"], bool)
    )


def comparable(value: dict[str, Any]) -> dict[str, Any]:
    return builder.digest_payload(value)


def gates_valid(gates: Any) -> bool:
    return (
        isinstance(gates, dict)
        and set(gates) == {"chart", "no_wrap", "B_inverse", "J_eta_invertible", "self_map", "contraction", "unique_root"}
        and all(isinstance(value, bool) for value in gates.values())
    )


def radius_records_valid(records: Any) -> bool:
    if not isinstance(records, list) or [item.get("r_eta") for item in records] != builder.ETA_RADII:
        return False
    for item in records:
        if not isinstance(item, dict):
            return False
        for key in [
            "Y0_center_residual",
            "Y1_first_order_cancellation_defect",
            "Y2_directional_hessian_lagrange",
            "Y_eta_cross",
            "Y_total",
            "Z",
            "Z_times_r_eta",
            "strict_self_map_margin",
        ]:
            if not bound_record(item.get(key)):
                return False
        if not gates_valid(item.get("gates")):
            return False
        if item.get("Y_eta_cross_policy") != "zero because eta variation is handled by Z*r_eta in the Krawczyk linear term, not by interval-subtracted forcing":
            return False
        gates = item["gates"]
        margin_positive = lower(item["strict_self_map_margin"]["lower"]) > 0
        expected_unique = bool(margin_positive and all(gates[key] for key in ["chart", "no_wrap", "B_inverse", "J_eta_invertible", "contraction"]))
        if gates["unique_root"] != expected_unique:
            return False
    return True


def leaf_records_valid(leaves: Any, status: str) -> bool:
    if not isinstance(leaves, list) or len(leaves) != 16:
        return False
    seen = set()
    all_formal_pass = True
    for expected_index, leaf in enumerate(leaves):
        if not isinstance(leaf, dict):
            return False
        if leaf.get("leaf_index") != expected_index:
            return False
        interval = leaf.get("leaf_interval")
        if interval != builder.LEAVES[expected_index]:
            return False
        key = tuple(interval)
        if key in seen:
            return False
        seen.add(key)
        if leaf.get("endpoint_rule") != "closed interval enclosure; adjacent branch gluing is deferred":
            return False
        if leaf.get("formal_radius") != builder.FORMAL_RADIUS:
            return False
        if leaf.get("formal_radius_status") not in {"CERTIFIED", "SELF_MAP_FAILED", "CONTRACTION_FAILED", "CHART_FAILED", "NO_WRAP_FAILED", "JACOBIAN_FAILED", "IMPLEMENTATION_ERROR", "INCONCLUSIVE"}:
            return False
        for key_name in ["alpha_radius", "P_F_at_center_inf_norm", "H_alpha", "Y0", "Y1", "Y2"]:
            if not bound_record(leaf.get(key_name)):
                return False
        for key_name, expected_len in [("b_C", 8), ("S", 8), ("w", 14)]:
            if not isinstance(leaf.get(key_name), list) or len(leaf[key_name]) != expected_len:
                return False
            if not all(bound_record(item) for item in leaf[key_name]):
                return False
        components = leaf.get("directional_hessian_components")
        if not isinstance(components, list) or len(components) != 8:
            return False
        if [item.get("component") for item in components] != list(range(8)):
            return False
        for component in components:
            for key_name in ["raw_D2R3_ww", "after_B", "after_P", "lagrange_contribution_bound"]:
                if not bound_record(component.get(key_name)):
                    return False
        if not radius_records_valid(leaf.get("radius_records")):
            return False
        formal = leaf.get("formal_radius_record")
        if not isinstance(formal, dict) or formal.get("r_eta") != builder.FORMAL_RADIUS:
            return False
        if not gates_valid(formal.get("gates")):
            return False
        if formal["gates"]["unique_root"] != (leaf.get("formal_radius_status") == "CERTIFIED"):
            return False
        all_formal_pass = all_formal_pass and formal["gates"]["unique_root"]
    return all_formal_pass == (status == builder.CERTIFIED)


def verify(record: dict[str, Any], expected: dict[str, Any] | None = None) -> dict[str, bool]:
    if expected is None:
        expected = builder.build_record()
    status = record.get("scientific_status")
    inputs = record.get("inputs", {})
    protocol = record.get("frozen_protocol", {})
    method = record.get("method", {})
    summary = record.get("summary", {})
    scope = record.get("scope", {})
    leaves = record.get("leaf_records")
    certified_count = sum(1 for leaf in leaves if isinstance(leaf, dict) and leaf.get("formal_radius_status") == "CERTIFIED") if isinstance(leaves, list) else -1

    checks = {
        "record_matches_recomputed_arb_record": comparable(record) == comparable(expected),
        "record_sha256": record.get("record_sha256") == builder.sha256_bytes(builder.canonical_json(comparable(record))),
        "schema_version": record.get("schema_version") == "1.0",
        "record_id": record.get("record_id") == "r5_all_leaves_hessian_krawczyk_v1_0",
        "record_kind": record.get("record_kind") == "prospective_r5_b2_all_leaves_hessian_krawczyk_preflight",
        "scientific_status_allowed": status in builder.ALLOWED_STATUSES,
        "scientific_status_consistent": (
            (status == builder.CERTIFIED and certified_count == 16)
            or (status == builder.NOT_CERTIFIED and 0 <= certified_count < 16)
            or status in {builder.INCONCLUSIVE, builder.BOUNDARY_MISMATCH, builder.IMPLEMENTATION_ERROR}
        ),
        "arb_precision": record.get("arb_precision_bits") == 192,
        "base_commit": record.get("base_commit") == builder.EXPECTED_BASE_COMMIT,
        "input_hashes": (
            inputs.get("parent_protocol_sha256") == preflight.EXPECTED_PARENT_PROTOCOL_SHA256
            and inputs.get("protocol_sha256") == preflight.EXPECTED_PROTOCOL_SHA256
            and inputs.get("auxiliary_sha256") == preflight.EXPECTED_AUXILIARY_SHA256
            and inputs.get("static_certificate_sha256") == preflight.EXPECTED_STATIC_CERT_SHA256
            and inputs.get("b1e_certificate_sha256") == builder.EXPECTED_B1E_CERT_SHA256
            and inputs.get("affine_diagnostic_sha256") == builder.EXPECTED_AFFINE_DIAG_SHA256
            and inputs.get("v0_7_4_source_sha256") == preflight.EXPECTED_V074_SOURCE_SHA256
            and inputs.get("object_sha256") == preflight.EXPECTED_OBJECT_SHA256
        ),
        "frozen_protocol": (
            protocol.get("leaf_list") == builder.LEAVES
            and protocol.get("leaf_order") == "increasing t from -1e-12 to 1e-12"
            and protocol.get("endpoint_rule") == "closed Arb intervals per leaf; overlap consistency deferred to B3"
            and protocol.get("center_rule") == "a_C=(left+right)/2"
            and protocol.get("normal_center_rule") == "b_C=-P*F(a_C,0) using frozen P and zero normal seed"
            and protocol.get("fixed_slope_source") == "B1c/B1e S reused for every leaf without refit"
            and protocol.get("formal_eta_radius") == builder.FORMAL_RADIUS
            and protocol.get("eta_radii_predeclared") == builder.ETA_RADII
            and protocol.get("precision_bits") == 192
            and protocol.get("result_adaptive_changes_allowed") is False
        ),
        "method": (
            method.get("equation") == "F_i(alpha,eta)=B(R3(theta_C,i+(T*v+N*S)*alpha+N*eta)-c)"
            and method.get("w_definition") == "w=T*v+N*S"
            and method.get("Y_total_decomposition") == "Y0+Y1+Y2+Y_eta_cross"
            and method.get("Y2_source") == "explicit directional-Hessian Lagrange remainder computed per leaf"
            and method.get("B1c_interval_subtraction_used_as_Y2") is False
            and method.get("finite_difference_used_as_strict_bound") is False
            and method.get("binary64_theorem_decision_used") is False
            and method.get("one_half_factor_included") is True
            and method.get("alpha_radius_squared_included") is True
            and method.get("Y_eta_cross_included") is True
            and method.get("eta_variation_handled_by_Z_times_radius") is True
        ),
        "leaf_records": leaf_records_valid(leaves, status),
        "summary": (
            summary.get("leaf_count") == 16
            and summary.get("certified_leaf_count") == certified_count
            and summary.get("worst_leaf_by_formal_self_map_margin") in range(16)
            and bound_record(summary.get("minimum_formal_self_map_margin"))
            and summary.get("max_Y2_leaf") in range(16)
            and bound_record(summary.get("max_Y2_abs_upper"))
            and summary.get("max_Z_leaf_at_formal_radius") in range(16)
            and bound_record(summary.get("max_Z_abs_upper_at_formal_radius"))
            and isinstance(summary.get("endpoint_or_branch_anomaly_detected"), bool)
            and summary.get("can_enter_B3_gluing") == (status == builder.CERTIFIED)
        ),
        "scope": (
            scope.get("all_leaf_local_root_gates_pass") == (status == builder.CERTIFIED)
            and scope.get("r5_all_leaves_locally_certified") == (status == builder.CERTIFIED)
            and scope.get("adjacent_leaf_gluing_certified") is False
            and scope.get("full_path_continuity_certified") is False
            and scope.get("positive_measure_nonconstancy_certified") is False
            and scope.get("zero_cost_full_path_certified") is False
            and scope.get("principle_r_r6_supplied") is False
            and scope.get("r5_certified") is False
            and scope.get("global_ode_flow_certified") is False
            and scope.get("r6_search_performed") is False
            and scope.get("normal_K1_residual_recovery_performed") is False
            and scope.get("other_leaf_inspected_outside_frozen_16") is False
        ),
    }
    return checks


def mutation_cases(record: dict[str, Any]) -> dict[str, dict[str, Any]]:
    cases: dict[str, dict[str, Any]] = {}
    mutated = copy.deepcopy(record); mutated["frozen_protocol"]["leaf_list"][0] = ["-1e-12", "-9e-13"]; cases["leaf_endpoint_change_fails"] = mutated
    mutated = copy.deepcopy(record); mutated["frozen_protocol"]["leaf_list"][0], mutated["frozen_protocol"]["leaf_list"][1] = mutated["frozen_protocol"]["leaf_list"][1], mutated["frozen_protocol"]["leaf_list"][0]; cases["leaf_order_change_fails"] = mutated
    mutated = copy.deepcopy(record); mutated["leaf_records"][1] = copy.deepcopy(mutated["leaf_records"][0]); cases["duplicate_leaf_fails"] = mutated
    mutated = copy.deepcopy(record); mutated["leaf_records"] = mutated["leaf_records"][:-1]; cases["missing_leaf_fails"] = mutated
    mutated = copy.deepcopy(record); mutated["inputs"]["b1e_certificate_sha256"] = "0" * 64; cases["b1e_sha_change_fails"] = mutated
    mutated = copy.deepcopy(record); mutated["leaf_records"][0]["Y2"]["abs_upper"] = "1e-99"; cases["hessian_bound_tamper_fails"] = mutated
    mutated = copy.deepcopy(record); mutated["method"]["one_half_factor_included"] = False; cases["missing_half_factor_fails"] = mutated
    mutated = copy.deepcopy(record); mutated["frozen_protocol"]["formal_eta_radius"] = "1e-22"; cases["formal_radius_change_fails"] = mutated
    mutated = copy.deepcopy(record); mutated["leaf_records"][0]["formal_radius_record"]["strict_self_map_margin"]["lower"] = "-1e-30"; cases["self_map_margin_tamper_fails"] = mutated
    mutated = copy.deepcopy(record); mutated["leaf_records"][0]["formal_radius_record"]["contraction_upper"] = "2"; cases["contraction_bound_tamper_fails"] = mutated
    mutated = copy.deepcopy(record); mutated["leaf_records"][0]["formal_radius_record"]["gates"]["unique_root"] = False; cases["unique_root_false_fails"] = mutated
    mutated = copy.deepcopy(record); mutated["scope"]["r5_certified"] = True; cases["local_success_as_r5_certified_fails"] = mutated
    mutated = copy.deepcopy(record); mutated["scope"]["principle_r_r6_supplied"] = True; cases["principle_r_r6_forged_fails"] = mutated
    mutated = copy.deepcopy(record); mutated["scope"]["global_ode_flow_certified"] = True; cases["global_flow_forged_fails"] = mutated
    mutated = copy.deepcopy(record); mutated["scope"]["r6_search_performed"] = True; cases["R6_marked_run_fails"] = mutated
    mutated = copy.deepcopy(record); mutated["scope"]["normal_K1_residual_recovery_performed"] = True; cases["normal_K1_marked_run_fails"] = mutated
    mutated = copy.deepcopy(record); mutated["method"]["B1c_interval_subtraction_used_as_Y2"] = True; cases["interval_subtraction_reintroduced_fails"] = mutated
    mutated = copy.deepcopy(record); mutated["method"]["Y_eta_cross_included"] = False; cases["missing_Y_eta_cross_fails"] = mutated
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
