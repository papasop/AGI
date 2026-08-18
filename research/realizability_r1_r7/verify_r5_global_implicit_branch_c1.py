#!/usr/bin/env python3
"""Verify the R5-B4 global implicit branch C1 record."""

from __future__ import annotations

import argparse
import copy
import json
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import certify_r5_global_implicit_branch_c1 as builder
import certify_r5_first_leaf_preflight as preflight


HERE = Path(__file__).resolve().parent
CERT_PATH = HERE / "certificates" / "r5_global_implicit_branch_c1_v1_0.json"
DIAG_PATH = HERE / "diagnostics" / "r5_global_implicit_branch_c1_v1_0.json"
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


def bound_vector(value: Any, size: int) -> bool:
    return isinstance(value, list) and len(value) == size and all(bound_record(item) for item in value)


def comparable(value: dict[str, Any]) -> dict[str, Any]:
    return builder.digest_payload(value)


def leaf_gates_valid(gates: Any) -> bool:
    required = {"b2_leaf_unique_root", "jacobian_invertible", "implicit_derivative_enclosed", "chart_admissible", "no_wrap", "leaf_c1_regular"}
    return isinstance(gates, dict) and set(gates) == required and all(isinstance(value, bool) for value in gates.values()) and gates["leaf_c1_regular"] == all(gates[key] for key in required - {"leaf_c1_regular"})


def seam_gates_valid(gates: Any) -> bool:
    required = {"b3b_common_root_certified", "common_jacobian_invertible", "common_derivative_unique", "left_derivative_attachment", "right_derivative_attachment", "physical_derivative_equality"}
    return isinstance(gates, dict) and set(gates) == required and all(isinstance(value, bool) for value in gates.values()) and gates["physical_derivative_equality"] == all(gates[key] for key in required - {"physical_derivative_equality"})


def leaf_records_valid(leaves: Any, status: str) -> bool:
    if not isinstance(leaves, list) or len(leaves) != 16:
        return False
    certified = 0
    for index, leaf in enumerate(leaves):
        if not isinstance(leaf, dict) or leaf.get("leaf_index") != index or leaf.get("leaf_interval") != builder.LEAVES[index]:
            return False
        if leaf.get("D_bF_definition") != "B*DR3(theta)*N" or leaf.get("D_tF_definition") != "B*DR3(theta)*T*v":
            return False
        if leaf.get("implicit_derivative_formula") != "b_prime=-(D_bF)^(-1)*D_tF":
            return False
        for key in ["D_bF_determinant", "inverse_defect", "strict_inverse_margin", "implicit_derivative_norm_upper", "chart_margin", "no_wrap_margin", "admissibility_margin"]:
            if not bound_record(leaf.get(key)):
                return False
        for key, size in [("D_tF", 8), ("P_D_tF", 8), ("implicit_derivative_enclosure", 8)]:
            if not bound_vector(leaf.get(key), size):
                return False
        if not leaf_gates_valid(leaf.get("gates")):
            return False
        if leaf["gates"]["jacobian_invertible"] != (lower(leaf["strict_inverse_margin"]["lower"]) > 0 and leaf["D_bF_determinant"]["contains_zero"] is False):
            return False
        if leaf["gates"]["implicit_derivative_enclosed"] != (lower(leaf["strict_inverse_margin"]["lower"]) > 0):
            return False
        if leaf["gates"]["chart_admissible"] != (lower(leaf["chart_margin"]["lower"]) > 0):
            return False
        if leaf["gates"]["no_wrap"] != (lower(leaf["no_wrap_margin"]["lower"]) > 0):
            return False
        if (leaf.get("leaf_final_status") == "LEAF_C1_CERTIFIED") != leaf["gates"]["leaf_c1_regular"]:
            return False
        certified += int(leaf["gates"]["leaf_c1_regular"])
    return (certified == 16) == (status == builder.CERTIFIED)


