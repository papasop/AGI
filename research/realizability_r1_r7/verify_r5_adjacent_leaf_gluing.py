#!/usr/bin/env python3
"""Verify the R5-B3 adjacent-leaf gluing record or diagnostic."""

from __future__ import annotations

import argparse
import copy
import json
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import certify_r5_adjacent_leaf_gluing as builder
import certify_r5_first_leaf_preflight as preflight

HERE = Path(__file__).resolve().parent
CERT_PATH = HERE / "certificates" / "r5_adjacent_leaf_gluing_v1_1.json"
DIAG_PATH = HERE / "diagnostics" / "r5_adjacent_leaf_gluing_v1_0.json"
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
            mid = Decimal(match.group("mid")); rad = Decimal(match.group("rad"))
        else:
            zero = ZERO_ARB_RE.match(value)
            if not zero:
                return None
            mid = Decimal("0"); rad = Decimal(zero.group("rad"))
        lower = mid - rad; upper = mid + rad
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


def box_record(value: Any) -> bool:
    if not isinstance(value, list) or len(value) != 8:
        return False
    for item in value:
        if not isinstance(item, dict) or set(item) != {"lower", "upper", "width"}:
            return False
        if decimal_bounds(item["lower"]) is None or decimal_bounds(item["upper"]) is None or decimal_bounds(item["width"]) is None:
            return False
    return True


def intersection_metadata_valid(value: Any) -> bool:
    if not isinstance(value, list) or len(value) != 8:
        return False
    required = {
        "lower_source",
        "upper_source",
        "left_lower_selected_or_strictly_below_selected",
        "right_lower_selected_or_strictly_below_selected",
        "left_upper_selected_or_strictly_above_selected",
        "right_upper_selected_or_strictly_above_selected",
    }
    for item in value:
        if not isinstance(item, dict) or set(item) != required:
            return False
        if item["lower_source"] not in {"left", "right"} or item["upper_source"] not in {"left", "right"}:
            return False
        if not all(isinstance(item[key], bool) for key in required - {"lower_source", "upper_source"}):
            return False
        if not item["left_lower_selected_or_strictly_below_selected"] or not item["right_lower_selected_or_strictly_below_selected"]:
            return False
        if not item["left_upper_selected_or_strictly_above_selected"] or not item["right_upper_selected_or_strictly_above_selected"]:
            return False
    return True


def comparable(value: dict[str, Any]) -> dict[str, Any]:
    return builder.digest_payload(value)


def gates_valid(gates: Any, status: str) -> bool:
    expected = {
        "endpoint_consistent", "same_physical_equation", "intersection_nonempty", "intersection_strict_interior",
        "coordinate_transform", "B_inverse", "J_eta_invertible", "common_self_map", "contraction",
        "common_unique_root", "left_attachment", "right_attachment", "physical_root_equality",
    }
    if not isinstance(gates, dict) or set(gates) != expected or not all(isinstance(v, bool) for v in gates.values()):
        return False
    if status == "SEAM_CERTIFIED" and gates["physical_root_equality"] is not True:
        return False
    if gates["physical_root_equality"] and not all(gates[k] for k in ["common_unique_root", "left_attachment", "right_attachment", "coordinate_transform"]):
        return False
    if gates["common_unique_root"] and not all(gates[k] for k in ["common_self_map", "contraction", "J_eta_invertible", "B_inverse", "intersection_strict_interior", "same_physical_equation"]):
        return False
    return True


def seam_records_valid(seams: Any, status: str) -> bool:
    if not isinstance(seams, list) or len(seams) != 15:
        return False
    seen = set(); certified = 0
    for index, seam in enumerate(seams):
        if not isinstance(seam, dict) or seam.get("seam_index") != index:
            return False
        if (seam.get("left_leaf"), seam.get("right_leaf"), seam.get("seam_t")) != (index, index + 1, builder.LEAVES[index][1]):
            return False
        if seam.get("periodic_closure_checked") is not False:
            return False
        key = (seam["left_leaf"], seam["right_leaf"], seam["seam_t"])
        if key in seen:
            return False
        seen.add(key)
        if seam.get("left_physical_equation_hash") != seam.get("right_physical_equation_hash"):
            return False
        if seam.get("seam_final_status") not in builder.SEAM_STATUSES:
            return False
        if not gates_valid(seam.get("gates"), seam.get("seam_final_status")):
            return False
        for key_name in ["left_predictor_b", "right_predictor_b", "predictor_difference", "common_krawczyk_center", "common_center_residual"]:
            if not bound_vector(seam.get(key_name), 8):
                return False
        for key_name in ["left_physical_box", "right_physical_box", "intersection_box"]:
            if not box_record(seam.get(key_name)):
                return False
        if not intersection_metadata_valid(seam.get("intersection_construction_metadata")):
            return False
        for key_name in [
            "predictor_difference_inf_norm", "intersection_min_radius", "intersection_max_radius",
            "intersection_interior_margin", "Y0", "Y1", "Y2", "Y_total", "Z", "Z_times_rmax",
            "inverse_defect", "determinant_enclosure", "strict_self_map_margin",
        ]:
            if not bound_record(seam.get(key_name)):
                return False
        if seam["gates"]["common_self_map"] != (lower(seam["strict_self_map_margin"]["lower"]) > 0):
            return False
        if seam["seam_final_status"] == "SEAM_CERTIFIED":
            certified += 1
    return (certified == 15) == (status == builder.CERTIFIED)


