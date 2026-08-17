#!/usr/bin/env python3
"""Verify the R5-B1c first-leaf affine feasibility diagnostic."""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import certify_r5_first_leaf_preflight as preflight
import diagnose_r5_first_leaf_affine as affine_builder


HERE = Path(__file__).resolve().parent
DIAGNOSTIC_PATH = HERE / "diagnostics" / "r5_first_leaf_affine_diagnostic_v1_0.json"

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


def lower(value: Any) -> Decimal:
    bounds = decimal_bounds(value)
    if bounds is None:
        raise ValueError(f"not a finite decimal/Arb bound: {value!r}")
    return bounds[0]


def upper(value: Any) -> Decimal:
    bounds = decimal_bounds(value)
    if bounds is None:
        raise ValueError(f"not a finite decimal/Arb bound: {value!r}")
    return bounds[1]


def finite_bound(value: Any) -> bool:
    return decimal_bounds(value) is not None


def positive_upper(value: Any) -> bool:
    return finite_bound(value) and upper(value) > 0


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


def matrix_bounds(value: Any, rows: int = 8, cols: int = 8) -> bool:
    return (
        isinstance(value, list)
        and len(value) == rows
        and all(isinstance(row, list) and len(row) == cols and all(bound_record(item) for item in row) for row in value)
    )


def comparable(value: dict[str, Any]) -> dict[str, Any]:
    return affine_builder.diagnostic_digest_payload(value)


def radius_records_valid(records: Any, expected_y_affine: dict[str, Any]) -> bool:
    if not isinstance(records, list) or len(records) != len(affine_builder.ETA_RADII):
        return False
    seen = []
    for record in records:
        if not isinstance(record, dict):
            return False
        seen.append(record.get("r_eta"))
        if record.get("r_eta") != record.get("eta_box_radius"):
            return False
        if not isinstance(record.get("eta_box_center"), list) or record["eta_box_center"] != ["0"] * 8:
            return False
        if record.get("Y_affine") != expected_y_affine:
            return False
        for key in [
            "Y_affine",
            "Z_eta",
            "Z_eta_times_r_eta",
            "total_image_radius",
            "strict_self_map_margin",
            "contraction_upper_bound",
            "chart_margin",
            "nowrap_margin",
        ]:
            if not bound_record(record.get(key)):
                return False
        if not isinstance(record.get("candidate_feasible"), bool):
            return False
        if record.get("candidate_feasible"):
            if upper(record["strict_self_map_margin"]["lower"]) <= 0:
                return False
            if upper(record["contraction_upper_bound"]["abs_upper"]) >= 1:
                return False
            if record.get("chart_gate") is not True or record.get("nowrap_gate") is not True:
                return False
        if not isinstance(record.get("failure_gate"), str):
            return False
        remainders = record.get("taylor_remainders", {})
        for key in ["pure_alpha_second_order", "alpha_eta_mixed", "pure_eta", "total"]:
            if not bound_record(remainders.get(key)):
                return False
    return seen == affine_builder.ETA_RADII


def no_certified_word(value: Any) -> bool:
    if isinstance(value, str):
        return "CERTIFIED" not in value
    if isinstance(value, dict):
        return all(no_certified_word(item) for item in value.values())
    if isinstance(value, list):
        return all(no_certified_word(item) for item in value)
    return True


