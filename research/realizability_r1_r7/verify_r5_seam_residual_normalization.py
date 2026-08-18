#!/usr/bin/env python3
"""Verify the R5-B3a seam residual normalization diagnostic."""

from __future__ import annotations

import argparse
import copy
import json
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import diagnose_r5_seam_residual_normalization as builder

HERE = Path(__file__).resolve().parent
DIAG_PATH = HERE / "diagnostics" / "r5_seam_residual_normalization_diagnostic_v1_0.json"

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


def bound_vector(value: Any, size: int) -> bool:
    return isinstance(value, list) and len(value) == size and all(bound_record(item) for item in value)


def comparable(value: dict[str, Any]) -> dict[str, Any]:
    return builder.digest_payload(value)


def seam_records_valid(seams: Any) -> bool:
    if not isinstance(seams, list) or len(seams) != 15:
        return False
    for index, seam in enumerate(seams):
        if seam.get("seam_index") != index or seam.get("left_leaf") != index or seam.get("right_leaf") != index + 1:
            return False
        if seam.get("seam_t") != builder.b2_builder.LEAVES[index][1]:
            return False
        for key in [
            "b2_left_leaf_Y_total_formal_upper",
            "b2_right_leaf_Y_total_formal_upper",
            "b2_adjacent_leaf_Y_total_max_upper",
            "left_predictor_PF_inf_norm",
            "right_predictor_PF_inf_norm",
            "point_midpoint_PF_inf_norm",
            "b3_interval_center_PF_inf_norm",
            "intersection_center_PF_inf_norm",
            "left_minus_slope_PF_inf_norm",
            "right_minus_slope_PF_inf_norm",
            "common_to_b2_adjacent_Y_total_ratio",
            "point_midpoint_to_b2_adjacent_Y_total_ratio",
            "b3_interval_center_over_point_midpoint_ratio",
            "sign_flip_improvement_ratio",
            "left_coordinate_equivalence_defect",
            "right_coordinate_equivalence_defect",
            "coordinate_equivalence_defect_inf_norm",
            "intersection_center_margin",
            "cap_residual_max_component_bound",
        ]:
            if not bound_record(seam.get(key)):
                return False
        for key in ["cap_center_residual_components", "point_midpoint_residual_components", "b3_interval_center_residual_components"]:
            if not bound_vector(seam.get(key), 8):
                return False
        diagnosis = seam.get("diagnosis")
        if not isinstance(diagnosis, dict):
            return False
        if diagnosis.get("normalization_difference_explains_gap") is not False:
            return False
        if diagnosis.get("b3_interval_center_not_point_center") is not True:
            return False
        if diagnosis.get("center_radius_bookkeeping_defect_explains_recorded_2e_minus_18_forcing") is not True:
            return False
        if diagnosis.get("plus_slope_used_by_B2_and_B3") is not True:
            return False
        if upper(seam["b3_interval_center_over_point_midpoint_ratio"]["lower"]) <= Decimal("1e6"):
            return False
    return True


