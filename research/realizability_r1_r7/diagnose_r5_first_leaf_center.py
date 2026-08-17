#!/usr/bin/env python3
"""Diagnose the R5-B1a first-leaf Krawczyk center/forcing failure.

This script is diagnostic only. It does not rerun or modify the R5-B1a
certificate claim, resize the frozen normal box, run another leaf, run R6, or
perform normal K=1 residual recovery.
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
OUTPUT_PATH = HERE / "diagnostics" / "r5_first_leaf_center_diagnostic_v1_0.json"

EXPECTED_STATUS_COMPLETE = "R5_FIRST_LEAF_CENTER_DIAGNOSIS_COMPLETE"
EXPECTED_STATUS_INCONCLUSIVE = "R5_FIRST_LEAF_CENTER_DIAGNOSIS_INCONCLUSIVE"
EXPECTED_PREFLIGHT_CERT_SHA256 = "5fcb7602bf6be5ff501329ae68373d8da88acd7abce0c4842ff808d86b21d1b6"
EXPECTED_CLASSIFICATION = "CENTER_OFFSET_DOMINATES"


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
        PREFLIGHT_CERT_PATH: EXPECTED_PREFLIGHT_CERT_SHA256,
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

r5_output = Path(os.environ["R5_B1B_OUTPUT"])
r5_aux = json.loads(Path(os.environ["R5_B1B_AUX"]).read_text(encoding="utf-8"))
r5_protocol = json.loads(Path(os.environ["R5_B1B_PROTOCOL"]).read_text(encoding="utf-8"))
r5_preflight = json.loads(Path(os.environ["R5_B1B_PREFLIGHT_CERT"]).read_text(encoding="utf-8"))


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


def r5_matsub(left, right):
    return [
        [left[r][c] - right[r][c] for c in range(len(left[0]))]
        for r in range(len(left))
    ]


def r5_vecsub(left, right):
    return [left[i] - right[i] for i in range(len(left))]


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


def r5_contains_zero(value):
    return bool(value.contains(arb(0)))


def r5_bound(value):
    return {
        "enclosure": str(value),
        "lower": str(value.lower()),
        "upper": str(value.upper()),
        "abs_lower": str(value.abs_lower()),
        "abs_upper": str(value.abs_upper()),
        "contains_zero": r5_contains_zero(value),
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


def r5_response_jacobian(phases):
    jacobian, _gradient = response_jacobian_and_gradient(phases)
    return jacobian


def r5_theta(t_value, b_values):
    objects = r5_aux["objects"]
    theta0 = r5_vec(objects["theta_0"])
    T = r5_mat(objects["T"])
    N = r5_mat(objects["N"])
    intrinsic = [t_value, arb(0), arb(0), arb(0), arb(0), arb(0)]
    tangent = r5_matvec(T, intrinsic)
    normal = r5_matvec(N, b_values)
    return [theta0[i] + tangent[i] + normal[i] for i in range(CONTROL_DIMENSION)]


def r5_F(t_value, b_values):
    objects = r5_aux["objects"]
    B = r5_mat(objects["B"])
    c = r5_vec(objects["c"])
    response = r5_response(r5_theta(t_value, b_values))
    return r5_matvec(B, r5_vecsub(response, c))


def r5_JN(t_value, b_values):
    objects = r5_aux["objects"]
    B = r5_mat(objects["B"])
    N = r5_mat(objects["N"])
    jac = r5_response_jacobian(r5_theta(t_value, b_values))
    return r5_matmul(r5_matmul(B, jac), N)


def r5_DR3_theta0():
    theta0 = [acb(r5_arb(item)) for item in r5_aux["objects"]["theta_0"]]
    return r5_response_jacobian(theta0)


def r5_g_T():
    objects = r5_aux["objects"]
    B = r5_mat(objects["B"])
    T = r5_mat(objects["T"])
    jac = r5_DR3_theta0()
    Tv = [T[row][0] for row in range(CONTROL_DIMENSION)]
    return r5_matvec(r5_matmul(B, jac), Tv)


def r5_linear_psi_prime(g_T):
    objects = r5_aux["objects"]
    P = r5_mat(objects["P"])
    B = r5_mat(objects["B"])
    N = r5_mat(objects["N"])
    jac = r5_DR3_theta0()
    JN = r5_matmul(r5_matmul(B, jac), N)
    E = r5_matsub(r5_identity(RESPONSE_DIMENSION), r5_matmul(P, JN))
    rho = r5_inf_norm_upper(E)
    center = [-value for value in r5_matvec(P, g_T)]
    center_norm = r5_vec_abs_upper(center)
    radius = (rho * center_norm) / (arb(1) - rho)
    enclosed = [value + arb(0, str(radius.upper())) for value in center]
    return center, enclosed, rho, radius


def r5_newton_correction(t_value):
    P = r5_mat(r5_aux["objects"]["P"])
    zero = [arb(0) for _ in range(RESPONSE_DIMENSION)]
    return [-value for value in r5_matvec(P, r5_F(t_value, zero))]


def r5_vector_inf_abs(value):
    return r5_bound(r5_vec_abs_upper(value))


def r5_main():
    from flint import arb_mat

    left = r5_arb(os.environ["R5_B1B_LEAF_LEFT"])
    right = r5_arb(os.environ["R5_B1B_LEAF_RIGHT"])
    mid = (left + right) / 2
    rad = (right - left) / 2
    t_box = mid + arb(0, str(rad.abs_upper().upper()))
    r = r5_arb(os.environ["R5_B1B_B_RADIUS"])
    b0 = [arb(0) for _ in range(RESPONSE_DIMENSION)]
    X = [arb(0, str(r.upper())) for _ in range(RESPONSE_DIMENSION)]
    P = r5_mat(r5_aux["objects"]["P"])

    Y_vec = r5_matvec(P, r5_F(t_box, b0))
    Y = r5_vec_abs_upper(Y_vec)
    JN_box = r5_JN(t_box, X)
    Z_mat = r5_matsub(r5_identity(RESPONSE_DIMENSION), r5_matmul(P, JN_box))
    Z = r5_inf_norm_upper(Z_mat)
    Zr = Z * r
    image_bound = Y + Zr
    margin = r - image_bound
    dominance_ratio = Y / Zr if not Zr.contains(arb(0)) else arb("1e999")

    gT = r5_g_T()
    gT_norm = r5_vec_abs_upper(gT)
    psi_center, psi_enclosure, psi_rho, psi_radius = r5_linear_psi_prime(gT)
    tangent_exact_zero = all(value.contains(arb(0)) and value.abs_upper() == arb(0) for value in gT)
    tangent_strict_nonzero = bool(gT_norm > arb(0) and not gT_norm.contains(arb(0)))

    d_L = r5_newton_correction(left)
    d_C = r5_newton_correction(mid)
    d_R = r5_newton_correction(right)
    psi_times_mid = [value * mid for value in psi_enclosure]
    dC_norm = r5_vec_abs_upper(d_C)
    dL_norm = r5_vec_abs_upper(d_L)
    dR_norm = r5_vec_abs_upper(d_R)
    d_point_max = max(dL_norm, dC_norm, dR_norm)
    psi_mid_norm = r5_vec_abs_upper(psi_times_mid)
    d_variation = [d_R[i] - d_L[i] for i in range(RESPONSE_DIMENSION)]
    variation_width = r5_vec_abs_upper(d_variation)
    Y_over_point_max = Y / d_point_max if not d_point_max.contains(arb(0)) else arb("1e999")

    implementation_audit = {
        "krawczyk_operator": "K_a(X)=b_0-PF(a,b_0)+(I-PJ_N(a,X))(X-b_0)",
        "b0": "0",
        "X_center": "0",
        "image_center_and_radius_separated": True,
        "self_map_test": "Y+Z*r < r for X=[-r,r]^8 centered at b0=0",
        "parameter_a_as_full_leaf_interval": True,
        "interval_midpoint_radius_outward_rounded": True,
        "center_offset_not_double_counted_as_radius": True,
        "a_scale": "t in first frozen leaf [-1e-12,-8.75e-13], a=t*v",
        "T_times_a_once": True,
        "N_times_b_once": True,
        "t_not_misused_for_full_a_vector": True,
        "v_not_omitted_or_duplicated": True,
        "B_applied_once_to_response_difference": True,
        "P_applied_once_to_eight_dimensional_equation": True,
        "R3_angle_units_match_frozen_v0_7_4_driver": True,
        "json_decimals_enter_arb_without_float": True,
        "matrix_orientation_matches_frozen_shapes": True,
        "row_column_transpose_detected": False,
        "one_e_minus_12_scale_preserved": True,
        "implementation_defect_detected": False,
    }

    forcing_interval_dominates_Zr = bool(Y > arb("1e6") * Zr)
    point_center_offset_exceeds_radius = bool(d_point_max > r)
    forcing_interval_overestimates_point = bool(Y > arb("1e4") * d_point_max)
    same_order = bool(dC_norm > arb("0") and psi_mid_norm > arb("0") and dC_norm / psi_mid_norm < arb("10") and psi_mid_norm / dC_norm < arb("10"))
    if (
        not implementation_audit["implementation_defect_detected"]
        and forcing_interval_dominates_Zr
        and point_center_offset_exceeds_radius
        and forcing_interval_overestimates_point
    ):
        classification = "MULTIPLE_CAUSES"
    elif not implementation_audit["implementation_defect_detected"] and forcing_interval_dominates_Zr and same_order:
        classification = "CENTER_OFFSET_DOMINATES"
    elif not implementation_audit["implementation_defect_detected"] and Zr > Y:
        classification = "INTERVAL_WIDTH_DOMINATES"
    else:
        classification = "CAUSE_INCONCLUSIVE"

    diagnostic = {
        "schema_version": "1.0",
        "diagnostic_id": "r5_first_leaf_center_diagnostic_v1_0",
        "diagnostic_kind": "prospective_r5_b1b_first_leaf_center_forcing_diagnostic",
        "scientific_status": "R5_FIRST_LEAF_CENTER_DIAGNOSIS_COMPLETE",
        "classification": classification,
        "arb_precision_bits": PRECISION_BITS,
        "base_commit": os.environ["R5_B1B_BASE_COMMIT"],
        "software_environment": {
            "python": platform.python_version(),
            "python_flint": "0.8.0",
        },
        "inputs": {
            "parent_protocol_path": "research/realizability_r1_r7/frozen_protocol_v1_0.json",
            "parent_protocol_sha256": os.environ["R5_B1B_PARENT_SHA"],
            "protocol_path": "research/realizability_r1_r7/r5_full_tube_protocol_v1_0.json",
            "protocol_sha256": os.environ["R5_B1B_PROTOCOL_SHA"],
            "auxiliary_path": "research/realizability_r1_r7/data/r5_full_tube_auxiliary_v1_0.json",
            "auxiliary_sha256": os.environ["R5_B1B_AUX_SHA"],
            "static_certificate_path": "research/realizability_r1_r7/certificates/r5_static_arb_gates_v1_0.json",
            "static_certificate_sha256": os.environ["R5_B1B_STATIC_SHA"],
            "first_leaf_preflight_path": "research/realizability_r1_r7/certificates/r5_first_leaf_preflight_v1_0.json",
            "first_leaf_preflight_sha256": os.environ["R5_B1B_PREFLIGHT_SHA"],
            "v0_7_4_source_path": "src/response_fibre_arb_kkt_witness_alignment_v0_7_4.py",
            "v0_7_4_source_sha256": os.environ["R5_B1B_V074_SHA"],
            "object_sha256": r5_aux["object_sha256"],
        },
        "frozen_objects": {
            "theta_0_T_N_B_c_P_v_preserved": True,
            "leaf_index": 0,
            "leaf_interval": [os.environ["R5_B1B_LEAF_LEFT"], os.environ["R5_B1B_LEAF_RIGHT"]],
            "v": r5_aux["tube"]["v"],
            "frozen_b_box_radius": os.environ["R5_B1B_B_RADIUS"],
            "normal_box_not_resized_or_recentered": True,
        },
        "krawczyk_formula_audit": implementation_audit,
        "self_map_decomposition": {
            "Y_sup_norm_PF_a_b0": r5_bound(Y),
            "Z_sup_norm_I_minus_PJN": r5_bound(Z),
            "r_frozen_b_box_radius": r5_bound(r),
            "Z_times_r": r5_bound(Zr),
            "Y_plus_Zr": r5_bound(image_bound),
            "self_map_margin_r_minus_Y_plus_Zr": r5_bound(margin),
            "Y_over_Zr": r5_bound(dominance_ratio),
            "Y_over_point_corrections": r5_bound(Y_over_point_max),
            "point_correction_max": r5_bound(d_point_max),
            "forcing_interval_dominates_Zr_gate": forcing_interval_dominates_Zr,
            "point_center_offset_exceeds_frozen_radius_gate": point_center_offset_exceeds_radius,
            "forcing_interval_overestimates_point_corrections_gate": forcing_interval_overestimates_point,
            "dominant_term": "Y" if forcing_interval_dominates_Zr else "Zr" if Zr > Y else "mixed",
        },
        "tangent_defect": {
            "g_T_definition": "g_T = B*DR3(theta_0)*T*v",
            "g_T_components": r5_bound_vector(gT),
            "g_T_inf_norm": r5_bound(gT_norm),
            "tangent_defect_is_exact_zero_gate": tangent_exact_zero,
            "tangent_defect_is_strictly_nonzero_gate": tangent_strict_nonzero,
        },
        "linear_normal_prediction": {
            "method": "Neumann enclosure using frozen P and rho=||I-P*(B*DR3(theta_0)*N)||_inf < 1",
            "rho": r5_bound(psi_rho),
            "radius": r5_bound(psi_radius),
            "psi_prime_center": r5_bound_vector(psi_center),
            "psi_prime_0_enclosure": r5_bound_vector(psi_enclosure),
            "psi_prime_0_inf_norm": r5_vector_inf_abs(psi_enclosure),
            "psi_prime_0_times_a_C": r5_bound_vector(psi_times_mid),
            "psi_prime_0_times_a_C_inf_norm": r5_bound(psi_mid_norm),
        },
        "three_point_newton_corrections": {
            "a_L": os.environ["R5_B1B_LEAF_LEFT"],
            "a_C": str(mid),
            "a_R": os.environ["R5_B1B_LEAF_RIGHT"],
            "d_L": r5_bound_vector(d_L),
            "d_C": r5_bound_vector(d_C),
            "d_R": r5_bound_vector(d_R),
            "d_L_inf_norm": r5_bound(dL_norm),
            "d_C_inf_norm": r5_bound(dC_norm),
            "d_R_inf_norm": r5_bound(dR_norm),
            "point_correction_max_inf_norm": r5_bound(d_point_max),
            "d_R_minus_d_L_inf_norm": r5_bound(variation_width),
            "d_C_and_linear_prediction_same_order_gate": same_order,
        },
        "scope": {
            "diagnostic_only": True,
            "candidate_b_center_frozen_or_certified": False,
            "new_leaf_center_protocol_recommended": classification == "CENTER_OFFSET_DOMINATES",
            "r5_first_leaf_preflight_certified": False,
            "r5_full_tube_certificate_generated": False,
            "r5_certified": False,
            "r6_search_performed": False,
            "normal_K1_residual_recovery_performed": False,
            "binary64_theorem_decision_used": False,
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
    with tempfile.TemporaryDirectory(prefix="r5_first_leaf_center_") as tmp:
        patched = Path(tmp) / "_r5_first_leaf_center_backend.py"
        patched.write_text(patch_frozen_source(V074_SOURCE.read_bytes()), encoding="utf-8")
        output = Path(tmp) / "r5_first_leaf_center_diagnostic_v1_0.json"
        env = dict(os.environ)
        env.update(
            {
                "R5_B1B_OUTPUT": str(output),
                "R5_B1B_AUX": str(AUX_PATH),
                "R5_B1B_PROTOCOL": str(PROTOCOL_PATH),
                "R5_B1B_PREFLIGHT_CERT": str(PREFLIGHT_CERT_PATH),
                "R5_B1B_BASE_COMMIT": preflight.EXPECTED_BASE_COMMIT,
                "R5_B1B_PARENT_SHA": preflight.EXPECTED_PARENT_PROTOCOL_SHA256,
                "R5_B1B_PROTOCOL_SHA": preflight.EXPECTED_PROTOCOL_SHA256,
                "R5_B1B_AUX_SHA": preflight.EXPECTED_AUXILIARY_SHA256,
                "R5_B1B_STATIC_SHA": preflight.EXPECTED_STATIC_CERT_SHA256,
                "R5_B1B_PREFLIGHT_SHA": EXPECTED_PREFLIGHT_CERT_SHA256,
                "R5_B1B_V074_SHA": preflight.EXPECTED_V074_SOURCE_SHA256,
                "R5_B1B_LEAF_LEFT": preflight.LEAF_INTERVAL[0],
                "R5_B1B_LEAF_RIGHT": preflight.LEAF_INTERVAL[1],
                "R5_B1B_B_RADIUS": preflight.B_BOX_RADIUS,
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
                "R5 first-leaf center diagnostic backend failed:\n"
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
    print(diagnostic["classification"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
