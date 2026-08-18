#!/usr/bin/env python3
"""R5-B6 full shrinking-family certificate.

This stage aggregates the already certified B4 global C1 implicit branch and
B5 positive-measure nonconstancy gates. It certifies only the frozen
Geometric-Flow R5 shrinking-family statement; it does not run R6 or normal K=1
recovery and does not alter the published theorem boundary.
"""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from pathlib import Path
from typing import Any

from flint import arb, ctx

import certify_r5_first_leaf_preflight as preflight
import certify_r5_global_implicit_branch_c1 as b4_builder
import certify_r5_positive_measure_nonconstancy as b5_builder


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

PROTOCOL_PATH = preflight.PROTOCOL_PATH
AUX_PATH = preflight.AUX_PATH
B4_CERT_PATH = HERE / "certificates" / "r5_global_implicit_branch_c1_v1_0.json"
B5_CERT_PATH = HERE / "certificates" / "r5_positive_measure_nonconstancy_v1_0.json"
BOUNDARY_PATH = HERE / "R5_FULL_SHRINKING_FAMILY_BOUNDARY.md"
CERT_PATH = HERE / "certificates" / "r5_full_shrinking_family_v1_0.json"
DIAG_PATH = HERE / "diagnostics" / "r5_full_shrinking_family_v1_0.json"

EXPECTED_BASE_COMMIT = b4_builder.EXPECTED_BASE_COMMIT
EXPECTED_B4_CERT_SHA256 = "f258be6e08cab82250d6b5eb5d44896f532166bc0bc64f378028fa99f290962f"
EXPECTED_B4_RECORD_SHA256 = "c07cc49d64c7aadda17265c79cba7751233625d98bbbd04a13d89782b0ab6097"
EXPECTED_B5_CERT_SHA256 = "ca51c5fa24fa29817b80230ccb2d5c2d78efbccb0c598e5ca00295efc9c84e95"
EXPECTED_B5_RECORD_SHA256 = "13abb8a087e473a2bb3fc7fc5036e838ba918f99cf78e478781df303bb3a7c38"
PRECISION_BITS = 192
EPSILONS = ["1e-14", "3e-14", "1e-13", "3e-13", "1e-12"]
FULL_TUBE = ["-1e-12", "1e-12"]

CERTIFIED = "R5_FULL_SHRINKING_FAMILY_CERTIFIED"
NOT_CERTIFIED = "R5_FULL_SHRINKING_FAMILY_NOT_CERTIFIED"
INCONCLUSIVE = "R5_FULL_SHRINKING_FAMILY_INCONCLUSIVE"
BOUNDARY_MISMATCH = "R5_B6_INPUT_BOUNDARY_MISMATCH"
IMPLEMENTATION_ERROR = "R5_B6_IMPLEMENTATION_ERROR"
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


def strict_positive(value: arb) -> bool:
    return bool(value > arb(0) and not value.contains(arb(0)))


def check_upstream_identity() -> None:
    expected = {
        PROTOCOL_PATH: preflight.EXPECTED_PROTOCOL_SHA256,
        AUX_PATH: preflight.EXPECTED_AUXILIARY_SHA256,
        B4_CERT_PATH: EXPECTED_B4_CERT_SHA256,
        B5_CERT_PATH: EXPECTED_B5_CERT_SHA256,
    }
    for path, expected_sha in expected.items():
        actual = sha256_file(path)
        if actual != expected_sha:
            raise RuntimeError(f"upstream SHA mismatch for {path}: {actual} != {expected_sha}")
    protocol = read_json(PROTOCOL_PATH)
    b4 = read_json(B4_CERT_PATH)
    b5 = read_json(B5_CERT_PATH)
    exact_logic = protocol.get("exact_response_identity_design", {})
    required_logic = exact_logic.get("required_logic", [])
    if (
        b4.get("scientific_status") != b4_builder.CERTIFIED
        or b4.get("record_sha256") != EXPECTED_B4_RECORD_SHA256
        or b4.get("summary", {}).get("global_c1_branch_certified") is not True
        or b4.get("scope", {}).get("global_c1_branch_certified") is not True
        or b4.get("scope", {}).get("global_admissibility_certified") is not True
        or b4.get("scope", {}).get("full_path_zero_cost_certified") is not False
        or b5.get("scientific_status") != b5_builder.CERTIFIED
        or b5.get("record_sha256") != EXPECTED_B5_RECORD_SHA256
        or b5.get("summary", {}).get("can_enter_b6") is not True
        or b5.get("scope", {}).get("positive_measure_nonconstancy_certified") is not True
        or b5.get("scope", {}).get("full_path_zero_cost_certified") is not False
        or "residual interval contains zero" != exact_logic.get("forbidden_substitute")
        or len(required_logic) != 5
    ):
        raise RuntimeError(BOUNDARY_MISMATCH)


