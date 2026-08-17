#!/usr/bin/env python3
"""Certify prospective R5-B0 static Arb gates.

This script verifies fixed candidate objects only. It does not generate an R5
full-tube certificate, run R6, search or optimize frames, or perform normal
K=1 residual recovery.
"""

from __future__ import annotations

import hashlib
import json
import platform
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from flint import arb, arb_mat, ctx


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PROTOCOL_PATH = HERE / "r5_full_tube_protocol_v1_0.json"
AUX_PATH = HERE / "data" / "r5_full_tube_auxiliary_v1_0.json"
BOUNDARY_PATH = HERE / "R5_STATIC_ARB_GATES_BOUNDARY.md"
CERT_PATH = HERE / "certificates" / "r5_static_arb_gates_v1_0.json"

EXPECTED_STATUS_CERTIFIED = "R5_STATIC_ARB_GATES_CERTIFIED"
EXPECTED_STATUS_INCONCLUSIVE = "R5_STATIC_ARB_GATES_INCONCLUSIVE"
EXPECTED_PROTOCOL_SHA256 = "1e757ff86759fd793f6743560e1f50040362f892e342db723c47a658a3078cd3"
EXPECTED_AUXILIARY_SHA256 = "434b8d58793b39462fc3dcf4e04f716b56e65de790e87daaecedf2e103e29037"
EXPECTED_PARENT_SHA256 = "e8519a644ab50a9989eb40bc34499055f83760563167d88da21d17b3c7539e1c"
EXPECTED_BASELINE = "350ddf6588082b5e175ba1ffcd0e6ddf51f9314a"
PRECISION_BITS = 192

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

EXPECTED_SHAPES = {
    "theta_0": [14],
    "T": [14, 6],
    "N": [14, 8],
    "B": [8, 8],
    "c": [8],
    "P": [8, 8],
    "midpoint_response_jacobian": [8, 14],
    "midpoint_response_singular_values": [8],
    "normal_derivative_midpoint": [8, 8],
}

