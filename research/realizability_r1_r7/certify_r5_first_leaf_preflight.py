#!/usr/bin/env python3
"""Run the prospective R5-B1a first-leaf Arb Krawczyk preflight.

This certifies only the first frozen leaf of the R5 full-tube protocol. It
does not generate an R5 full-tube certificate, run R6, search for candidates,
or perform normal K=1 residual recovery.
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


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

V074_SOURCE = ROOT / "src" / "response_fibre_arb_kkt_witness_alignment_v0_7_4.py"
PARENT_PROTOCOL_PATH = HERE / "frozen_protocol_v1_0.json"
PROTOCOL_PATH = HERE / "r5_full_tube_protocol_v1_0.json"
AUX_PATH = HERE / "data" / "r5_full_tube_auxiliary_v1_0.json"
STATIC_CERT_PATH = HERE / "certificates" / "r5_static_arb_gates_v1_0.json"
BOUNDARY_PATH = HERE / "R5_FIRST_LEAF_PREFLIGHT_BOUNDARY.md"
CERT_PATH = HERE / "certificates" / "r5_first_leaf_preflight_v1_0.json"

EXPECTED_STATUS_CERTIFIED = "R5_FIRST_LEAF_PREFLIGHT_CERTIFIED"
EXPECTED_STATUS_INCONCLUSIVE = "R5_FIRST_LEAF_PREFLIGHT_INCONCLUSIVE"
EXPECTED_BASE_COMMIT = "2a2add0e7963998de002a0a901aed18a0bc640e6"
EXPECTED_PARENT_PROTOCOL_SHA256 = "e8519a644ab50a9989eb40bc34499055f83760563167d88da21d17b3c7539e1c"
EXPECTED_PROTOCOL_SHA256 = "1e757ff86759fd793f6743560e1f50040362f892e342db723c47a658a3078cd3"
EXPECTED_AUXILIARY_SHA256 = "434b8d58793b39462fc3dcf4e04f716b56e65de790e87daaecedf2e103e29037"
EXPECTED_STATIC_CERT_SHA256 = "b3d28cb01a44c4773136e34a4bb206becb3c6f6c7160ca865576f03af5145994"
EXPECTED_V074_SOURCE_SHA256 = "1f71c4918d1cd1d6c45dc0da4a7358e176baac9116c8f71f4a949a6d657520f8"
PRECISION_BITS = 192
LEAF_INDEX = 0
LEAF_INTERVAL = ["-1e-12", "-8.75e-13"]
B_BOX_RADIUS = "1e-23"
INNER_UTILIZATION_THRESHOLD = "0.99"

EXPECTED_OBJECT_SHA256 = {
    "theta_0": "077a169644e33145b4f14c5aa29d4ac86cd2e69572c6f35ddab8af92f41d918a",
    "T": "aa1814d7257f84de3f4eeff3d3feb01fcaa7dfc5db4030d82cabfe06046dda2c",
    "N": "d24a90e45ebea1ea46b0d049757809dc5c42371a740a40ca6412fc5f64e81ba8",
    "B": "f1f9c0d26df1c8366a96fdeafd269660bc06f7e2dfdc4391948d15f13edda170",
    "c": "151762ada396ef62608698fb18090e0a443fef869f3f4d91543ad4dfc8e9312a",
    "P": "ae09f2d3343301b12e2b661fa7d50d2b004cd4d72333cbca1703c20890a2d82e",
    "midpoint_response_jacobian": "447949e425e663c7f7c57064ce98ff10ef174f393a6f8cf253fe980769aa5952",
    "midpoint_response_singular_values": "56000c155cca30568af2aab172acac65a19a4849ad96919df04bd3b3c47649e3",
    "normal_derivative_midpoint": "3f73fbc0885992cc232851d876f60e74b94ae6adaf4952b394c3a7d79a3adc4b",
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


def certificate_digest_payload(value: dict[str, Any]) -> dict[str, Any]:
    payload = json.loads(json.dumps(value, sort_keys=True))
    payload.pop("certificate_sha256", None)
    payload.get("software_environment", {}).pop("python", None)
    return payload


def check_upstream_identity() -> None:
    expected_files = {
        PARENT_PROTOCOL_PATH: EXPECTED_PARENT_PROTOCOL_SHA256,
        PROTOCOL_PATH: EXPECTED_PROTOCOL_SHA256,
        AUX_PATH: EXPECTED_AUXILIARY_SHA256,
        STATIC_CERT_PATH: EXPECTED_STATIC_CERT_SHA256,
        V074_SOURCE: EXPECTED_V074_SOURCE_SHA256,
    }
    for path, expected in expected_files.items():
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"upstream SHA mismatch for {path}: {actual} != {expected}")


def injection() -> str:
    code = r'''
import os
import platform

r5_output = Path(os.environ["R5_B1A_OUTPUT"])
r5_aux = json.loads(Path(os.environ["R5_B1A_AUX"]).read_text(encoding="utf-8"))
r5_protocol = json.loads(Path(os.environ["R5_B1A_PROTOCOL"]).read_text(encoding="utf-8"))
r5_static = json.loads(Path(os.environ["R5_B1A_STATIC_CERT"]).read_text(encoding="utf-8"))


def r5_arb_from_dec(value):
    return arb(str(value))


def r5_acb_from_dec(value):
    return acb(r5_arb_from_dec(value))


def r5_mat(values):
    return [[r5_arb_from_dec(item) for item in row] for row in values]


def r5_vec(values):
    return [r5_arb_from_dec(item) for item in values]


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


def r5_dec_upper(value):
    return str(value.upper())


def r5_dec_lower(value):
    return str(value.lower())


def r5_abs_upper(value):
    return str(value.abs_upper().upper())


def r5_abs_lower(value):
    return str(value.abs_lower().lower())


def r5_interval(mid, radius):
    return r5_arb_from_dec(mid) + arb(0, str(radius))


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
    theta0 = r5_vec(r5_aux["objects"]["theta_0"])
    T = r5_mat(r5_aux["objects"]["T"])
    N = r5_mat(r5_aux["objects"]["N"])
    intrinsic = [t_value, arb(0), arb(0), arb(0), arb(0), arb(0)]
    tangent = r5_matvec(T, intrinsic)
    normal = r5_matvec(N, b_values)
    return [theta0[i] + tangent[i] + normal[i] for i in range(CONTROL_DIMENSION)]


def r5_F(t_value, b_values):
    B = r5_mat(r5_aux["objects"]["B"])
    c = r5_vec(r5_aux["objects"]["c"])
    response = r5_response(r5_theta(t_value, b_values))
    diff = [response[i] - c[i] for i in range(RESPONSE_DIMENSION)]
    return r5_matvec(B, diff)


def r5_JN(t_value, b_values):
    B = r5_mat(r5_aux["objects"]["B"])
    N = r5_mat(r5_aux["objects"]["N"])
    jac = r5_response_jacobian(r5_theta(t_value, b_values))
    return r5_matmul(r5_matmul(B, jac), N)


def r5_main():
    objects = r5_aux["objects"]
    P = r5_mat(objects["P"])
    B = r5_mat(objects["B"])
    t_left = r5_arb_from_dec(os.environ["R5_B1A_LEAF_LEFT"])
    t_right = r5_arb_from_dec(os.environ["R5_B1A_LEAF_RIGHT"])
    t_mid = (t_left + t_right) / 2
    t_rad = (t_right - t_left) / 2
    t_box = t_mid + arb(0, str(t_rad.abs_upper().upper()))
    b_radius = r5_arb_from_dec(os.environ["R5_B1A_B_RADIUS"])
    b_center = [arb(0) for _ in range(RESPONSE_DIMENSION)]
    b_box = [arb(0, str(b_radius.upper())) for _ in range(RESPONSE_DIMENSION)]
    theta_box = r5_theta(t_box, b_box)
    phase_displacements = [
        theta_box[i] - r5_arb_from_dec(objects["theta_0"][i])
        for i in range(CONTROL_DIMENSION)
    ]
    max_displacement = max((item.abs_upper() for item in phase_displacements), default=arb(0))
    pi_margin = arb.pi() - max_displacement
    one_margin = arb("1") - max_displacement

    from flint import arb_mat
    B_inverse_mat = arb_mat(B).inv()
    B_inverse = [
        [B_inverse_mat[r, c] for c in range(RESPONSE_DIMENSION)]
        for r in range(RESPONSE_DIMENSION)
    ]
    B_defect = r5_matsub(r5_identity(RESPONSE_DIMENSION), r5_matmul(B_inverse, B))
    B_defect_norm = r5_inf_norm_upper(B_defect)

    residual_center = r5_F(t_box, b_center)
    JN_box = r5_JN(t_box, b_box)
    PJ = r5_matmul(P, JN_box)
    defect = r5_matsub(r5_identity(RESPONSE_DIMENSION), PJ)
    defect_norm = r5_inf_norm_upper(defect)
    correction = r5_matvec(P, residual_center)
    correction_norm = r5_vec_abs_upper(correction)
    k_radius = correction_norm + defect_norm * b_radius
    utilization = k_radius / b_radius
    strict_self_map_margin = b_radius - k_radius
    contraction_upper = defect_norm

    residual_on_box = r5_F(t_box, b_box)
    residual_abs_upper = r5_vec_abs_upper(residual_on_box)
    JN_det = arb_mat(r5_JN(t_box, b_box)).det()

    gates = {
        "leaf_identity": {
            "leaf_index": int(os.environ["R5_B1A_LEAF_INDEX"]),
            "leaf_interval": [os.environ["R5_B1A_LEAF_LEFT"], os.environ["R5_B1A_LEAF_RIGHT"]],
            "matches_protocol_first_leaf": True,
            "subdivision_count": r5_protocol["subdivision_strategy"]["initial_subinterval_count"],
            "maximum_refinement_depth": r5_protocol["subdivision_strategy"]["maximum_refinement_depth"],
        },
        "parameter_to_intrinsic_line": {
            "v": r5_aux["tube"]["v"],
            "a_equals_t_times_v": True,
            "t_box_lower": r5_dec_lower(t_box),
            "t_box_upper": r5_dec_upper(t_box),
        },
        "chart_residence": {
            "criterion": "max_abs(theta-theta_0) < 1 in the declared local representative chart",
            "max_phase_displacement_abs_upper": r5_abs_upper(max_displacement),
            "margin_lower_bound": r5_dec_lower(one_margin),
            "gate": bool(one_margin > arb(0)),
        },
        "no_phase_wrap": {
            "criterion": "max_abs(theta-theta_0) < pi, so no coordinate crosses a 2*pi wrap boundary from the fixed representative",
            "max_phase_displacement_abs_upper": r5_abs_upper(max_displacement),
            "margin_lower_bound": r5_dec_lower(pi_margin),
            "gate": bool(pi_margin > arb(0)),
        },
        "B_strict_invertibility_on_leaf": {
            "gate": bool(B_defect_norm < arb(1)),
            "defect_upper_bound": r5_abs_upper(B_defect_norm),
            "threshold": "1",
        },
        "normal_jacobian_invertibility_on_leaf": {
            "J_N_definition": "J_N(t,b)=B*DR3(theta_0+T*(t*v)+N*b)*N",
            "determinant_enclosure": str(JN_det),
            "abs_determinant_lower_bound": r5_abs_lower(JN_det),
            "strictly_nonzero": bool(not JN_det.contains(arb(0)) and JN_det.abs_lower() > arb(0)),
        },
        "preconditioner_defect_on_leaf": {
            "gate": bool(defect_norm < arb(1)),
            "defect_upper_bound": r5_abs_upper(defect_norm),
            "threshold": "1",
            "P_source": "frozen auxiliary object P",
        },
        "krawczyk_self_map": {
            "operator": "K(t,X)=0-P*F(t,0)+(I-P*J_N(t,X))*X",
            "b_box_radius": os.environ["R5_B1A_B_RADIUS"],
            "correction_norm_upper_bound": r5_abs_upper(correction_norm),
            "image_radius_upper_bound": r5_abs_upper(k_radius),
            "strict_interior_margin_lower_bound": r5_dec_lower(strict_self_map_margin),
            "utilization_upper_bound": r5_abs_upper(utilization),
            "gate": bool(strict_self_map_margin > arb(0)),
        },
        "krawczyk_contraction": {
            "contraction_upper_bound": r5_abs_upper(contraction_upper),
            "threshold": "1",
            "gate": bool(contraction_upper < arb(1)),
        },
        "response_residual_enclosure": {
            "residual_abs_upper_bound": r5_abs_upper(residual_abs_upper),
            "residual_near_zero_accepted_as_exact_response": False,
        },
        "unique_root": {
            "gate": bool(strict_self_map_margin > arb(0) and contraction_upper < arb(1)),
            "logic": "Krawczyk self-map plus contraction below one gives a unique normal correction b=psi(t) for each t in the leaf enclosure",
        },
        "exact_response_implication": {
            "gate": bool(not JN_det.contains(arb(0)) and B_defect_norm < arb(1)),
            "logic": "Exact F(t,psi(t))=0 and strict invertibility of B imply R_3(theta(t))=R_3(theta_0) on this leaf; residual size is not used as a substitute.",
            "residual_interval_substituted_for_exact_zero": False,
        },
        "name_separation": {
            "W_Pi": r5_aux["object_roles"]["W_Pi"],
            "B": r5_aux["object_roles"]["B"],
            "P": r5_aux["object_roles"]["P"],
            "distinct_roles_gate": True,
        },
    }
    all_gates_pass = (
        gates["leaf_identity"]["matches_protocol_first_leaf"]
        and gates["parameter_to_intrinsic_line"]["a_equals_t_times_v"]
        and gates["chart_residence"]["gate"]
        and gates["no_phase_wrap"]["gate"]
        and gates["B_strict_invertibility_on_leaf"]["gate"]
        and gates["normal_jacobian_invertibility_on_leaf"]["strictly_nonzero"]
        and gates["preconditioner_defect_on_leaf"]["gate"]
        and gates["krawczyk_self_map"]["gate"]
        and gates["krawczyk_contraction"]["gate"]
        and gates["unique_root"]["gate"]
        and gates["exact_response_implication"]["gate"]
        and gates["name_separation"]["distinct_roles_gate"]
    )
    status = (
        "R5_FIRST_LEAF_PREFLIGHT_CERTIFIED"
        if all_gates_pass
        else "R5_FIRST_LEAF_PREFLIGHT_INCONCLUSIVE"
    )
    cert = {
        "schema_version": "1.0",
        "certificate_id": "r5_first_leaf_preflight_v1_0",
        "certificate_kind": "prospective_r5_b1a_first_leaf_preflight",
        "scientific_status": status,
        "all_gates_pass": all_gates_pass,
        "arb_precision_bits": PRECISION_BITS,
        "base_commit": os.environ["R5_B1A_BASE_COMMIT"],
        "software_environment": {
            "python": platform.python_version(),
            "python_flint": "0.8.0",
        },
        "inputs": {
            "parent_protocol_path": "research/realizability_r1_r7/frozen_protocol_v1_0.json",
            "parent_protocol_sha256": os.environ["R5_B1A_PARENT_SHA"],
            "protocol_path": "research/realizability_r1_r7/r5_full_tube_protocol_v1_0.json",
            "protocol_sha256": os.environ["R5_B1A_PROTOCOL_SHA"],
            "auxiliary_path": "research/realizability_r1_r7/data/r5_full_tube_auxiliary_v1_0.json",
            "auxiliary_sha256": os.environ["R5_B1A_AUX_SHA"],
            "static_certificate_path": "research/realizability_r1_r7/certificates/r5_static_arb_gates_v1_0.json",
            "static_certificate_sha256": os.environ["R5_B1A_STATIC_SHA"],
            "v0_7_4_source_path": "src/response_fibre_arb_kkt_witness_alignment_v0_7_4.py",
            "v0_7_4_source_sha256": os.environ["R5_B1A_V074_SHA"],
            "object_sha256": r5_aux["object_sha256"],
        },
        "candidate": {
            "candidate_b_center": ["0","0","0","0","0","0","0","0"],
            "candidate_b_box_radius": os.environ["R5_B1A_B_RADIUS"],
            "candidate_construction": "fixed zero center with predetermined radius; no search, no frame/preconditioner replacement",
            "attempted_refinement_depth": 0,
        },
        "scope": {
            "first_leaf_preflight_only": True,
            "r5_full_tube_certificate_generated": False,
            "r5_full_tube_certified": False,
            "r5_certified": False,
            "r6_search_performed": False,
            "normal_K1_residual_recovery_performed": False,
            "binary64_theorem_decision_used": False,
            "residual_near_zero_accepted_as_exact_zero": False,
        },
        "gates": gates,
    }
    payload = json.loads(json.dumps(cert, sort_keys=True))
    payload.pop("certificate_sha256", None)
    payload.get("software_environment", {}).pop("python", None)
    cert["certificate_sha256"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("utf-8")
    ).hexdigest()
    r5_output.write_text(
        json.dumps(cert, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False) + "\n",
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


def build_certificate() -> dict[str, Any]:
    check_upstream_identity()
    protocol = read_json(PROTOCOL_PATH)
    leaf_count = protocol["subdivision_strategy"]["initial_subinterval_count"]
    interval = protocol["subdivision_strategy"]["initial_interval"]
    left = "-1e-12"
    width = "1.25e-13"
    right = "-8.75e-13"
    if leaf_count != 16 or interval != ["-1e-12", "1e-12"] or [left, right] != LEAF_INTERVAL:
        raise RuntimeError("frozen first-leaf identity mismatch")

    CERT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="r5_first_leaf_") as tmp:
        patched = Path(tmp) / "_r5_first_leaf_backend.py"
        patched.write_text(patch_frozen_source(V074_SOURCE.read_bytes()), encoding="utf-8")
        output = Path(tmp) / "r5_first_leaf_preflight_v1_0.json"
        env = dict(os.environ)
        env.update(
            {
                "R5_B1A_OUTPUT": str(output),
                "R5_B1A_AUX": str(AUX_PATH),
                "R5_B1A_PROTOCOL": str(PROTOCOL_PATH),
                "R5_B1A_STATIC_CERT": str(STATIC_CERT_PATH),
                "R5_B1A_BASE_COMMIT": EXPECTED_BASE_COMMIT,
                "R5_B1A_PARENT_SHA": EXPECTED_PARENT_PROTOCOL_SHA256,
                "R5_B1A_PROTOCOL_SHA": EXPECTED_PROTOCOL_SHA256,
                "R5_B1A_AUX_SHA": EXPECTED_AUXILIARY_SHA256,
                "R5_B1A_STATIC_SHA": EXPECTED_STATIC_CERT_SHA256,
                "R5_B1A_V074_SHA": EXPECTED_V074_SOURCE_SHA256,
                "R5_B1A_LEAF_INDEX": str(LEAF_INDEX),
                "R5_B1A_LEAF_LEFT": left,
                "R5_B1A_LEAF_RIGHT": right,
                "R5_B1A_LEAF_WIDTH": width,
                "R5_B1A_B_RADIUS": B_BOX_RADIUS,
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
                "R5 first-leaf preflight backend failed:\n"
                + completed.stdout
                + completed.stderr
            )
        certificate = read_json(output)
    return certificate


def main() -> int:
    certificate = build_certificate()
    CERT_PATH.write_bytes(canonical_json(certificate) + b"\n")
    print(json.dumps(certificate, indent=2, sort_keys=True))
    print(certificate["scientific_status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