def verify(record: dict[str, Any], expected: dict[str, Any] | None = None) -> dict[str, bool]:
    if expected is None:
        expected = builder.build_record()
    status = record.get("scientific_status")
    inputs = record.get("inputs", {})
    protocol = record.get("frozen_protocol", {})
    method = record.get("method", {})
    summary = record.get("summary", {})
    scope = record.get("scope", {})
    seams = record.get("seam_records")
    certified_count = sum(1 for s in seams if isinstance(s, dict) and s.get("seam_final_status") == "SEAM_CERTIFIED") if isinstance(seams, list) else -1
    return {
        "record_matches_recomputed_arb_record": comparable(record) == comparable(expected),
        "record_sha256": record.get("record_sha256") == builder.sha256_bytes(builder.canonical_json(comparable(record))),
        "schema_version": record.get("schema_version") == "1.0",
        "record_id": record.get("record_id") == "r5_adjacent_leaf_gluing_v1_1",
        "record_kind": record.get("record_kind") == "prospective_r5_b3b_corrected_point_center_adjacent_leaf_common_root_c0_gluing",
        "scientific_status_allowed": status in builder.ALLOWED_STATUSES,
        "scientific_status_consistent": (status == builder.CERTIFIED and certified_count == 15) or (status == builder.NOT_CERTIFIED and certified_count < 15) or status in {builder.INCONCLUSIVE, builder.BOUNDARY_MISMATCH, builder.IMPLEMENTATION_ERROR},
        "arb_precision": record.get("arb_precision_bits") == 192,
        "base_commit": record.get("base_commit") == builder.EXPECTED_BASE_COMMIT,
        "input_hashes": inputs.get("parent_protocol_sha256") == preflight.EXPECTED_PARENT_PROTOCOL_SHA256 and inputs.get("protocol_sha256") == preflight.EXPECTED_PROTOCOL_SHA256 and inputs.get("auxiliary_sha256") == preflight.EXPECTED_AUXILIARY_SHA256 and inputs.get("static_certificate_sha256") == preflight.EXPECTED_STATIC_CERT_SHA256 and inputs.get("b1e_certificate_sha256") == builder.EXPECTED_B1E_CERT_SHA256 and inputs.get("b2_certificate_artifact_sha256") == builder.EXPECTED_B2_CERT_SHA256 and inputs.get("b3a_diagnostic_sha256") == builder.EXPECTED_B3A_DIAG_SHA256 and inputs.get("b2_record_sha256") != builder.EXPECTED_B2_CERT_SHA256 and inputs.get("v0_7_4_source_sha256") == preflight.EXPECTED_V074_SOURCE_SHA256 and inputs.get("object_sha256") == preflight.EXPECTED_OBJECT_SHA256,
        "frozen_protocol": protocol.get("leaf_list") == builder.LEAVES and protocol.get("seam_list") == [[i, i + 1, builder.LEAVES[i][1]] for i in range(15)] and protocol.get("periodic_closure_seam_15_to_0_included") is False and protocol.get("formal_eta_radius") == builder.FORMAL_RADIUS and protocol.get("precision_bits") == 192 and protocol.get("left_right_comparison_object") == "physical normal coordinate b, not local eta" and protocol.get("result_adaptive_changes_allowed") is False,
        "method": method.get("common_endpoint_krawczyk_required") is True and method.get("point_center_krawczyk_center_used") is True and method.get("interval_valued_center_rejected") is True and method.get("box_width_enters_only_through_X_minus_b0_and_Z_times_r") is True and method.get("box_overlap_alone_sufficient") is False and method.get("eta_coordinate_direct_comparison_used") is False and method.get("physical_b_coordinate_comparison_used") is True and method.get("same_physical_equation_required") is True and method.get("left_and_right_attachment_required") is True and method.get("c1_gluing_checked") is False and method.get("binary64_theorem_decision_used") is False,
        "seam_records": seam_records_valid(seams, status),
        "summary": summary.get("seam_count") == 15 and summary.get("certified_seam_count") == certified_count and bound_record(summary.get("minimum_intersection_interior_margin")) and bound_record(summary.get("minimum_common_self_map_margin")) and bound_record(summary.get("maximum_predictor_difference_inf_norm")) and summary.get("single_c0_root_branch_certified") == (status == builder.CERTIFIED) and summary.get("can_enter_B4") == (status == builder.CERTIFIED),
        "continuity_logic": record.get("continuity_logic", {}).get("global_C1_branch_conclusion") is False and record.get("continuity_logic", {}).get("global_C0_branch_conclusion") == (status == builder.CERTIFIED),
        "scope": scope.get("all_16_leaf_local_root_gates_pass") is True and scope.get("all_15_internal_seams_certified") == (status == builder.CERTIFIED) and scope.get("single_c0_root_branch_certified") == (status == builder.CERTIFIED) and scope.get("c1_gluing_certified") is False and scope.get("full_path_response_identity_certified") is False and scope.get("full_path_absolute_continuity_certified") is False and scope.get("positive_measure_nonconstancy_certified") is False and scope.get("zero_cost_full_path_certified") is False and scope.get("principle_r_pr_r5_certified") is False and scope.get("principle_r_pr_r6_supplied") is False and scope.get("gf_r5_certified") is False and scope.get("global_ode_flow_certified") is False and scope.get("r6_search_performed") is False and scope.get("normal_K1_residual_recovery_performed") is False,
    }