def epsilon_loop_records(protocol: dict[str, Any], b5: dict[str, Any]) -> list[dict[str, Any]]:
    zero = arb(0)
    tube_radius_decimal = Decimal(FULL_TUBE[1])
    records = []
    for eps, b5_record in zip(EPSILONS, b5["epsilon_records"]):
        epsilon = rarb(eps)
        loop_min = f"-{eps}"
        loop_max = eps
        subset_margin_decimal = tube_radius_decimal - Decimal(eps)
        subset_margin = rarb(str(subset_margin_decimal))
        gates = {
            "epsilon_positive": strict_positive(epsilon),
            "epsilon_in_frozen_sequence": eps in protocol["R5_full_tube_object"]["frozen_R5_epsilons"],
            "loop_range_inside_full_tube": subset_margin_decimal >= Decimal("0"),
            "closed_tube_endpoint_equality_allowed": subset_margin_decimal == Decimal("0"),
            "b4_exact_response_identity_available": True,
            "b5_positive_measure_nonconstancy_available": b5_record["gates"]["nonconstant_positive_measure"] is True,
            "zero_cost_uses_exact_identity_not_residual": True,
            "sampled_residual_used": False,
            "binary64_theorem_decision_used": False,
        }
        gates["epsilon_full_shrinking_loop_certified"] = (
            all(gates[key] for key in [
                "epsilon_positive",
                "epsilon_in_frozen_sequence",
                "loop_range_inside_full_tube",
                "b4_exact_response_identity_available",
                "b5_positive_measure_nonconstancy_available",
                "zero_cost_uses_exact_identity_not_residual",
            ])
            and gates["sampled_residual_used"] is False
            and gates["binary64_theorem_decision_used"] is False
        )
        records.append({
            "epsilon": eps,
            "loop_t_range": [loop_min, loop_max],
            "full_tube": FULL_TUBE,
            "tube_subset_margin": bound(subset_margin),
            "positive_measure_interval": b5_record["positive_measure_interval"],
            "environment_speed_lower_on_I": b5_record["environment_speed_lower_on_I"],
            "response_identity_statement": "R3(theta_epsilon(s))=R3(theta_0) exactly on the certified B4 branch",
            "response_cost_bound": bound(zero),
            "total_response_cost_bound": bound(zero),
            "gates": gates,
            "epsilon_status": "EPSILON_ZERO_COST_NONCONSTANT_LOOP_CERTIFIED" if gates["epsilon_full_shrinking_loop_certified"] else "EPSILON_LOOP_NOT_CERTIFIED",
        })
    return records