def seam_records_valid(seams: Any, status: str) -> bool:
    if not isinstance(seams, list) or len(seams) != 15:
        return False
    certified = 0
    for index, seam in enumerate(seams):
        if not isinstance(seam, dict) or seam.get("seam_index") != index:
            return False
        if (seam.get("left_leaf"), seam.get("right_leaf"), seam.get("seam_t")) != (index, index + 1, builder.LEAVES[index][1]):
            return False
        if seam.get("common_root_reference") != "R5-B3b common physical endpoint root":
            return False
        if seam.get("overlap_alone_used") is not False:
            return False
        for key in ["D_bF_determinant", "inverse_defect", "strict_inverse_margin", "common_physical_derivative_norm_upper", "coordinate_equivalence_defect"]:
            if not bound_record(seam.get(key)):
                return False
        for key in ["D_tF", "common_physical_derivative_enclosure", "left_recovered_derivative_enclosure", "right_recovered_derivative_enclosure"]:
            if not bound_vector(seam.get(key), 8):
                return False
        if not seam_gates_valid(seam.get("gates")):
            return False
        if seam["gates"]["common_jacobian_invertible"] != (lower(seam["strict_inverse_margin"]["lower"]) > 0 and seam["D_bF_determinant"]["contains_zero"] is False):
            return False
        if seam["gates"]["common_derivative_unique"] != (lower(seam["strict_inverse_margin"]["lower"]) > 0):
            return False
        if (seam.get("seam_final_status") == "SEAM_DERIVATIVE_ATTACHED") != seam["gates"]["physical_derivative_equality"]:
            return False
        certified += int(seam["gates"]["physical_derivative_equality"])
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
    leaves = record.get("leaf_records")
    seams = record.get("seam_records")
    leaf_count = sum(1 for leaf in leaves if isinstance(leaf, dict) and leaf.get("gates", {}).get("leaf_c1_regular") is True) if isinstance(leaves, list) else -1
    seam_count = sum(1 for seam in seams if isinstance(seam, dict) and seam.get("gates", {}).get("physical_derivative_equality") is True) if isinstance(seams, list) else -1
    return {
        "record_matches_recomputed_arb_record": comparable(record) == comparable(expected),
        "record_sha256": record.get("record_sha256") == builder.sha256_bytes(builder.canonical_json(comparable(record))),
        "schema_version": record.get("schema_version") == "1.0",
        "record_id": record.get("record_id") == "r5_global_implicit_branch_c1_v1_0",
        "record_kind": record.get("record_kind") == "prospective_r5_b4_global_implicit_branch_c1_certificate",
        "stage": record.get("stage") == "R5-B4",
        "scientific_status_allowed": status in builder.ALLOWED_STATUSES,
        "scientific_status_consistent": (status == builder.CERTIFIED and leaf_count == 16 and seam_count == 15) or (status == builder.NOT_CERTIFIED and (leaf_count < 16 or seam_count < 15)) or status in {builder.INCONCLUSIVE, builder.BOUNDARY_MISMATCH, builder.IMPLEMENTATION_ERROR},
        "arb_precision": record.get("arb_precision_bits") == 192,
        "base_commit": record.get("base_commit") == builder.EXPECTED_BASE_COMMIT,
        "input_hashes": inputs.get("parent_protocol_sha256") == preflight.EXPECTED_PARENT_PROTOCOL_SHA256 and inputs.get("protocol_sha256") == preflight.EXPECTED_PROTOCOL_SHA256 and inputs.get("auxiliary_sha256") == preflight.EXPECTED_AUXILIARY_SHA256 and inputs.get("static_certificate_sha256") == preflight.EXPECTED_STATIC_CERT_SHA256 and inputs.get("b2_certificate_artifact_sha256") == builder.EXPECTED_B2_CERT_SHA256 and inputs.get("b3b_certificate_artifact_sha256") == builder.EXPECTED_B3B_CERT_SHA256 and inputs.get("b3b_internal_record_sha256") == builder.EXPECTED_B3B_RECORD_SHA256 and inputs.get("v0_7_4_source_sha256") == preflight.EXPECTED_V074_SOURCE_SHA256 and inputs.get("object_sha256") == preflight.EXPECTED_OBJECT_SHA256,
        "frozen_protocol": protocol.get("leaf_list") == builder.LEAVES and protocol.get("seam_list") == [[i, i + 1, builder.LEAVES[i][1]] for i in range(15)] and protocol.get("formal_eta_radius") == builder.FORMAL_RADIUS and protocol.get("precision_bits") == 192 and protocol.get("independent_frozen_ode_field_declared") is False and protocol.get("result_adaptive_changes_allowed") is False,
        "method": method.get("D_bF_formula") == "B*DR3(theta)*N" and method.get("D_tF_formula") == "B*DR3(theta)*T*v" and method.get("implicit_derivative_formula") == "b_prime=-(D_bF)^(-1)*D_tF" and method.get("inverse_certification") == "Neumann defect ||I-P*D_bF||_inf < 1 with frozen P" and method.get("point_center_required_for_forcing") is True and method.get("physical_b_coordinate_used_for_seams") is True and method.get("derivative_overlap_alone_sufficient") is False and method.get("same_common_equation_and_unique_root_required") is True and method.get("binary64_theorem_decision_used") is False and method.get("finite_difference_derivative_used") is False and method.get("frozen_ode_consistency_checked") is False,
        "leaf_records": leaf_records_valid(leaves, status),
        "seam_records": seam_records_valid(seams, status),
        "summary": summary.get("leaves_total") == 16 and summary.get("leaves_certified") == leaf_count and summary.get("seams_total") == 15 and summary.get("seams_certified") == seam_count and bound_record(summary.get("minimum_jacobian_margin")) and bound_record(summary.get("maximum_inverse_defect")) and bound_record(summary.get("maximum_derivative_norm_upper")) and bound_record(summary.get("maximum_coordinate_equivalence_defect")) and bound_record(summary.get("minimum_admissibility_margin")) and summary.get("global_c1_branch_certified") == (status == builder.CERTIFIED) and summary.get("frozen_ode_consistency_certified") is False and summary.get("can_enter_b5") == (status == builder.CERTIFIED),
        "scope": scope.get("all_leaf_roots_certified") is True and scope.get("all_internal_seams_c0_certified") is True and scope.get("global_c0_root_branch_certified") is True and scope.get("all_leaf_jacobians_invertible") == (status == builder.CERTIFIED) and scope.get("implicit_derivative_certified") == (status == builder.CERTIFIED) and scope.get("all_seam_derivatives_attached") == (status == builder.CERTIFIED) and scope.get("global_c1_branch_certified") == (status == builder.CERTIFIED) and scope.get("frozen_ode_consistency_certified") is False and scope.get("global_admissibility_certified") == (status == builder.CERTIFIED) and scope.get("positive_measure_nonconstancy_certified") is False and scope.get("full_path_zero_cost_certified") is False and scope.get("full_r5_certificate_generated") is False and scope.get("r5_certified") is False and scope.get("r6_search_performed") is False and scope.get("normal_K1_residual_recovery_performed") is False and scope.get("principle_r_pr_r5_certified") is False and scope.get("principle_r_pr_r6_supplied") is False and scope.get("principle_r_fully_witnessed") is False and scope.get("global_ode_flow_certified") is False,
        "all_gates_pass": record.get("all_gates_pass") == (status == builder.CERTIFIED),
    }


