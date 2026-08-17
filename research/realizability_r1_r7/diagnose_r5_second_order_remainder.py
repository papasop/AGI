#!/usr/bin/env python3
"""R5-B1d second-order remainder provenance diagnostic.

This diagnostic does not certify an R5 leaf or full tube, run R6, inspect other
leaves, or perform normal K=1 residual recovery.
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
import diagnose_r5_first_leaf_affine as affine_builder


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

V074_SOURCE = preflight.V074_SOURCE
PARENT_PROTOCOL_PATH = preflight.PARENT_PROTOCOL_PATH
PROTOCOL_PATH = preflight.PROTOCOL_PATH
AUX_PATH = preflight.AUX_PATH
STATIC_CERT_PATH = preflight.STATIC_CERT_PATH
PREFLIGHT_CERT_PATH = HERE / "certificates" / "r5_first_leaf_preflight_v1_0.json"
CENTER_DIAG_PATH = HERE / "diagnostics" / "r5_first_leaf_center_diagnostic_v1_0.json"
AFFINE_DIAG_PATH = HERE / "diagnostics" / "r5_first_leaf_affine_diagnostic_v1_0.json"
BOUNDARY_PATH = HERE / "R5_SECOND_ORDER_REMAINDER_DIAGNOSTIC.md"
OUTPUT_PATH = HERE / "diagnostics" / "r5_second_order_remainder_diagnostic_v1_0.json"

EXPECTED_BASE_COMMIT = "8184e42744cb58190f0f9a6213da2bd1e5098f6b"
EXPECTED_AFFINE_DIAG_FILE_SHA256 = "e102ee96d229c9f98d1048a65b9a3bacb0c6f0d633b5df7d758ca3c9e8f58afd"
EXPECTED_CENTER_DIAG_FILE_SHA256 = affine_builder.EXPECTED_CENTER_DIAG_FILE_SHA256
EXPECTED_PREFLIGHT_CERT_FILE_SHA256 = affine_builder.EXPECTED_PREFLIGHT_CERT_FILE_SHA256
PRECISION_BITS = 192

ALLOWED_CLASSIFICATIONS = {
    "SECOND_ORDER_REMAINDER_ANALYTICALLY_RESOLVED",
    "B1C_REMAINDER_DEPENDENCY_ARTIFACT",
    "B1C_REMAINDER_IMPLEMENTATION_DEFECT",
    "TRUE_HESSIAN_BOUND_REMAINS_TOO_WIDE",
    "R5_SECOND_ORDER_REMAINDER_DIAGNOSIS_INCONCLUSIVE",
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
        AFFINE_DIAG_PATH: EXPECTED_AFFINE_DIAG_FILE_SHA256,
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

r5_output = Path(os.environ["R5_B1D_OUTPUT"])
r5_aux = json.loads(Path(os.environ["R5_B1D_AUX"]).read_text(encoding="utf-8"))
r5_affine = json.loads(Path(os.environ["R5_B1D_AFFINE_DIAG"]).read_text(encoding="utf-8"))


def r5_arb(value):
    return arb(str(value))


def r5_mat(values):
    return [[r5_arb(item) for item in row] for row in values]


def r5_vec(values):
    return [r5_arb(item) for item in values]


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


def r5_scalar_vecmul(scalar, vec):
    return [scalar * value for value in vec]


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


def r5_bound_matrix(matrix):
    return [[r5_bound(item) for item in row] for row in matrix]


def r5_response(phases):
    z, _ = projective_jet_and_derivatives(phases, mirror=False)
    zbar, _ = projective_jet_and_derivatives(phases, mirror=True)
    values = []
    for order in range(RESPONSE_ORDER + 1):
        values.append(((z.c[order] + zbar.c[order]) / 2).real)
    for order in range(RESPONSE_ORDER + 1):
        values.append(((z.c[order] - zbar.c[order]) / (2 * I)).real)
    return values


def r5_theta_from_t_b(t_value, b_values):
    objects = r5_aux["objects"]
    theta0 = r5_vec(objects["theta_0"])
    T = r5_mat(objects["T"])
    N = r5_mat(objects["N"])
    intrinsic = [t_value, arb(0), arb(0), arb(0), arb(0), arb(0)]
    tangent = r5_matvec(T, intrinsic)
    normal = r5_matvec(N, b_values)
    return [theta0[i] + tangent[i] + normal[i] for i in range(CONTROL_DIMENSION)]


def r5_F_from_theta(theta):
    objects = r5_aux["objects"]
    B = r5_mat(objects["B"])
    c = r5_vec(objects["c"])
    response = r5_response(theta)
    return r5_matvec(B, [response[i] - c[i] for i in range(RESPONSE_DIMENSION)])


def r5_Jalpha_at_theta(theta, direction):
    objects = r5_aux["objects"]
    B = r5_mat(objects["B"])
    jac = response_jacobian_and_gradient(theta)[0]
    return r5_matvec(r5_matmul(B, jac), direction)


def r5_F_affine(theta_C, w, alpha):
    theta = [theta_C[i] + w[i] * alpha for i in range(CONTROL_DIMENSION)]
    return r5_F_from_theta(theta)


def r5_midpoint_string(value):
    midpoint = (value.lower() + value.upper()) / 2
    return str(midpoint)


def r5_interval_from_bound(record):
    return r5_arb(record["enclosure"])


class AlphaJet:
    order = 2

    def __init__(self, coefficients=0):
        if isinstance(coefficients, AlphaJet):
            self.c = coefficients.c[:]
        elif isinstance(coefficients, (list, tuple)):
            self.c = [item if isinstance(item, DeltaJet) else DeltaJet(item) for item in coefficients]
            self.c += [DeltaJet(0)] * (self.order + 1 - len(self.c))
        else:
            self.c = [coefficients if isinstance(coefficients, DeltaJet) else DeltaJet(coefficients)]
            self.c += [DeltaJet(0)] * self.order
        self.c = self.c[: self.order + 1]

    def __add__(self, other):
        other = AlphaJet(other)
        return AlphaJet([self.c[k] + other.c[k] for k in range(self.order + 1)])

    __radd__ = __add__

    def __neg__(self):
        return AlphaJet([-item for item in self.c])

    def __sub__(self, other):
        return self + (-AlphaJet(other))

    def __rsub__(self, other):
        return AlphaJet(other) - self

    def __mul__(self, other):
        other = AlphaJet(other)
        return AlphaJet([
            sum((self.c[k] * other.c[n - k] for k in range(n + 1)), DeltaJet(0))
            for n in range(self.order + 1)
        ])

    __rmul__ = __mul__

    def inv(self):
        result = [self.c[0].inv()]
        for n in range(1, self.order + 1):
            result.append(
                -result[0]
                * sum((self.c[k] * result[n - k] for k in range(1, n + 1)), DeltaJet(0))
            )
        return AlphaJet(result)

    def __truediv__(self, other):
        return self * AlphaJet(other).inv()

    def __rtruediv__(self, other):
        return AlphaJet(other) / self


def alpha_matvec(matrix, vector):
    return [
        matrix[0][0] * vector[0] + matrix[0][1] * vector[1],
        matrix[1][0] * vector[0] + matrix[1][1] * vector[1],
    ]


def alpha_exp_linear(sign, phase0, velocity):
    base = (sign * I * acb(phase0)).exp()
    slope = sign * I * acb(velocity)
    return AlphaJet([
        DeltaJet(base),
        DeltaJet(base * slope),
        DeltaJet(base * slope * slope / 2),
    ])


def alpha_projective_jet(phases0, direction, alpha_box, mirror=False):
    delta = DeltaJet([0, 1])
    radius = (1 + delta * delta).sqrt()
    half_duration = ap(TAU) / 2
    cosine = AlphaJet((radius * half_duration).cos())
    sine = AlphaJet((radius * half_duration).sin() / radius)
    state = [AlphaJet(DeltaJet(1)), AlphaJet(DeltaJet(0))]

    for phase_index in range(CONTROL_DIMENSION):
        phase0 = acb(phases0[phase_index] + direction[phase_index] * alpha_box)
        velocity = acb(direction[phase_index])
        em = alpha_exp_linear(-1, phase0, velocity)
        ep = alpha_exp_linear(1, phase0, velocity)
        if not mirror:
            matrix = [
                [cosine - AlphaJet(I) * sine * AlphaJet(delta), -AlphaJet(I) * sine * em],
                [-AlphaJet(I) * sine * ep, cosine + AlphaJet(I) * sine * AlphaJet(delta)],
            ]
        else:
            matrix = [
                [cosine + AlphaJet(I) * sine * AlphaJet(delta), AlphaJet(I) * sine * ep],
                [AlphaJet(I) * sine * em, cosine - AlphaJet(I) * sine * AlphaJet(delta)],
            ]
        state = alpha_matvec(matrix, state)

    if not mirror:
        numerator_weights = [item.conjugate() for item in orthogonal]
        denominator_weights = [item.conjugate() for item in target]
    else:
        numerator_weights = orthogonal
        denominator_weights = target

    numerator = AlphaJet(DeltaJet(numerator_weights[0])) * state[0] + AlphaJet(DeltaJet(numerator_weights[1])) * state[1]
    denominator = AlphaJet(DeltaJet(denominator_weights[0])) * state[0] + AlphaJet(DeltaJet(denominator_weights[1])) * state[1]
    return numerator / denominator


def r5_response_directional_hessian(phases0, direction, alpha_box):
    z = alpha_projective_jet(phases0, direction, alpha_box, mirror=False)
    zbar = alpha_projective_jet(phases0, direction, alpha_box, mirror=True)
    values = []
    for order in range(RESPONSE_ORDER + 1):
        alpha_second_coeff = ((z.c[2].c[order] + zbar.c[2].c[order]) / 2).real
        values.append(2 * alpha_second_coeff)
    for order in range(RESPONSE_ORDER + 1):
        alpha_second_coeff = ((z.c[2].c[order] - zbar.c[2].c[order]) / (2 * I)).real
        values.append(2 * alpha_second_coeff)
    return values


def r5_main():
    objects = r5_aux["objects"]
    P = r5_mat(objects["P"])
    B = r5_mat(objects["B"])
    T = r5_mat(objects["T"])
    N = r5_mat(objects["N"])
    Tv = [T[row][0] for row in range(CONTROL_DIMENSION)]

    left = r5_arb(os.environ["R5_B1D_LEAF_LEFT"])
    right = r5_arb(os.environ["R5_B1D_LEAF_RIGHT"])
    a_C = (left + right) / 2
    alpha_radius = (right - left).abs_upper() / 2
    alpha = arb(0, str(alpha_radius.upper()))
    zero_b = [arb(0) for _ in range(RESPONSE_DIMENSION)]

    b_C = r5_vec(r5_affine["candidate_center"]["b_C"])
    S = r5_vec(r5_affine["candidate_slope"]["S"])
    NS = r5_matvec(N, S)
    w = [Tv[i] + NS[i] for i in range(CONTROL_DIMENSION)]
    theta_C = r5_theta_from_t_b(a_C, b_C)

    F0 = r5_F_from_theta(theta_C)
    J_alpha_affine = r5_Jalpha_at_theta(theta_C, w)
    F_aff_alpha = r5_F_affine(theta_C, w, alpha)
    first_alpha = r5_scalar_vecmul(alpha, J_alpha_affine)
    interval_subtracted_R2 = [F_aff_alpha[i] - F0[i] - first_alpha[i] for i in range(RESPONSE_DIMENSION)]
    interval_subtracted_R2_P = r5_matvec(P, interval_subtracted_R2)

    response_hessian = r5_response_directional_hessian(theta_C, w, alpha)
    B_response_hessian = r5_matvec(B, response_hessian)
    P_B_response_hessian = r5_matvec(P, B_response_hessian)
    H_alpha = r5_vec_abs_upper(P_B_response_hessian)
    alpha_radius_arb = r5_arb(str(alpha_radius.upper()))
    alpha_radius_squared = alpha_radius_arb * alpha_radius_arb
    true_Y2 = H_alpha * alpha_radius_squared / 2

    B1c_Y2 = r5_interval_from_bound(r5_affine["taylor_decomposition"]["pure_alpha_second_order_remainder"])
    ratio_B1c_true = B1c_Y2 / true_Y2 if not true_Y2.contains(arb(0)) else arb("1e999")

    F_L = r5_matvec(P, r5_F_affine(theta_C, w, left - a_C))
    F_C = r5_matvec(P, r5_F_affine(theta_C, w, arb(0)))
    F_R = r5_matvec(P, r5_F_affine(theta_C, w, right - a_C))
    center_second_difference = [F_R[i] - 2 * F_C[i] + F_L[i] for i in range(RESPONSE_DIMENSION)]
    center_second_difference_norm = r5_vec_abs_upper(center_second_difference)

    component_records = []
    max_index = 0
    max_value = arb(0)
    for index in range(RESPONSE_DIMENSION):
        contribution = P_B_response_hessian[index].abs_upper()
        if contribution > max_value:
            max_value = contribution
            max_index = index
        component_records.append({
            "component": index,
            "raw_D2R3_ww": r5_bound(response_hessian[index]),
            "after_B": r5_bound(B_response_hessian[index]),
            "after_P": r5_bound(P_B_response_hessian[index]),
            "lagrange_contribution_bound": r5_bound(P_B_response_hessian[index].abs_upper() * alpha_radius_squared / 2),
        })

    implementation_defect = False
    if r5_vec_abs_upper(interval_subtracted_R2_P) != B1c_Y2:
        implementation_defect = True

    dependency_ratio_large = bool(ratio_B1c_true > arb("1e12") and not ratio_B1c_true.contains(arb(0)))
    true_bound_small = bool(true_Y2 < arb("1e-20") and not true_Y2.contains(arb(0)))
    if implementation_defect:
        classification = "B1C_REMAINDER_IMPLEMENTATION_DEFECT"
    elif dependency_ratio_large and true_bound_small:
        classification = "B1C_REMAINDER_DEPENDENCY_ARTIFACT"
    elif true_Y2 > arb("1e-20"):
        classification = "TRUE_HESSIAN_BOUND_REMAINS_TOO_WIDE"
    else:
        classification = "R5_SECOND_ORDER_REMAINDER_DIAGNOSIS_INCONCLUSIVE"

    diagnostic = {
        "schema_version": "1.0",
        "diagnostic_id": "r5_second_order_remainder_diagnostic_v1_0",
        "diagnostic_kind": "prospective_r5_b1d_second_order_remainder_provenance_diagnostic",
        "scientific_status": classification,
        "arb_precision_bits": PRECISION_BITS,
        "base_commit": os.environ["R5_B1D_BASE_COMMIT"],
        "software_environment": {
            "python": platform.python_version(),
            "python_flint": "0.8.0",
        },
        "inputs": {
            "parent_protocol_path": "research/realizability_r1_r7/frozen_protocol_v1_0.json",
            "parent_protocol_sha256": os.environ["R5_B1D_PARENT_SHA"],
            "protocol_path": "research/realizability_r1_r7/r5_full_tube_protocol_v1_0.json",
            "protocol_sha256": os.environ["R5_B1D_PROTOCOL_SHA"],
            "auxiliary_path": "research/realizability_r1_r7/data/r5_full_tube_auxiliary_v1_0.json",
            "auxiliary_sha256": os.environ["R5_B1D_AUX_SHA"],
            "static_certificate_path": "research/realizability_r1_r7/certificates/r5_static_arb_gates_v1_0.json",
            "static_certificate_sha256": os.environ["R5_B1D_STATIC_SHA"],
            "first_leaf_preflight_path": "research/realizability_r1_r7/certificates/r5_first_leaf_preflight_v1_0.json",
            "first_leaf_preflight_sha256": os.environ["R5_B1D_PREFLIGHT_SHA"],
            "center_diagnostic_path": "research/realizability_r1_r7/diagnostics/r5_first_leaf_center_diagnostic_v1_0.json",
            "center_diagnostic_sha256": os.environ["R5_B1D_CENTER_SHA"],
            "affine_diagnostic_path": "research/realizability_r1_r7/diagnostics/r5_first_leaf_affine_diagnostic_v1_0.json",
            "affine_diagnostic_sha256": os.environ["R5_B1D_AFFINE_SHA"],
            "v0_7_4_source_path": "src/response_fibre_arb_kkt_witness_alignment_v0_7_4.py",
            "v0_7_4_source_sha256": os.environ["R5_B1D_V074_SHA"],
            "object_sha256": r5_aux["object_sha256"],
        },
        "code_provenance": {
            "source_file": "research/realizability_r1_r7/diagnose_r5_first_leaf_affine.py",
            "source_lines": "330-342 in the B1c script at commit 8184e427",
            "original_expression": "R2_alpha = F_aff_alpha - F0 - first_alpha; pure_alpha_second_order = ||P*R2_alpha||_inf",
            "input_interval": "alpha = [-alpha_radius,+alpha_radius] over first leaf",
            "directly_calls_F_alpha_box": True,
            "subtracts_F0_and_Fprime_alpha": True,
            "subtraction_layer": "after Arb interval evaluation of F(alpha_box)",
            "same_correlated_alpha_used_before_intervalization": False,
            "symbolic_or_taylor_layer_subtraction": False,
            "computes_D2F": False,
            "constant_or_first_order_terms_repeated": False,
            "finite_difference_used_for_strict_bound": False,
            "provenance_classification": "intervalized natural evaluation minus intervalized constant and first-order terms",
            "not_a_valid_correlated_taylor_remainder": True,
        },
        "frozen_objects": {
            "theta_0_T_N_B_c_P_v_preserved": True,
            "leaf_index": 0,
            "leaf_interval": [os.environ["R5_B1D_LEAF_LEFT"], os.environ["R5_B1D_LEAF_RIGHT"]],
            "v": r5_aux["tube"]["v"],
            "formal_radius_not_modified": True,
        },
        "analytic_directional_hessian": {
            "definition": "H_alpha = sup ||P*B*D2R3(theta_C+(T*v+N*S)alpha)[w,w]||_inf",
            "w_definition": "w = T*v + N*S",
            "w": [r5_midpoint_string(value) for value in w],
            "w_enclosure": r5_bound_vector(w),
            "theta_C": r5_bound_vector(theta_C),
            "alpha_interval": r5_bound(alpha),
            "alpha_radius": r5_bound(alpha_radius_arb),
            "alpha_radius_squared": r5_bound(alpha_radius_squared),
            "raw_response_directional_hessian": r5_bound_vector(response_hessian),
            "B_response_directional_hessian": r5_bound_vector(B_response_hessian),
            "P_B_response_directional_hessian": r5_bound_vector(P_B_response_hessian),
            "H_alpha": r5_bound(H_alpha),
            "Y2_true_lagrange_bound": r5_bound(true_Y2),
            "one_half_factor_included": True,
            "alpha_squared_factor_included": True,
            "finite_difference_used": False,
            "whole_leaf_enclosure": True,
        },
        "b1c_remainder_comparison": {
            "B1c_reported_pure_alpha_second_order": r5_bound(B1c_Y2),
            "recomputed_interval_subtraction_remainder": r5_bound(r5_vec_abs_upper(interval_subtracted_R2_P)),
            "B1c_reported_matches_interval_subtraction": not implementation_defect,
            "B1c_reported_over_true_Y2": r5_bound(ratio_B1c_true),
            "true_Y2_significantly_smaller_than_B1c": dependency_ratio_large,
            "future_revision_should_use_directional_hessian_remainder": dependency_ratio_large,
        },
        "three_point_cross_check": {
            "status": "DIAGNOSTIC_ONLY_NOT_A_STRICT_BOUND",
            "F_affine_a_L_after_P": r5_bound_vector(F_L),
            "F_affine_a_C_after_P": r5_bound_vector(F_C),
            "F_affine_a_R_after_P": r5_bound_vector(F_R),
            "center_second_difference": r5_bound_vector(center_second_difference),
            "center_second_difference_inf_norm": r5_bound(center_second_difference_norm),
            "not_used_as_theorem_bound": True,
        },
        "component_sources": {
            "records": component_records,
            "max_component_after_P": max_index,
            "max_component_after_P_abs_upper": r5_bound(max_value),
            "single_component_dominates_1e_minus_9": False,
        },
        "decision": {
            "dependency_artifact": classification == "B1C_REMAINDER_DEPENDENCY_ARTIFACT",
            "true_curvature_bound_too_wide": classification == "TRUE_HESSIAN_BOUND_REMAINS_TOO_WIDE",
            "implementation_defect_found": implementation_defect,
            "revise_affine_diagnostic_recommended": classification == "B1C_REMAINDER_DEPENDENCY_ARTIFACT",
            "do_not_modify_B1c_result_in_this_round": True,
        },
        "scope": {
            "diagnostic_only": True,
            "r5_first_leaf_certified": False,
            "r5_full_tube_certificate_generated": False,
            "r5_certified": False,
            "r6_search_performed": False,
            "normal_K1_residual_recovery_performed": False,
            "other_leaf_inspected": False,
            "binary64_theorem_decision_used": False,
            "all_gates_pass": False,
            "forged_resolved_status": False,
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
    with tempfile.TemporaryDirectory(prefix="r5_second_order_remainder_") as tmp:
        patched = Path(tmp) / "_r5_second_order_remainder_backend.py"
        patched.write_text(patch_frozen_source(V074_SOURCE.read_bytes()), encoding="utf-8")
        output = Path(tmp) / "r5_second_order_remainder_diagnostic_v1_0.json"
        env = dict(os.environ)
        env.update(
            {
                "R5_B1D_OUTPUT": str(output),
                "R5_B1D_AUX": str(AUX_PATH),
                "R5_B1D_AFFINE_DIAG": str(AFFINE_DIAG_PATH),
                "R5_B1D_BASE_COMMIT": EXPECTED_BASE_COMMIT,
                "R5_B1D_PARENT_SHA": preflight.EXPECTED_PARENT_PROTOCOL_SHA256,
                "R5_B1D_PROTOCOL_SHA": preflight.EXPECTED_PROTOCOL_SHA256,
                "R5_B1D_AUX_SHA": preflight.EXPECTED_AUXILIARY_SHA256,
                "R5_B1D_STATIC_SHA": preflight.EXPECTED_STATIC_CERT_SHA256,
                "R5_B1D_PREFLIGHT_SHA": EXPECTED_PREFLIGHT_CERT_FILE_SHA256,
                "R5_B1D_CENTER_SHA": EXPECTED_CENTER_DIAG_FILE_SHA256,
                "R5_B1D_AFFINE_SHA": EXPECTED_AFFINE_DIAG_FILE_SHA256,
                "R5_B1D_V074_SHA": preflight.EXPECTED_V074_SOURCE_SHA256,
                "R5_B1D_LEAF_LEFT": preflight.LEAF_INTERVAL[0],
                "R5_B1D_LEAF_RIGHT": preflight.LEAF_INTERVAL[1],
            }
        )
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
            raise RuntimeError(
                "patched v0.7.4 backend failed\n"
                f"STDOUT:\n{completed.stdout}\n"
                f"STDERR:\n{completed.stderr}"
            )
        return read_json(output)


def main() -> int:
    diagnostic = build_diagnostic()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(diagnostic, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": diagnostic["scientific_status"],
        "diagnostic_sha256": diagnostic["diagnostic_sha256"],
        "H_alpha_abs_upper": diagnostic["analytic_directional_hessian"]["H_alpha"]["abs_upper"],
        "Y2_true_abs_upper": diagnostic["analytic_directional_hessian"]["Y2_true_lagrange_bound"]["abs_upper"],
        "B1c_over_true_abs_upper": diagnostic["b1c_remainder_comparison"]["B1c_reported_over_true_Y2"]["abs_upper"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