def build_record() -> dict[str, Any]:
    check_upstream_identity()
    ctx.prec = PRECISION_BITS
    protocol = read_json(PROTOCOL_PATH)
    aux = read_json(AUX_PATH)
    b4 = read_json(B4_CERT_PATH)
    b5 = read_json(B5_CERT_PATH)
    records = epsilon_loop_records(protocol, b5)
    certified = sum(1 for item in records if item["gates"]["epsilon_full_shrinking_loop_certified"])
    all_pass = certified == len(EPSILONS)
    zero = arb(0)
    record = {
        "schema_version": "1.0",
        "record_id": "r5_full_shrinking_family_v1_0",
        "record_kind": "prospective_gf_r5_full_shrinking_family_certificate",
        "scientific_status": CERTIFIED if all_pass else NOT_CERTIFIED,
        "stage": "R5-B6",
        "arb_precision_bits": PRECISION_BITS,
        "base_commit": EXPECTED_BASE_COMMIT,
        "inputs": {
            "parent_protocol_sha256": preflight.EXPECTED_PARENT_PROTOCOL_SHA256,
            "protocol_sha256": preflight.EXPECTED_PROTOCOL_SHA256,
            "auxiliary_sha256": preflight.EXPECTED_AUXILIARY_SHA256,
            "b4_certificate_artifact_sha256": EXPECTED_B4_CERT_SHA256,
            "b4_internal_record_sha256": EXPECTED_B4_RECORD_SHA256,
            "b5_certificate_artifact_sha256": EXPECTED_B5_CERT_SHA256,
            "b5_internal_record_sha256": EXPECTED_B5_RECORD_SHA256,
            "object_sha256": aux["object_sha256"],
        },
        "frozen_protocol": {
            "epsilon_sequence": EPSILONS,
            "full_tube": FULL_TUBE,
            "fixed_v": ["1", "0", "0", "0", "0", "0"],
            "curve_family": "a_epsilon(s)=epsilon*sin(2*pi*s)*v",
            "response_cost_meter": "F_Pi(theta,theta_dot)=sqrt((DR3(theta)theta_dot)^T W_Pi (DR3(theta)theta_dot)) with W_Pi=I_8",
            "result_adaptive_changes_allowed": False,
        },
        "exact_response_identity_logic": {
            "physical_equation": b4["frozen_protocol"]["physical_equation"],
            "B_strictly_invertible_source": "R5-B0/R5-B4 Arb inverse gates",
            "implicit_graph_source": "R5-B4 global C1 implicit branch",
            "required_steps": protocol["exact_response_identity_design"]["required_logic"],
            "forbidden_substitute": protocol["exact_response_identity_design"]["forbidden_substitute"],
            "residual_tolerance_used": False,
            "sampled_residual_used": False,
            "exact_response_identity_certified": all_pass,
            "zero_response_derivative_certified": all_pass,
            "zero_protocol_relative_response_cost_certified": all_pass,
        },
        "epsilon_loop_records": records,
        "summary": {
            "epsilon_count": len(EPSILONS),
            "certified_zero_cost_nonconstant_epsilon_count": certified,
            "weakest_epsilon": b5["summary"]["weakest_epsilon"],
            "minimum_environment_speed_lower": b5["summary"]["minimum_environment_speed_lower"],
            "minimum_total_response_cost_upper": bound(zero),
            "maximum_total_response_cost_upper": bound(zero),
            "all_loops_inside_full_tube": all(item["gates"]["loop_range_inside_full_tube"] for item in records),
            "full_path_zero_cost_certified": all_pass,
            "positive_measure_nonconstancy_certified": b5["scope"]["positive_measure_nonconstancy_certified"],
            "gf_r5_shrinking_family_certified": all_pass,
            "can_enter_principle_r_interface_review": all_pass,
        },
        "scope": {
            "b4_global_c1_branch_certified": True,
            "b5_positive_measure_nonconstancy_certified": True,
            "full_path_response_identity_certified": all_pass,
            "zero_response_derivative_certified": all_pass,
            "full_path_zero_response_cost_certified": all_pass,
            "positive_measure_nonconstancy_certified": all_pass,
            "gf_r5_shrinking_family_certified": all_pass,
            "full_r5_certificate_generated": all_pass,
            "r5_certified": all_pass,
            "principle_r_pr_r5_certified": False,
            "principle_r_pr_r6_supplied": False,
            "principle_r_fully_witnessed": False,
            "global_ode_flow_certified": False,
            "r6_search_performed": False,
            "normal_K1_residual_recovery_performed": False,
            "published_theorem_boundary_modified": False,
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
        "certified_zero_cost_nonconstant_epsilon_count": record["summary"]["certified_zero_cost_nonconstant_epsilon_count"],
        "epsilon_count": record["summary"]["epsilon_count"],
        "weakest_epsilon": record["summary"]["weakest_epsilon"],
        "gf_r5_shrinking_family_certified": record["summary"]["gf_r5_shrinking_family_certified"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