def mutation_cases(record: dict[str, Any]) -> dict[str, dict[str, Any]]:
    cases = {}
    m = copy.deepcopy(record); m["inputs"]["parent_protocol_sha256"] = "0" * 64; cases["frozen_protocol_sha_fails"] = m
    m = copy.deepcopy(record); m["inputs"]["b3b_certificate_artifact_sha256"] = "0" * 64; cases["b3b_artifact_sha_fails"] = m
    m = copy.deepcopy(record); m["inputs"]["b3b_internal_record_sha256"] = "0" * 64; cases["b3b_record_sha_fails"] = m
    m = copy.deepcopy(record); m["leaf_records"] = m["leaf_records"][:-1]; cases["delete_leaf_fails"] = m
    m = copy.deepcopy(record); m["leaf_records"][0], m["leaf_records"][1] = m["leaf_records"][1], m["leaf_records"][0]; cases["reorder_leaf_fails"] = m
    m = copy.deepcopy(record); m["leaf_records"][0]["leaf_interval"] = ["0", "1e-13"]; cases["leaf_interval_fails"] = m
    m = copy.deepcopy(record); m["leaf_records"][0]["gates"]["jacobian_invertible"] = True; m["leaf_records"][0]["D_bF_determinant"]["contains_zero"] = True; cases["forged_jacobian_gate_fails"] = m
    m = copy.deepcopy(record); m["leaf_records"][0]["D_bF_determinant"]["contains_zero"] = True; cases["determinant_contains_zero_fails"] = m
    m = copy.deepcopy(record); m["leaf_records"][0]["inverse_defect"]["abs_upper"] = "1.1"; cases["inverse_defect_over_one_fails"] = m
    m = copy.deepcopy(record); m["leaf_records"][0]["D_tF"][0]["enclosure"] = "1"; cases["D_tF_tamper_fails"] = m
    m = copy.deepcopy(record); m["leaf_records"][0]["implicit_derivative_enclosure"][0]["enclosure"] = "NaN"; cases["bprime_nan_fails"] = m
    m = copy.deepcopy(record); m["method"]["implicit_derivative_formula"] = "eta_prime=-(D_bF)^(-1)*D_tF"; cases["eta_prime_as_physical_fails"] = m
    m = copy.deepcopy(record); m["seam_records"] = m["seam_records"][:-1]; cases["delete_seam_fails"] = m
    m = copy.deepcopy(record); m["seam_records"][0]["common_root_reference"] = "overlap only"; cases["common_root_reference_fails"] = m
    m = copy.deepcopy(record); m["seam_records"][0]["gates"]["left_derivative_attachment"] = False; cases["left_derivative_attachment_fails"] = m
    m = copy.deepcopy(record); m["method"]["derivative_overlap_alone_sufficient"] = True; cases["overlap_only_derivative_fails"] = m
    m = copy.deepcopy(record); m["seam_records"][0]["coordinate_equivalence_defect"]["enclosure"] = "Infinity"; cases["coordinate_defect_inf_fails"] = m
    m = copy.deepcopy(record); m["scope"]["global_c1_branch_certified"] = True; m["seam_records"][0]["gates"]["physical_derivative_equality"] = False; cases["c1_forged_with_failed_seam_fails"] = m
    m = copy.deepcopy(record); m["scope"]["positive_measure_nonconstancy_certified"] = True; cases["nonconstancy_forged_fails"] = m
    m = copy.deepcopy(record); m["scope"]["full_path_zero_cost_certified"] = True; cases["zero_cost_forged_fails"] = m
    m = copy.deepcopy(record); m["scope"]["r5_certified"] = True; cases["r5_forged_fails"] = m
    m = copy.deepcopy(record); m["scope"]["r6_search_performed"] = True; cases["r6_forged_fails"] = m
    m = copy.deepcopy(record); m["scope"]["normal_K1_residual_recovery_performed"] = True; cases["normal_k1_forged_fails"] = m
    m = copy.deepcopy(record); m["record_sha256"] = "0" * 64; cases["internal_record_hash_fails"] = m
    m = copy.deepcopy(record); del m["summary"]["minimum_jacobian_margin"]; cases["missing_field_fails"] = m
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
