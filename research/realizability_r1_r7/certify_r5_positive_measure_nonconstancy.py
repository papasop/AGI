#!/usr/bin/env python3
"""R5-B5 positive-measure nonconstancy certification.

This stage certifies only the predeclared nonconstancy gate for the frozen
shrinking loop family, using the B4 C1 implicit branch. It does not certify
zero response cost, full GF-R5, PR-R5, PR-R6, R6 search, normal K=1 recovery,
or any global ODE flow.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from flint import arb, ctx

import certify_r5_global_implicit_branch_c1 as b4_builder
import certify_r5_first_leaf_preflight as preflight


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

PROTOCOL_PATH = preflight.PROTOCOL_PATH
AUX_PATH = preflight.AUX_PATH
B4_CERT_PATH = HERE / "certificates" / "r5_global_implicit_branch_c1_v1_0.json"
BOUNDARY_PATH = HERE / "R5_POSITIVE_MEASURE_NONCONSTANCY_BOUNDARY.md"
CERT_PATH = HERE / "certificates" / "r5_positive_measure_nonconstancy_v1_0.json"
DIAG_PATH = HERE / "diagnostics" / "r5_positive_measure_nonconstancy_v1_0.json"

EXPECTED_BASE_COMMIT = b4_builder.EXPECTED_BASE_COMMIT
EXPECTED_B4_CERT_SHA256 = "f258be6e08cab82250d6b5eb5d44896f532166bc0bc64f378028fa99f290962f"
EXPECTED_B4_RECORD_SHA256 = "c07cc49d64c7aadda17265c79cba7751233625d98bbbd04a13d89782b0ab6097"
PRECISION_BITS = 192
EPSILONS = ["1e-14", "3e-14", "1e-13", "3e-13", "1e-12"]
S_INTERVAL = ["0", "1/12"]

CERTIFIED = "R5_POSITIVE_MEASURE_NONCONSTANCY_CERTIFIED"
NOT_CERTIFIED = "R5_POSITIVE_MEASURE_NONCONSTANCY_NOT_CERTIFIED"
INCONCLUSIVE = "R5_POSITIVE_MEASURE_NONCONSTANCY_INCONCLUSIVE"
BOUNDARY_MISMATCH = "R5_B5_INPUT_BOUNDARY_MISMATCH"
IMPLEMENTATION_ERROR = "R5_B5_IMPLEMENTATION_ERROR"
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
    return payload


def rarb(value: Any) -> arb:
    return arb(str(value))


def bound(value: arb) -> dict[str, Any]:
    return {
        "enclosure": str(value),
        "lower": str(value.lower()),
        "upper": str(value.upper()),
        "abs_lower": str(value.abs_lower()),
        "abs_upper": str(value.abs_upper()),
        "contains_zero": bool(value.contains(arb(0))),
    }


def mat(values: list[list[str]]) -> list[list[arb]]:
    return [[rarb(item) for item in row] for row in values]


def matvec(left: list[list[arb]], vec: list[arb]) -> list[arb]:
    return [sum((left[r][k] * vec[k] for k in range(len(vec))), arb(0)) for r in range(len(left))]


def vec_abs_upper(vec: list[arb]) -> arb:
    best = arb(0)
    for value in vec:
        upper = value.abs_upper()
        if upper > best:
            best = upper
    return best


def vector_bound(vec: list[arb]) -> list[dict[str, Any]]:
    return [bound(value) for value in vec]


def strict_positive(value: arb) -> bool:
    return bool(value > arb(0) and not value.contains(arb(0)))


def check_upstream_identity() -> None:
    expected = {
        PROTOCOL_PATH: preflight.EXPECTED_PROTOCOL_SHA256,
        AUX_PATH: preflight.EXPECTED_AUXILIARY_SHA256,
        B4_CERT_PATH: EXPECTED_B4_CERT_SHA256,
    }
    for path, expected_sha in expected.items():
        actual = sha256_file(path)
        if actual != expected_sha:
            raise RuntimeError(f"upstream SHA mismatch for {path}: {actual} != {expected_sha}")
    protocol = read_json(PROTOCOL_PATH)
    b4 = read_json(B4_CERT_PATH)
    nonconstancy = protocol.get("nonconstancy_design", {})
    if (
        nonconstancy.get("s_interval") != S_INTERVAL
        or "cos(2*pi*s) >= 1/2" not in nonconstancy.get("required_cosine_bound", "")
        or "a_dot" not in nonconstancy.get("intrinsic_speed", "")
        or b4.get("scientific_status") != b4_builder.CERTIFIED
        or b4.get("record_sha256") != EXPECTED_B4_RECORD_SHA256
        or b4.get("summary", {}).get("can_enter_b5") is not True
        or b4.get("scope", {}).get("global_c1_branch_certified") is not True
        or b4.get("scope", {}).get("positive_measure_nonconstancy_certified") is not False
    ):
        raise RuntimeError(BOUNDARY_MISMATCH)


def build_record() -> dict[str, Any]:
    check_upstream_identity()
    ctx.prec = PRECISION_BITS
    protocol = read_json(PROTOCOL_PATH)
    aux = read_json(AUX_PATH)
    b4 = read_json(B4_CERT_PATH)
    objects = aux["objects"]
    T = mat(objects["T"])
    N = mat(objects["N"])
    Tv = [T[row][0] for row in range(14)]
    bprime_norm = rarb(b4["summary"]["maximum_derivative_norm_upper"]["abs_upper"])
    row_bounds = []
    coordinate_margins = []
    for row in range(14):
        normal_row_bound = sum((N[row][col].abs_upper() * bprime_norm for col in range(8)), arb(0))
        margin = Tv[row].abs_lower() - normal_row_bound
        row_bounds.append({
            "coordinate": row,
            "T_v_component": bound(Tv[row]),
            "normal_correction_abs_upper": bound(normal_row_bound),
            "environment_direction_component_abs_lower": bound(margin),
            "strictly_nonzero_gate": strict_positive(margin),
        })
        coordinate_margins.append(margin)
    best_coordinate = max(range(14), key=lambda index: coordinate_margins[index].lower())
    environment_speed_per_t_lower = coordinate_margins[best_coordinate]

    s_left = arb(0)
    s_right = arb(1) / arb(12)
    interval_length = s_right - s_left
    cosine_lower = arb(1) / arb(2)
    two_pi = 2 * arb.pi()
    epsilon_records = []
    certified = 0
    minimum_speed = None
    weakest_epsilon = None
    for eps in EPSILONS:
        epsilon = rarb(eps)
        intrinsic_speed_lower = epsilon * two_pi * cosine_lower
        environment_speed_lower = intrinsic_speed_lower * environment_speed_per_t_lower
        positive_measure_speed_lower = environment_speed_lower
        gates = {
            "epsilon_positive": strict_positive(epsilon),
            "epsilon_in_frozen_sequence": eps in protocol["R5_full_tube_object"]["frozen_R5_epsilons"],
            "s_interval_matches_protocol": S_INTERVAL == protocol["nonconstancy_design"]["s_interval"],
            "cosine_lower_bound_positive": strict_positive(cosine_lower),
            "intrinsic_speed_positive_on_I": strict_positive(intrinsic_speed_lower),
            "environment_direction_projection_positive": strict_positive(environment_speed_per_t_lower),
            "environment_speed_positive_on_I": strict_positive(environment_speed_lower),
            "positive_measure_interval": strict_positive(interval_length),
            "endpoint_comparison_used": False,
            "binary64_theorem_decision_used": False,
        }
        gates["nonconstant_positive_measure"] = (
            all(gates[k] for k in [
                "epsilon_positive",
                "epsilon_in_frozen_sequence",
                "s_interval_matches_protocol",
                "cosine_lower_bound_positive",
                "intrinsic_speed_positive_on_I",
                "environment_direction_projection_positive",
                "environment_speed_positive_on_I",
                "positive_measure_interval",
            ])
            and gates["endpoint_comparison_used"] is False
            and gates["binary64_theorem_decision_used"] is False
        )
        if gates["nonconstant_positive_measure"]:
            certified += 1
        if minimum_speed is None or environment_speed_lower.lower() < minimum_speed.lower():
            minimum_speed = environment_speed_lower
            weakest_epsilon = eps
        epsilon_records.append({
            "epsilon": eps,
            "positive_measure_interval": S_INTERVAL,
            "positive_measure_interval_length": bound(interval_length),
            "cosine_lower_bound": bound(cosine_lower),
            "intrinsic_speed_lower": bound(intrinsic_speed_lower),
            "environment_projection_coordinate": best_coordinate,
            "environment_direction_component_abs_lower": bound(environment_speed_per_t_lower),
            "environment_speed_lower_on_I": bound(environment_speed_lower),
            "gates": gates,
            "epsilon_status": "EPSILON_NONCONSTANT_CERTIFIED" if gates["nonconstant_positive_measure"] else "EPSILON_NONCONSTANT_NOT_CERTIFIED",
        })

    all_pass = certified == len(EPSILONS)
    record = {
        "schema_version": "1.0",
        "record_id": "r5_positive_measure_nonconstancy_v1_0",
        "record_kind": "prospective_r5_b5_positive_measure_nonconstancy_certificate",
        "scientific_status": CERTIFIED if all_pass else NOT_CERTIFIED,
        "stage": "R5-B5",
        "arb_precision_bits": PRECISION_BITS,
        "base_commit": EXPECTED_BASE_COMMIT,
        "inputs": {
            "protocol_sha256": preflight.EXPECTED_PROTOCOL_SHA256,
            "auxiliary_sha256": preflight.EXPECTED_AUXILIARY_SHA256,
            "b4_certificate_artifact_sha256": EXPECTED_B4_CERT_SHA256,
            "b4_internal_record_sha256": EXPECTED_B4_RECORD_SHA256,
            "object_sha256": aux["object_sha256"],
        },
        "frozen_protocol": {
            "epsilon_sequence": EPSILONS,
            "s_interval": S_INTERVAL,
            "fixed_v": ["1", "0", "0", "0", "0", "0"],
            "cosine_lower_bound_required": "cos(2*pi*s) >= 1/2 on I=[0,1/12]",
            "intrinsic_speed_formula": "a_dot(s)=epsilon*2*pi*cos(2*pi*s)*v",
            "environment_speed_formula": "dtheta/ds=(T*v+N*b_prime(t))*epsilon*2*pi*cos(2*pi*s)",
            "result_adaptive_changes_allowed": False,
        },
        "method": {
            "source_branch": "R5-B4 C1 implicit branch",
            "environment_projection_gate": "single frozen phase-coordinate projection lower bound",
            "endpoint_comparison_used": False,
            "sampling_used": False,
            "binary64_theorem_decision_used": False,
            "new_observable_introduced": False,
            "zero_cost_checked": False,
            "r6_search_performed": False,
            "normal_K1_residual_recovery_performed": False,
        },
        "environment_direction": {
            "T_v": vector_bound(Tv),
            "b_prime_inf_norm_upper_from_B4": bound(bprime_norm),
            "coordinate_projection_bounds": row_bounds,
            "selected_coordinate": best_coordinate,
            "selected_coordinate_abs_lower": bound(environment_speed_per_t_lower),
        },
        "epsilon_records": epsilon_records,
        "summary": {
            "epsilon_count": len(EPSILONS),
            "certified_epsilon_count": certified,
            "positive_measure_interval": S_INTERVAL,
            "weakest_epsilon": weakest_epsilon,
            "minimum_environment_speed_lower": bound(minimum_speed if minimum_speed is not None else arb(0)),
            "selected_environment_coordinate": best_coordinate,
            "environment_direction_lower": bound(environment_speed_per_t_lower),
            "can_enter_b6": all_pass,
        },
        "scope": {
            "b4_global_c1_branch_certified": True,
            "positive_measure_nonconstancy_certified": all_pass,
            "full_path_zero_cost_certified": False,
            "full_r5_certificate_generated": False,
            "r5_certified": False,
            "principle_r_pr_r5_certified": False,
            "principle_r_pr_r6_supplied": False,
            "principle_r_fully_witnessed": False,
            "global_ode_flow_certified": False,
            "r6_search_performed": False,
            "normal_K1_residual_recovery_performed": False,
        },
        "all_gates_pass": all_pass,
    }
    record["record_sha256"] = sha256_bytes(canonical_json(digest_payload(record)))
    return record


def write_record(record: dict[str, Any]) -> Path:
    target = CERT_PATH if record["scientific_status"] == CERTIFIED else DIAG_PATH
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
        "certified_epsilon_count": record["summary"]["certified_epsilon_count"],
        "epsilon_count": record["summary"]["epsilon_count"],
        "weakest_epsilon": record["summary"]["weakest_epsilon"],
        "can_enter_b6": record["summary"]["can_enter_b6"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