def verify(diagnostic: dict[str, Any]) -> dict[str, bool]:
    expected = affine_builder.build_diagnostic()
    inputs = diagnostic.get("inputs", {})
    frozen = diagnostic.get("frozen_objects", {})
    center = diagnostic.get("candidate_center", {})
    slope = diagnostic.get("candidate_slope", {})
    policy = diagnostic.get("affine_correlation_policy", {})
    comparison = diagnostic.get("enclosure_comparison", {})
    direct = comparison.get("direct_zero_centered_natural_interval", {})
    centered = comparison.get("constant_leaf_centered_natural_interval", {})
    affine = comparison.get("affine_correlated_centered_taylor", {})
    ratios = comparison.get("reduction_ratios", {})
    taylor = diagnostic.get("taylor_decomposition", {})
    questions = diagnostic.get("decision_questions", {})
    scope = diagnostic.get("scope", {})

    Y_direct = direct.get("Y_direct", {})
    Y_centered = centered.get("Y_centered", {})
    Y_affine = affine.get("Y_affine", {})
    records = taylor.get("eta_radius_records")

    feasible_count = (
        sum(1 for item in records if isinstance(item, dict) and item.get("candidate_feasible") is True)
        if isinstance(records, list)
        else -1
    )

    checks = {
        "diagnostic_matches_recomputed_arb_diagnostic": comparable(diagnostic) == comparable(expected),
        "diagnostic_sha256": (
            diagnostic.get("diagnostic_sha256")
            == affine_builder.sha256_bytes(affine_builder.canonical_json(comparable(diagnostic)))
        ),
        "schema_version": diagnostic.get("schema_version") == "1.0",
        "diagnostic_id": diagnostic.get("diagnostic_id") == "r5_first_leaf_affine_diagnostic_v1_0",
        "diagnostic_kind": (
            diagnostic.get("diagnostic_kind")
            == "prospective_r5_b1c_leaf_centered_affine_feasibility_diagnostic"
        ),
        "scientific_status_allowed": diagnostic.get("scientific_status") in affine_builder.ALLOWED_CLASSIFICATIONS,
        "scientific_status_observed": diagnostic.get("scientific_status") == "AFFINE_CORRELATED_REMAINDER_TOO_WIDE",
        "no_certified_status_or_kind": no_certified_word(
            {
                "scientific_status": diagnostic.get("scientific_status"),
                "diagnostic_kind": diagnostic.get("diagnostic_kind"),
                "scope": scope,
            }
        ),
        "arb_precision": diagnostic.get("arb_precision_bits") == 192,
        "base_commit": diagnostic.get("base_commit") == affine_builder.EXPECTED_BASE_COMMIT,
        "input_hashes": (
            inputs.get("parent_protocol_sha256") == preflight.EXPECTED_PARENT_PROTOCOL_SHA256
            and inputs.get("protocol_sha256") == preflight.EXPECTED_PROTOCOL_SHA256
            and inputs.get("auxiliary_sha256") == preflight.EXPECTED_AUXILIARY_SHA256
            and inputs.get("static_certificate_sha256") == preflight.EXPECTED_STATIC_CERT_SHA256
            and inputs.get("first_leaf_preflight_sha256") == affine_builder.EXPECTED_PREFLIGHT_CERT_FILE_SHA256
            and inputs.get("center_diagnostic_sha256") == affine_builder.EXPECTED_CENTER_DIAG_FILE_SHA256
            and inputs.get("v0_7_4_source_sha256") == preflight.EXPECTED_V074_SOURCE_SHA256
            and inputs.get("object_sha256") == preflight.EXPECTED_OBJECT_SHA256
        ),
        "frozen_objects_preserved": (
            frozen.get("theta_0_T_N_B_c_P_v_preserved") is True
            and frozen.get("leaf_index") == 0
            and frozen.get("leaf_interval") == preflight.LEAF_INTERVAL
            and frozen.get("v") == ["1", "0", "0", "0", "0", "0"]
            and frozen.get("frozen_b_box_radius") == preflight.B_BOX_RADIUS
            and frozen.get("formal_radius_not_modified") is True
            and frozen.get("eta_radius_policy_declared_before_run") is True
            and frozen.get("eta_radius_candidates") == affine_builder.ETA_RADII
        ),
        "upstream_reproduction": (
            bound_record(diagnostic.get("upstream_consistency", {}).get("Y_direct_reproduced"))
            and bound_record(diagnostic.get("upstream_consistency", {}).get("Z_direct_reproduced"))
            and bound_record(diagnostic.get("upstream_consistency", {}).get("Z_direct_times_r_old"))
            and bound_record(diagnostic.get("upstream_consistency", {}).get("d_L_inf_norm_reproduced"))
            and bound_record(diagnostic.get("upstream_consistency", {}).get("d_C_inf_norm_reproduced"))
            and bound_record(diagnostic.get("upstream_consistency", {}).get("d_R_inf_norm_reproduced"))
            and bound_record(diagnostic.get("upstream_consistency", {}).get("d_R_minus_d_L_inf_norm_reproduced"))
        ),
        "candidate_center": (
            center.get("candidate_status") == "NON_THEOREM_CANDIDATE_DATA"
            and isinstance(center.get("b_C"), list)
            and len(center.get("b_C")) == 8
            and all(isinstance(item, str) and finite_bound(item) for item in center.get("b_C"))
            and bound_vector(center.get("b_C_enclosure"))
            and bound_record(center.get("b_C_inf_norm"))
            and bound_vector(center.get("F_aC_bC"))
            and bound_vector(center.get("P_F_aC_bC"))
            and bound_record(center.get("P_F_aC_bC_inf_norm"))
            and bound_vector(center.get("d_C_minus_b_C"))
            and center.get("center_point_solve_gate") is True
            and center.get("b_C_certified") is False
        ),
        "candidate_slope": (
            slope.get("candidate_status") == "NON_THEOREM_CANDIDATE_DATA"
            and isinstance(slope.get("S"), list)
            and len(slope.get("S")) == 8
            and all(isinstance(item, str) and finite_bound(item) for item in slope.get("S"))
            and matrix_bounds(slope.get("J_N"))
            and bound_vector(slope.get("J_a"))
            and bound_vector(slope.get("S_enclosure"))
            and bound_vector(slope.get("linear_cancellation_residual"))
            and bound_record(slope.get("linear_cancellation_inf_norm"))
            and slope.get("S_certified") is False
        ),
        "affine_correlation_policy": (
            policy.get("representation") == "theta(alpha,eta)=theta_C+(T*v+N*S)*alpha+N*eta"
            and bound_record(policy.get("alpha_interval"))
            and policy.get("alpha_correlation_preserved") is True
            and policy.get("alpha_not_independently_copied") is True
            and policy.get("sampled_endpoints_used_for_whole_leaf") is False
            and policy.get("taylor_remainder_included") is True
            and policy.get("first_order_NS_not_double_counted") is True
        ),
        "enclosure_comparison": (
            bound_record(Y_direct)
            and bound_record(Y_centered)
            and bound_record(Y_affine)
            and direct.get("correlation_preserved") is False
            and centered.get("correlation_preserved") is False
            and affine.get("correlation_preserved") is True
            and bound_record(ratios.get("Y_direct_over_Y_centered"))
            and bound_record(ratios.get("Y_direct_over_Y_affine"))
            and bound_record(ratios.get("Y_centered_over_Y_affine"))
            and positive_upper(ratios.get("Y_direct_over_Y_affine", {}).get("abs_upper"))
        ),
        "taylor_decomposition": (
            taylor.get("derivative_source")
            == "B*DR3 from frozen v0.7.4 Arb response_jacobian_and_gradient"
            and bound_record(taylor.get("Y_0_center_residual"))
            and bound_record(taylor.get("Y_1_first_order_cancellation_defect"))
            and bound_record(taylor.get("pure_alpha_second_order_remainder"))
            and radius_records_valid(records, Y_affine)
        ),
        "all_candidate_radii_recorded": (
            isinstance(records, list)
            and [item.get("r_eta") for item in records] == affine_builder.ETA_RADII
        ),
        "no_candidate_radius_feasible": feasible_count == 0,
        "classification_consistent": (
            diagnostic.get("scientific_status") == "AFFINE_CORRELATED_REMAINDER_TOO_WIDE"
            and feasible_count == 0
            and upper(Y_affine.get("abs_upper")) > Decimal("1e-20")
        ),
        "decision_questions": (
            questions.get("is_1e_minus_9_mainly_natural_interval_dependency_artifact") is True
            and questions.get("b_C_is_about_1_3543e_minus_14") is True
            and questions.get("pointwise_variation_about_1e_minus_26") is True
            and questions.get("affine_predictor_reduces_forcing_below_small_remainder_box") is False
            and questions.get("basis_for_future_protocol_v1_1") is False
        ),
        "scope_exclusions": (
            scope.get("diagnostic_only") is True
            and scope.get("candidate_b_C_or_S_certified") is False
            and scope.get("candidate_b_C_or_S_frozen") is False
            and scope.get("r5_first_leaf_certified") is False
            and scope.get("r5_full_tube_certificate_generated") is False
            and scope.get("r5_certified") is False
            and scope.get("r6_search_performed") is False
            and scope.get("normal_K1_residual_recovery_performed") is False
            and scope.get("binary64_theorem_decision_used") is False
            and scope.get("all_gates_pass") is False
            and scope.get("forged_feasible_status") is False
        ),
    }
    return checks


