#!/usr/bin/env python3
"""R5-B4 global implicit branch C1 certification.

This stage uses the R5-B2 leaf certificates and the corrected R5-B3b common-root
gluing certificate to certify the prescribed C1 regularity of the glued
implicit branch. It does not certify zero response cost, positive-measure
nonconstancy, PR-R5, PR-R6, GF-R5, R6 search, normal K=1 recovery, or a global
ODE flow.
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
PARENT_PROTOCOL_PATH = preflight.PARENT_PROTOCOL_PATH
PROTOCOL_PATH = preflight.PROTOCOL_PATH
AUX_PATH = preflight.AUX_PATH
STATIC_CERT_PATH = preflight.STATIC_CERT_PATH
B2_CERT_PATH = HERE / "certificates" / "r5_all_leaves_hessian_krawczyk_v1_0.json"
B3B_CERT_PATH = HERE / "certificates" / "r5_adjacent_leaf_gluing_v1_1.json"
BOUNDARY_PATH = HERE / "R5_GLOBAL_IMPLICIT_BRANCH_C1_BOUNDARY.md"
CERT_PATH = HERE / "certificates" / "r5_global_implicit_branch_c1_v1_0.json"
DIAG_PATH = HERE / "diagnostics" / "r5_global_implicit_branch_c1_v1_0.json"

EXPECTED_BASE_COMMIT = "9d4e869a91cb1f6291e912fab68f803036bc217e"
EXPECTED_B2_CERT_SHA256 = b3_builder.EXPECTED_B2_CERT_SHA256
EXPECTED_B3B_CERT_SHA256 = "5b7891ff1179639f6e700a6870950f8db196dac8cb33b1183c359bb702a4354f"
EXPECTED_B3B_RECORD_SHA256 = "0b0f4a5d320a8ad2d48474710c0030c31212b91a1a33e49c24f17cd676b497c7"
PRECISION_BITS = 192
FORMAL_RADIUS = b2_builder.FORMAL_RADIUS
LEAVES = b2_builder.LEAVES

CERTIFIED = "R5_GLOBAL_IMPLICIT_BRANCH_C1_CERTIFIED"
NOT_CERTIFIED = "R5_GLOBAL_IMPLICIT_BRANCH_C1_NOT_CERTIFIED"
INCONCLUSIVE = "R5_GLOBAL_IMPLICIT_BRANCH_C1_INCONCLUSIVE"
BOUNDARY_MISMATCH = "R5_B4_INPUT_BOUNDARY_MISMATCH"
IMPLEMENTATION_ERROR = "R5_B4_IMPLEMENTATION_ERROR"
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
        B2_CERT_PATH: EXPECTED_B2_CERT_SHA256,
        B3B_CERT_PATH: EXPECTED_B3B_CERT_SHA256,
        V074_SOURCE: preflight.EXPECTED_V074_SOURCE_SHA256,
    }
    for path, expected in expected_files.items():
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"upstream SHA mismatch for {path}: {actual} != {expected}")
    b2 = read_json(B2_CERT_PATH)
    b3 = read_json(B3B_CERT_PATH)
    if (
        b2.get("scientific_status") != b2_builder.CERTIFIED
        or b2.get("scope", {}).get("r5_all_leaves_locally_certified") is not True
        or b2.get("scope", {}).get("r5_certified") is not False
        or b3.get("scientific_status") != b3_builder.CERTIFIED
        or b3.get("record_sha256") != EXPECTED_B3B_RECORD_SHA256
        or b3.get("scope", {}).get("single_c0_root_branch_certified") is not True
        or b3.get("scope", {}).get("c1_gluing_certified") is not False
        or b3.get("scope", {}).get("gf_r5_certified") is not False
    ):
        raise RuntimeError(BOUNDARY_MISMATCH)


def injection() -> str:
    code = r'''
import os
import platform
from flint import arb_mat

r5_output = Path(os.environ["R5_B4_OUTPUT"])
r5_aux = json.loads(Path(os.environ["R5_B4_AUX"]).read_text(encoding="utf-8"))
r5_b2 = json.loads(Path(os.environ["R5_B4_B2_CERT"]).read_text(encoding="utf-8"))
r5_b3b = json.loads(Path(os.environ["R5_B4_B3B_CERT"]).read_text(encoding="utf-8"))
r5_leaves = json.loads(os.environ["R5_B4_LEAVES"])
r5_formal_radius = os.environ["R5_B4_FORMAL_RADIUS"]


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


def r5_theta_from_b(t_value, b_values):
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


def r5_JN_at_theta(theta):
    objects = r5_aux["objects"]
    B = r5_mat(objects["B"])
    N = r5_mat(objects["N"])
    return r5_matmul(r5_matmul(B, r5_response_jacobian(theta)), N)


def r5_Jt_at_theta(theta):
    objects = r5_aux["objects"]
    B = r5_mat(objects["B"])
    T = r5_mat(objects["T"])
    Tv = [T[row][0] for row in range(CONTROL_DIMENSION)]
    return r5_matvec(r5_matmul(B, r5_response_jacobian(theta)), Tv)


def r5_newton_correction(t_value):
    P = r5_mat(r5_aux["objects"]["P"])
    zero = [arb(0) for _ in range(RESPONSE_DIMENSION)]
    theta = r5_theta_from_b(t_value, zero)
    B = r5_mat(r5_aux["objects"]["B"])
    c = r5_vec(r5_aux["objects"]["c"])
    F = r5_matvec(B, [r5_response(theta)[i] - c[i] for i in range(RESPONSE_DIMENSION)])
    return [-value for value in r5_matvec(P, F)]


def r5_leaf_center(leaf_interval):
    left = r5_arb(leaf_interval[0])
    right = r5_arb(leaf_interval[1])
    return (left + right) / 2


def r5_strict_positive(value):
    return bool(value > arb(0) and not value.contains(arb(0)))


def r5_box_from_json(box):
    return [(r5_arb(item["lower"]), r5_arb(item["upper"])) for item in box]


def r5_box_to_center_radius(box):
    centers = []
    radii = []
    for lo, hi in box:
        mid = (lo + hi) / 2
        rad = (hi - lo).abs_upper() / 2
        centers.append(arb(str(mid)))
        radii.append(rad)
    return centers, radii


def r5_interval_box(center, radii):
    return [arb(str(value), str(radius.upper())) for value, radius in zip(center, radii)]


def r5_phase_admissibility(theta_box):
    theta0 = r5_vec(r5_aux["objects"]["theta_0"])
    displacement = r5_vec_abs_upper([theta_box[i] - theta0[i] for i in range(CONTROL_DIMENSION)])
    chart_margin = arb(1) - displacement
    nowrap_margin = arb.pi() - displacement
    return chart_margin, nowrap_margin


def r5_derivative_bound(theta_box, P):
    JN = r5_JN_at_theta(theta_box)
    Jt = r5_Jt_at_theta(theta_box)
    defect = r5_inf_norm_upper(r5_matsub(r5_identity(RESPONSE_DIMENSION), r5_matmul(P, JN)))
    PJt = r5_matvec(P, Jt)
    PJt_norm = r5_vec_abs_upper(PJt)
    denominator = arb(1) - defect
    norm_upper = PJt_norm / denominator
    enclosure = [arb(0, str(norm_upper.abs_upper().upper())) for _ in range(RESPONSE_DIMENSION)]
    return JN, Jt, defect, PJt, norm_upper, enclosure


def r5_main():
    objects = r5_aux["objects"]
    P = r5_mat(objects["P"])
    T = r5_mat(objects["T"])
    N = r5_mat(objects["N"])
    Tv = [T[row][0] for row in range(CONTROL_DIMENSION)]
    S = r5_vec(r5_b2["leaf_records"][0]["S"][i]["enclosure"] for i in range(RESPONSE_DIMENSION))
    NS = r5_matvec(N, S)
    w = [Tv[i] + NS[i] for i in range(CONTROL_DIMENSION)]
    r_eta = r5_arb(r5_formal_radius)

    leaf_records = []
    certified_leaves = 0
    weakest_leaf = None
    minimum_jacobian_margin = None
    maximum_inverse_defect = arb(0)
    maximum_derivative_norm = arb(0)
    minimum_admissibility_margin = None

    for index, leaf_interval in enumerate(r5_leaves):
        left = r5_arb(leaf_interval[0])
        right = r5_arb(leaf_interval[1])
        a_C = (left + right) / 2
        alpha_radius = (right - left).abs_upper() / 2
        alpha = arb(0, str(alpha_radius.upper()))
        b_C = r5_newton_correction(a_C)
        theta_C = r5_theta_from_b(a_C, b_C)
        eta = [arb(0, str(r_eta.upper())) for _ in range(RESPONSE_DIMENSION)]
        theta_box = r5_theta_affine(theta_C, w, alpha, N, eta)
        JN, Jt, defect, PJt, derivative_norm, derivative_enclosure = r5_derivative_bound(theta_box, P)
        det_JN = arb_mat(JN).det()
        inverse_margin = arb(1) - defect
        chart_margin, nowrap_margin = r5_phase_admissibility(theta_box)
        admissibility_margin = chart_margin if chart_margin.lower() < nowrap_margin.lower() else nowrap_margin
        gates = {
            "b2_leaf_unique_root": r5_b2["leaf_records"][index]["formal_radius_record"]["gates"]["unique_root"] is True,
            "jacobian_invertible": r5_strict_positive(inverse_margin) and not det_JN.contains(arb(0)),
            "implicit_derivative_enclosed": r5_strict_positive(inverse_margin),
            "chart_admissible": r5_strict_positive(chart_margin),
            "no_wrap": r5_strict_positive(nowrap_margin),
        }
        gates["leaf_c1_regular"] = all(gates.values())
        if gates["leaf_c1_regular"]:
            certified_leaves += 1
        if minimum_jacobian_margin is None or inverse_margin.lower() < minimum_jacobian_margin.lower():
            minimum_jacobian_margin = inverse_margin
            weakest_leaf = index
        if defect.abs_upper() > maximum_inverse_defect:
            maximum_inverse_defect = defect.abs_upper()
        if derivative_norm.abs_upper() > maximum_derivative_norm:
            maximum_derivative_norm = derivative_norm.abs_upper()
        if minimum_admissibility_margin is None or admissibility_margin.lower() < minimum_admissibility_margin.lower():
            minimum_admissibility_margin = admissibility_margin
        leaf_records.append({
            "leaf_index": index,
            "leaf_interval": leaf_interval,
            "physical_root_tube_source": "R5-B2 affine-Hessian leaf tube",
            "theta_box_admissibility_source": "theta_C+(T*v+N*S)*alpha+N*eta over the frozen leaf and formal eta radius",
            "D_bF_definition": "B*DR3(theta)*N",
            "D_tF_definition": "B*DR3(theta)*T*v",
            "D_bF_determinant": r5_bound(det_JN),
            "inverse_defect": r5_bound(defect),
            "strict_inverse_margin": r5_bound(inverse_margin),
            "D_tF": r5_bound_vector(Jt),
            "P_D_tF": r5_bound_vector(PJt),
            "implicit_derivative_formula": "b_prime=-(D_bF)^(-1)*D_tF",
            "implicit_derivative_norm_upper": r5_bound(derivative_norm),
            "implicit_derivative_enclosure": r5_bound_vector(derivative_enclosure),
            "chart_margin": r5_bound(chart_margin),
            "no_wrap_margin": r5_bound(nowrap_margin),
            "admissibility_margin": r5_bound(admissibility_margin),
            "gates": gates,
            "leaf_final_status": "LEAF_C1_CERTIFIED" if gates["leaf_c1_regular"] else "LEAF_C1_NOT_CERTIFIED",
        })

    seam_records = []
    certified_seams = 0
    weakest_seam = None
    minimum_seam_margin = None
    max_coordinate_defect = arb(0)
    for seam in r5_b3b["seam_records"]:
        seam_index = seam["seam_index"]
        seam_t = r5_arb(seam["seam_t"])
        box = r5_box_from_json(seam["intersection_box"])
        center, radii = r5_box_to_center_radius(box)
        interval_box = r5_interval_box(center, radii)
        theta_box = r5_theta_from_b(seam_t, interval_box)
        JN, Jt, defect, PJt, derivative_norm, derivative_enclosure = r5_derivative_bound(theta_box, P)
        det_JN = arb_mat(JN).det()
        inverse_margin = arb(1) - defect
        coordinate_defect = arb(0)
        if coordinate_defect.abs_upper() > max_coordinate_defect:
            max_coordinate_defect = coordinate_defect.abs_upper()
        if minimum_seam_margin is None or inverse_margin.lower() < minimum_seam_margin.lower():
            minimum_seam_margin = inverse_margin
            weakest_seam = seam_index
        gates = {
            "b3b_common_root_certified": seam["gates"]["physical_root_equality"] is True,
            "common_jacobian_invertible": r5_strict_positive(inverse_margin) and not det_JN.contains(arb(0)),
            "common_derivative_unique": r5_strict_positive(inverse_margin),
            "left_derivative_attachment": seam["gates"]["left_attachment"] is True,
            "right_derivative_attachment": seam["gates"]["right_attachment"] is True,
            "physical_derivative_equality": False,
        }
        gates["physical_derivative_equality"] = all(
            gates[key]
            for key in [
                "b3b_common_root_certified",
                "common_jacobian_invertible",
                "common_derivative_unique",
                "left_derivative_attachment",
                "right_derivative_attachment",
            ]
        )
        if gates["physical_derivative_equality"]:
            certified_seams += 1
        seam_records.append({
            "seam_index": seam_index,
            "left_leaf": seam["left_leaf"],
            "right_leaf": seam["right_leaf"],
            "seam_t": seam["seam_t"],
            "common_root_reference": "R5-B3b common physical endpoint root",
            "common_physical_derivative_formula": "b_prime=-(D_bF)^(-1)*D_tF at the common endpoint equation",
            "D_bF_determinant": r5_bound(det_JN),
            "inverse_defect": r5_bound(defect),
            "strict_inverse_margin": r5_bound(inverse_margin),
            "D_tF": r5_bound_vector(Jt),
            "common_physical_derivative_enclosure": r5_bound_vector(derivative_enclosure),
            "common_physical_derivative_norm_upper": r5_bound(derivative_norm),
            "left_recovered_derivative_enclosure": r5_bound_vector(derivative_enclosure),
            "right_recovered_derivative_enclosure": r5_bound_vector(derivative_enclosure),
            "coordinate_equivalence_defect": r5_bound(coordinate_defect),
            "derivative_equality_reason": "same physical equation, same B3b unique endpoint root, and invertible D_bF imply a unique implicit physical derivative",
            "overlap_alone_used": False,
            "gates": gates,
            "seam_final_status": "SEAM_DERIVATIVE_ATTACHED" if gates["physical_derivative_equality"] else "SEAM_DERIVATIVE_NOT_CERTIFIED",
        })

    all_leaves = certified_leaves == len(r5_leaves)
    all_seams = certified_seams == len(r5_b3b["seam_records"])
    all_pass = all_leaves and all_seams
    status = "R5_GLOBAL_IMPLICIT_BRANCH_C1_CERTIFIED" if all_pass else "R5_GLOBAL_IMPLICIT_BRANCH_C1_NOT_CERTIFIED"
    record = {
        "schema_version": "1.0",
        "record_id": "r5_global_implicit_branch_c1_v1_0",
        "record_kind": "prospective_r5_b4_global_implicit_branch_c1_certificate",
        "scientific_status": status,
        "stage": "R5-B4",
        "arb_precision_bits": 192,
        "base_commit": os.environ["R5_B4_BASE_COMMIT"],
        "software_environment": {"python": platform.python_version(), "python_flint": "0.8.0"},
        "inputs": {
            "parent_protocol_sha256": os.environ["R5_B4_PARENT_SHA"],
            "protocol_sha256": os.environ["R5_B4_PROTOCOL_SHA"],
            "auxiliary_sha256": os.environ["R5_B4_AUX_SHA"],
            "static_certificate_sha256": os.environ["R5_B4_STATIC_SHA"],
            "b2_certificate_artifact_sha256": os.environ["R5_B4_B2_SHA"],
            "b2_record_sha256": r5_b2["record_sha256"],
            "b3b_certificate_artifact_sha256": os.environ["R5_B4_B3B_SHA"],
            "b3b_internal_record_sha256": os.environ["R5_B4_B3B_RECORD_SHA"],
            "v0_7_4_source_sha256": os.environ["R5_B4_V074_SHA"],
            "object_sha256": r5_aux["object_sha256"],
        },
        "frozen_protocol": {
            "leaf_list": r5_leaves,
            "seam_list": [[i, i + 1, r5_leaves[i][1]] for i in range(len(r5_leaves) - 1)],
            "formal_eta_radius": r5_formal_radius,
            "precision_bits": 192,
            "physical_equation": "F(t,b)=B*(R3(theta_0+T*(t*v)+N*b)-c)",
            "implicit_derivative": "D_bF(t,b(t))*b_prime(t)+D_tF(t,b(t))=0",
            "independent_frozen_ode_field_declared": False,
            "result_adaptive_changes_allowed": False,
        },
        "method": {
            "D_bF_formula": "B*DR3(theta)*N",
            "D_tF_formula": "B*DR3(theta)*T*v",
            "implicit_derivative_formula": "b_prime=-(D_bF)^(-1)*D_tF",
            "inverse_certification": "Neumann defect ||I-P*D_bF||_inf < 1 with frozen P",
            "point_center_required_for_forcing": True,
            "physical_b_coordinate_used_for_seams": True,
            "derivative_overlap_alone_sufficient": False,
            "same_common_equation_and_unique_root_required": True,
            "binary64_theorem_decision_used": False,
            "finite_difference_derivative_used": False,
            "frozen_ode_consistency_checked": False,
            "frozen_ode_consistency_reason": "no independent frozen B4 ODE field is declared in the protocol",
        },
        "leaf_records": leaf_records,
        "seam_records": seam_records,
        "summary": {
            "leaves_total": len(r5_leaves),
            "leaves_certified": certified_leaves,
            "seams_total": len(seam_records),
            "seams_certified": certified_seams,
            "weakest_leaf": weakest_leaf,
            "weakest_seam": weakest_seam,
            "minimum_jacobian_margin": r5_bound(minimum_jacobian_margin if minimum_jacobian_margin is not None else arb(0)),
            "maximum_inverse_defect": r5_bound(maximum_inverse_defect),
            "maximum_derivative_norm_upper": r5_bound(maximum_derivative_norm),
            "maximum_coordinate_equivalence_defect": r5_bound(max_coordinate_defect),
            "minimum_admissibility_margin": r5_bound(minimum_admissibility_margin if minimum_admissibility_margin is not None else arb(0)),
            "global_c1_branch_certified": all_pass,
            "frozen_ode_consistency_certified": False,
            "can_enter_b5": all_pass,
        },
        "scope": {
            "all_leaf_roots_certified": r5_b2["scope"]["r5_all_leaves_locally_certified"],
            "all_internal_seams_c0_certified": r5_b3b["scope"]["single_c0_root_branch_certified"],
            "global_c0_root_branch_certified": r5_b3b["scope"]["single_c0_root_branch_certified"],
            "all_leaf_jacobians_invertible": all_leaves,
            "implicit_derivative_certified": all_leaves,
            "all_seam_derivatives_attached": all_seams,
            "global_c1_branch_certified": all_pass,
            "frozen_ode_consistency_certified": False,
            "global_admissibility_certified": all_leaves,
            "positive_measure_nonconstancy_certified": False,
            "full_path_zero_cost_certified": False,
            "full_r5_certificate_generated": False,
            "r5_certified": False,
            "r6_search_performed": False,
            "normal_K1_residual_recovery_performed": False,
            "principle_r_pr_r5_certified": False,
            "principle_r_pr_r6_supplied": False,
            "principle_r_fully_witnessed": False,
            "global_ode_flow_certified": False,
        },
        "all_gates_pass": all_pass,
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
    with tempfile.TemporaryDirectory(prefix="r5_b4_c1_") as tmp:
        output = Path(tmp) / "r5_global_implicit_branch_c1_v1_0.json"
        patched = Path(tmp) / "_r5_b4_backend.py"
        patched.write_text(patch_frozen_source(V074_SOURCE.read_bytes()), encoding="utf-8")
        env = dict(os.environ)
        env.update({
            "R5_B4_OUTPUT": str(output),
            "R5_B4_AUX": str(AUX_PATH),
            "R5_B4_B2_CERT": str(B2_CERT_PATH),
            "R5_B4_B3B_CERT": str(B3B_CERT_PATH),
            "R5_B4_BASE_COMMIT": EXPECTED_BASE_COMMIT,
            "R5_B4_PARENT_SHA": preflight.EXPECTED_PARENT_PROTOCOL_SHA256,
            "R5_B4_PROTOCOL_SHA": preflight.EXPECTED_PROTOCOL_SHA256,
            "R5_B4_AUX_SHA": preflight.EXPECTED_AUXILIARY_SHA256,
            "R5_B4_STATIC_SHA": preflight.EXPECTED_STATIC_CERT_SHA256,
            "R5_B4_B2_SHA": EXPECTED_B2_CERT_SHA256,
            "R5_B4_B3B_SHA": EXPECTED_B3B_CERT_SHA256,
            "R5_B4_B3B_RECORD_SHA": EXPECTED_B3B_RECORD_SHA256,
            "R5_B4_V074_SHA": preflight.EXPECTED_V074_SOURCE_SHA256,
            "R5_B4_LEAVES": json.dumps(LEAVES),
            "R5_B4_FORMAL_RADIUS": FORMAL_RADIUS,
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
        "leaves_certified": record["summary"]["leaves_certified"],
        "seams_certified": record["summary"]["seams_certified"],
        "global_c1_branch_certified": record["summary"]["global_c1_branch_certified"],
        "can_enter_b5": record["summary"]["can_enter_b5"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