def mutation_cases(record: dict[str, Any]) -> dict[str, dict[str, Any]]:
    cases = {}
    m = copy.deepcopy(record); m["seam_records"] = m["seam_records"][:-1]; cases["delete_seam_fails"] = m
    m = copy.deepcopy(record); m["seam_records"][1] = copy.deepcopy(m["seam_records"][0]); cases["duplicate_seam_fails"] = m
    m = copy.deepcopy(record); m["seam_records"][0]["seam_t"] = "-8e-13"; cases["modify_seam_endpoint_fails"] = m
    m = copy.deepcopy(record); m["seam_records"][0]["left_leaf"], m["seam_records"][0]["right_leaf"] = 1, 0; cases["swap_left_right_leaf_fails"] = m
    m = copy.deepcopy(record); m["frozen_protocol"]["periodic_closure_seam_15_to_0_included"] = True; cases["periodic_15_to_0_fails"] = m
    m = copy.deepcopy(record); m["inputs"]["b2_certificate_artifact_sha256"] = "0" * 64; cases["b2_artifact_sha_fails"] = m
    m = copy.deepcopy(record); m["inputs"]["b2_certificate_artifact_sha256"] = record["inputs"]["b2_record_sha256"]; cases["b2_record_as_artifact_sha_fails"] = m
    m = copy.deepcopy(record); m["inputs"]["b3a_diagnostic_sha256"] = "0" * 64; cases["b3a_diagnostic_sha_fails"] = m
    m = copy.deepcopy(record); m["method"]["point_center_krawczyk_center_used"] = False; cases["point_center_gate_removed_fails"] = m
    m = copy.deepcopy(record); m["method"]["interval_valued_center_rejected"] = False; cases["interval_center_reintroduced_fails"] = m
    m = copy.deepcopy(record); m["method"]["box_width_enters_only_through_X_minus_b0_and_Z_times_r"] = False; cases["box_width_double_count_fails"] = m
    m = copy.deepcopy(record); m["seam_records"][0]["intersection_construction_metadata"][0]["left_lower_selected_or_strictly_below_selected"] = False; cases["intersection_metadata_tamper_fails"] = m
    m = copy.deepcopy(record); m["method"]["physical_b_coordinate_comparison_used"] = False; cases["predictor_transform_removed_fails"] = m
    m = copy.deepcopy(record); m["method"]["eta_coordinate_direct_comparison_used"] = True; cases["eta_direct_comparison_fails"] = m
    m = copy.deepcopy(record); m["method"]["box_overlap_alone_sufficient"] = True; cases["overlap_as_equality_fails"] = m
    m = copy.deepcopy(record); m["seam_records"][0]["gates"]["intersection_strict_interior"] = True; m["seam_records"][0]["intersection_interior_margin"]["lower"] = "-1e-30"; cases["forged_strict_intersection_fails"] = m
    m = copy.deepcopy(record); m["seam_records"][0]["strict_self_map_margin"]["lower"] = "1e-20"; cases["self_map_margin_tamper_fails"] = m
    m = copy.deepcopy(record); m["seam_records"][0]["gates"]["common_unique_root"] = False; cases["common_unique_gate_forged_fails"] = m
    m = copy.deepcopy(record); del m["seam_records"][0]["gates"]["left_attachment"]; cases["missing_left_attachment_fails"] = m
    m = copy.deepcopy(record); del m["seam_records"][0]["gates"]["right_attachment"]; cases["missing_right_attachment_fails"] = m
    m = copy.deepcopy(record); m["seam_records"][0]["seam_final_status"] = "SEAM_COMMON_SELF_MAP_FAILED"; cases["c0_forged_with_failed_seam_fails"] = m
    m = copy.deepcopy(record); m["scope"]["c1_gluing_certified"] = True; cases["c1_forged_fails"] = m
    m = copy.deepcopy(record); m["scope"]["principle_r_pr_r6_supplied"] = True; cases["pr_r6_forged_fails"] = m
    m = copy.deepcopy(record); m["scope"]["gf_r5_certified"] = True; cases["gf_r5_forged_fails"] = m
    m = copy.deepcopy(record); m["scope"]["global_ode_flow_certified"] = True; cases["global_flow_forged_fails"] = m
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
