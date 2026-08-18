#!/usr/bin/env python3
"""R5-B1e first-leaf affine-Hessian Krawczyk verification.

This checks only the first frozen leaf and does not run R6, inspect other
leaves, perform normal K=1 recovery, or generate a full-tube R5 certificate.
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
import diagnose_r5_second_order_remainder as b1d_builder


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
B1D_DIAG_PATH = HERE / "diagnostics" / "r5_second_order_remainder_diagnostic_v1_0.json"
BOUNDARY_PATH = HERE / "R5_FIRST_LEAF_HESSIAN_KRAWCZYK_BOUNDARY.md"
CERT_PATH = HERE / "certificates" / "r5_first_leaf_hessian_krawczyk_v1_0.json"
DIAG_PATH = HERE / "diagnostics" / "r5_first_leaf_hessian_krawczyk_v1_0.json"

EXPECTED_BASE_COMMIT = "653097380b50c829e45c42a7dbb873bfc4352071"
EXPECTED_B1D_DIAG_SHA256 = "a678e21f9dae384bf3d1697d01f3beb42771d569f573e0a743824eec8dff1172"
EXPECTED_AFFINE_DIAG_SHA256 = b1d_builder.EXPECTED_AFFINE_DIAG_FILE_SHA256
EXPECTED_CENTER_DIAG_SHA256 = b1d_builder.EXPECTED_CENTER_DIAG_FILE_SHA256
EXPECTED_PREFLIGHT_CERT_SHA256 = b1d_builder.EXPECTED_PREFLIGHT_CERT_FILE_SHA256
PRECISION_BITS = 192
ETA_RADII = ["1e-30", "1e-28", "1e-26", "1e-24", "1e-23", "1e-22", "1e-20"]

CERTIFIED = "R5_FIRST_LEAF_HESSIAN_KRAWCZYK_CERTIFIED"
INCONCLUSIVE = "R5_FIRST_LEAF_HESSIAN_KRAWCZYK_INCONCLUSIVE"
BOUNDARY_FAILURE = "R5_B1E_IMPLEMENTATION_OR_BOUNDARY_FAILURE"
BOUNDARY_MISMATCH = "R5_B1E_INPUT_BOUNDARY_MISMATCH"
ALLOWED_STATUSES = {CERTIFIED, INCONCLUSIVE, BOUNDARY_FAILURE, BOUNDARY_MISMATCH}


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode()


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
        PREFLIGHT_CERT_PATH: EXPECTED_PREFLIGHT_CERT_SHA256,
        CENTER_DIAG_PATH: EXPECTED_CENTER_DIAG_SHA256,
        AFFINE_DIAG_PATH: EXPECTED_AFFINE_DIAG_SHA256,
        B1D_DIAG_PATH: EXPECTED_B1D_DIAG_SHA256,
        V074_SOURCE: preflight.EXPECTED_V074_SOURCE_SHA256,
    }
    for path, expected in expected_files.items():
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"upstream SHA mismatch for {path}: {actual} != {expected}")
    b1d = read_json(B1D_DIAG_PATH)
    hessian = b1d.get("analytic_directional_hessian", {})
    if (
        b1d.get("scientific_status") != "B1C_REMAINDER_DEPENDENCY_ARTIFACT"
        or hessian.get("whole_leaf_enclosure") is not True
        or hessian.get("w_definition") != "w = T*v + N*S"
        or hessian.get("one_half_factor_included") is not True
        or hessian.get("alpha_squared_factor_included") is not True
        or hessian.get("finite_difference_used") is not False
    ):
        raise RuntimeError(BOUNDARY_MISMATCH)


def injection() -> str:
    code = r'''
import os
import platform
from flint import arb_mat

r5_output = Path(os.environ["R5_B1E_OUTPUT"])
r5_aux = json.loads(Path(os.environ["R5_B1E_AUX"]).read_text(encoding="utf-8"))
r5_affine = json.loads(Path(os.environ["R5_B1E_AFFINE"]).read_text(encoding="utf-8"))
r5_b1d = json.loads(Path(os.environ["R5_B1E_B1D"]).read_text(encoding="utf-8"))
r5_eta_radii = json.loads(os.environ["R5_B1E_ETA_RADII"])


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


def r5_main():
    objects = r5_aux["objects"]
    P = r5_mat(objects["P"])
    B = r5_mat(objects["B"])
    T = r5_mat(objects["T"])
    N = r5_mat(objects["N"])
    Tv = [T[row][0] for row in range(CONTROL_DIMENSION)]
    left = r5_arb(os.environ["R5_B1E_LEAF_LEFT"])
    right = r5_arb(os.environ["R5_B1E_LEAF_RIGHT"])
    a_C = (left + right) / 2
    alpha_radius = (right - left).abs_upper() / 2
    alpha = arb(0, str(alpha_radius.upper()))
    b_C = r5_vec(r5_affine["candidate_center"]["b_C"])
    S = r5_vec(r5_affine["candidate_slope"]["S"])
    NS = r5_matvec(N, S)
    w = [Tv[i] + NS[i] for i in range(CONTROL_DIMENSION)]
    theta_C = r5_theta(a_C, b_C)
    theta_alpha = r5_theta_affine(theta_C, w, alpha, N, [arb(0) for _ in range(RESPONSE_DIMENSION)])
    F0 = r5_F_from_theta(theta_C)
    J_alpha = r5_Jalpha_at_theta(theta_C, w)
    first_alpha = [alpha * value for value in J_alpha]
    Y0 = r5_vec_abs_upper(r5_matvec(P, F0))
    Y1 = r5_vec_abs_upper(r5_matvec(P, first_alpha))
    Y2 = r5_arb(r5_b1d["analytic_directional_hessian"]["Y2_true_lagrange_bound"]["enclosure"])
    JN_C = r5_JN_at_theta(theta_C)
    B_inv = arb_mat(B).inv()
    B_defect = r5_matsub(r5_identity(RESPONSE_DIMENSION), r5_matmul([[B_inv[r, c] for c in range(RESPONSE_DIMENSION)] for r in range(RESPONSE_DIMENSION)], B))
    B_defect_norm = r5_inf_norm_upper(B_defect)

    records = []
    certified_any = False
    dominant_failures = {}
    for radius_text in r5_eta_radii:
        r_eta = r5_arb(radius_text)
        eta = [arb(0, str(r_eta.upper())) for _ in range(RESPONSE_DIMENSION)]
        theta_total = r5_theta_affine(theta_C, w, alpha, N, eta)
        # The Krawczyk forcing is evaluated at the eta-box centre:
        # -P*F(alpha, 0). Eta-dependent terms are not part of the forcing
        # radius; they are enclosed by Z*r_eta below through the interval
        # Jacobian J_eta(A,E). This avoids reintroducing B1c-style natural
        # interval subtraction as a fake correlated remainder.
        Y_eta_cross = arb(0)
        Y_total = Y0 + Y1 + Y2 + Y_eta_cross
        JN_box = r5_JN_at_theta(theta_total)
        JN_det = arb_mat(JN_box).det()
        Z_mat = r5_matsub(r5_identity(RESPONSE_DIMENSION), r5_matmul(P, JN_box))
        Z = r5_inf_norm_upper(Z_mat)
        Zr = Z * r_eta
        image_radius = Y_total + Zr
        margin = r_eta - image_radius
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
        if unique_root_gate:
            certified_any = True
        failure_items = {
            "center_residual": Y0,
            "first_order_defect": Y1,
            "second_order_curvature": Y2,
            "eta_cross_term": Y_eta_cross,
            "jacobian_defect_times_radius": Zr,
        }
        dominant = max(failure_items, key=lambda key: failure_items[key].abs_upper())
        if not unique_root_gate:
            if not chart_gate or not nowrap_gate:
                dominant = "chart/no-wrap"
            elif not contraction_gate or not det_gate:
                dominant = "Jacobian defect"
            dominant_failures[dominant] = dominant_failures.get(dominant, 0) + 1
        records.append({
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
            "dominant_failure_item": "none" if unique_root_gate else dominant,
        })

    status = "R5_FIRST_LEAF_HESSIAN_KRAWCZYK_CERTIFIED" if certified_any else "R5_FIRST_LEAF_HESSIAN_KRAWCZYK_INCONCLUSIVE"
    if certified_any:
        dominant_failure = "none"
    elif dominant_failures:
        dominant_failure = max(dominant_failures, key=lambda key: dominant_failures[key])
    else:
        dominant_failure = "unknown"
    record = {
        "schema_version": "1.0",
        "record_id": "r5_first_leaf_hessian_krawczyk_v1_0",
        "record_kind": "prospective_r5_b1e_first_leaf_hessian_krawczyk",
        "scientific_status": status,
        "arb_precision_bits": PRECISION_BITS,
        "base_commit": os.environ["R5_B1E_BASE_COMMIT"],
        "software_environment": {"python": platform.python_version(), "python_flint": "0.8.0"},
        "inputs": {
            "parent_protocol_sha256": os.environ["R5_B1E_PARENT_SHA"],
            "protocol_sha256": os.environ["R5_B1E_PROTOCOL_SHA"],
            "auxiliary_sha256": os.environ["R5_B1E_AUX_SHA"],
            "static_certificate_sha256": os.environ["R5_B1E_STATIC_SHA"],
            "first_leaf_preflight_sha256": os.environ["R5_B1E_PREFLIGHT_SHA"],
            "center_diagnostic_sha256": os.environ["R5_B1E_CENTER_SHA"],
            "affine_diagnostic_sha256": os.environ["R5_B1E_AFFINE_SHA"],
            "second_order_remainder_diagnostic_sha256": os.environ["R5_B1E_B1D_SHA"],
            "v0_7_4_source_sha256": os.environ["R5_B1E_V074_SHA"],
            "object_sha256": r5_aux["object_sha256"],
        },
        "frozen_scope": {
            "leaf_index": 0,
            "leaf_interval": [os.environ["R5_B1E_LEAF_LEFT"], os.environ["R5_B1E_LEAF_RIGHT"]],
            "theta_0_T_N_B_c_P_v_preserved": True,
            "b_C_from_B1c_preserved": True,
            "S_from_B1c_preserved": True,
            "eta_radii_predeclared": r5_eta_radii,
            "full_tube_protocol_modified": False,
        },
        "method": {
            "equation": "F(a,eta)=B(R3(theta0+T*(a*v)+N*(b_C+S*alpha+eta))-c)",
            "alpha_definition": "alpha=a-a_C",
            "b_predictor": "b_pred(a)=b_C+S*alpha",
            "w_definition": "w=T*v+N*S",
            "Y_total_decomposition": "Y0+Y1+Y2+Y_eta_cross",
            "Y2_source": "B1d explicit directional-Hessian Lagrange remainder",
            "B1c_interval_subtraction_used_as_Y2": False,
            "finite_difference_used_as_strict_bound": False,
            "binary64_theorem_decision_used": False,
            "one_half_factor_included": True,
            "alpha_radius_squared_included": True,
            "Y_eta_cross_included": True,
            "eta_variation_handled_by_Z_times_radius": True,
        },
        "global_quantities": {
            "alpha_radius": r5_bound(r5_arb(str(alpha_radius.upper()))),
            "b_C": r5_affine["candidate_center"]["b_C"],
            "S": r5_affine["candidate_slope"]["S"],
            "w": [str((value.lower() + value.upper()) / 2) for value in w],
            "Y0": r5_bound(Y0),
            "Y1": r5_bound(Y1),
            "Y2": r5_bound(Y2),
        },
        "radius_records": records,
        "dominant_failure_item": dominant_failure,
        "scope": {
            "first_leaf_only": True,
            "first_leaf_gates_pass": certified_any,
            "r5_first_leaf_certified": certified_any,
            "r5_full_tube_certificate_generated": False,
            "r5_certified": False,
            "all_gates_pass": False,
            "r6_search_performed": False,
            "normal_K1_residual_recovery_performed": False,
            "other_leaf_inspected": False,
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
    b1d = read_json(B1D_DIAG_PATH)
    out_path = CERT_PATH if False else DIAG_PATH
    with tempfile.TemporaryDirectory(prefix="r5_b1e_hessian_krawczyk_") as tmp:
        output = Path(tmp) / "r5_first_leaf_hessian_krawczyk_v1_0.json"
        patched = Path(tmp) / "_r5_b1e_backend.py"
        patched.write_text(patch_frozen_source(V074_SOURCE.read_bytes()), encoding="utf-8")
        env = dict(os.environ)
        env.update({
            "R5_B1E_OUTPUT": str(output),
            "R5_B1E_AUX": str(AUX_PATH),
            "R5_B1E_AFFINE": str(AFFINE_DIAG_PATH),
            "R5_B1E_B1D": str(B1D_DIAG_PATH),
            "R5_B1E_BASE_COMMIT": EXPECTED_BASE_COMMIT,
            "R5_B1E_PARENT_SHA": preflight.EXPECTED_PARENT_PROTOCOL_SHA256,
            "R5_B1E_PROTOCOL_SHA": preflight.EXPECTED_PROTOCOL_SHA256,
            "R5_B1E_AUX_SHA": preflight.EXPECTED_AUXILIARY_SHA256,
            "R5_B1E_STATIC_SHA": preflight.EXPECTED_STATIC_CERT_SHA256,
            "R5_B1E_PREFLIGHT_SHA": EXPECTED_PREFLIGHT_CERT_SHA256,
            "R5_B1E_CENTER_SHA": EXPECTED_CENTER_DIAG_SHA256,
            "R5_B1E_AFFINE_SHA": EXPECTED_AFFINE_DIAG_SHA256,
            "R5_B1E_B1D_SHA": EXPECTED_B1D_DIAG_SHA256,
            "R5_B1E_V074_SHA": preflight.EXPECTED_V074_SOURCE_SHA256,
            "R5_B1E_LEAF_LEFT": preflight.LEAF_INTERVAL[0],
            "R5_B1E_LEAF_RIGHT": preflight.LEAF_INTERVAL[1],
            "R5_B1E_ETA_RADII": json.dumps(ETA_RADII),
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
        "dominant_failure_item": record["dominant_failure_item"],
        "certified_radii": [item["r_eta"] for item in record["radius_records"] if item["gates"]["unique_root"]],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