def verify(record: dict[str, Any], expected: dict[str, Any] | None = None) -> dict[str, bool]:
    if expected is None:
        expected = builder.build_record()
    summary = record.get("summary", {})
    method = record.get("method", {})
    scope = record.get("scope", {})
    inputs = record.get("inputs", {})
    return {
        "record_matches_recomputed_arb_diagnostic": comparable(record) == comparable(expected),
        "diagnostic_sha256": record.get("diagnostic_sha256") == builder.sha256_bytes(builder.canonical_json(comparable(record))),
        "schema_version": record.get("schema_version") == "1.0",
        "diagnostic_id": record.get("diagnostic_id") == "r5_seam_residual_normalization_diagnostic_v1_0",
        "diagnostic_kind": record.get("diagnostic_kind") == "prospective_r5_b3a_seam_residual_normalization_and_coordinate_equivalence_audit",
        "scientific_status": record.get("scientific_status") == builder.STATUS_COMPLETE,
        "classification": record.get("classification") == "KRAWCZYK_BOOKKEEPING_DEFECT",
        "arb_precision": record.get("arb_precision_bits") == 192,
        "base_commit": record.get("base_commit") == builder.EXPECTED_BASE_COMMIT,
        "input_hashes": inputs.get("b2_certificate_artifact_sha256") == builder.EXPECTED_B2_CERT_SHA256 and inputs.get("b3_diagnostic_sha256") == builder.EXPECTED_B3_DIAG_SHA256 and inputs.get("affine_diagnostic_sha256") == builder.EXPECTED_AFFINE_DIAG_SHA256 and inputs.get("auxiliary_sha256") == builder.preflight.EXPECTED_AUXILIARY_SHA256 and inputs.get("v0_7_4_source_sha256") == builder.preflight.EXPECTED_V074_SOURCE_SHA256,
        "method": method.get("diagnostic_only") is True and method.get("theorem_certificate_generated") is False and method.get("R6_run") is False and method.get("normal_K1_residual_recovery_performed") is False and method.get("formal_radius_changed") is False and method.get("T_N_B_P_S_changed") is False and method.get("frozen_protocol_changed") is False and "interval-valued box center" in method.get("B3_forcing_quantity", "") and "Z*rmax" in method.get("bookkeeping_audit", ""),
        "seam_records": seam_records_valid(record.get("seam_records")),
        "summary": summary.get("seam_count") == 15 and bound_record(summary.get("max_common_to_b2_adjacent_Y_total_ratio")) and upper(summary["max_common_to_b2_adjacent_Y_total_ratio"]["lower"]) > Decimal("1e8") and bound_record(summary.get("max_coordinate_equivalence_defect")) and upper(summary["max_coordinate_equivalence_defect"]["upper"]) < Decimal("1e-48") and "bookkeeping artifact" in summary.get("conclusion", ""),
        "scope": scope.get("diagnostic_non_theorem") is True and scope.get("B3_certified") is False and scope.get("B4_started") is False and scope.get("R6_run") is False and scope.get("normal_K1_residual_recovery_performed") is False and scope.get("frozen_protocol_modified") is False and scope.get("formal_radius_modified") is False,
    }


def mutation_cases(record: dict[str, Any]) -> dict[str, dict[str, Any]]:
    cases = {}
    m = copy.deepcopy(record); m["inputs"]["b3_diagnostic_sha256"] = "0" * 64; cases["upstream_sha_tamper_fails"] = m
    m = copy.deepcopy(record); m["classification"] = "NORMALIZATION_GAP"; cases["classification_forged_fails"] = m
    m = copy.deepcopy(record); m["method"]["diagnostic_only"] = False; cases["diagnostic_marked_certificate_fails"] = m
    m = copy.deepcopy(record); m["method"]["theorem_certificate_generated"] = True; cases["theorem_certificate_forged_fails"] = m
    m = copy.deepcopy(record); m["method"]["R6_run"] = True; cases["r6_run_forged_fails"] = m
    m = copy.deepcopy(record); m["method"]["normalization_audit"] = "normalization explains the gap"; cases["normalization_claim_fails"] = m
    m = copy.deepcopy(record); m["method"]["bookkeeping_audit"] = "no bookkeeping issue"; cases["bookkeeping_removed_fails"] = m
    m = copy.deepcopy(record); m["seam_records"][0]["diagnosis"]["b3_interval_center_not_point_center"] = False; cases["interval_center_flag_removed_fails"] = m
    m = copy.deepcopy(record); m["seam_records"][0]["diagnosis"]["center_radius_bookkeeping_defect_explains_recorded_2e_minus_18_forcing"] = False; cases["bookkeeping_explanation_removed_fails"] = m
    m = copy.deepcopy(record); m["seam_records"][0]["common_to_b2_adjacent_Y_total_ratio"]["lower"] = "1"; cases["ratio_tamper_fails"] = m
    m = copy.deepcopy(record); m["seam_records"][0]["point_midpoint_PF_inf_norm"]["upper"] = "1e-18"; cases["point_midpoint_tamper_fails"] = m
    m = copy.deepcopy(record); m["summary"]["max_coordinate_equivalence_defect"]["upper"] = "1e-20"; cases["coordinate_equivalence_defect_fails"] = m
    m = copy.deepcopy(record); m["scope"]["B3_certified"] = True; cases["b3_certified_forged_fails"] = m
    m = copy.deepcopy(record); m["scope"]["B4_started"] = True; cases["b4_started_forged_fails"] = m
    return cases


def run_mutation_tests(record: dict[str, Any], expected: dict[str, Any]) -> dict[str, bool]:
    return {name: not all(verify(case, expected).values()) for name, case in mutation_cases(record).items()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mutation-tests", action="store_true")
    args = parser.parse_args()
    record = read_json(DIAG_PATH)
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
