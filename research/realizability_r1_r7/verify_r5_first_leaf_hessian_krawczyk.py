#!/usr/bin/env python3
"""Verify the R5-B1e first-leaf affine-Hessian Krawczyk record."""

from __future__ import annotations

import argparse
import copy
import json
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import certify_r5_first_leaf_hessian_krawczyk as builder
import certify_r5_first_leaf_preflight as preflight


HERE = Path(__file__).resolve().parent
CERT_PATH = HERE / "certificates" / "r5_first_leaf_hessian_krawczyk_v1_0.json"
DIAG_PATH = HERE / "diagnostics" / "r5_first_leaf_hessian_krawczyk_v1_0.json"
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


def radius_records_valid(records: Any, status: str) -> bool:
    if not isinstance(records, list) or [item.get("r_eta") for item in records] != builder.ETA_RADII:
        return False
    any_unique = False
    for index, item in enumerate(records):
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
        gates = item.get("gates", {})
        if set(gates) != {"chart", "no_wrap", "B_inverse", "J_eta_invertible", "self_map", "contraction", "unique_root"}:
            return False
        if not all(isinstance(value, bool) for value in gates.values()):
            return False
        if item.get("Y_eta_cross_policy") != "zero because eta variation is handled by Z*r_eta in the Krawczyk linear term, not by interval-subtracted forcing":
            return False
        margin_positive = lower(item["strict_self_map_margin"]["lower"]) > 0
        expected_unique = bool(margin_positive and all(gates[key] for key in ["chart", "no_wrap", "B_inverse", "J_eta_invertible", "contraction"]))
        if gates["unique_root"] != expected_unique:
            return False
        any_unique = any_unique or gates["unique_root"]
        if index < 2 and gates["unique_root"]:
            return False
    return any_unique == (status == builder.CERTIFIED)


def verify(record: dict[str, Any]) -> dict[str, bool]:
    expected = builder.build_record()
    method = record.get("method", {})
    frozen = record.get("frozen_scope", {})
    inputs = record.get("inputs", {})
    scope = record.get("scope", {})
    global_q = record.get("global_quantities", {})
    status = record.get("scientific_status")
    records = record.get("radius_records")
    certified_radii = [item.get("r_eta") for item in records if isinstance(item, dict) and item.get("gates", {}).get("unique_root") is True] if isinstance(records, list) else []
    checks = {
        "record_matches_recomputed_arb_record": comparable(record) == comparable(expected),
        "record_sha256": record.get("record_sha256") == builder.sha256_bytes(builder.canonical_json(comparable(record))),
        "schema_version": record.get("schema_version") == "1.0",
        "record_id": record.get("record_id") == "r5_first_leaf_hessian_krawczyk_v1_0",
        "record_kind": record.get("record_kind") == "prospective_r5_b1e_first_leaf_hessian_krawczyk",
        "scientific_status_allowed": status in builder.ALLOWED_STATUSES,
        "scientific_status_consistent": status == builder.CERTIFIED and certified_radii == ["1e-26", "1e-24", "1e-23", "1e-22", "1e-20"],
        "arb_precision": record.get("arb_precision_bits") == 192,
        "base_commit": record.get("base_commit") == builder.EXPECTED_BASE_COMMIT,
        "input_hashes": (
            inputs.get("parent_protocol_sha256") == preflight.EXPECTED_PARENT_PROTOCOL_SHA256
            and inputs.get("protocol_sha256") == preflight.EXPECTED_PROTOCOL_SHA256
            and inputs.get("auxiliary_sha256") == preflight.EXPECTED_AUXILIARY_SHA256
            and inputs.get("static_certificate_sha256") == preflight.EXPECTED_STATIC_CERT_SHA256
            and inputs.get("first_leaf_preflight_sha256") == builder.EXPECTED_PREFLIGHT_CERT_SHA256
            and inputs.get("center_diagnostic_sha256") == builder.EXPECTED_CENTER_DIAG_SHA256
            and inputs.get("affine_diagnostic_sha256") == builder.EXPECTED_AFFINE_DIAG_SHA256
            and inputs.get("second_order_remainder_diagnostic_sha256") == builder.EXPECTED_B1D_DIAG_SHA256
            and inputs.get("v0_7_4_source_sha256") == preflight.EXPECTED_V074_SOURCE_SHA256
            and inputs.get("object_sha256") == preflight.EXPECTED_OBJECT_SHA256
        ),
        "frozen_scope": (
            frozen.get("leaf_index") == 0
            and frozen.get("leaf_interval") == preflight.LEAF_INTERVAL
            and frozen.get("theta_0_T_N_B_c_P_v_preserved") is True
            and frozen.get("b_C_from_B1c_preserved") is True
            and frozen.get("S_from_B1c_preserved") is True
            and frozen.get("eta_radii_predeclared") == builder.ETA_RADII
            and frozen.get("full_tube_protocol_modified") is False
        ),
        "method": (
            method.get("equation") == "F(a,eta)=B(R3(theta0+T*(a*v)+N*(b_C+S*alpha+eta))-c)"
            and method.get("w_definition") == "w=T*v+N*S"
            and method.get("Y_total_decomposition") == "Y0+Y1+Y2+Y_eta_cross"
            and method.get("Y2_source") == "B1d explicit directional-Hessian Lagrange remainder"
            and method.get("B1c_interval_subtraction_used_as_Y2") is False
            and method.get("finite_difference_used_as_strict_bound") is False
            and method.get("binary64_theorem_decision_used") is False
            and method.get("one_half_factor_included") is True
            and method.get("alpha_radius_squared_included") is True
            and method.get("Y_eta_cross_included") is True
            and method.get("eta_variation_handled_by_Z_times_radius") is True
        ),
        "global_quantities": (
            bound_record(global_q.get("alpha_radius"))
            and isinstance(global_q.get("b_C"), list)
            and len(global_q.get("b_C")) == 8
            and isinstance(global_q.get("S"), list)
            and len(global_q.get("S")) == 8
            and isinstance(global_q.get("w"), list)
            and len(global_q.get("w")) == 14
            and bound_record(global_q.get("Y0"))
            and bound_record(global_q.get("Y1"))
            and bound_record(global_q.get("Y2"))
            and upper(global_q["Y2"]["abs_upper"]) < Decimal("1e-20")
        ),
        "radius_records": radius_records_valid(records, status),
        "scope": (
            scope.get("first_leaf_only") is True
            and scope.get("first_leaf_gates_pass") is True
            and scope.get("r5_first_leaf_certified") is True
            and scope.get("r5_full_tube_certificate_generated") is False
            and scope.get("r5_certified") is False
            and scope.get("all_gates_pass") is False
            and scope.get("r6_search_performed") is False
            and scope.get("normal_K1_residual_recovery_performed") is False
            and scope.get("other_leaf_inspected") is False
        ),
    }
    return checks


