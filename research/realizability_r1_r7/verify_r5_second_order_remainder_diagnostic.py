#!/usr/bin/env python3
"""Verify the R5-B1d second-order remainder provenance diagnostic."""

from __future__ import annotations

import argparse
import copy
import json
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import certify_r5_first_leaf_preflight as preflight
import diagnose_r5_first_leaf_affine as affine_builder
import diagnose_r5_second_order_remainder as b1d_builder


HERE = Path(__file__).resolve().parent
DIAGNOSTIC_PATH = HERE / "diagnostics" / "r5_second_order_remainder_diagnostic_v1_0.json"

ARB_RE = re.compile(
    r"^\[(?P<mid>[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?) "
    r"\+/- (?P<rad>(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\]$"
)
ZERO_ARB_RE = re.compile(
    r"^\[\+/- (?P<rad>(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\]$"
)


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
            try:
                mid = Decimal(match.group("mid"))
                rad = Decimal(match.group("rad"))
            except (InvalidOperation, ValueError, OverflowError):
                return None
        else:
            zero_match = ZERO_ARB_RE.match(value)
            if not zero_match:
                return None
            try:
                mid = Decimal("0")
                rad = Decimal(zero_match.group("rad"))
            except (InvalidOperation, ValueError, OverflowError):
                return None
        lower = mid - rad
        upper = mid + rad
    else:
        lower = parsed
        upper = parsed
    if not lower.is_finite() or not upper.is_finite() or lower > upper:
        return None
    return lower, upper


def upper(value: Any) -> Decimal:
    bounds = decimal_bounds(value)
    if bounds is None:
        raise ValueError(f"not a finite decimal/Arb bound: {value!r}")
    return bounds[1]


def finite_bound(value: Any) -> bool:
    return decimal_bounds(value) is not None