def mutation_cases(diagnostic: dict[str, Any]) -> dict[str, dict[str, Any]]:
    cases: dict[str, dict[str, Any]] = {}

    mutated = copy.deepcopy(diagnostic)
    mutated["base_commit"] = "0" * 40
    cases["base_commit_change_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["inputs"]["center_diagnostic_sha256"] = "f" * 64
    cases["upstream_sha_change_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["frozen_objects"]["leaf_index"] = 1
    cases["leaf_index_change_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["frozen_objects"]["leaf_interval"] = ["-1e-12", "-9e-13"]
    cases["leaf_interval_change_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["arb_precision_bits"] = 128
    cases["precision_change_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["inputs"]["object_sha256"]["P"] = "0" * 64
    cases["frozen_object_sha_change_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["candidate_center"]["b_C"][0] = "NaN"
    cases["nan_candidate_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["candidate_slope"]["S"][0] = "Infinity"
    cases["infinity_candidate_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["candidate_center"]["b_C_certified"] = True
    cases["b_C_certified_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["candidate_slope"]["S_certified"] = True
    cases["S_certified_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["affine_correlation_policy"]["alpha_correlation_preserved"] = False
    cases["lost_alpha_correlation_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["affine_correlation_policy"]["taylor_remainder_included"] = False
    cases["missing_taylor_remainder_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["taylor_decomposition"]["pure_alpha_second_order_remainder"]["abs_upper"] = "0"
    cases["second_order_deleted_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["taylor_decomposition"]["eta_radius_records"][0]["taylor_remainders"]["alpha_eta_mixed"]["abs_upper"] = "0"
    cases["mixed_remainder_omitted_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["affine_correlation_policy"]["sampled_endpoints_used_for_whole_leaf"] = True
    cases["sampled_endpoint_substitute_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["frozen_objects"]["eta_radius_candidates"] = ["1e-30"]
    cases["candidate_radius_list_change_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["taylor_decomposition"]["eta_radius_records"] = mutated["taylor_decomposition"]["eta_radius_records"][:1]
    cases["hidden_failed_radius_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["enclosure_comparison"]["reduction_ratios"]["Y_direct_over_Y_affine"]["abs_upper"] = "NaN"
    cases["reduction_ratio_tamper_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["taylor_decomposition"]["eta_radius_records"][0]["strict_self_map_margin"]["upper"] = "1"
    cases["self_map_margin_forged_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["taylor_decomposition"]["eta_radius_records"][0]["candidate_feasible"] = True
    mutated["taylor_decomposition"]["eta_radius_records"][0]["contraction_upper_bound"]["abs_upper"] = "1"
    cases["contraction_ge_one_feasible_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["taylor_decomposition"]["eta_radius_records"][0]["candidate_feasible"] = True
    mutated["taylor_decomposition"]["eta_radius_records"][0]["chart_gate"] = False
    cases["chart_failure_feasible_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["diagnostic_kind"] = "r5_certificate"
    cases["diagnostic_as_certificate_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["inputs"]["parent_protocol_sha256"] = "1" * 64
    cases["frozen_protocol_change_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["scope"]["r6_search_performed"] = True
    cases["R6_marked_run_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["scope"]["normal_K1_residual_recovery_performed"] = True
    cases["normal_K1_marked_run_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["scope"]["all_gates_pass"] = True
    cases["forged_all_gates_pass_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["scientific_status"] = "AFFINE_CORRELATED_FIRST_LEAF_FEASIBLE"
    cases["forged_feasible_status_fails"] = mutated

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
