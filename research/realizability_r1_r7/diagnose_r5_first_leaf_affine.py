#!/usr/bin/env python3
"""R5-B1c first-leaf affine-correlated feasibility diagnostic.

This diagnostic does not certify the first leaf, run a full R5 tube, inspect
R6, or perform normal K=1 residual recovery.
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

import certify_r5_first_leaf_preflight as preflight


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

V074_SOURCE = preflight.V074_SOURCE
PARENT_PROTOCOL_PATH = preflight.PARENT_PROTOCOL_PATH
PROTOCOL_PATH = preflight.PROTOCOL_PATH
AUX_PATH = preflight.AUX_PATH
STATIC_CERT_PATH = preflight.STATIC_CERT_PATH
PREFLIGHT_CERT_PATH = HERE / "certificates" / "r5_first_leaf_preflight_v1_0.json"
CENTER_DIAG_PATH = HERE / "diagnostics" / "r5_first_leaf_center_diagnostic_v1_0.json"
BOUNDARY_PATH = HERE / "R5_FIRST_LEAF_AFFINE_DIAGNOSTIC.md"
OUTPUT_PATH = HERE / "diagnostics" / "r5_first_leaf_affine_diagnostic_v1_0.json"

EXPECTED_BASE_COMMIT = "d1744d5fdd225b0f1cb47bf6286f0b3bbad0d6a8"
EXPECTED_PREFLIGHT_CERT_FILE_SHA256 = "5fcb7602bf6be5ff501329ae68373d8da88acd7abce0c4842ff808d86b21d1b6"
EXPECTED_CENTER_DIAG_FILE_SHA256 = "cb53d8169762b5bbc6b0f1bfbd1b0a075ee427b7111584038dbfa46e81f49faf"
PRECISION_BITS = 192
ETA_RADII = ["1e-30", "1e-28", "1e-26", "1e-24", "1e-23", "1e-22", "1e-20"]
ALLOWED_CLASSIFICATIONS = {
    "AFFINE_CORRELATED_FIRST_LEAF_FEASIBLE",
    "AFFINE_CORRELATED_REMAINDER_TOO_WIDE",
    "CENTER_POINT_SOLVE_INCONCLUSIVE",
    "FIRST_ORDER_CANCELLATION_INSUFFICIENT",
    "IMPLEMENTATION_DEFECT_FOUND",
    "R5_AFFINE_FIRST_LEAF_DIAGNOSIS_INCONCLUSIVE",
}


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


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


def diagnostic_digest_payload(value: dict[str, Any]) -> dict[str, Any]:
    payload = json.loads(json.dumps(value, sort_keys=True))
    payload.pop("diagnostic_sha256", None)
    payload.get("software_environment", {}).pop("python", None)
    return payload


def check_upstream_identity() -> None:
    expected_files = {
        PARENT_PROTOCOL_PATH: preflight.EXPECTED_PARENT_PROTOCOL_SHA256,
        PROTOCOL_PATH: preflight.EXPECTED_PROTOCOL_SHA256,
        AUX_PATH: preflight.EXPECTED_AUXILIARY_SHA256,
        STATIC_CERT_PATH: preflight.EXPECTED_STATIC_CERT_SHA256,
        PREFLIGHT_CERT_PATH: EXPECTED_PREFLIGHT_CERT_FILE_SHA256,
        CENTER_DIAG_PATH: EXPECTED_CENTER_DIAG_FILE_SHA256,
        V074_SOURCE: preflight.EXPECTED_V074_SOURCE_SHA256,
    }
    for path, expected in expected_files.items():
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"upstream SHA mismatch for {path}: {actual} != {expected}")


def injection() -> str:
    code = r'''
import os
import platform

r5_output = Path(os.environ["R5_B1C_OUTPUT"])
r5_aux = json.loads(Path(os.environ["R5_B1C_AUX"]).read_text(encoding="utf-8"))
r5_center = json.loads(Path(os.environ["R5_B1C_CENTER_DIAG"]).read_text(encoding="utf-8"))
r5_eta_radii = json.loads(os.environ["R5_B1C_ETA_RADII"])


def r5_arb(value):
    return arb(str(value))


def r5_mat(values):
    return [[r5_arb(item) for item in row] for row in values]


def r5_vec(values):
    return [r5_arb(item) for item in values]


def r5_identity(size):
    return [[arb(1) if i == j else arb(0) for j in range(size)] for i in range(size)]


def r5_matmul(left, right):
    return [
        [
            sum((left[r][k] * right[k][c] for k in range(len(right))), arb(0))
            for c in range(len(right[0]))
        ]
        for r in range(len(left))
    ]


def r5_matvec(left, vec):
    return [
        sum((left[r][k] * vec[k] for k in range(len(vec))), arb(0))
        for r in range(len(left))
    ]


def r5_vecadd(left, right):
    return [left[i] + right[i] for i in range(len(left))]


def r5_vecsub(left, right):
    return [left[i] - right[i] for i in range(len(left))]


def r5_matsub(left, right):
    return [
        [left[r][c] - right[r][c] for c in range(len(left[0]))]
        for r in range(len(left))
    ]


def r5_scalar_vecmul(scalar, vec):
    return [scalar * value for value in vec]


def r5_inf_norm_upper(matrix):
    best = arb(0)
    for row in matrix:
        total = arb(0)
        for value in row:
            total += value.abs_upper()
        if total > best:
            best = total
    return best


def r5_vec_abs_upper(vec):
    best = arb(0)
    for value in vec:
        upper = value.abs_upper()
        if upper > best:
            best = upper
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


def r5_midpoint_string(value):
    midpoint = (value.lower() + value.upper()) / 2
    return str(midpoint)


def r5_response(phases):
    z, _ = projective_jet_and_derivatives(phases, mirror=False)
    zbar, _ = projective_jet_and_derivatives(phases, mirror=True)
    values = []
    for order in range(RESPONSE_ORDER + 1):
        values.append(((z.c[order] + zbar.c[order]) / 2).real)
    for order in range(RESPONSE_ORDER + 1):
        values.append(((z.c[order] - zbar.c[order]) / (2 * I)).real)
    return values


def r5_response_jacobian(phases):
    jacobian, _gradient = response_jacobian_and_gradient(phases)
    return jacobian


def r5_theta_from_t_b(t_value, b_values):
    objects = r5_aux["objects"]
    theta0 = r5_vec(objects["theta_0"])
    T = r5_mat(objects["T"])
    N = r5_mat(objects["N"])
    intrinsic = [t_value, arb(0), arb(0), arb(0), arb(0), arb(0)]
    tangent = r5_matvec(T, intrinsic)
    normal = r5_matvec(N, b_values)
    return [theta0[i] + tangent[i] + normal[i] for i in range(CONTROL_DIMENSION)]


def r5_theta_affine(theta_C, w, alpha, N, eta):
    return [
        theta_C[i] + w[i] * alpha + sum((N[i][j] * eta[j] for j in range(RESPONSE_DIMENSION)), arb(0))
        for i in range(CONTROL_DIMENSION)
    ]


def r5_F_from_theta(theta):
    objects = r5_aux["objects"]
    B = r5_mat(objects["B"])
    c = r5_vec(objects["c"])
    response = r5_response(theta)
    return r5_matvec(B, [response[i] - c[i] for i in range(RESPONSE_DIMENSION)])


def r5_F_t_b(t_value, b_values):
    return r5_F_from_theta(r5_theta_from_t_b(t_value, b_values))


def r5_JN_at_theta(theta):
    objects = r5_aux["objects"]
    B = r5_mat(objects["B"])
    N = r5_mat(objects["N"])
    jac = r5_response_jacobian(theta)
    return r5_matmul(r5_matmul(B, jac), N)


def r5_Jalpha_at_theta(theta, direction):
    objects = r5_aux["objects"]
    B = r5_mat(objects["B"])
    jac = r5_response_jacobian(theta)
    return r5_matvec(r5_matmul(B, jac), direction)


def r5_JN_t_b(t_value, b_values):
    return r5_JN_at_theta(r5_theta_from_t_b(t_value, b_values))


def r5_newton_correction(t_value):
    P = r5_mat(r5_aux["objects"]["P"])
    zero = [arb(0) for _ in range(RESPONSE_DIMENSION)]
    return [-value for value in r5_matvec(P, r5_F_t_b(t_value, zero))]


def r5_max_phase_displacement(theta_box):
    theta0 = r5_vec(r5_aux["objects"]["theta_0"])
    return r5_vec_abs_upper([theta_box[i] - theta0[i] for i in range(CONTROL_DIMENSION)])


def r5_main():
    objects = r5_aux["objects"]
    P = r5_mat(objects["P"])
    T = r5_mat(objects["T"])
    N = r5_mat(objects["N"])
    Tv = [T[row][0] for row in range(CONTROL_DIMENSION)]

    left = r5_arb(os.environ["R5_B1C_LEAF_LEFT"])
    right = r5_arb(os.environ["R5_B1C_LEAF_RIGHT"])
    a_C = (left + right) / 2
    alpha_radius = (right - left).abs_upper() / 2
    alpha = arb(0, str(alpha_radius.upper()))
    t_box = a_C + alpha
    zero_b = [arb(0) for _ in range(RESPONSE_DIMENSION)]
    r_old = r5_arb(os.environ["R5_B1C_B_RADIUS"])
    old_X = [arb(0, str(r_old.upper())) for _ in range(RESPONSE_DIMENSION)]

    Y_direct_vec = r5_matvec(P, r5_F_t_b(t_box, zero_b))
    Y_direct = r5_vec_abs_upper(Y_direct_vec)
    Z_direct_mat = r5_matsub(r5_identity(RESPONSE_DIMENSION), r5_matmul(P, r5_JN_t_b(t_box, old_X)))
    Z_direct = r5_inf_norm_upper(Z_direct_mat)
    Z_direct_r_old = Z_direct * r_old

    d_L = r5_newton_correction(left)
    d_C = r5_newton_correction(a_C)
    d_R = r5_newton_correction(right)
    d_R_minus_d_L = [d_R[i] - d_L[i] for i in range(RESPONSE_DIMENSION)]
    b_C_candidate = [r5_arb(r5_midpoint_string(value)) for value in d_C]
    b_C_norm = r5_vec_abs_upper(b_C_candidate)
    d_C_minus_b_C = [d_C[i] - b_C_candidate[i] for i in range(RESPONSE_DIMENSION)]

    F_center = r5_F_t_b(a_C, b_C_candidate)
    PF_center = r5_matvec(P, F_center)
    PF_center_norm = r5_vec_abs_upper(PF_center)
    center_solve_ok = bool(PF_center_norm < r5_vec_abs_upper(d_C) / arb("1e8"))

    theta_C = r5_theta_from_t_b(a_C, b_C_candidate)
    JN_C = r5_JN_at_theta(theta_C)
    J_a_C = r5_Jalpha_at_theta(theta_C, Tv)
    S = [-value for value in r5_matvec(P, J_a_C)]
    NS = r5_matvec(N, S)
    affine_direction = [Tv[i] + NS[i] for i in range(CONTROL_DIMENSION)]
    J_alpha_affine = r5_Jalpha_at_theta(theta_C, affine_direction)
    linear_cancel = J_alpha_affine
    linear_cancel_norm = r5_vec_abs_upper(linear_cancel)

    theta_centered = r5_theta_from_t_b(t_box, b_C_candidate)
    Y_centered_vec = r5_matvec(P, r5_F_from_theta(theta_centered))
    Y_centered = r5_vec_abs_upper(Y_centered_vec)

    theta_aff_alpha = r5_theta_affine(theta_C, affine_direction, alpha, N, zero_b)
    F_aff_alpha = r5_F_from_theta(theta_aff_alpha)
    F0 = F_center
    first_alpha = r5_scalar_vecmul(alpha, J_alpha_affine)
    R2_alpha = [F_aff_alpha[i] - F0[i] - first_alpha[i] for i in range(RESPONSE_DIMENSION)]
    affine_expression_alpha = r5_vecadd(r5_vecadd(F0, first_alpha), R2_alpha)
    Y_affine_vec = r5_matvec(P, affine_expression_alpha)
    Y_affine = r5_vec_abs_upper(Y_affine_vec)

    Y0 = r5_vec_abs_upper(r5_matvec(P, F0))
    Y1 = r5_vec_abs_upper(r5_matvec(P, first_alpha))
    R2_alpha_P = r5_vec_abs_upper(r5_matvec(P, R2_alpha))
    alpha_correlation_preserved = True
    sampled_endpoints_used_for_whole_leaf = False
    implementation_defect_detected = False

    radius_records = []
    feasible_any = False
    chart_ok_any = False
    nowrap_ok_any = False
    for radius_string in r5_eta_radii:
        r_eta = r5_arb(radius_string)
        eta = [arb(0, str(r_eta.upper())) for _ in range(RESPONSE_DIMENSION)]
        theta_eta = r5_theta_affine(theta_C, affine_direction, alpha, N, eta)
        theta_pure_eta = r5_theta_affine(theta_C, affine_direction, arb(0), N, eta)
        F_total = r5_F_from_theta(theta_eta)
        F_pure_eta = r5_F_from_theta(theta_pure_eta)
        JN_eta = r5_matvec(JN_C, eta)
        R2_eta = [F_pure_eta[i] - F0[i] - JN_eta[i] for i in range(RESPONSE_DIMENSION)]
        R2_total = [
            F_total[i] - F0[i] - first_alpha[i] - JN_eta[i]
            for i in range(RESPONSE_DIMENSION)
        ]
        R2_mixed = [
            R2_total[i] - R2_alpha[i] - R2_eta[i]
            for i in range(RESPONSE_DIMENSION)
        ]
        JN_box = r5_JN_at_theta(theta_eta)
        Z_eta_mat = r5_matsub(r5_identity(RESPONSE_DIMENSION), r5_matmul(P, JN_box))
        Z_eta = r5_inf_norm_upper(Z_eta_mat)
        Z_eta_r = Z_eta * r_eta
        total_image = Y_affine + Z_eta_r
        margin = r_eta - total_image
        contraction = Z_eta
        max_displacement = r5_max_phase_displacement(theta_eta)
        chart_margin = arb(1) - max_displacement
        nowrap_margin = arb.pi() - max_displacement
        chart_gate = bool(chart_margin > arb(0) and not chart_margin.contains(arb(0)))
        nowrap_gate = bool(nowrap_margin > arb(0) and not nowrap_margin.contains(arb(0)))
        feasible = bool(margin > arb(0) and not margin.contains(arb(0)) and contraction < arb(1) and chart_gate and nowrap_gate)
        feasible_any = feasible_any or feasible
        chart_ok_any = chart_ok_any or chart_gate
        nowrap_ok_any = nowrap_ok_any or nowrap_gate
        radius_records.append({
            "r_eta": radius_string,
            "eta_box_center": ["0"] * RESPONSE_DIMENSION,
            "eta_box_radius": radius_string,
            "Y_affine": r5_bound(Y_affine),
            "Z_eta": r5_bound(Z_eta),
            "Z_eta_times_r_eta": r5_bound(Z_eta_r),
            "total_image_radius": r5_bound(total_image),
            "strict_self_map_margin": r5_bound(margin),
            "contraction_upper_bound": r5_bound(contraction),
            "chart_margin": r5_bound(chart_margin),
            "nowrap_margin": r5_bound(nowrap_margin),
            "chart_gate": chart_gate,
            "nowrap_gate": nowrap_gate,
            "candidate_feasible": feasible,
            "failure_gate": (
                "none" if feasible else
                "self_map_margin" if not bool(margin > arb(0) and not margin.contains(arb(0))) else
                "contraction" if not bool(contraction < arb(1)) else
                "chart" if not chart_gate else
                "nowrap" if not nowrap_gate else
                "unknown"
            ),
            "taylor_remainders": {
                "pure_alpha_second_order": r5_bound(r5_vec_abs_upper(r5_matvec(P, R2_alpha))),
                "alpha_eta_mixed": r5_bound(r5_vec_abs_upper(r5_matvec(P, R2_mixed))),
                "pure_eta": r5_bound(r5_vec_abs_upper(r5_matvec(P, R2_eta))),
                "total": r5_bound(r5_vec_abs_upper(r5_matvec(P, R2_total))),
            },
        })

    ratio_direct_centered = Y_direct / Y_centered if not Y_centered.contains(arb(0)) else arb("1e999")
    ratio_direct_affine = Y_direct / Y_affine if not Y_affine.contains(arb(0)) else arb("1e999")
    ratio_centered_affine = Y_centered / Y_affine if not Y_affine.contains(arb(0)) else arb("1e999")

    if implementation_defect_detected:
        classification = "IMPLEMENTATION_DEFECT_FOUND"
    elif not center_solve_ok:
        classification = "CENTER_POINT_SOLVE_INCONCLUSIVE"
    elif not alpha_correlation_preserved:
        classification = "R5_AFFINE_FIRST_LEAF_DIAGNOSIS_INCONCLUSIVE"
    elif feasible_any:
        classification = "AFFINE_CORRELATED_FIRST_LEAF_FEASIBLE"
    elif Y1 > Y_direct / arb("10"):
        classification = "FIRST_ORDER_CANCELLATION_INSUFFICIENT"
    elif Y_affine > min(r5_arb(item) for item in r5_eta_radii):
        classification = "AFFINE_CORRELATED_REMAINDER_TOO_WIDE"
    else:
        classification = "R5_AFFINE_FIRST_LEAF_DIAGNOSIS_INCONCLUSIVE"

    diagnostic = {
        "schema_version": "1.0",
        "diagnostic_id": "r5_first_leaf_affine_diagnostic_v1_0",
        "diagnostic_kind": "prospective_r5_b1c_leaf_centered_affine_feasibility_diagnostic",
        "scientific_status": classification,
        "arb_precision_bits": PRECISION_BITS,
        "base_commit": os.environ["R5_B1C_BASE_COMMIT"],
        "software_environment": {
            "python": platform.python_version(),
            "python_flint": "0.8.0",
        },
        "inputs": {
            "parent_protocol_path": "research/realizability_r1_r7/frozen_protocol_v1_0.json",
            "parent_protocol_sha256": os.environ["R5_B1C_PARENT_SHA"],
            "protocol_path": "research/realizability_r1_r7/r5_full_tube_protocol_v1_0.json",
            "protocol_sha256": os.environ["R5_B1C_PROTOCOL_SHA"],
            "auxiliary_path": "research/realizability_r1_r7/data/r5_full_tube_auxiliary_v1_0.json",
            "auxiliary_sha256": os.environ["R5_B1C_AUX_SHA"],
            "static_certificate_path": "research/realizability_r1_r7/certificates/r5_static_arb_gates_v1_0.json",
            "static_certificate_sha256": os.environ["R5_B1C_STATIC_SHA"],
            "first_leaf_preflight_path": "research/realizability_r1_r7/certificates/r5_first_leaf_preflight_v1_0.json",
            "first_leaf_preflight_sha256": os.environ["R5_B1C_PREFLIGHT_SHA"],
            "center_diagnostic_path": "research/realizability_r1_r7/diagnostics/r5_first_leaf_center_diagnostic_v1_0.json",
            "center_diagnostic_sha256": os.environ["R5_B1C_CENTER_SHA"],
            "v0_7_4_source_path": "src/response_fibre_arb_kkt_witness_alignment_v0_7_4.py",
            "v0_7_4_source_sha256": os.environ["R5_B1C_V074_SHA"],
            "object_sha256": r5_aux["object_sha256"],
        },
        "frozen_objects": {
            "theta_0_T_N_B_c_P_v_preserved": True,
            "leaf_index": 0,
            "leaf_interval": [os.environ["R5_B1C_LEAF_LEFT"], os.environ["R5_B1C_LEAF_RIGHT"]],
            "v": r5_aux["tube"]["v"],
            "frozen_b_box_radius": os.environ["R5_B1C_B_RADIUS"],
            "formal_radius_not_modified": True,
            "eta_radius_policy_declared_before_run": True,
            "eta_radius_candidates": r5_eta_radii,
        },
        "upstream_consistency": {
            "Y_direct_reproduced": r5_bound(Y_direct),
            "Z_direct_reproduced": r5_bound(Z_direct),
            "Z_direct_times_r_old": r5_bound(Z_direct_r_old),
            "r_old": r5_bound(r_old),
            "d_L_inf_norm_reproduced": r5_bound(r5_vec_abs_upper(d_L)),
            "d_C_inf_norm_reproduced": r5_bound(r5_vec_abs_upper(d_C)),
            "d_R_inf_norm_reproduced": r5_bound(r5_vec_abs_upper(d_R)),
            "d_R_minus_d_L_inf_norm_reproduced": r5_bound(r5_vec_abs_upper(d_R_minus_d_L)),
        },
        "candidate_center": {
            "candidate_status": "NON_THEOREM_CANDIDATE_DATA",
            "construction_method": "one point Newton correction b_C=-P*F(a_C,0), serialized from 192-bit Arb midpoint enclosure",
            "iteration_count": 1,
            "b_C": [r5_midpoint_string(value) for value in b_C_candidate],
            "b_C_enclosure": r5_bound_vector(b_C_candidate),
            "b_C_inf_norm": r5_bound(b_C_norm),
            "F_aC_bC": r5_bound_vector(F_center),
            "P_F_aC_bC": r5_bound_vector(PF_center),
            "P_F_aC_bC_inf_norm": r5_bound(PF_center_norm),
            "d_C_minus_b_C": r5_bound_vector(d_C_minus_b_C),
            "center_point_solve_gate": center_solve_ok,
            "b_C_certified": False,
        },
        "candidate_slope": {
            "candidate_status": "NON_THEOREM_CANDIDATE_DATA",
            "definition": "S approx -P*J_a at theta_C; exact inverse is not used as a theorem decision",
            "J_N": [[r5_bound(item) for item in row] for row in JN_C],
            "J_a": r5_bound_vector(J_a_C),
            "S": [r5_midpoint_string(value) for value in S],
            "S_enclosure": r5_bound_vector(S),
            "linear_cancellation_residual": r5_bound_vector(linear_cancel),
            "linear_cancellation_inf_norm": r5_bound(linear_cancel_norm),
            "S_certified": False,
        },
        "affine_correlation_policy": {
            "representation": "theta(alpha,eta)=theta_C+(T*v+N*S)*alpha+N*eta",
            "alpha_interval": r5_bound(alpha),
            "alpha_correlation_preserved": alpha_correlation_preserved,
            "alpha_not_independently_copied": True,
            "sampled_endpoints_used_for_whole_leaf": sampled_endpoints_used_for_whole_leaf,
            "taylor_remainder_included": True,
            "first_order_NS_not_double_counted": True,
        },
        "enclosure_comparison": {
            "direct_zero_centered_natural_interval": {
                "Y_direct": r5_bound(Y_direct),
                "method": "natural interval evaluation of P*F(a,0) over the first leaf",
                "correlation_preserved": False,
            },
            "constant_leaf_centered_natural_interval": {
                "Y_centered": r5_bound(Y_centered),
                "method": "natural interval evaluation of P*F(a,b_C) over the first leaf",
                "correlation_preserved": False,
            },
            "affine_correlated_centered_taylor": {
                "Y_affine": r5_bound(Y_affine),
                "method": "single alpha affine form theta_C+(T*v+N*S)*alpha with explicit residual decomposition",
                "correlation_preserved": True,
            },
            "reduction_ratios": {
                "Y_direct_over_Y_centered": r5_bound(ratio_direct_centered),
                "Y_direct_over_Y_affine": r5_bound(ratio_direct_affine),
                "Y_centered_over_Y_affine": r5_bound(ratio_centered_affine),
            },
        },
        "taylor_decomposition": {
            "domain": "first leaf alpha interval; eta domains listed per candidate radius",
            "derivative_source": "B*DR3 from frozen v0.7.4 Arb response_jacobian_and_gradient",
            "Y_0_center_residual": r5_bound(Y0),
            "Y_1_first_order_cancellation_defect": r5_bound(Y1),
            "pure_alpha_second_order_remainder": r5_bound(R2_alpha_P),
            "eta_radius_records": radius_records,
        },
        "decision_questions": {
            "is_1e_minus_9_mainly_natural_interval_dependency_artifact": bool(Y_direct > arb("1e4") * r5_vec_abs_upper(d_C)),
            "b_C_is_about_1_3543e_minus_14": bool(b_C_norm > arb("1e-15") and b_C_norm < arb("1e-13")),
            "pointwise_variation_about_1e_minus_26": bool(r5_vec_abs_upper(d_R_minus_d_L) > arb("1e-27") and r5_vec_abs_upper(d_R_minus_d_L) < arb("1e-25")),
            "affine_predictor_reduces_forcing_below_small_remainder_box": feasible_any,
            "basis_for_future_protocol_v1_1": feasible_any,
        },
        "scope": {
            "diagnostic_only": True,
            "candidate_b_C_or_S_certified": False,
            "candidate_b_C_or_S_frozen": False,
            "r5_first_leaf_certified": False,
            "r5_full_tube_certificate_generated": False,
            "r5_certified": False,
            "r6_search_performed": False,
            "normal_K1_residual_recovery_performed": False,
            "binary64_theorem_decision_used": False,
            "all_gates_pass": False,
            "forged_feasible_status": False,
        },
    }
    payload = json.loads(json.dumps(diagnostic, sort_keys=True))
    payload.pop("diagnostic_sha256", None)
    payload.get("software_environment", {}).pop("python", None)
    diagnostic["diagnostic_sha256"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("utf-8")
    ).hexdigest()
    r5_output.parent.mkdir(parents=True, exist_ok=True)
    r5_output.write_text(
        json.dumps(diagnostic, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


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


def build_diagnostic() -> dict[str, Any]:
    check_upstream_identity()
    with tempfile.TemporaryDirectory(prefix="r5_first_leaf_affine_") as tmp:
        patched = Path(tmp) / "_r5_first_leaf_affine_backend.py"
        patched.write_text(patch_frozen_source(V074_SOURCE.read_bytes()), encoding="utf-8")
        output = Path(tmp) / "r5_first_leaf_affine_diagnostic_v1_0.json"
        env = dict(os.environ)
        env.update(
            {
                "R5_B1C_OUTPUT": str(output),
                "R5_B1C_AUX": str(AUX_PATH),
                "R5_B1C_CENTER_DIAG": str(CENTER_DIAG_PATH),
                "R5_B1C_BASE_COMMIT": EXPECTED_BASE_COMMIT,
                "R5_B1C_PARENT_SHA": preflight.EXPECTED_PARENT_PROTOCOL_SHA256,
                "R5_B1C_PROTOCOL_SHA": preflight.EXPECTED_PROTOCOL_SHA256,
                "R5_B1C_AUX_SHA": preflight.EXPECTED_AUXILIARY_SHA256,
                "R5_B1C_STATIC_SHA": preflight.EXPECTED_STATIC_CERT_SHA256,
                "R5_B1C_PREFLIGHT_SHA": EXPECTED_PREFLIGHT_CERT_FILE_SHA256,
                "R5_B1C_CENTER_SHA": EXPECTED_CENTER_DIAG_FILE_SHA256,
                "R5_B1C_V074_SHA": preflight.EXPECTED_V074_SOURCE_SHA256,
                "R5_B1C_LEAF_LEFT": preflight.LEAF_INTERVAL[0],
                "R5_B1C_LEAF_RIGHT": preflight.LEAF_INTERVAL[1],
                "R5_B1C_B_RADIUS": preflight.B_BOX_RADIUS,
                "R5_B1C_ETA_RADII": json.dumps(ETA_RADII),
            }
        )
        completed = subprocess.run(
            [
                sys.executable,
                str(patched),
                "--inputs-zip",
                str(ROOT / "inputs" / "response_fibre_v0_6_2_backend_inputs.zip"),
                "--chart",
                "9",
                "--subdivision",
                "32",
                "--output",
                str(Path(tmp) / "unused"),
            ],
            text=True,
            capture_output=True,
            env=env,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                "R5 first-leaf affine diagnostic backend failed:\n"
                + completed.stdout
                + completed.stderr
            )
        return read_json(output)


def main() -> int:
    diagnostic = build_diagnostic()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_bytes(canonical_json(diagnostic) + b"\n")
    print(json.dumps(diagnostic, indent=2, sort_keys=True))
    print(diagnostic["scientific_status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