def bound_record(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    required = {"enclosure", "lower", "upper", "abs_lower", "abs_upper", "contains_zero"}
    return (
        set(value) == required
        and finite_bound(value["enclosure"])
        and finite_bound(value["lower"])
        and finite_bound(value["upper"])
        and finite_bound(value["abs_lower"])
        and finite_bound(value["abs_upper"])
        and isinstance(value["contains_zero"], bool)
    )


def bound_vector(value: Any, length: int = 8) -> bool:
    return isinstance(value, list) and len(value) == length and all(bound_record(item) for item in value)


def comparable(value: dict[str, Any]) -> dict[str, Any]:
    return b1d_builder.diagnostic_digest_payload(value)


def no_certificate_claim(value: Any) -> bool:
    if isinstance(value, str):
        return "CERTIFICATE" not in value and "CERTIFIED" not in value
    if isinstance(value, dict):
        return all(no_certificate_claim(item) for item in value.values())
    if isinstance(value, list):
        return all(no_certificate_claim(item) for item in value)
    return True


def verify(diagnostic: dict[str, Any]) -> dict[str, bool]:
    expected = b1d_builder.build_diagnostic()
    inputs = diagnostic.get("inputs", {})
    provenance = diagnostic.get("code_provenance", {})
    hessian = diagnostic.get("analytic_directional_hessian", {})
    comparison = diagnostic.get("b1c_remainder_comparison", {})
    cross = diagnostic.get("three_point_cross_check", {})
    components = diagnostic.get("component_sources", {})
    decision = diagnostic.get("decision", {})
    scope = diagnostic.get("scope", {})

    records = components.get("records")
    ratio_upper = upper(comparison.get("B1c_reported_over_true_Y2", {}).get("abs_upper", "0")) if bound_record(comparison.get("B1c_reported_over_true_Y2")) else Decimal("0")
    true_y2_upper = upper(hessian.get("Y2_true_lagrange_bound", {}).get("abs_upper", "Infinity")) if bound_record(hessian.get("Y2_true_lagrange_bound")) else Decimal("Infinity")

    checks = {
        "diagnostic_matches_recomputed_arb_diagnostic": comparable(diagnostic) == comparable(expected),
        "diagnostic_sha256": (
            diagnostic.get("diagnostic_sha256")
            == b1d_builder.sha256_bytes(b1d_builder.canonical_json(comparable(diagnostic)))
        ),
        "schema_version": diagnostic.get("schema_version") == "1.0",
        "diagnostic_id": diagnostic.get("diagnostic_id") == "r5_second_order_remainder_diagnostic_v1_0",
        "diagnostic_kind": (
            diagnostic.get("diagnostic_kind")
            == "prospective_r5_b1d_second_order_remainder_provenance_diagnostic"
        ),
        "scientific_status_allowed": diagnostic.get("scientific_status") in b1d_builder.ALLOWED_CLASSIFICATIONS,
        "scientific_status_observed": diagnostic.get("scientific_status") == "B1C_REMAINDER_DEPENDENCY_ARTIFACT",
        "no_certificate_claim": no_certificate_claim({"kind": diagnostic.get("diagnostic_kind"), "scope": scope}),
        "arb_precision": diagnostic.get("arb_precision_bits") == 192,
        "base_commit": diagnostic.get("base_commit") == b1d_builder.EXPECTED_BASE_COMMIT,
        "input_hashes": (
            inputs.get("parent_protocol_sha256") == preflight.EXPECTED_PARENT_PROTOCOL_SHA256
            and inputs.get("protocol_sha256") == preflight.EXPECTED_PROTOCOL_SHA256
            and inputs.get("auxiliary_sha256") == preflight.EXPECTED_AUXILIARY_SHA256
            and inputs.get("static_certificate_sha256") == preflight.EXPECTED_STATIC_CERT_SHA256
            and inputs.get("first_leaf_preflight_sha256") == b1d_builder.EXPECTED_PREFLIGHT_CERT_FILE_SHA256
            and inputs.get("center_diagnostic_sha256") == b1d_builder.EXPECTED_CENTER_DIAG_FILE_SHA256
            and inputs.get("affine_diagnostic_sha256") == b1d_builder.EXPECTED_AFFINE_DIAG_FILE_SHA256
            and inputs.get("v0_7_4_source_sha256") == preflight.EXPECTED_V074_SOURCE_SHA256
            and inputs.get("object_sha256") == preflight.EXPECTED_OBJECT_SHA256
        ),
        "provenance_traces_interval_subtraction": (
            provenance.get("source_file") == "research/realizability_r1_r7/diagnose_r5_first_leaf_affine.py"
            and "R2_alpha = F_aff_alpha - F0 - first_alpha" in provenance.get("original_expression", "")
            and provenance.get("directly_calls_F_alpha_box") is True
            and provenance.get("subtracts_F0_and_Fprime_alpha") is True
            and provenance.get("subtraction_layer") == "after Arb interval evaluation of F(alpha_box)"
            and provenance.get("same_correlated_alpha_used_before_intervalization") is False
            and provenance.get("symbolic_or_taylor_layer_subtraction") is False
            and provenance.get("computes_D2F") is False
            and provenance.get("finite_difference_used_for_strict_bound") is False
            and provenance.get("not_a_valid_correlated_taylor_remainder") is True
        ),
        "frozen_objects": (
            diagnostic.get("frozen_objects", {}).get("theta_0_T_N_B_c_P_v_preserved") is True
            and diagnostic.get("frozen_objects", {}).get("leaf_index") == 0
            and diagnostic.get("frozen_objects", {}).get("leaf_interval") == preflight.LEAF_INTERVAL
            and diagnostic.get("frozen_objects", {}).get("v") == ["1", "0", "0", "0", "0", "0"]
            and diagnostic.get("frozen_objects", {}).get("formal_radius_not_modified") is True
        ),
        "hessian_bound_shape": (
            hessian.get("definition") == "H_alpha = sup ||P*B*D2R3(theta_C+(T*v+N*S)alpha)[w,w]||_inf"
            and hessian.get("w_definition") == "w = T*v + N*S"
            and isinstance(hessian.get("w"), list)
            and len(hessian.get("w")) == 14
            and bound_vector(hessian.get("w_enclosure"), 14)
            and bound_vector(hessian.get("theta_C"), 14)
            and bound_record(hessian.get("alpha_interval"))
            and bound_record(hessian.get("alpha_radius"))
            and bound_record(hessian.get("alpha_radius_squared"))
            and bound_vector(hessian.get("raw_response_directional_hessian"))
            and bound_vector(hessian.get("B_response_directional_hessian"))
            and bound_vector(hessian.get("P_B_response_directional_hessian"))
            and bound_record(hessian.get("H_alpha"))
            and bound_record(hessian.get("Y2_true_lagrange_bound"))
            and hessian.get("one_half_factor_included") is True
            and hessian.get("alpha_squared_factor_included") is True
            and hessian.get("finite_difference_used") is False
            and hessian.get("whole_leaf_enclosure") is True
        ),
        "comparison": (
            bound_record(comparison.get("B1c_reported_pure_alpha_second_order"))
            and bound_record(comparison.get("recomputed_interval_subtraction_remainder"))
            and comparison.get("B1c_reported_matches_interval_subtraction") is True
            and bound_record(comparison.get("B1c_reported_over_true_Y2"))
            and comparison.get("true_Y2_significantly_smaller_than_B1c") is True
            and comparison.get("future_revision_should_use_directional_hessian_remainder") is True
            and ratio_upper > Decimal("1e12")
            and true_y2_upper < Decimal("1e-20")
        ),
        "three_point_cross_check": (
            cross.get("status") == "DIAGNOSTIC_ONLY_NOT_A_STRICT_BOUND"
            and bound_vector(cross.get("F_affine_a_L_after_P"))
            and bound_vector(cross.get("F_affine_a_C_after_P"))
            and bound_vector(cross.get("F_affine_a_R_after_P"))
            and bound_vector(cross.get("center_second_difference"))
            and bound_record(cross.get("center_second_difference_inf_norm"))
            and cross.get("not_used_as_theorem_bound") is True
        ),
        "component_records": (
            isinstance(records, list)
            and len(records) == 8
            and all(
                isinstance(item, dict)
                and item.get("component") == index
                and bound_record(item.get("raw_D2R3_ww"))
                and bound_record(item.get("after_B"))
                and bound_record(item.get("after_P"))
                and bound_record(item.get("lagrange_contribution_bound"))
                for index, item in enumerate(records)
            )
            and isinstance(components.get("max_component_after_P"), int)
            and 0 <= components.get("max_component_after_P") < 8
            and bound_record(components.get("max_component_after_P_abs_upper"))
            and components.get("single_component_dominates_1e_minus_9") is False
        ),
        "decision": (
            decision.get("dependency_artifact") is True
            and decision.get("true_curvature_bound_too_wide") is False
            and decision.get("implementation_defect_found") is False
            and decision.get("revise_affine_diagnostic_recommended") is True
            and decision.get("do_not_modify_B1c_result_in_this_round") is True
        ),
        "scope": (
            scope.get("diagnostic_only") is True
            and scope.get("r5_first_leaf_certified") is False
            and scope.get("r5_full_tube_certificate_generated") is False
            and scope.get("r5_certified") is False
            and scope.get("r6_search_performed") is False
            and scope.get("normal_K1_residual_recovery_performed") is False
            and scope.get("other_leaf_inspected") is False
            and scope.get("binary64_theorem_decision_used") is False
            and scope.get("all_gates_pass") is False
            and scope.get("forged_resolved_status") is False
        ),
    }
    return checks


def mutation_cases(diagnostic: dict[str, Any]) -> dict[str, dict[str, Any]]:
    cases: dict[str, dict[str, Any]] = {}

    mutated = copy.deepcopy(diagnostic)
    mutated["code_provenance"]["same_correlated_alpha_used_before_intervalization"] = True
    cases["natural_interval_subtraction_marked_correlated_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["analytic_directional_hessian"].pop("H_alpha")
    cases["missing_hessian_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["analytic_directional_hessian"]["one_half_factor_included"] = False
    cases["missing_one_half_factor_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["analytic_directional_hessian"]["alpha_squared_factor_included"] = False
    cases["missing_alpha_squared_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["analytic_directional_hessian"]["finite_difference_used"] = True
    cases["finite_difference_as_strict_bound_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["frozen_objects"]["leaf_interval"] = ["-1e-12", "-9e-13"]
    cases["leaf_change_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["analytic_directional_hessian"]["alpha_radius"]["abs_upper"] = "1e-12"
    cases["alpha_radius_change_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["analytic_directional_hessian"]["w_definition"] = "w = N*S"
    cases["missing_Tv_in_w_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["analytic_directional_hessian"]["w_definition"] = "w = T*v"
    cases["missing_NS_in_w_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["analytic_directional_hessian"]["definition"] = "H_alpha = sup ||D2R3||"
    cases["B_or_P_omitted_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["analytic_directional_hessian"]["definition"] = "H_alpha = sup ||P*P*B*D2R3||"
    cases["P_repeated_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["analytic_directional_hessian"]["whole_leaf_enclosure"] = False
    cases["sampled_hessian_as_whole_leaf_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["diagnostic_kind"] = "r5_certificate"
    cases["diagnostic_as_certificate_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["scientific_status"] = "SECOND_ORDER_REMAINDER_ANALYTICALLY_RESOLVED"
    cases["forged_resolved_status_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["scope"]["r6_search_performed"] = True
    cases["R6_marked_run_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["scope"]["normal_K1_residual_recovery_performed"] = True
    cases["normal_K1_marked_run_fails"] = mutated

    return cases


def run_mutation_tests(diagnostic: dict[str, Any]) -> dict[str, bool]:
    return {name: not all(verify(case).values()) for name, case in mutation_cases(diagnostic).items()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mutation-tests", action="store_true")
    args = parser.parse_args()

    diagnostic = read_json(DIAGNOSTIC_PATH)
    checks = verify(diagnostic)
    if args.mutation_tests:
        checks.update(run_mutation_tests(diagnostic))
    print(json.dumps(checks, indent=2, sort_keys=True))
    if not all(checks.values()):
        print("FAIL")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
