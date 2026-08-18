#!/usr/bin/env python3
"""R5-B2 all-leaves affine-Hessian Krawczyk preflight.

This checks the 16 frozen leaves independently. It does not certify adjacent
leaf gluing, full-path continuity, zero cost, nonconstancy, PR-R6, normal K=1
recovery, or any global flow statement.
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

import certify_r5_first_leaf_hessian_krawczyk as b1e_builder
import certify_r5_first_leaf_preflight as preflight


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

V074_SOURCE = preflight.V074_SOURCE
PARENT_PROTOCOL_PATH = preflight.PARENT_PROTOCOL_PATH
PROTOCOL_PATH = preflight.PROTOCOL_PATH
AUX_PATH = preflight.AUX_PATH
STATIC_CERT_PATH = preflight.STATIC_CERT_PATH
B1E_CERT_PATH = HERE / "certificates" / "r5_first_leaf_hessian_krawczyk_v1_0.json"
B1D_DIAG_PATH = HERE / "diagnostics" / "r5_second_order_remainder_diagnostic_v1_0.json"
AFFINE_DIAG_PATH = HERE / "diagnostics" / "r5_first_leaf_affine_diagnostic_v1_0.json"
BOUNDARY_PATH = HERE / "R5_ALL_LEAVES_HESSIAN_KRAWCZYK_BOUNDARY.md"
NAMING_BOUNDARY_PATH = HERE / "GF_PR_STAGE_NAMING_BOUNDARY.md"
COMPLIANCE_MATRIX_PATH = HERE / "PRINCIPLE_R_COMPLIANCE_MATRIX.md"
CERT_PATH = HERE / "certificates" / "r5_all_leaves_hessian_krawczyk_v1_0.json"
DIAG_PATH = HERE / "diagnostics" / "r5_all_leaves_hessian_krawczyk_v1_0.json"

EXPECTED_BASE_COMMIT = "1d6ca4fd7e8eda0977e66d869715ca1c22d75144"
EXPECTED_B1E_CERT_SHA256 = "e1ff18f9891c60fdfae51726b0d16cc713ffbaa241d518e9741f60e514078ccd"
EXPECTED_B1D_DIAG_SHA256 = b1e_builder.EXPECTED_B1D_DIAG_SHA256
EXPECTED_AFFINE_DIAG_SHA256 = b1e_builder.EXPECTED_AFFINE_DIAG_SHA256
PRECISION_BITS = 192
FORMAL_RADIUS = "1e-23"
ETA_RADII = ["1e-30", "1e-28", "1e-26", "1e-24", "1e-23", "1e-22", "1e-20"]
LEAVES = [
    ["-1e-12", "-8.75e-13"],
    ["-8.75e-13", "-7.5e-13"],
    ["-7.5e-13", "-6.25e-13"],
    ["-6.25e-13", "-5e-13"],
    ["-5e-13", "-3.75e-13"],
    ["-3.75e-13", "-2.5e-13"],
    ["-2.5e-13", "-1.25e-13"],
    ["-1.25e-13", "0"],
    ["0", "1.25e-13"],
    ["1.25e-13", "2.5e-13"],
    ["2.5e-13", "3.75e-13"],
    ["3.75e-13", "5e-13"],
    ["5e-13", "6.25e-13"],
    ["6.25e-13", "7.5e-13"],
    ["7.5e-13", "8.75e-13"],
    ["8.75e-13", "1e-12"],
]

CERTIFIED = "R5_ALL_LEAVES_HESSIAN_KRAWCZYK_CERTIFIED"
NOT_CERTIFIED = "R5_ALL_LEAVES_HESSIAN_KRAWCZYK_NOT_CERTIFIED"
INCONCLUSIVE = "R5_ALL_LEAVES_HESSIAN_KRAWCZYK_INCONCLUSIVE"
BOUNDARY_MISMATCH = "R5_B2_INPUT_BOUNDARY_MISMATCH"
IMPLEMENTATION_ERROR = "R5_B2_IMPLEMENTATION_ERROR"
ALLOWED_STATUSES = {CERTIFIED, NOT_CERTIFIED, INCONCLUSIVE, BOUNDARY_MISMATCH, IMPLEMENTATION_ERROR}


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
    payload.pop("record_sha256", None)
    payload.get("software_environment", {}).pop("python", None)
    return payload


def check_upstream_identity() -> None:
    expected_files = {
        PARENT_PROTOCOL_PATH: preflight.EXPECTED_PARENT_PROTOCOL_SHA256,
        PROTOCOL_PATH: preflight.EXPECTED_PROTOCOL_SHA256,
        AUX_PATH: preflight.EXPECTED_AUXILIARY_SHA256,
        STATIC_CERT_PATH: preflight.EXPECTED_STATIC_CERT_SHA256,
        B1E_CERT_PATH: EXPECTED_B1E_CERT_SHA256,
        B1D_DIAG_PATH: EXPECTED_B1D_DIAG_SHA256,
        AFFINE_DIAG_PATH: EXPECTED_AFFINE_DIAG_SHA256,
        V074_SOURCE: preflight.EXPECTED_V074_SOURCE_SHA256,
    }
    for path, expected in expected_files.items():
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"upstream SHA mismatch for {path}: {actual} != {expected}")

    b1e = read_json(B1E_CERT_PATH)
    if (
        b1e.get("scientific_status") != b1e_builder.CERTIFIED
        or b1e.get("scope", {}).get("first_leaf_gates_pass") is not True
        or b1e.get("scope", {}).get("all_gates_pass") is not False
        or b1e.get("scope", {}).get("r5_certified") is not False
    ):
        raise RuntimeError(BOUNDARY_MISMATCH)


def injection() -> str:
    code = r'''
import os
import platform
from flint import arb_mat

r5_output = Path(os.environ["R5_B2_OUTPUT"])
r5_aux = json.loads(Path(os.environ["R5_B2_AUX"]).read_text(encoding="utf-8"))
r5_affine = json.loads(Path(os.environ["R5_B2_AFFINE"]).read_text(encoding="utf-8"))
r5_leaves = json.loads(os.environ["R5_B2_LEAVES"])
r5_eta_radii = json.loads(os.environ["R5_B2_ETA_RADII"])
r5_formal_radius = os.environ["R5_B2_FORMAL_RADIUS"]


def r5_arb(value):
    return arb(str(value))


def r5_mat(values):
    return [[r5_arb(item) for item in row] for row in values]


def r5_vec(values):
    return [r5_arb(item) for item in values]


def r5_identity(size):
    return [[arb(1) if i == j else arb(0) for j in range(size)] for i in range(size)]


def r5_matmul(left, right):
    return [[sum((left[r][k] * right[k][c] for k in range(len(right))), arb(0)) for c in range(len(right[0]))] for r in range(len(left))]


def r5_matvec(left, vec):
    return [sum((left[r][k] * vec[k] for k in range(len(vec))), arb(0)) for r in range(len(left))]


def r5_matsub(left, right):
    return [[left[r][c] - right[r][c] for c in range(len(left[0]))] for r in range(len(left))]


def r5_vec_abs_upper(vec):
    best = arb(0)
    for value in vec:
        upper = value.abs_upper()
        if upper > best:
            best = upper
    return best


def r5_inf_norm_upper(matrix):
    best = arb(0)
    for row in matrix:
        total = arb(0)
        for value in row:
            total += value.abs_upper()
        if total > best:
            best = total
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
    return str((value.lower() + value.upper()) / 2)


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
    return response_jacobian_and_gradient(phases)[0]


def r5_theta(t_value, b_values):
    objects = r5_aux["objects"]
    theta0 = r5_vec(objects["theta_0"])
    T = r5_mat(objects["T"])
    N = r5_mat(objects["N"])
    intrinsic = [t_value, arb(0), arb(0), arb(0), arb(0), arb(0)]
    tangent = r5_matvec(T, intrinsic)
    normal = r5_matvec(N, b_values)
    return [theta0[i] + tangent[i] + normal[i] for i in range(CONTROL_DIMENSION)]


def r5_theta_affine(theta_C, w, alpha, N, eta):
    return [theta_C[i] + w[i] * alpha + sum((N[i][j] * eta[j] for j in range(RESPONSE_DIMENSION)), arb(0)) for i in range(CONTROL_DIMENSION)]


def r5_F_from_theta(theta):
    objects = r5_aux["objects"]
    B = r5_mat(objects["B"])
    c = r5_vec(objects["c"])
    response = r5_response(theta)
    return r5_matvec(B, [response[i] - c[i] for i in range(RESPONSE_DIMENSION)])


def r5_F_t_b(t_value, b_values):
    return r5_F_from_theta(r5_theta(t_value, b_values))


def r5_JN_at_theta(theta):
    objects = r5_aux["objects"]
    B = r5_mat(objects["B"])
    N = r5_mat(objects["N"])
    return r5_matmul(r5_matmul(B, r5_response_jacobian(theta)), N)


def r5_Jalpha_at_theta(theta, direction):
    objects = r5_aux["objects"]
    B = r5_mat(objects["B"])
    return r5_matvec(r5_matmul(B, r5_response_jacobian(theta)), direction)


def r5_max_phase_displacement(theta_box):
    theta0 = r5_vec(r5_aux["objects"]["theta_0"])
    return r5_vec_abs_upper([theta_box[i] - theta0[i] for i in range(CONTROL_DIMENSION)])


def r5_strict_positive(value):
    return bool(value > arb(0) and not value.contains(arb(0)))


def r5_newton_correction(t_value):
    P = r5_mat(r5_aux["objects"]["P"])
    zero = [arb(0) for _ in range(RESPONSE_DIMENSION)]
    return [-value for value in r5_matvec(P, r5_F_t_b(t_value, zero))]


def alpha_matvec(matrix, vector):
    return [
        matrix[0][0] * vector[0] + matrix[0][1] * vector[1],
        matrix[1][0] * vector[0] + matrix[1][1] * vector[1],
    ]


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
            result.append(-result[0] * sum((self.c[k] * result[n - k] for k in range(1, n + 1)), DeltaJet(0)))
        return AlphaJet(result)

    def __truediv__(self, other):
        return self * AlphaJet(other).inv()

    def __rtruediv__(self, other):
        return AlphaJet(other) / self


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


def r5_leaf_status(gates):
    if gates["unique_root"]:
        return "CERTIFIED"
    if not gates["chart"]:
        return "CHART_FAILED"
    if not gates["no_wrap"]:
        return "NO_WRAP_FAILED"
    if not gates["J_eta_invertible"]:
        return "JACOBIAN_FAILED"
    if not gates["contraction"]:
        return "CONTRACTION_FAILED"
    if not gates["self_map"]:
        return "SELF_MAP_FAILED"
    return "INCONCLUSIVE"


def r5_formal_radius_record(radius_records):
    for item in radius_records:
        if item["r_eta"] == r5_formal_radius:
            return item
    raise RuntimeError("formal radius missing")


def r5_main():
    objects = r5_aux["objects"]
    P = r5_mat(objects["P"])
    B = r5_mat(objects["B"])
    T = r5_mat(objects["T"])
    N = r5_mat(objects["N"])
    Tv = [T[row][0] for row in range(CONTROL_DIMENSION)]
    S = r5_vec(r5_affine["candidate_slope"]["S"])
    NS = r5_matvec(N, S)
    w = [Tv[i] + NS[i] for i in range(CONTROL_DIMENSION)]
    B_inv = arb_mat(B).inv()
    B_defect = r5_matsub(r5_identity(RESPONSE_DIMENSION), r5_matmul([[B_inv[r, c] for c in range(RESPONSE_DIMENSION)] for r in range(RESPONSE_DIMENSION)], B))
    B_defect_norm = r5_inf_norm_upper(B_defect)

    leaf_records = []
    certified_count = 0
    worst_margin = None
    worst_leaf = None
    max_Y2 = arb(0)
    max_Y2_leaf = None
    max_Z = arb(0)
    max_Z_leaf = None

    for leaf_index, leaf_interval in enumerate(r5_leaves):
        left = r5_arb(leaf_interval[0])
        right = r5_arb(leaf_interval[1])
        a_C = (left + right) / 2
        alpha_radius = (right - left).abs_upper() / 2
        alpha = arb(0, str(alpha_radius.upper()))
        b_C = r5_newton_correction(a_C)
        theta_C = r5_theta(a_C, b_C)
        theta_alpha = r5_theta_affine(theta_C, w, alpha, N, [arb(0) for _ in range(RESPONSE_DIMENSION)])
        F0 = r5_F_from_theta(theta_C)
        J_alpha = r5_Jalpha_at_theta(theta_C, w)
        first_alpha = [alpha * value for value in J_alpha]
        Y0 = r5_vec_abs_upper(r5_matvec(P, F0))
        Y1 = r5_vec_abs_upper(r5_matvec(P, first_alpha))
        response_hessian = r5_response_directional_hessian(theta_C, w, alpha)
        B_response_hessian = r5_matvec(B, response_hessian)
        P_B_response_hessian = r5_matvec(P, B_response_hessian)
        H_alpha = r5_vec_abs_upper(P_B_response_hessian)
        alpha_radius_arb = r5_arb(str(alpha_radius.upper()))
        alpha_radius_squared = alpha_radius_arb * alpha_radius_arb
        Y2 = H_alpha * alpha_radius_squared / 2
        if Y2.abs_upper() > max_Y2:
            max_Y2 = Y2.abs_upper()
            max_Y2_leaf = leaf_index

        component_records = []
        for component in range(RESPONSE_DIMENSION):
            component_records.append({
                "component": component,
                "raw_D2R3_ww": r5_bound(response_hessian[component]),
                "after_B": r5_bound(B_response_hessian[component]),
                "after_P": r5_bound(P_B_response_hessian[component]),
                "lagrange_contribution_bound": r5_bound(P_B_response_hessian[component].abs_upper() * alpha_radius_squared / 2),
            })

        radius_records = []
        for radius_text in r5_eta_radii:
            r_eta = r5_arb(radius_text)
            eta = [arb(0, str(r_eta.upper())) for _ in range(RESPONSE_DIMENSION)]
            theta_total = r5_theta_affine(theta_C, w, alpha, N, eta)
            Y_eta_cross = arb(0)
            Y_total = Y0 + Y1 + Y2 + Y_eta_cross
            JN_box = r5_JN_at_theta(theta_total)
            JN_det = arb_mat(JN_box).det()
            Z_mat = r5_matsub(r5_identity(RESPONSE_DIMENSION), r5_matmul(P, JN_box))
            Z = r5_inf_norm_upper(Z_mat)
            if radius_text == r5_formal_radius and Z.abs_upper() > max_Z:
                max_Z = Z.abs_upper()
                max_Z_leaf = leaf_index
            Zr = Z * r_eta
            image_radius = Y_total + Zr
            margin = r_eta - image_radius
            if radius_text == r5_formal_radius and (worst_margin is None or margin.lower() < worst_margin.lower()):
                worst_margin = margin
                worst_leaf = leaf_index
            max_displacement = r5_max_phase_displacement(theta_total)
            chart_margin = arb(1) - max_displacement
            nowrap_margin = arb.pi() - max_displacement
            chart_gate = r5_strict_positive(chart_margin)
            nowrap_gate = r5_strict_positive(nowrap_margin)
            b_gate = bool(B_defect_norm < arb(1) and not B_defect_norm.contains(arb(1)))
            det_gate = bool(not JN_det.contains(arb(0)) and JN_det.abs_lower() > arb(0))
            contraction_gate = bool(Z < arb(1) and not Z.contains(arb(1)))
            self_map_gate = r5_strict_positive(margin)
            unique_root_gate = bool(self_map_gate and contraction_gate and chart_gate and nowrap_gate and b_gate and det_gate)
            radius_records.append({
                "r_eta": radius_text,
                "chart_margin_lower": str(chart_margin.lower()),
                "no_wrap_margin_lower": str(nowrap_margin.lower()),
                "B_inverse_defect_upper": str(B_defect_norm.abs_upper().upper()),
                "det_J_eta_enclosure": str(JN_det),
                "det_J_eta_abs_lower": str(JN_det.abs_lower().lower()),
                "Y0_center_residual": r5_bound(Y0),
                "Y1_first_order_cancellation_defect": r5_bound(Y1),
                "Y2_directional_hessian_lagrange": r5_bound(Y2),
                "Y_eta_cross": r5_bound(Y_eta_cross),
                "Y_eta_cross_policy": "zero because eta variation is handled by Z*r_eta in the Krawczyk linear term, not by interval-subtracted forcing",
                "Y_total": r5_bound(Y_total),
                "Z": r5_bound(Z),
                "Z_times_r_eta": r5_bound(Zr),
                "krawczyk_image_radius_upper": str(image_radius.abs_upper().upper()),
                "strict_self_map_margin": r5_bound(margin),
                "contraction_upper": str(Z.abs_upper().upper()),
                "gates": {
                    "chart": chart_gate,
                    "no_wrap": nowrap_gate,
                    "B_inverse": b_gate,
                    "J_eta_invertible": det_gate,
                    "self_map": self_map_gate,
                    "contraction": contraction_gate,
                    "unique_root": unique_root_gate,
                },
            })

        formal_record = r5_formal_radius_record(radius_records)
        leaf_status = r5_leaf_status(formal_record["gates"])
        if leaf_status == "CERTIFIED":
            certified_count += 1
        leaf_records.append({
            "leaf_index": leaf_index,
            "leaf_interval": leaf_interval,
            "endpoint_rule": "closed interval enclosure; adjacent branch gluing is deferred",
            "a_C": str(a_C),
            "alpha_radius": r5_bound(alpha_radius_arb),
            "b_C": r5_bound_vector(b_C),
            "S": r5_bound_vector(S),
            "w": r5_bound_vector(w),
            "P_F_at_center_inf_norm": r5_bound(Y0),
            "directional_hessian_components": component_records,
            "H_alpha": r5_bound(H_alpha),
            "Y0": r5_bound(Y0),
            "Y1": r5_bound(Y1),
            "Y2": r5_bound(Y2),
            "radius_records": radius_records,
            "formal_radius": r5_formal_radius,
            "formal_radius_status": leaf_status,
            "formal_radius_record": formal_record,
        })

    all_pass = certified_count == len(r5_leaves)
    if all_pass:
        status = "R5_ALL_LEAVES_HESSIAN_KRAWCZYK_CERTIFIED"
    elif certified_count < len(r5_leaves):
        status = "R5_ALL_LEAVES_HESSIAN_KRAWCZYK_NOT_CERTIFIED"
    else:
        status = "R5_ALL_LEAVES_HESSIAN_KRAWCZYK_INCONCLUSIVE"

    record = {
        "schema_version": "1.0",
        "record_id": "r5_all_leaves_hessian_krawczyk_v1_0",
        "record_kind": "prospective_r5_b2_all_leaves_hessian_krawczyk_preflight",
        "scientific_status": status,
        "arb_precision_bits": PRECISION_BITS,
        "base_commit": os.environ["R5_B2_BASE_COMMIT"],
        "software_environment": {"python": platform.python_version(), "python_flint": "0.8.0"},
        "inputs": {
            "parent_protocol_sha256": os.environ["R5_B2_PARENT_SHA"],
            "protocol_sha256": os.environ["R5_B2_PROTOCOL_SHA"],
            "auxiliary_sha256": os.environ["R5_B2_AUX_SHA"],
            "static_certificate_sha256": os.environ["R5_B2_STATIC_SHA"],
            "b1e_certificate_sha256": os.environ["R5_B2_B1E_SHA"],
            "affine_diagnostic_sha256": os.environ["R5_B2_AFFINE_SHA"],
            "v0_7_4_source_sha256": os.environ["R5_B2_V074_SHA"],
            "object_sha256": r5_aux["object_sha256"],
        },
        "frozen_protocol": {
            "leaf_list": r5_leaves,
            "leaf_order": "increasing t from -1e-12 to 1e-12",
            "endpoint_rule": "closed Arb intervals per leaf; overlap consistency deferred to B3",
            "center_rule": "a_C=(left+right)/2",
            "normal_center_rule": "b_C=-P*F(a_C,0) using frozen P and zero normal seed",
            "fixed_slope_source": "B1c/B1e S reused for every leaf without refit",
            "directional_hessian_formula": "Y2_i <= 1/2 sup ||P*B*D2R3(theta_C,i+(T*v+N*S)alpha)[w,w]||_inf * alpha_radius^2",
            "formal_eta_radius": r5_formal_radius,
            "eta_radii_predeclared": r5_eta_radii,
            "precision_bits": PRECISION_BITS,
            "result_adaptive_changes_allowed": False,
        },
        "method": {
            "equation": "F_i(alpha,eta)=B(R3(theta_C,i+(T*v+N*S)*alpha+N*eta)-c)",
            "w_definition": "w=T*v+N*S",
            "Y_total_decomposition": "Y0+Y1+Y2+Y_eta_cross",
            "Y2_source": "explicit directional-Hessian Lagrange remainder computed per leaf",
            "B1c_interval_subtraction_used_as_Y2": False,
            "finite_difference_used_as_strict_bound": False,
            "binary64_theorem_decision_used": False,
            "one_half_factor_included": True,
            "alpha_radius_squared_included": True,
            "Y_eta_cross_included": True,
            "eta_variation_handled_by_Z_times_radius": True,
        },
        "leaf_records": leaf_records,
        "summary": {
            "leaf_count": len(r5_leaves),
            "certified_leaf_count": certified_count,
            "worst_leaf_by_formal_self_map_margin": worst_leaf,
            "minimum_formal_self_map_margin": r5_bound(worst_margin if worst_margin is not None else arb(0)),
            "max_Y2_leaf": max_Y2_leaf,
            "max_Y2_abs_upper": r5_bound(max_Y2),
            "max_Z_leaf_at_formal_radius": max_Z_leaf,
            "max_Z_abs_upper_at_formal_radius": r5_bound(max_Z),
            "endpoint_or_branch_anomaly_detected": False,
            "can_enter_B3_gluing": all_pass,
        },
        "scope": {
            "all_leaf_local_root_gates_pass": all_pass,
            "r5_all_leaves_locally_certified": all_pass,
            "adjacent_leaf_gluing_certified": False,
            "full_path_continuity_certified": False,
            "positive_measure_nonconstancy_certified": False,
            "zero_cost_full_path_certified": False,
            "principle_r_r6_supplied": False,
            "r5_certified": False,
            "global_ode_flow_certified": False,
            "r6_search_performed": False,
            "normal_K1_residual_recovery_performed": False,
            "other_leaf_inspected_outside_frozen_16": False,
        },
    }
    payload = json.loads(json.dumps(record, sort_keys=True))
    payload.pop("record_sha256", None)
    payload.get("software_environment", {}).pop("python", None)
    record["record_sha256"] = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("utf-8")).hexdigest()
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
    with tempfile.TemporaryDirectory(prefix="r5_b2_all_leaves_") as tmp:
        output = Path(tmp) / "r5_all_leaves_hessian_krawczyk_v1_0.json"
        patched = Path(tmp) / "_r5_b2_backend.py"
        patched.write_text(patch_frozen_source(V074_SOURCE.read_bytes()), encoding="utf-8")
        env = dict(os.environ)
        env.update({
            "R5_B2_OUTPUT": str(output),
            "R5_B2_AUX": str(AUX_PATH),
            "R5_B2_AFFINE": str(AFFINE_DIAG_PATH),
            "R5_B2_BASE_COMMIT": EXPECTED_BASE_COMMIT,
            "R5_B2_PARENT_SHA": preflight.EXPECTED_PARENT_PROTOCOL_SHA256,
            "R5_B2_PROTOCOL_SHA": preflight.EXPECTED_PROTOCOL_SHA256,
            "R5_B2_AUX_SHA": preflight.EXPECTED_AUXILIARY_SHA256,
            "R5_B2_STATIC_SHA": preflight.EXPECTED_STATIC_CERT_SHA256,
            "R5_B2_B1E_SHA": EXPECTED_B1E_CERT_SHA256,
            "R5_B2_AFFINE_SHA": EXPECTED_AFFINE_DIAG_SHA256,
            "R5_B2_V074_SHA": preflight.EXPECTED_V074_SOURCE_SHA256,
            "R5_B2_LEAVES": json.dumps(LEAVES),
            "R5_B2_ETA_RADII": json.dumps(ETA_RADII),
            "R5_B2_FORMAL_RADIUS": FORMAL_RADIUS,
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
    target = CERT_PATH if record.get("scientific_status") == CERTIFIED else DIAG_PATH
    stale = DIAG_PATH if target == CERT_PATH else CERT_PATH
    if stale.exists():
        stale.unlink()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False) + "\n", encoding="utf-8")
    return target


def main() -> int:
    record = build_record()
    target = write_record(record)
    print(json.dumps({
        "scientific_status": record["scientific_status"],
        "target": str(target.relative_to(ROOT)),
        "record_sha256": record["record_sha256"],
        "certified_leaf_count": record["summary"]["certified_leaf_count"],
        "leaf_count": record["summary"]["leaf_count"],
        "worst_leaf_by_formal_self_map_margin": record["summary"]["worst_leaf_by_formal_self_map_margin"],
        "can_enter_B3_gluing": record["summary"]["can_enter_B3_gluing"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