def mutation_cases(record: dict[str, Any]) -> dict[str, dict[str, Any]]:
    cases: dict[str, dict[str, Any]] = {}
    mutated = copy.deepcopy(record); mutated["frozen_scope"]["leaf_index"] = 1; cases["leaf_index_change_fails"] = mutated
    mutated = copy.deepcopy(record); mutated["frozen_scope"]["leaf_interval"] = ["-1e-12", "-9e-13"]; cases["leaf_interval_change_fails"] = mutated
    mutated = copy.deepcopy(record); mutated["inputs"]["object_sha256"]["T"] = "0" * 64; cases["object_sha_change_fails"] = mutated
    mutated = copy.deepcopy(record); mutated["global_quantities"]["b_C"][0] = "0"; cases["b_C_change_fails"] = mutated
    mutated = copy.deepcopy(record); mutated["global_quantities"]["S"][0] = "0"; cases["S_change_fails"] = mutated
    mutated = copy.deepcopy(record); mutated["method"]["B1c_interval_subtraction_used_as_Y2"] = True; cases["B1c_remainder_as_Y2_fails"] = mutated
    mutated = copy.deepcopy(record); mutated["method"]["one_half_factor_included"] = False; cases["missing_half_factor_fails"] = mutated
    mutated = copy.deepcopy(record); mutated["method"]["alpha_radius_squared_included"] = False; cases["missing_alpha_squared_fails"] = mutated
    mutated = copy.deepcopy(record); mutated["method"]["w_definition"] = "w=T*v"; cases["missing_NS_in_w_fails"] = mutated
    mutated = copy.deepcopy(record); mutated["method"]["w_definition"] = "w=N*S"; cases["missing_Tv_in_w_fails"] = mutated
    mutated = copy.deepcopy(record); mutated["method"]["Y_eta_cross_included"] = False; cases["missing_Y_eta_cross_fails"] = mutated
    mutated = copy.deepcopy(record); mutated["method"]["finite_difference_used_as_strict_bound"] = True; cases["finite_difference_strict_bound_fails"] = mutated
    mutated = copy.deepcopy(record); mutated["method"]["binary64_theorem_decision_used"] = True; cases["binary64_gate_fails"] = mutated
    mutated = copy.deepcopy(record); mutated["radius_records"] = mutated["radius_records"][2:]; cases["hidden_failed_radii_fails"] = mutated
    mutated = copy.deepcopy(record); mutated["frozen_scope"]["eta_radii_predeclared"].append("1e-18"); cases["posthoc_radius_fails"] = mutated
    mutated = copy.deepcopy(record); mutated["scope"]["all_gates_pass"] = True; cases["full_r5_all_gates_forged_fails"] = mutated
    mutated = copy.deepcopy(record); mutated["scope"]["r5_certified"] = True; cases["first_leaf_as_full_r5_fails"] = mutated
    mutated = copy.deepcopy(record); mutated["scope"]["r6_search_performed"] = True; cases["R6_marked_run_fails"] = mutated
    mutated = copy.deepcopy(record); mutated["scope"]["normal_K1_residual_recovery_performed"] = True; cases["normal_K1_marked_run_fails"] = mutated
    mutated = copy.deepcopy(record); mutated["inputs"]["second_order_remainder_diagnostic_sha256"] = "f" * 64; cases["input_sha_tamper_fails"] = mutated
    return cases


def run_mutation_tests(record: dict[str, Any]) -> dict[str, bool]:
    return {name: not all(verify(case).values()) for name, case in mutation_cases(record).items()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mutation-tests", action="store_true")
    args = parser.parse_args()
    record = read_json(RECORD_PATH)
    checks = verify(record)
    if args.mutation_tests:
        checks.update(run_mutation_tests(record))
    print(json.dumps(checks, indent=2, sort_keys=True))
    if not all(checks.values()):
        print("FAIL")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
