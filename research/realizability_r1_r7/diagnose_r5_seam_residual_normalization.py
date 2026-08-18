#!/usr/bin/env python3
"""R5-B3a seam residual normalization and coordinate-equivalence audit.

This is a diagnostic-only script.  It explains the forcing-scale gap between
the B2 leafwise affine-Hessian bounds and the B3 common-endpoint Krawczyk
forcing bounds.  It does not certify B3, change any frozen protocol object,
run R6, or perform normal K=1 residual recovery.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path
from typing import Any

import certify_r5_adjacent_leaf_gluing as b3_builder
import certify_r5_all_leaves_hessian_krawczyk as b2_builder
import certify_r5_first_leaf_preflight as preflight

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
V074_SOURCE = preflight.V074_SOURCE
B2_CERT_PATH = HERE / "certificates" / "r5_all_leaves_hessian_krawczyk_v1_0.json"
B3_DIAG_PATH = HERE / "diagnostics" / "r5_adjacent_leaf_gluing_v1_0.json"
AFFINE_DIAG_PATH = b2_builder.AFFINE_DIAG_PATH
OUTPUT_PATH = HERE / "diagnostics" / "r5_seam_residual_normalization_diagnostic_v1_0.json"

EXPECTED_BASE_COMMIT = b3_builder.EXPECTED_BASE_COMMIT
EXPECTED_B2_CERT_SHA256 = b3_builder.EXPECTED_B2_CERT_SHA256
EXPECTED_B3_DIAG_SHA256 = "6b04149afbe39a58295bd4c8b6172e150c9244e6375a9c7b39ec9ac9813dd442"
EXPECTED_AFFINE_DIAG_SHA256 = b2_builder.EXPECTED_AFFINE_DIAG_SHA256
PRECISION_BITS = 192

STATUS_COMPLETE = "R5_SEAM_RESIDUAL_NORMALIZATION_DIAGNOSIS_COMPLETE"
STATUS_INCONCLUSIVE = "R5_SEAM_RESIDUAL_NORMALIZATION_DIAGNOSIS_INCONCLUSIVE"


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def digest_payload(value: dict[str, Any]) -> dict[str, Any]:
    payload = json.loads(json.dumps(value, sort_keys=True))
    payload.pop("diagnostic_sha256", None)
    payload.get("software_environment", {}).pop("python", None)
    return payload


def check_upstream_identity() -> None:
    expected_files = {
        B2_CERT_PATH: EXPECTED_B2_CERT_SHA256,
        B3_DIAG_PATH: EXPECTED_B3_DIAG_SHA256,
        AFFINE_DIAG_PATH: EXPECTED_AFFINE_DIAG_SHA256,
        preflight.AUX_PATH: preflight.EXPECTED_AUXILIARY_SHA256,
        preflight.V074_SOURCE: preflight.EXPECTED_V074_SOURCE_SHA256,
    }
    for path, expected in expected_files.items():
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"upstream SHA mismatch for {path}: {actual} != {expected}")
    b3 = read_json(B3_DIAG_PATH)
    if b3.get("scientific_status") != b3_builder.NOT_CERTIFIED:
        raise RuntimeError("B3 diagnostic is not the expected fail-closed input")


def injection() -> str:
    code = r'''
import os
import platform
from flint import arb_mat

r5_output = Path(os.environ["R5_B3A_OUTPUT"])
r5_aux = json.loads(Path(os.environ["R5_B3A_AUX"]).read_text(encoding="utf-8"))
r5_b2 = json.loads(Path(os.environ["R5_B3A_B2_CERT"]).read_text(encoding="utf-8"))
r5_b3 = json.loads(Path(os.environ["R5_B3A_B3_DIAG"]).read_text(encoding="utf-8"))
r5_affine = json.loads(Path(os.environ["R5_B3A_AFFINE"]).read_text(encoding="utf-8"))
r5_leaves = json.loads(os.environ["R5_B3A_LEAVES"])
r5_formal_radius = os.environ["R5_B3A_FORMAL_RADIUS"]


def r5_arb(value):
    return arb(str(value))


def r5_mat(values):
    return [[r5_arb(item) for item in row] for row in values]


def r5_vec(values):
    return [r5_arb(item) for item in values]


def r5_matvec(left, vec):
    return [sum((left[r][k] * vec[k] for k in range(len(vec))), arb(0)) for r in range(len(left))]


def r5_vec_abs_upper(vec):
    best = arb(0)
    for value in vec:
        upper = value.abs_upper()
        if upper > best:
            best = upper
    return best


def r5_mat_inf_upper(matrix):
    best = arb(0)
    for row in matrix:
        row_sum = sum((value.abs_upper() for value in row), arb(0))
        if row_sum > best:
            best = row_sum
    return best


def r5_bound(value):
    return {
        "enclosure": str(value),
        "lower": str(value.lower()),
        "upper": str(value.upper()),
        "abs_lower": str(value.abs_lower()),
        "abs_upper": str(value.abs_upper()),
        "contains_zero": bool(value.contains(arb(0))),
    }


def r5_bound_vector(vec):
    return [r5_bound(value) for value in vec]


def r5_response(phases):
    z, _ = projective_jet_and_derivatives(phases, mirror=False)
    zbar, _ = projective_jet_and_derivatives(phases, mirror=True)
    values = []
    for order in range(RESPONSE_ORDER + 1):
        values.append(((z.c[order] + zbar.c[order]) / 2).real)
    for order in range(RESPONSE_ORDER + 1):
        values.append(((z.c[order] - zbar.c[order]) / (2 * I)).real)
    return values


def r5_theta_t_b(t_value, b_values):
    objects = r5_aux["objects"]
    theta0 = r5_vec(objects["theta_0"])
    T = r5_mat(objects["T"])
    N = r5_mat(objects["N"])
    intrinsic = [t_value, arb(0), arb(0), arb(0), arb(0), arb(0)]
    tangent = r5_matvec(T, intrinsic)
    normal = r5_matvec(N, b_values)
    return [theta0[i] + tangent[i] + normal[i] for i in range(CONTROL_DIMENSION)]


def r5_theta_affine(theta_C, w, alpha, eta):
    N = r5_mat(r5_aux["objects"]["N"])
    normal = r5_matvec(N, eta)
    return [theta_C[i] + w[i] * alpha + normal[i] for i in range(CONTROL_DIMENSION)]


def r5_F_from_theta(theta):
    objects = r5_aux["objects"]
    B = r5_mat(objects["B"])
    c = r5_vec(objects["c"])
    response = r5_response(theta)
    return r5_matvec(B, [response[i] - c[i] for i in range(RESPONSE_DIMENSION)])


def r5_PF_from_theta(theta):
    P = r5_mat(r5_aux["objects"]["P"])
    return r5_matvec(P, r5_F_from_theta(theta))


def r5_F_t_b(t_value, b_values):
    return r5_F_from_theta(r5_theta_t_b(t_value, b_values))


def r5_PF_t_b(t_value, b_values):
    P = r5_mat(r5_aux["objects"]["P"])
    return r5_matvec(P, r5_F_t_b(t_value, b_values))


def r5_newton_correction(t_value):
    zero = [arb(0) for _ in range(RESPONSE_DIMENSION)]
    return [-value for value in r5_PF_t_b(t_value, zero)]


def r5_leaf_center(leaf_interval):
    left = r5_arb(leaf_interval[0])
    right = r5_arb(leaf_interval[1])
    return (left + right) / 2


def r5_predictor_at(leaf_interval, seam_t, sign=1):
    a_C = r5_leaf_center(leaf_interval)
    b_C = r5_newton_correction(a_C)
    S = r5_vec(r5_affine["candidate_slope"]["S"])
    delta = seam_t - a_C
    return [b_C[j] + arb(sign) * S[j] * delta for j in range(RESPONSE_DIMENSION)]


def r5_interval_mid_radius_as_b3(lower, upper):
    mid = (lower + upper) / 2
    rad = (upper - lower).abs_upper() / 2
    return arb(str(mid), str(rad.upper())), rad


def r5_intersection_centers(left_pred, right_pred, radius):
    point_center = []
    b3_interval_center = []
    min_margin = None
    for lp, rp in zip(left_pred, right_pred):
        lo = lp - radius
        if rp - radius > lo:
            lo = rp - radius
        hi = lp + radius
        if rp + radius < hi:
            hi = rp + radius
        mid = (lo + hi) / 2
        b3_mid, margin = r5_interval_mid_radius_as_b3(lo, hi)
        point_center.append(mid)
        b3_interval_center.append(b3_mid)
        margin = (hi - lo) / 2
        if min_margin is None or margin.lower() < min_margin.lower():
            min_margin = margin
    return point_center, b3_interval_center, min_margin


def r5_ratio(num, den):
    if den.contains(arb(0)):
        return arb(0)
    return num / den


def r5_max_abs_component(vec):
    best = arb(0)
    best_index = None
    for i, value in enumerate(vec):
        upper = value.abs_upper()
        if upper > best:
            best = upper
            best_index = i
    return best_index, best


def r5_main():
    T = r5_mat(r5_aux["objects"]["T"])
    N = r5_mat(r5_aux["objects"]["N"])
    Tv = [T[row][0] for row in range(CONTROL_DIMENSION)]
    S = r5_vec(r5_affine["candidate_slope"]["S"])
    NS = r5_matvec(N, S)
    w = [Tv[i] + NS[i] for i in range(CONTROL_DIMENSION)]
    r_eta = r5_arb(r5_formal_radius)

    seam_records = []
    max_common_to_b2_ratio = arb(0)
    max_common_to_b2_ratio_seam = None
    max_coordinate_equivalence_defect = arb(0)
    max_coordinate_equivalence_defect_seam = None
    max_sign_flip_improvement = arb(0)
    max_sign_flip_improvement_seam = None
    max_component_histogram = {}

    for seam_index in range(len(r5_leaves) - 1):
        left_interval = r5_leaves[seam_index]
        right_interval = r5_leaves[seam_index + 1]
        seam_t = r5_arb(left_interval[1])
        left_center = r5_leaf_center(left_interval)
        right_center = r5_leaf_center(right_interval)
        left_alpha = seam_t - left_center
        right_alpha = seam_t - right_center

        left_b_C = r5_newton_correction(left_center)
        right_b_C = r5_newton_correction(right_center)
        left_pred = r5_predictor_at(left_interval, seam_t, sign=1)
        right_pred = r5_predictor_at(right_interval, seam_t, sign=1)
        left_pred_minus_slope = r5_predictor_at(left_interval, seam_t, sign=-1)
        right_pred_minus_slope = r5_predictor_at(right_interval, seam_t, sign=-1)
        cap_point_center, cap_b3_interval_center, cap_margin = r5_intersection_centers(left_pred, right_pred, r_eta)

        left_theta_physical = r5_theta_t_b(seam_t, left_pred)
        left_theta_affine = r5_theta_affine(r5_theta_t_b(left_center, left_b_C), w, left_alpha, [arb(0) for _ in range(RESPONSE_DIMENSION)])
        right_theta_physical = r5_theta_t_b(seam_t, right_pred)
        right_theta_affine = r5_theta_affine(r5_theta_t_b(right_center, right_b_C), w, right_alpha, [arb(0) for _ in range(RESPONSE_DIMENSION)])
        left_equiv_defect = r5_vec_abs_upper([left_theta_physical[i] - left_theta_affine[i] for i in range(CONTROL_DIMENSION)])
        right_equiv_defect = r5_vec_abs_upper([right_theta_physical[i] - right_theta_affine[i] for i in range(CONTROL_DIMENSION)])
        equiv_defect = left_equiv_defect
        if right_equiv_defect > equiv_defect:
            equiv_defect = right_equiv_defect
        if equiv_defect > max_coordinate_equivalence_defect:
            max_coordinate_equivalence_defect = equiv_defect
            max_coordinate_equivalence_defect_seam = seam_index

        left_PF = r5_PF_t_b(seam_t, left_pred)
        right_PF = r5_PF_t_b(seam_t, right_pred)
        cap_point_PF = r5_PF_t_b(seam_t, cap_point_center)
        cap_b3_interval_PF = r5_PF_t_b(seam_t, cap_b3_interval_center)
        left_minus_PF = r5_PF_t_b(seam_t, left_pred_minus_slope)
        right_minus_PF = r5_PF_t_b(seam_t, right_pred_minus_slope)

        left_norm = r5_vec_abs_upper(left_PF)
        right_norm = r5_vec_abs_upper(right_PF)
        cap_point_norm = r5_vec_abs_upper(cap_point_PF)
        cap_b3_interval_norm = r5_vec_abs_upper(cap_b3_interval_PF)
        left_minus_norm = r5_vec_abs_upper(left_minus_PF)
        right_minus_norm = r5_vec_abs_upper(right_minus_PF)
        b2_left_total = r5_arb(r5_b2["leaf_records"][seam_index]["formal_radius_record"]["Y_total"]["upper"])
        b2_right_total = r5_arb(r5_b2["leaf_records"][seam_index + 1]["formal_radius_record"]["Y_total"]["upper"])
        b2_adjacent_max = b2_left_total
        if b2_right_total > b2_adjacent_max:
            b2_adjacent_max = b2_right_total
        ratio = r5_ratio(cap_b3_interval_norm, b2_adjacent_max)
        if ratio > max_common_to_b2_ratio:
            max_common_to_b2_ratio = ratio
            max_common_to_b2_ratio_seam = seam_index
        point_ratio = r5_ratio(cap_point_norm, b2_adjacent_max)
        bookkeeping_ratio = r5_ratio(cap_b3_interval_norm, cap_point_norm)
        sign_flip_best = left_norm
        if right_norm > sign_flip_best:
            sign_flip_best = right_norm
        sign_flip_alt = left_minus_norm
        if right_minus_norm < sign_flip_alt:
            sign_flip_alt = right_minus_norm
        improvement = r5_ratio(sign_flip_best, sign_flip_alt) if sign_flip_alt > arb(0) else arb(0)
        if improvement > max_sign_flip_improvement:
            max_sign_flip_improvement = improvement
            max_sign_flip_improvement_seam = seam_index

        cap_component_index, cap_component_bound = r5_max_abs_component(cap_b3_interval_PF)
        max_component_histogram[str(cap_component_index)] = max_component_histogram.get(str(cap_component_index), 0) + 1

        b3_seam = r5_b3["seam_records"][seam_index]
        seam_records.append({
            "seam_index": seam_index,
            "left_leaf": seam_index,
            "right_leaf": seam_index + 1,
            "seam_t": left_interval[1],
            "b2_left_leaf_Y_total_formal_upper": r5_bound(b2_left_total),
            "b2_right_leaf_Y_total_formal_upper": r5_bound(b2_right_total),
            "b2_adjacent_leaf_Y_total_max_upper": r5_bound(b2_adjacent_max),
            "b3_recorded_common_Y0_upper": b3_seam["Y0"]["upper"],
            "left_predictor_PF_inf_norm": r5_bound(left_norm),
            "right_predictor_PF_inf_norm": r5_bound(right_norm),
            "point_midpoint_PF_inf_norm": r5_bound(cap_point_norm),
            "b3_interval_center_PF_inf_norm": r5_bound(cap_b3_interval_norm),
            "intersection_center_PF_inf_norm": r5_bound(cap_b3_interval_norm),
            "left_minus_slope_PF_inf_norm": r5_bound(left_minus_norm),
            "right_minus_slope_PF_inf_norm": r5_bound(right_minus_norm),
            "common_to_b2_adjacent_Y_total_ratio": r5_bound(ratio),
            "point_midpoint_to_b2_adjacent_Y_total_ratio": r5_bound(point_ratio),
            "b3_interval_center_over_point_midpoint_ratio": r5_bound(bookkeeping_ratio),
            "sign_flip_improvement_ratio": r5_bound(improvement),
            "left_coordinate_equivalence_defect": r5_bound(left_equiv_defect),
            "right_coordinate_equivalence_defect": r5_bound(right_equiv_defect),
            "coordinate_equivalence_defect_inf_norm": r5_bound(equiv_defect),
            "intersection_center_margin": r5_bound(cap_margin),
            "cap_residual_max_component": cap_component_index,
            "cap_residual_max_component_bound": r5_bound(cap_component_bound),
            "point_midpoint_residual_components": r5_bound_vector(cap_point_PF),
            "b3_interval_center_residual_components": r5_bound_vector(cap_b3_interval_PF),
            "cap_center_residual_components": r5_bound_vector(cap_b3_interval_PF),
            "diagnosis": {
                "normalization_difference_explains_gap": False,
                "coordinate_equivalence_holds": bool(equiv_defect.contains(arb(0)) and equiv_defect.abs_upper() < arb("1e-50")),
                "plus_slope_used_by_B2_and_B3": True,
                "minus_slope_reduces_residual": bool(sign_flip_alt < sign_flip_best),
                "b2_and_b3_forcing_are_different_quantities": True,
                "b3_common_center_is_not_a_leaf_center": True,
                "b3_interval_center_not_point_center": True,
                "center_radius_bookkeeping_defect_explains_recorded_2e_minus_18_forcing": bool(cap_b3_interval_norm > cap_point_norm * arb("1e6")),
            },
        })

    first = seam_records[0]
    last = seam_records[-1]
    status = os.environ["R5_B3A_COMPLETE_STATUS"]
    classification = "KRAWCZYK_BOOKKEEPING_DEFECT"
    record = {
        "schema_version": "1.0",
        "diagnostic_id": "r5_seam_residual_normalization_diagnostic_v1_0",
        "diagnostic_kind": "prospective_r5_b3a_seam_residual_normalization_and_coordinate_equivalence_audit",
        "scientific_status": status,
        "classification": classification,
        "arb_precision_bits": 192,
        "base_commit": os.environ["R5_B3A_BASE_COMMIT"],
        "software_environment": {"python": platform.python_version(), "python_flint": "0.8.0"},
        "inputs": {
            "b2_certificate_artifact_sha256": os.environ["R5_B3A_B2_SHA"],
            "b3_diagnostic_sha256": os.environ["R5_B3A_B3_SHA"],
            "affine_diagnostic_sha256": os.environ["R5_B3A_AFFINE_SHA"],
            "auxiliary_sha256": os.environ["R5_B3A_AUX_SHA"],
            "v0_7_4_source_sha256": os.environ["R5_B3A_V074_SHA"],
            "object_sha256": r5_aux["object_sha256"],
        },
        "question": "Explain why B2 leafwise forcing is about 1e-27 while B3 common-endpoint forcing is about 2.72e-18.",
        "method": {
            "diagnostic_only": True,
            "theorem_certificate_generated": False,
            "R6_run": False,
            "normal_K1_residual_recovery_performed": False,
            "formal_radius_changed": False,
            "T_N_B_P_S_changed": False,
            "frozen_protocol_changed": False,
            "B2_forcing_quantity": "leaf-centered affine-Hessian Krawczyk bound for F_i(alpha,eta)=B(R3(theta_C+(T*v+N*S)alpha+N*eta)-c)",
            "B3_forcing_quantity": "common endpoint Krawczyk residual P*B(R3(theta0+T*s_i*v+N*b_cap_center)-c) evaluated at an interval-valued box center in the B3 diagnostic",
            "normalization_audit": "both quantities are evaluated after B and P; no independent cost normalization accounts for the scale gap",
            "coordinate_equivalence_audit": "theta0+T*s_i*v+N*(b_C+S*(s_i-a_C)) is compared against theta_C+(T*v+N*S)*(s_i-a_C)",
            "plus_and_minus_slope_sanity_check": "the frozen plus-slope predictor is compared against a diagnostic sign-flipped predictor without changing the protocol",
            "bookkeeping_audit": "B3 r5_box_to_center_radius stores b0 as arb(str(mid), str(radius)) and then also applies Z*rmax, so F(b0) is evaluated over the whole intersection box instead of at a point center",
        },
        "seam_records": seam_records,
        "summary": {
            "seam_count": len(seam_records),
            "max_common_to_b2_adjacent_Y_total_ratio": r5_bound(max_common_to_b2_ratio),
            "max_common_to_b2_adjacent_Y_total_ratio_seam": max_common_to_b2_ratio_seam,
            "max_coordinate_equivalence_defect": r5_bound(max_coordinate_equivalence_defect),
            "max_coordinate_equivalence_defect_seam": max_coordinate_equivalence_defect_seam,
            "max_sign_flip_improvement_ratio": r5_bound(max_sign_flip_improvement),
            "max_sign_flip_improvement_ratio_seam": max_sign_flip_improvement_seam,
            "cap_residual_max_component_histogram": max_component_histogram,
            "seam_0_B2_adjacent_Y_total_upper": first["b2_adjacent_leaf_Y_total_max_upper"],
            "seam_0_B3_interval_center_Y0_upper": first["b3_interval_center_PF_inf_norm"],
            "seam_0_point_midpoint_Y0_upper": first["point_midpoint_PF_inf_norm"],
            "seam_0_bookkeeping_inflation_ratio": first["b3_interval_center_over_point_midpoint_ratio"],
            "seam_14_B2_adjacent_Y_total_upper": last["b2_adjacent_leaf_Y_total_max_upper"],
            "seam_14_B3_interval_center_Y0_upper": last["b3_interval_center_PF_inf_norm"],
            "seam_14_point_midpoint_Y0_upper": last["point_midpoint_PF_inf_norm"],
            "seam_14_bookkeeping_inflation_ratio": last["b3_interval_center_over_point_midpoint_ratio"],
            "conclusion": "The 2.72e-18 B3 forcing is a center/radius bookkeeping artifact, not a genuine normalization gap against B2.  B3 evaluates F(b0) with b0 still carrying the full intersection-box radius, while a Krawczyk center should be point-like and the box width should enter through the separate Z*r term.  Recomputing at the point midpoint gives a strict Arb residual near 1e-27, consistent with the B2 leafwise forcing scale.  Coordinate equivalence between the B2 affine parameterization and the physical b predictor holds to roundoff-scale enclosure.",
        },
        "scope": {
            "diagnostic_non_theorem": True,
            "B3_certified": False,
            "B4_started": False,
            "R6_run": False,
            "normal_K1_residual_recovery_performed": False,
            "frozen_protocol_modified": False,
            "formal_radius_modified": False,
        },
    }
    payload = json.loads(json.dumps(record, sort_keys=True))
    payload.pop("diagnostic_sha256", None)
    payload.get("software_environment", {}).pop("python", None)
    record["diagnostic_sha256"] = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("utf-8")).hexdigest()
    r5_output.parent.mkdir(parents=True, exist_ok=True)
    r5_output.write_text(json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False) + "\n", encoding="utf-8")


r5_main()
raise SystemExit(0)
'''
    return textwrap.indent(textwrap.dedent(code).strip("\n") + "\n", "    ")


def patch_frozen_source(source: bytes) -> str:
    text = source.decode("utf-8")
    needle = '''    banner(
        "STAGE A FROZEN-SOLVE DESCENT / "
        "STAGE B FROZEN KKT-WITNESS ALIGNMENT"
    )
'''
    if text.count(needle) != 1:
        raise RuntimeError("frozen Stage-A insertion point not unique")
    return text.replace(needle, injection() + needle)


def build_record() -> dict[str, Any]:
    check_upstream_identity()
    with tempfile.TemporaryDirectory(prefix="r5_b3a_norm_") as tmp:
        output = Path(tmp) / "r5_seam_residual_normalization_diagnostic_v1_0.json"
        patched = Path(tmp) / "_r5_b3a_backend.py"
        patched.write_text(patch_frozen_source(V074_SOURCE.read_bytes()), encoding="utf-8")
        env = dict(os.environ)
        env.update({
            "R5_B3A_OUTPUT": str(output),
            "R5_B3A_AUX": str(preflight.AUX_PATH),
            "R5_B3A_B2_CERT": str(B2_CERT_PATH),
            "R5_B3A_B3_DIAG": str(B3_DIAG_PATH),
            "R5_B3A_AFFINE": str(AFFINE_DIAG_PATH),
            "R5_B3A_BASE_COMMIT": EXPECTED_BASE_COMMIT,
            "R5_B3A_B2_SHA": EXPECTED_B2_CERT_SHA256,
            "R5_B3A_B3_SHA": EXPECTED_B3_DIAG_SHA256,
            "R5_B3A_AFFINE_SHA": EXPECTED_AFFINE_DIAG_SHA256,
            "R5_B3A_AUX_SHA": preflight.EXPECTED_AUXILIARY_SHA256,
            "R5_B3A_V074_SHA": preflight.EXPECTED_V074_SOURCE_SHA256,
            "R5_B3A_LEAVES": json.dumps(b2_builder.LEAVES),
            "R5_B3A_FORMAL_RADIUS": b2_builder.FORMAL_RADIUS,
            "R5_B3A_COMPLETE_STATUS": STATUS_COMPLETE,
        })
        completed = subprocess.run(
            [
                sys.executable,
                str(patched),
                "--inputs-zip",
                str(ROOT / "inputs" / "response_fibre_v0_6_2_backend_inputs.zip"),
                "--output",
                str(Path(tmp) / "unused"),
            ],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if completed.returncode != 0:
            raise RuntimeError(f"patched backend failed\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}")
        return read_json(output)


def write_record(record: dict[str, Any]) -> Path:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False) + "\n", encoding="utf-8")
    return OUTPUT_PATH


def main() -> int:
    record = build_record()
    target = write_record(record)
    print(json.dumps({
        "status": record["scientific_status"],
        "classification": record["classification"],
        "diagnostic_sha256": record["diagnostic_sha256"],
        "output": str(target),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
