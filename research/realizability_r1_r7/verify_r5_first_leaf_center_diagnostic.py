#!/usr/bin/env python3
"""Verify the R5-B1b first-leaf center/forcing diagnostic."""

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
import diagnose_r5_first_leaf_center as diagnostic_builder


HERE = Path(__file__).resolve().parent
DIAGNOSTIC_PATH = HERE / "diagnostics" / "r5_first_leaf_center_diagnostic_v1_0.json"
ALLOWED_STATUSES = {
    diagnostic_builder.EXPECTED_STATUS_COMPLETE,
    diagnostic_builder.EXPECTED_STATUS_INCONCLUSIVE,
}
ALLOWED_CLASSIFICATIONS = {
    "CENTER_OFFSET_DOMINATES",
    "TANGENT_DEFECT_DOMINATES",
    "INTERVAL_WIDTH_DOMINATES",
    "SCALING_OR_IMPLEMENTATION_DEFECT",
    "KRAWCZYK_BOOKKEEPING_DEFECT",
    "MULTIPLE_CAUSES",
    "CAUSE_INCONCLUSIVE",
}
ARB_RE = re.compile(
    r"^\[(?P<mid>[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?) "
    r"\+/- (?P<rad>(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\]$"
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
        if not match:
            return None
        try:
            mid = Decimal(match.group("mid"))
            rad = Decimal(match.group("rad"))
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


def positive_bound(value: Any) -> bool:
    return finite_bound(value) and lower(value) > 0


def nonnegative_bound(value: Any) -> bool:
    return finite_bound(value) and lower(value) >= 0


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
    return diagnostic_builder.diagnostic_digest_payload(value)


def verify(diagnostic: dict[str, Any]) -> dict[str, bool]:
    expected = diagnostic_builder.build_diagnostic()
    inputs = diagnostic.get("inputs", {})
    frozen = diagnostic.get("frozen_objects", {})
    formula = diagnostic.get("krawczyk_formula_audit", {})
    decomp = diagnostic.get("self_map_decomposition", {})
    tangent = diagnostic.get("tangent_defect", {})
    prediction = diagnostic.get("linear_normal_prediction", {})
    corrections = diagnostic.get("three_point_newton_corrections", {})
    scope = diagnostic.get("scope", {})

    Y = decomp.get("Y_sup_norm_PF_a_b0", {})
    Z = decomp.get("Z_sup_norm_I_minus_PJN", {})
    r = decomp.get("r_frozen_b_box_radius", {})
    Zr = decomp.get("Z_times_r", {})
    total = decomp.get("Y_plus_Zr", {})
    margin = decomp.get("self_map_margin_r_minus_Y_plus_Zr", {})
    point_max = decomp.get("point_correction_max", {})

    checks = {
        "diagnostic_matches_recomputed_arb_diagnostic": (
            comparable(diagnostic) == comparable(expected)
        ),
        "diagnostic_sha256": (
            diagnostic.get("diagnostic_sha256")
            == diagnostic_builder.sha256_bytes(
                diagnostic_builder.canonical_json(comparable(diagnostic))
            )
        ),
        "schema_version": diagnostic.get("schema_version") == "1.0",
        "diagnostic_id": diagnostic.get("diagnostic_id") == "r5_first_leaf_center_diagnostic_v1_0",
        "diagnostic_kind": (
            diagnostic.get("diagnostic_kind")
            == "prospective_r5_b1b_first_leaf_center_forcing_diagnostic"
        ),
        "scientific_status": diagnostic.get("scientific_status") in ALLOWED_STATUSES,
        "classification_allowed": diagnostic.get("classification") in ALLOWED_CLASSIFICATIONS,
        "classification": diagnostic.get("classification") == "MULTIPLE_CAUSES",
        "arb_precision": diagnostic.get("arb_precision_bits") == 192,
        "base_commit": diagnostic.get("base_commit") == preflight.EXPECTED_BASE_COMMIT,
        "input_hashes": (
            inputs.get("parent_protocol_sha256") == preflight.EXPECTED_PARENT_PROTOCOL_SHA256
            and inputs.get("protocol_sha256") == preflight.EXPECTED_PROTOCOL_SHA256
            and inputs.get("auxiliary_sha256") == preflight.EXPECTED_AUXILIARY_SHA256
            and inputs.get("static_certificate_sha256") == preflight.EXPECTED_STATIC_CERT_SHA256
            and inputs.get("first_leaf_preflight_sha256")
            == diagnostic_builder.EXPECTED_PREFLIGHT_CERT_SHA256
            and inputs.get("v0_7_4_source_sha256") == preflight.EXPECTED_V074_SOURCE_SHA256
            and inputs.get("object_sha256") == preflight.EXPECTED_OBJECT_SHA256
        ),
        "frozen_objects_preserved": (
            frozen.get("theta_0_T_N_B_c_P_v_preserved") is True
            and frozen.get("leaf_index") == 0
            and frozen.get("leaf_interval") == preflight.LEAF_INTERVAL
            and frozen.get("v") == ["1", "0", "0", "0", "0", "0"]
            and frozen.get("frozen_b_box_radius") == preflight.B_BOX_RADIUS
            and frozen.get("normal_box_not_resized_or_recentered") is True
        ),
        "formula_audit": (
            formula.get("krawczyk_operator")
            == "K_a(X)=b_0-PF(a,b_0)+(I-PJ_N(a,X))(X-b_0)"
            and formula.get("b0") == "0"
            and formula.get("X_center") == "0"
            and formula.get("image_center_and_radius_separated") is True
            and formula.get("center_offset_not_double_counted_as_radius") is True
            and formula.get("parameter_a_as_full_leaf_interval") is True
            and formula.get("json_decimals_enter_arb_without_float") is True
            and formula.get("matrix_orientation_matches_frozen_shapes") is True
            and formula.get("row_column_transpose_detected") is False
            and formula.get("implementation_defect_detected") is False
        ),
        "self_map_bound_records": all(
            bound_record(item) for item in [Y, Z, r, Zr, total, margin, point_max]
        ),
        "self_map_relationships": (
            positive_bound(Y.get("abs_lower"))
            and positive_bound(Z.get("abs_lower"))
            and positive_bound(r.get("abs_lower"))
            and positive_bound(Zr.get("abs_lower"))
            and positive_bound(total.get("abs_lower"))
            and upper(margin.get("upper")) < 0
            and upper(total.get("abs_upper")) > upper(r.get("abs_upper"))
        ),
        "dominance_gates": (
            decomp.get("forcing_interval_dominates_Zr_gate") is True
            and decomp.get("point_center_offset_exceeds_frozen_radius_gate") is True
            and decomp.get("forcing_interval_overestimates_point_corrections_gate") is True
            and decomp.get("dominant_term") == "Y"
            and positive_bound(decomp.get("Y_over_Zr", {}).get("abs_lower"))
            and positive_bound(decomp.get("Y_over_point_corrections", {}).get("abs_lower"))
        ),
        "tangent_defect": (
            tangent.get("g_T_definition") == "g_T = B*DR3(theta_0)*T*v"
            and bound_vector(tangent.get("g_T_components"))
            and bound_record(tangent.get("g_T_inf_norm"))
            and tangent.get("tangent_defect_is_exact_zero_gate") is False
            and tangent.get("tangent_defect_is_strictly_nonzero_gate") is True
            and positive_bound(tangent.get("g_T_inf_norm", {}).get("abs_lower"))
        ),
        "linear_prediction": (
            bound_record(prediction.get("rho"))
            and bound_record(prediction.get("radius"))
            and bound_vector(prediction.get("psi_prime_center"))
            and bound_vector(prediction.get("psi_prime_0_enclosure"))
            and bound_record(prediction.get("psi_prime_0_inf_norm"))
            and bound_vector(prediction.get("psi_prime_0_times_a_C"))
            and bound_record(prediction.get("psi_prime_0_times_a_C_inf_norm"))
            and upper(prediction.get("rho", {}).get("abs_upper")) < 1
        ),
        "three_point_corrections": (
            corrections.get("a_L") == preflight.LEAF_INTERVAL[0]
            and corrections.get("a_R") == preflight.LEAF_INTERVAL[1]
            and bound_vector(corrections.get("d_L"))
            and bound_vector(corrections.get("d_C"))
            and bound_vector(corrections.get("d_R"))
            and bound_record(corrections.get("d_L_inf_norm"))
            and bound_record(corrections.get("d_C_inf_norm"))
            and bound_record(corrections.get("d_R_inf_norm"))
            and bound_record(corrections.get("point_correction_max_inf_norm"))
            and bound_record(corrections.get("d_R_minus_d_L_inf_norm"))
            and corrections.get("d_C_and_linear_prediction_same_order_gate") is False
        ),
        "scope_exclusions": (
            scope.get("diagnostic_only") is True
            and scope.get("candidate_b_center_frozen_or_certified") is False
            and scope.get("r5_first_leaf_preflight_certified") is False
            and scope.get("r5_full_tube_certificate_generated") is False
            and scope.get("r5_certified") is False
            and scope.get("r6_search_performed") is False
            and scope.get("normal_K1_residual_recovery_performed") is False
            and scope.get("binary64_theorem_decision_used") is False
        ),
    }
    return checks


def mutation_cases(diagnostic: dict[str, Any]) -> dict[str, dict[str, Any]]:
    cases: dict[str, dict[str, Any]] = {}

    mutated = copy.deepcopy(diagnostic)
    mutated["inputs"]["protocol_sha256"] = "0" * 64
    cases["upstream_sha_change_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["frozen_objects"]["leaf_index"] = 1
    cases["leaf_index_change_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["frozen_objects"]["leaf_interval"] = ["-9e-13", "-8.75e-13"]
    cases["leaf_interval_change_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["inputs"]["object_sha256"]["T"] = "f" * 64
    cases["object_sha_change_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["frozen_objects"]["v"] = ["0", "1", "0", "0", "0", "0"]
    cases["v_change_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["arb_precision_bits"] = 128
    cases["precision_change_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["self_map_decomposition"]["Y_sup_norm_PF_a_b0"]["abs_upper"] = "NaN"
    cases["nan_bound_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["self_map_decomposition"]["Z_sup_norm_I_minus_PJN"]["abs_upper"] = "Infinity"
    cases["infinity_bound_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["self_map_decomposition"]["Y_plus_Zr"]["abs_upper"] = "1e-30"
    cases["Y_plus_Zr_tamper_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["self_map_decomposition"]["Z_times_r"]["abs_upper"] = "1e9"
    cases["Zr_tamper_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["self_map_decomposition"]["self_map_margin_r_minus_Y_plus_Zr"]["upper"] = "1"
    cases["self_map_margin_tamper_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["tangent_defect"]["g_T_components"][0]["contains_zero"] = True
    mutated["tangent_defect"]["tangent_defect_is_strictly_nonzero_gate"] = True
    cases["contains_zero_tangent_strict_nonzero_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["diagnostic_kind"] = "certificate"
    cases["diagnostic_as_certificate_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["scope"]["candidate_b_center_frozen_or_certified"] = True
    cases["candidate_center_frozen_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["scope"]["r5_first_leaf_preflight_certified"] = True
    cases["preflight_certified_fails"] = mutated

    mutated = copy.deepcopy(diagnostic)
    mutated["classification"] = "CENTER_OFFSET_DOMINATES"
    cases["classification_tamper_fails"] = mutated

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

    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
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