FORBIDDEN_KEYS = {
    "R5_CERTIFIED",
    "R5_full_tube_certificate",
    "R5_certificate",
    "R5_result",
    "R6_CERTIFIED",
    "R6_search_performed",
    "R6_search_result",
    "R6_certificate",
    "normal_K1_residual_recovery_performed",
    "normal_K1_recovery_result",
    "exact_response_preservation_certified",
    "zero_total_response_cost_certified",
    "full_tube_certificate_generated",
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


def certificate_digest_payload(value: dict[str, Any]) -> dict[str, Any]:
    payload = json.loads(json.dumps(value, sort_keys=True))
    payload.pop("certificate_sha256", None)
    payload.get("software_environment", {}).pop("python", None)
    return payload


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def finite_decimal_string(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = Decimal(value)
    except (InvalidOperation, ValueError, OverflowError):
        return False
    return parsed.is_finite()


def all_finite_decimal_strings(value: Any) -> bool:
    if isinstance(value, str):
        return finite_decimal_string(value)
    if isinstance(value, list):
        return all(all_finite_decimal_strings(item) for item in value)
    return False


def shape_of(value: Any) -> list[int] | None:
    if not isinstance(value, list):
        return None
    if not value:
        return [0]
    if all(not isinstance(item, list) for item in value):
        return [len(value)]
    if not all(isinstance(item, list) for item in value):
        return None
    lengths = {len(row) for row in value}
    if len(lengths) != 1:
        return None
    return [len(value), lengths.pop()]


def arb_from_decimal(value: str) -> arb:
    if not finite_decimal_string(value):
        raise ValueError(f"not a finite decimal string: {value!r}")
    return arb(value)


def matrix_from_object(value: list[list[str]]) -> arb_mat:
    return arb_mat([[arb_from_decimal(item) for item in row] for row in value])


def vector_from_object(value: list[str]) -> list[arb]:
    return [arb_from_decimal(item) for item in value]


def gram(matrix: arb_mat) -> arb_mat:
    return matrix.transpose() * matrix


def concat_columns(left: arb_mat, right: arb_mat) -> arb_mat:
    rows = left.nrows()
    return arb_mat(
        [
            [left[i, j] for j in range(left.ncols())]
            + [right[i, j] for j in range(right.ncols())]
            for i in range(rows)
        ]
    )


def identity(size: int) -> arb_mat:
    return arb_mat([[arb(1) if i == j else arb(0) for j in range(size)] for i in range(size)])


def inf_norm_upper(matrix: arb_mat) -> arb:
    best = arb(0)
    for row in range(matrix.nrows()):
        total = arb(0)
        for col in range(matrix.ncols()):
            total += matrix[row, col].abs_upper()
        if total > best:
            best = total
    return best


def decimal_out(value: arb) -> str:
    return format(float(value), ".17g")


def positive_lower_bound(value: arb) -> str:
    return decimal_out(value.abs_lower())


def upper_bound(value: arb) -> str:
    return decimal_out(value.abs_upper())


def determinant_gate(name: str, matrix: arb_mat) -> dict[str, Any]:
    determinant = matrix.det()
    lower = determinant.abs_lower()
    return {
        "gate": name,
        "determinant_enclosure": str(determinant),
        "abs_determinant_lower_bound": positive_lower_bound(determinant),
        "strictly_nonzero": bool(lower > arb(0) and not determinant.contains(arb(0))),
    }


def neumann_defect_gate(name: str, defect: arb_mat) -> dict[str, Any]:
    norm = inf_norm_upper(defect)
    return {
        "gate": name,
        "norm": "infinity",
        "defect_upper_bound": upper_bound(norm),
        "threshold": "1",
        "strictly_less_than_one": bool(norm < arb(1)),
    }


def object_hashes_match(aux: dict[str, Any]) -> bool:
    objects = aux.get("objects", {})
    hashes = aux.get("object_sha256", {})
    for name, expected in EXPECTED_OBJECT_SHA256.items():
        if name not in objects or hashes.get(name) != expected:
            return False
        if sha256_bytes(canonical_json(objects[name])) != expected:
            return False
    return True


def objects_well_formed(aux: dict[str, Any]) -> bool:
    objects = aux.get("objects", {})
    dimensions = aux.get("dimensions", {})
    if set(objects) != set(EXPECTED_OBJECT_SHA256):
        return False
    for name, expected_shape in EXPECTED_SHAPES.items():
        if shape_of(objects.get(name)) != expected_shape:
            return False
        if not all_finite_decimal_strings(objects.get(name)):
            return False
    return (
        dimensions.get("control_dimension") == "14"
        and dimensions.get("response_dimension") == "8"
        and dimensions.get("tangent_dimension") == "6"
        and dimensions.get("normal_dimension") == "8"
        and dimensions.get("T") == ["14", "6"]
        and dimensions.get("N") == ["14", "8"]
        and dimensions.get("B") == ["8", "8"]
        and dimensions.get("P") == ["8", "8"]
    )


def protocol_identity(protocol: dict[str, Any], aux: dict[str, Any]) -> dict[str, bool]:
    policy = protocol.get("auxiliary_artifact_policy", {})
    return {
        "protocol_sha256": sha256_file(PROTOCOL_PATH) == EXPECTED_PROTOCOL_SHA256,
        "auxiliary_sha256": sha256_file(AUX_PATH) == EXPECTED_AUXILIARY_SHA256,
        "parent_protocol_sha256": aux.get("parent_protocol_sha256") == EXPECTED_PARENT_SHA256,
        "baseline_commit": aux.get("baseline_commit") == EXPECTED_BASELINE,
        "protocol_status": protocol.get("status") == "R5_FULL_TUBE_PROTOCOL_FROZEN_NO_CERTIFICATE_RUN",
        "auxiliary_status": aux.get("scientific_status")
        == "R5_AUXILIARY_CANDIDATE_DATA_FROZEN_PENDING_ARB_VALIDATION",
        "protocol_auxiliary_policy": (
            policy.get("artifact_path")
            == "research/realizability_r1_r7/data/r5_full_tube_auxiliary_v1_0.json"
            and policy.get("artifact_sha256") == EXPECTED_AUXILIARY_SHA256
            and policy.get("candidate_artifact_byte_frozen") is True
            and policy.get("theorem_certified") is False
        ),
        "no_r5_r6_or_normal_recovery": (
            aux.get("r5_certificate_run") is False
            and aux.get("r6_search_performed") is False
            and aux.get("normal_K1_residual_recovery_performed") is False
            and aux.get("theorem_certified") is False
            and protocol.get("boundary", {}).get("R6_search_performed") is False
        ),
    }


def build_certificate() -> dict[str, Any]:
    ctx.prec = PRECISION_BITS
    protocol = read_json(PROTOCOL_PATH)
    aux = read_json(AUX_PATH)
    objects = aux["objects"]

    T = matrix_from_object(objects["T"])
    N = matrix_from_object(objects["N"])
    B = matrix_from_object(objects["B"])
    P = matrix_from_object(objects["P"])
    jacobian = matrix_from_object(objects["midpoint_response_jacobian"])
    theta_0 = vector_from_object(objects["theta_0"])
    c = vector_from_object(objects["c"])
    _ = (theta_0, c)

    T_gram = gram(T)
    N_gram = gram(N)
    TN = concat_columns(T, N)
    B_inverse = B.inv()
    B_inverse_defect = identity(8) - (B_inverse * B)
    J_N = B * jacobian * N
    preconditioner_defect = identity(8) - (P * J_N)

    gates: dict[str, Any] = {
        "object_identity": {
            "path_shape_sha256_and_finiteness": (
                objects_well_formed(aux) and object_hashes_match(aux)
            ),
            "theta0_T_N_B_c_P_bound_to_protocol": all(
                item.get("sha256") == EXPECTED_AUXILIARY_SHA256
                and item.get("object_sha256")
                == EXPECTED_OBJECT_SHA256.get(item.get("object_key"))
                for item in protocol.get("required_frozen_data_before_certificate", [])
            ),
        },
        "protocol_identity": protocol_identity(protocol, aux),
        "name_separation": {
            "W_Pi": aux.get("object_roles", {}).get("W_Pi"),
            "B": aux.get("object_roles", {}).get("B"),
            "P": aux.get("object_roles", {}).get("P"),
            "distinct_roles_gate": (
                "response-cost weight" in aux.get("object_roles", {}).get("W_Pi", "")
                and "graph equation" in aux.get("object_roles", {}).get("B", "")
                and "preconditioner" in aux.get("object_roles", {}).get("P", "")
            ),
        },
        "frame_rank_T": determinant_gate("det(T^T*T)", T_gram),
        "frame_rank_N": determinant_gate("det(N^T*N)", N_gram),
        "T_N_transversality": determinant_gate("det([T N])", TN),
        "B_strict_invertibility": {
            **determinant_gate("det(B)", B),
            **neumann_defect_gate("||I-inv(B)*B||_inf", B_inverse_defect),
        },
        "preconditioner_defect": {
            "J_N_definition": "J_N = B * DR3(theta_0) * N",
            "DR3_source": "frozen auxiliary midpoint_response_jacobian object",
            **determinant_gate("det(J_N)", J_N),
            **neumann_defect_gate("||I-P*J_N||_inf", preconditioner_defect),
        },
    }

    all_gates_pass = (
        gates["object_identity"]["path_shape_sha256_and_finiteness"]
        and gates["object_identity"]["theta0_T_N_B_c_P_bound_to_protocol"]
        and all(gates["protocol_identity"].values())
        and gates["name_separation"]["distinct_roles_gate"]
        and gates["frame_rank_T"]["strictly_nonzero"]
        and gates["frame_rank_N"]["strictly_nonzero"]
        and gates["T_N_transversality"]["strictly_nonzero"]
        and gates["B_strict_invertibility"]["strictly_nonzero"]
        and gates["B_strict_invertibility"]["strictly_less_than_one"]
        and gates["preconditioner_defect"]["strictly_nonzero"]
        and gates["preconditioner_defect"]["strictly_less_than_one"]
    )
    status = EXPECTED_STATUS_CERTIFIED if all_gates_pass else EXPECTED_STATUS_INCONCLUSIVE

    certificate: dict[str, Any] = {
        "schema_version": "1.0",
        "certificate_id": "r5_static_arb_gates_v1_0",
        "certificate_kind": "prospective_r5_b0_static_arb_gates",
        "scientific_status": status,
        "all_gates_pass": all_gates_pass,
        "arb_precision_bits": PRECISION_BITS,
        "software_environment": {
            "python": platform.python_version(),
            "python_flint": "0.8.0",
        },
        "inputs": {
            "protocol_path": str(PROTOCOL_PATH.relative_to(ROOT)),
            "protocol_sha256": EXPECTED_PROTOCOL_SHA256,
            "auxiliary_path": str(AUX_PATH.relative_to(ROOT)),
            "auxiliary_sha256": EXPECTED_AUXILIARY_SHA256,
            "parent_protocol_sha256": EXPECTED_PARENT_SHA256,
            "baseline_commit": EXPECTED_BASELINE,
            "object_sha256": EXPECTED_OBJECT_SHA256,
        },
        "scope": {
            "r5_static_gates_only": True,
            "r5_full_tube_certificate_generated": False,
            "r5_graph_existence_certified": False,
            "r5_exact_response_preservation_certified": False,
            "r5_zero_total_cost_certified": False,
            "r6_search_performed": False,
            "normal_K1_residual_recovery_performed": False,
            "binary64_theorem_decision_used": False,
            "binary64_candidate_construction_used": True,
            "residual_near_zero_accepted_as_exact_zero": False,
        },
        "gates": gates,
    }
    certificate["certificate_sha256"] = sha256_bytes(
        canonical_json(certificate_digest_payload(certificate))
    )
    return certificate


def main() -> int:
    certificate = build_certificate()
    CERT_PATH.write_bytes(canonical_json(certificate) + b"\n")
    print(json.dumps(certificate, indent=2, sort_keys=True))
    print(certificate["scientific_status"])
    return 0 if certificate["scientific_status"] == EXPECTED_STATUS_CERTIFIED else 1


if __name__ == "__main__":
    raise SystemExit(main())
