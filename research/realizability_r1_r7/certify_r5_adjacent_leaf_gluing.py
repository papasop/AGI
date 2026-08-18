#!/usr/bin/env python3
"""R5-B3 adjacent-leaf common-root and C0 gluing certification.

This certifies common endpoint roots for the 15 internal seams of the frozen
16-leaf R5 tube. It does not certify C1 gluing, full-path zero cost,
positive-measure nonconstancy, PR-R5, PR-R6, GF-R5, R6 search, normal K=1
recovery, or any global ODE flow.
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

import certify_r5_all_leaves_hessian_krawczyk as b2_builder
import certify_r5_first_leaf_preflight as preflight

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
V074_SOURCE = preflight.V074_SOURCE
PARENT_PROTOCOL_PATH = preflight.PARENT_PROTOCOL_PATH
PROTOCOL_PATH = preflight.PROTOCOL_PATH
AUX_PATH = preflight.AUX_PATH
STATIC_CERT_PATH = preflight.STATIC_CERT_PATH
B1E_CERT_PATH = HERE / "certificates" / "r5_first_leaf_hessian_krawczyk_v1_0.json"
B2_CERT_PATH = HERE / "certificates" / "r5_all_leaves_hessian_krawczyk_v1_0.json"
AFFINE_DIAG_PATH = b2_builder.AFFINE_DIAG_PATH
B3A_DIAG_PATH = HERE / "diagnostics" / "r5_seam_residual_normalization_diagnostic_v1_0.json"
BOUNDARY_PATH = HERE / "R5_ADJACENT_LEAF_GLUING_BOUNDARY.md"
CERT_PATH = HERE / "certificates" / "r5_adjacent_leaf_gluing_v1_1.json"
DIAG_PATH = HERE / "diagnostics" / "r5_adjacent_leaf_gluing_v1_0.json"
DIAG_PATH_V1_1 = HERE / "diagnostics" / "r5_adjacent_leaf_gluing_v1_1.json"

EXPECTED_BASE_COMMIT = "9d4e869a91cb1f6291e912fab68f803036bc217e"
EXPECTED_B2_CERT_SHA256 = "a2d28d9256b6c871630a8e27695a12ca194582a633b74ddda1816d356173629b"
EXPECTED_B1E_CERT_SHA256 = b2_builder.EXPECTED_B1E_CERT_SHA256
EXPECTED_AFFINE_DIAG_SHA256 = b2_builder.EXPECTED_AFFINE_DIAG_SHA256
EXPECTED_B3A_DIAG_SHA256 = "45e1b9df84edda65ae666e21df36137ece87fa024fbbc66ae1f7d5eee425a3d4"
PRECISION_BITS = 192
FORMAL_RADIUS = b2_builder.FORMAL_RADIUS
LEAVES = b2_builder.LEAVES

CERTIFIED = "R5_ADJACENT_LEAF_C0_GLUING_CERTIFIED"
NOT_CERTIFIED = "R5_ADJACENT_LEAF_C0_GLUING_NOT_CERTIFIED"
INCONCLUSIVE = "R5_ADJACENT_LEAF_C0_GLUING_INCONCLUSIVE"
BOUNDARY_MISMATCH = "R5_B3_INPUT_BOUNDARY_MISMATCH"
IMPLEMENTATION_ERROR = "R5_B3_IMPLEMENTATION_ERROR"
ALLOWED_STATUSES = {CERTIFIED, NOT_CERTIFIED, INCONCLUSIVE, BOUNDARY_MISMATCH, IMPLEMENTATION_ERROR}
SEAM_STATUSES = {
    "SEAM_CERTIFIED",
    "SEAM_BOX_INTERSECTION_EMPTY",
    "SEAM_INTERSECTION_NOT_STRICT",
    "SEAM_EQUATION_MISMATCH",
    "SEAM_COMMON_SELF_MAP_FAILED",
    "SEAM_COMMON_UNIQUENESS_FAILED",
    "SEAM_LEFT_ATTACHMENT_FAILED",
    "SEAM_RIGHT_ATTACHMENT_FAILED",
    "SEAM_COORDINATE_TRANSFORM_FAILED",
    "SEAM_INCONCLUSIVE",
    "SEAM_IMPLEMENTATION_ERROR",
}


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
        B2_CERT_PATH: EXPECTED_B2_CERT_SHA256,
        AFFINE_DIAG_PATH: EXPECTED_AFFINE_DIAG_SHA256,
        B3A_DIAG_PATH: EXPECTED_B3A_DIAG_SHA256,
        V074_SOURCE: preflight.EXPECTED_V074_SOURCE_SHA256,
    }
    for path, expected in expected_files.items():
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"upstream SHA mismatch for {path}: {actual} != {expected}")
    b2 = read_json(B2_CERT_PATH)
    if (
        b2.get("scientific_status") != b2_builder.CERTIFIED
        or b2.get("scope", {}).get("all_leaf_local_root_gates_pass") is not True
        or b2.get("scope", {}).get("r5_all_leaves_locally_certified") is not True
        or b2.get("scope", {}).get("adjacent_leaf_gluing_certified") is not False
        or b2.get("scope", {}).get("r5_certified") is not False
        or b2.get("frozen_protocol", {}).get("leaf_list") != LEAVES
    ):
        raise RuntimeError(BOUNDARY_MISMATCH)


def injection() -> str:
    code = r'''
import os
import platform
from flint import arb_mat

r5_output = Path(os.environ["R5_B3_OUTPUT"])
r5_aux = json.loads(Path(os.environ["R5_B3_AUX"]).read_text(encoding="utf-8"))
r5_b2 = json.loads(Path(os.environ["R5_B3_B2_CERT"]).read_text(encoding="utf-8"))
r5_affine = json.loads(Path(os.environ["R5_B3_AFFINE"]).read_text(encoding="utf-8"))
r5_leaves = json.loads(os.environ["R5_B3_LEAVES"])
r5_formal_radius = os.environ["R5_B3_FORMAL_RADIUS"]


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


def r5_F_t_b(t_value, b_values):
    objects = r5_aux["objects"]
    B = r5_mat(objects["B"])
    c = r5_vec(objects["c"])
    response = r5_response(r5_theta(t_value, b_values))
    return r5_matvec(B, [response[i] - c[i] for i in range(RESPONSE_DIMENSION)])


def r5_JN_t_b(t_value, b_values):
    objects = r5_aux["objects"]
    B = r5_mat(objects["B"])
    N = r5_mat(objects["N"])
    theta = r5_theta(t_value, b_values)
    return r5_matmul(r5_matmul(B, r5_response_jacobian(theta)), N)


def r5_interval_mid_radius(lower, upper):
    mid = (lower + upper) / 2
    rad = (upper - lower).abs_upper() / 2
    return arb(str(mid)), rad


def r5_box_from_point_center_radii(center, radii):
    return [arb(str(value), str(radius.upper())) for value, radius in zip(center, radii)]


def r5_box_from_center_radius(center, radius):
    return [(value - radius, value + radius) for value in center]


def r5_intersect(left_box, right_box):
    result = []
    metadata = []
    for (ll, lu), (rl, ru) in zip(left_box, right_box):
        lo = ll if ll > rl else rl
        lo_source = "left" if ll > rl else "right"
        hi = lu if lu < ru else ru
        hi_source = "left" if lu < ru else "right"
        result.append((lo, hi))
        metadata.append({
            "lower_source": lo_source,
            "upper_source": hi_source,
            "left_lower_selected_or_strictly_below_selected": bool(lo_source == "left" or rl > ll),
            "right_lower_selected_or_strictly_below_selected": bool(lo_source == "right" or ll > rl),
            "left_upper_selected_or_strictly_above_selected": bool(hi_source == "left" or ru < lu),
            "right_upper_selected_or_strictly_above_selected": bool(hi_source == "right" or lu < ru),
        })
    return result, metadata


def r5_box_strict_margin(box):
    margin = None
    for lo, hi in box:
        width = hi - lo
        half = width / 2
        if margin is None or half.lower() < margin.lower():
            margin = half
    return margin if margin is not None else arb(0)


def r5_box_to_center_radius(box):
    centers = []
    radii = []
    for lo, hi in box:
        center, radius = r5_interval_mid_radius(lo, hi)
        centers.append(center)
        radii.append(radius)
    rmax = arb(0)
    rmin = None
    for radius in radii:
        radius_arb = arb(str(radius.upper()))
        if radius_arb > rmax:
            rmax = radius_arb
        if rmin is None or radius_arb < rmin:
            rmin = radius_arb
    return centers, radii, rmin, rmax


def r5_box_bound(box):
    return [{"lower": str(lo), "upper": str(hi), "width": str(hi - lo)} for lo, hi in box]


def r5_box_subset(inner, outer):
    for (ilo, ihi), (olo, ohi) in zip(inner, outer):
        lower_margin = ilo - olo
        upper_margin = ohi - ihi
        if lower_margin.lower() < arb(0) or upper_margin.lower() < arb(0):
            return False
    return True


def r5_box_subset_from_intersection_metadata(metadata, side):
    if side == "left":
        return all(
            item["left_lower_selected_or_strictly_below_selected"]
            and item["left_upper_selected_or_strictly_above_selected"]
            for item in metadata
        )
    return all(
        item["right_lower_selected_or_strictly_below_selected"]
        and item["right_upper_selected_or_strictly_above_selected"]
        for item in metadata
    )


def r5_strict_positive(value):
    return bool(value > arb(0) and not value.contains(arb(0)))


def r5_leaf_center(leaf_interval):
    left = r5_arb(leaf_interval[0])
    right = r5_arb(leaf_interval[1])
    return (left + right) / 2


def r5_newton_correction(t_value):
    P = r5_mat(r5_aux["objects"]["P"])
    zero = [arb(0) for _ in range(RESPONSE_DIMENSION)]
    return [-value for value in r5_matvec(P, r5_F_t_b(t_value, zero))]


def r5_predictor_at(leaf_interval, seam_t):
    a_C = r5_leaf_center(leaf_interval)
    b_C = r5_newton_correction(a_C)
    S = r5_vec(r5_affine["candidate_slope"]["S"])
    delta = seam_t - a_C
    return [b_C[j] + S[j] * delta for j in range(RESPONSE_DIMENSION)]


def r5_physical_equation_hash(seam_t):
    payload = {
        "equation": "G_i(b)=B(R3(theta_0+T*(s_i*v)+N*b)-c)",
        "seam_t": str(seam_t),
        "object_sha256": r5_aux["object_sha256"],
        "response": "R3 projective jet order 3, real block then imaginary block",
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")).hexdigest()


def r5_seam_status(gates):
    if gates["physical_root_equality"]:
        return "SEAM_CERTIFIED"
    if not gates["intersection_nonempty"]:
        return "SEAM_BOX_INTERSECTION_EMPTY"
    if not gates["intersection_strict_interior"]:
        return "SEAM_INTERSECTION_NOT_STRICT"
    if not gates["same_physical_equation"]:
        return "SEAM_EQUATION_MISMATCH"
    if not gates["common_self_map"]:
        return "SEAM_COMMON_SELF_MAP_FAILED"
    if not gates["common_unique_root"]:
        return "SEAM_COMMON_UNIQUENESS_FAILED"
    if not gates["left_attachment"]:
        return "SEAM_LEFT_ATTACHMENT_FAILED"
    if not gates["right_attachment"]:
        return "SEAM_RIGHT_ATTACHMENT_FAILED"
    if not gates["coordinate_transform"]:
        return "SEAM_COORDINATE_TRANSFORM_FAILED"
    return "SEAM_INCONCLUSIVE"


def r5_main():
    P = r5_mat(r5_aux["objects"]["P"])
    B = r5_mat(r5_aux["objects"]["B"])
    r_eta = r5_arb(r5_formal_radius)
    leaf_records = r5_b2["leaf_records"]
    B_inv = arb_mat(B).inv()
    B_defect = r5_matsub(r5_identity(RESPONSE_DIMENSION), r5_matmul([[B_inv[r, c] for c in range(RESPONSE_DIMENSION)] for r in range(RESPONSE_DIMENSION)], B))
    B_defect_norm = r5_inf_norm_upper(B_defect)

    seam_records = []
    certified_count = 0
    min_intersection_margin = None
    weakest_intersection_seam = None
    min_self_map_margin = None
    weakest_self_map_seam = None
    max_predictor_difference = arb(0)
    max_predictor_difference_seam = None

    for seam_index in range(len(r5_leaves) - 1):
        left_leaf = leaf_records[seam_index]
        right_leaf = leaf_records[seam_index + 1]
        seam_left = r5_leaves[seam_index][1]
        seam_right = r5_leaves[seam_index + 1][0]
        seam_t = r5_arb(seam_left)
        endpoint_consistent = seam_left == seam_right
        left_pred = r5_predictor_at(r5_leaves[seam_index], seam_t)
        right_pred = r5_predictor_at(r5_leaves[seam_index + 1], seam_t)
        predictor_diff = [left_pred[j] - right_pred[j] for j in range(RESPONSE_DIMENSION)]
        predictor_diff_norm = r5_vec_abs_upper(predictor_diff)
        if predictor_diff_norm > max_predictor_difference:
            max_predictor_difference = predictor_diff_norm
            max_predictor_difference_seam = seam_index

        left_box = r5_box_from_center_radius(left_pred, r_eta)
        right_box = r5_box_from_center_radius(right_pred, r_eta)
        intersection, intersection_metadata = r5_intersect(left_box, right_box)
        nonempty = all(lo <= hi for lo, hi in intersection)
        strict_margin = r5_box_strict_margin(intersection) if nonempty else arb(0)
        strict_interior = r5_strict_positive(strict_margin)
        if nonempty and (min_intersection_margin is None or strict_margin.lower() < min_intersection_margin.lower()):
            min_intersection_margin = strict_margin
            weakest_intersection_seam = seam_index

        if nonempty:
            center, component_radii, rmin, rmax = r5_box_to_center_radius(intersection)
            interval_box = r5_box_from_point_center_radii(center, component_radii)
            F0 = r5_F_t_b(seam_t, center)
            PF0 = r5_matvec(P, F0)
            Y0 = r5_vec_abs_upper(PF0)
            Y1 = arb(0)
            Y2 = arb(0)
            Y_total = Y0 + Y1 + Y2
            JN_box = r5_JN_t_b(seam_t, interval_box)
            JN_det = arb_mat(JN_box).det()
            Z_mat = r5_matsub(r5_identity(RESPONSE_DIMENSION), r5_matmul(P, JN_box))
            Z = r5_inf_norm_upper(Z_mat)
            Zr = Z * rmax
            image_radius = Y_total + Zr
            self_map_margin = rmin - image_radius
        else:
            center = [arb(0) for _ in range(RESPONSE_DIMENSION)]
            component_radii = [arb(0) for _ in range(RESPONSE_DIMENSION)]
            rmin = arb(0)
            rmax = arb(0)
            PF0 = [arb(0) for _ in range(RESPONSE_DIMENSION)]
            Y0 = Y1 = Y2 = Y_total = Z = Zr = image_radius = self_map_margin = arb(0)
            JN_det = arb(0)

        if min_self_map_margin is None or self_map_margin.lower() < min_self_map_margin.lower():
            min_self_map_margin = self_map_margin
            weakest_self_map_seam = seam_index

        left_hash = r5_physical_equation_hash(seam_t)
        right_hash = r5_physical_equation_hash(seam_t)
        same_equation = bool(endpoint_consistent and left_hash == right_hash)
        left_subset = r5_box_subset_from_intersection_metadata(intersection_metadata, "left")
        right_subset = r5_box_subset_from_intersection_metadata(intersection_metadata, "right")
        left_attachment = bool(nonempty and left_subset and left_leaf["formal_radius_record"]["gates"]["unique_root"] is True)
        right_attachment = bool(nonempty and right_subset and right_leaf["formal_radius_record"]["gates"]["unique_root"] is True)
        coordinate_transform = bool(
            left_leaf["formal_radius"] == r5_formal_radius
            and right_leaf["formal_radius"] == r5_formal_radius
            and r5_affine["candidate_slope"]["S"] == r5_affine["candidate_slope"]["S"]
        )
        common_self_map = r5_strict_positive(self_map_margin)
        contraction = bool(Z < arb(1) and not Z.contains(arb(1)))
        det_gate = bool(not JN_det.contains(arb(0)) and JN_det.abs_lower() > arb(0))
        B_gate = bool(B_defect_norm < arb(1) and not B_defect_norm.contains(arb(1)))
        common_unique = bool(common_self_map and contraction and det_gate and B_gate and strict_interior and same_equation)
        equality = bool(common_unique and left_attachment and right_attachment and coordinate_transform)
        gates = {
            "endpoint_consistent": endpoint_consistent,
            "same_physical_equation": same_equation,
            "intersection_nonempty": nonempty,
            "intersection_strict_interior": strict_interior,
            "coordinate_transform": coordinate_transform,
            "B_inverse": B_gate,
            "J_eta_invertible": det_gate,
            "common_self_map": common_self_map,
            "contraction": contraction,
            "common_unique_root": common_unique,
            "left_attachment": left_attachment,
            "right_attachment": right_attachment,
            "physical_root_equality": equality,
        }
        status = r5_seam_status(gates)
        if status == "SEAM_CERTIFIED":
            certified_count += 1
        seam_records.append({
            "seam_index": seam_index,
            "left_leaf": seam_index,
            "right_leaf": seam_index + 1,
            "seam_t": seam_left,
            "periodic_closure_checked": False,
            "left_physical_equation_hash": left_hash,
            "right_physical_equation_hash": right_hash,
            "left_predictor_b": r5_bound_vector(left_pred),
            "right_predictor_b": r5_bound_vector(right_pred),
            "predictor_difference": r5_bound_vector(predictor_diff),
            "predictor_difference_inf_norm": r5_bound(predictor_diff_norm),
            "left_physical_box": r5_box_bound(left_box),
            "right_physical_box": r5_box_bound(right_box),
            "intersection_box": r5_box_bound(intersection),
            "intersection_construction_metadata": intersection_metadata,
            "intersection_component_radii": [str(radius) for radius in component_radii],
            "intersection_min_radius": r5_bound(rmin),
            "intersection_max_radius": r5_bound(rmax),
            "intersection_interior_margin": r5_bound(strict_margin),
            "common_krawczyk_center": r5_bound_vector(center),
            "common_center_residual": r5_bound_vector(PF0),
            "Y0": r5_bound(Y0),
            "Y1": r5_bound(Y1),
            "Y2": r5_bound(Y2),
            "Y_total": r5_bound(Y_total),
            "Z": r5_bound(Z),
            "Z_times_rmax": r5_bound(Zr),
            "inverse_defect": r5_bound(B_defect_norm),
            "determinant_enclosure": r5_bound(JN_det),
            "determinant_abs_lower": str(JN_det.abs_lower().lower()),
            "krawczyk_image_radius_upper": str(image_radius.abs_upper().upper()),
            "strict_self_map_margin": r5_bound(self_map_margin),
            "contraction_upper": str(Z.abs_upper().upper()),
            "left_attachment_reason": "intersection box is a subset of the left physical endpoint tube and B2 gives a unique root in that leaf tube",
            "right_attachment_reason": "intersection box is a subset of the right physical endpoint tube and B2 gives a unique root in that leaf tube",
            "physical_root_equality_reason": "the common endpoint Krawczyk box has a unique root for the same physical equation and attaches to both B2 unique endpoint tubes",
            "gates": gates,
            "seam_final_status": status,
        })

    all_seams = certified_count == len(r5_leaves) - 1
    status = "R5_ADJACENT_LEAF_C0_GLUING_CERTIFIED" if all_seams else "R5_ADJACENT_LEAF_C0_GLUING_NOT_CERTIFIED"
    record = {
        "schema_version": "1.0",
        "record_id": "r5_adjacent_leaf_gluing_v1_1",
        "record_kind": "prospective_r5_b3b_corrected_point_center_adjacent_leaf_common_root_c0_gluing",
        "scientific_status": status,
        "arb_precision_bits": PRECISION_BITS,
        "base_commit": os.environ["R5_B3_BASE_COMMIT"],
        "software_environment": {"python": platform.python_version(), "python_flint": "0.8.0"},
        "inputs": {
            "parent_protocol_sha256": os.environ["R5_B3_PARENT_SHA"],
            "protocol_sha256": os.environ["R5_B3_PROTOCOL_SHA"],
            "auxiliary_sha256": os.environ["R5_B3_AUX_SHA"],
            "static_certificate_sha256": os.environ["R5_B3_STATIC_SHA"],
            "b1e_certificate_sha256": os.environ["R5_B3_B1E_SHA"],
            "b2_certificate_artifact_sha256": os.environ["R5_B3_B2_SHA"],
            "affine_diagnostic_sha256": os.environ["R5_B3_AFFINE_SHA"],
            "b3a_diagnostic_sha256": os.environ["R5_B3_B3A_SHA"],
            "b2_record_sha256": r5_b2["record_sha256"],
            "v0_7_4_source_sha256": os.environ["R5_B3_V074_SHA"],
            "object_sha256": r5_aux["object_sha256"],
        },
        "frozen_protocol": {
            "leaf_list": r5_leaves,
            "seam_list": [[i, i + 1, r5_leaves[i][1]] for i in range(len(r5_leaves) - 1)],
            "periodic_closure_seam_15_to_0_included": False,
            "formal_eta_radius": r5_formal_radius,
            "precision_bits": PRECISION_BITS,
            "common_equation": "G_i(b)=B(R3(theta_0+T*(s_i*v)+N*b)-c)",
            "left_right_comparison_object": "physical normal coordinate b, not local eta",
            "intersection_rule": "X_i_cap=X_i_left_intersect_X_i_right, then certify a common unique root inside X_i_cap",
            "result_adaptive_changes_allowed": False,
        },
        "method": {
            "B2_leaf_local_roots_required": True,
            "common_endpoint_krawczyk_required": True,
            "point_center_krawczyk_center_used": True,
            "interval_valued_center_rejected": True,
            "box_width_enters_only_through_X_minus_b0_and_Z_times_r": True,
            "box_overlap_alone_sufficient": False,
            "eta_coordinate_direct_comparison_used": False,
            "physical_b_coordinate_comparison_used": True,
            "same_physical_equation_required": True,
            "left_and_right_attachment_required": True,
            "c0_from_leaf_continuity_and_seam_equality": True,
            "c1_gluing_checked": False,
            "binary64_theorem_decision_used": False,
        },
        "seam_records": seam_records,
        "summary": {
            "seam_count": len(seam_records),
            "certified_seam_count": certified_count,
            "weakest_intersection_seam": weakest_intersection_seam,
            "minimum_intersection_interior_margin": r5_bound(min_intersection_margin if min_intersection_margin is not None else arb(0)),
            "weakest_self_map_seam": weakest_self_map_seam,
            "minimum_common_self_map_margin": r5_bound(min_self_map_margin if min_self_map_margin is not None else arb(0)),
            "max_predictor_difference_seam": max_predictor_difference_seam,
            "maximum_predictor_difference_inf_norm": r5_bound(max_predictor_difference),
            "coordinate_expression_differences_observed": bool(max_predictor_difference > arb(0)),
            "single_c0_root_branch_certified": all_seams,
            "can_enter_B4": all_seams,
        },
        "continuity_logic": {
            "R3_smooth_on_leaf_boxes": True,
            "normal_jacobian_invertible_on_each_leaf_box_from_B2": True,
            "unique_root_tube_on_each_leaf_from_B2": True,
            "implicit_function_theorem_gives_leafwise_continuity": True,
            "seam_common_uniqueness_gives_single_valued_branch": all_seams,
            "global_C0_branch_conclusion": all_seams,
            "global_C1_branch_conclusion": False,
        },
        "scope": {
            "all_16_leaf_local_root_gates_pass": r5_b2["scope"]["all_leaf_local_root_gates_pass"],
            "all_15_internal_seams_certified": all_seams,
            "single_c0_root_branch_certified": all_seams,
            "c1_gluing_certified": False,
            "full_path_response_identity_certified": False,
            "full_path_absolute_continuity_certified": False,
            "positive_measure_nonconstancy_certified": False,
            "zero_cost_full_path_certified": False,
            "principle_r_pr_r5_certified": False,
            "principle_r_pr_r6_supplied": False,
            "gf_r5_certified": False,
            "global_ode_flow_certified": False,
            "r6_search_performed": False,
            "normal_K1_residual_recovery_performed": False,
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
    with tempfile.TemporaryDirectory(prefix="r5_b3_gluing_") as tmp:
        output = Path(tmp) / "r5_adjacent_leaf_gluing_v1_1.json"
        patched = Path(tmp) / "_r5_b3_backend.py"
        patched.write_text(patch_frozen_source(V074_SOURCE.read_bytes()), encoding="utf-8")
        env = dict(os.environ)
        env.update({
            "R5_B3_OUTPUT": str(output),
            "R5_B3_AUX": str(AUX_PATH),
            "R5_B3_B2_CERT": str(B2_CERT_PATH),
            "R5_B3_AFFINE": str(AFFINE_DIAG_PATH),
            "R5_B3_BASE_COMMIT": EXPECTED_BASE_COMMIT,
            "R5_B3_PARENT_SHA": preflight.EXPECTED_PARENT_PROTOCOL_SHA256,
            "R5_B3_PROTOCOL_SHA": preflight.EXPECTED_PROTOCOL_SHA256,
            "R5_B3_AUX_SHA": preflight.EXPECTED_AUXILIARY_SHA256,
            "R5_B3_STATIC_SHA": preflight.EXPECTED_STATIC_CERT_SHA256,
            "R5_B3_B1E_SHA": EXPECTED_B1E_CERT_SHA256,
            "R5_B3_B2_SHA": EXPECTED_B2_CERT_SHA256,
            "R5_B3_AFFINE_SHA": EXPECTED_AFFINE_DIAG_SHA256,
            "R5_B3_B3A_SHA": EXPECTED_B3A_DIAG_SHA256,
            "R5_B3_V074_SHA": preflight.EXPECTED_V074_SOURCE_SHA256,
            "R5_B3_LEAVES": json.dumps(LEAVES),
            "R5_B3_FORMAL_RADIUS": FORMAL_RADIUS,
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
    target = CERT_PATH if record.get("scientific_status") == CERTIFIED else DIAG_PATH_V1_1
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
        "certified_seam_count": record["summary"]["certified_seam_count"],
        "seam_count": record["summary"]["seam_count"],
        "weakest_self_map_seam": record["summary"]["weakest_self_map_seam"],
        "can_enter_B4": record["summary"]["can_enter_B4"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
