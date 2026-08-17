#!/usr/bin/env python3
"""Verify the prospective R5-B0 static Arb gate record."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import certify_r5_static_arb_gates as certifier


HERE = Path(__file__).resolve().parent
CERT_PATH = HERE / "certificates" / "r5_static_arb_gates_v1_0.json"
EXPECTED_STATUS = "R5_STATIC_ARB_GATES_CERTIFIED"
EXPECTED_AUXILIARY_SHA256 = certifier.EXPECTED_AUXILIARY_SHA256
EXPECTED_PROTOCOL_SHA256 = certifier.EXPECTED_PROTOCOL_SHA256
FORBIDDEN_KEYS = certifier.FORBIDDEN_KEYS


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


def positive_decimal_string(value: Any) -> bool:
    if not finite_decimal_string(value):
        return False
    return Decimal(value) > 0


def less_than_one_decimal_string(value: Any) -> bool:
    if not finite_decimal_string(value):
        return False
    return Decimal(value) < 1


def find_forbidden_keys(value: Any) -> list[str]:
    found: list[str] = []

    def walk(node: Any, prefix: str) -> None:
        if isinstance(node, dict):
            for key, child in node.items():
                path = f"{prefix}.{key}" if prefix else str(key)
                if key in FORBIDDEN_KEYS and child is not False:
                    found.append(path)
                walk(child, path)
        elif isinstance(node, list):
            for index, child in enumerate(node):
                walk(child, f"{prefix}[{index}]")

    walk(value, "")
    return found


def comparable_certificate(value: dict[str, Any]) -> dict[str, Any]:
    return certifier.certificate_digest_payload(value)


def verify(certificate: dict[str, Any]) -> dict[str, bool]:
    expected = certifier.build_certificate()
    gates = certificate.get("gates", {})
    object_identity = gates.get("object_identity", {})
    protocol_identity = gates.get("protocol_identity", {})
    frame_T = gates.get("frame_rank_T", {})
    frame_N = gates.get("frame_rank_N", {})
    transversality = gates.get("T_N_transversality", {})
    B_gate = gates.get("B_strict_invertibility", {})
    P_gate = gates.get("preconditioner_defect", {})
    scope = certificate.get("scope", {})
    inputs = certificate.get("inputs", {})

    checks = {
        "certificate_matches_recomputed_arb_gates": (
            comparable_certificate(certificate) == comparable_certificate(expected)
        ),
        "certificate_sha256": (
            certificate.get("certificate_sha256")
            == certifier.sha256_bytes(certifier.canonical_json(comparable_certificate(certificate)))
        ),
        "schema_version": certificate.get("schema_version") == "1.0",
        "certificate_id": certificate.get("certificate_id") == "r5_static_arb_gates_v1_0",
        "certificate_kind": (
            certificate.get("certificate_kind") == "prospective_r5_b0_static_arb_gates"
        ),
        "scientific_status": certificate.get("scientific_status") == EXPECTED_STATUS,
        "all_gates_pass": certificate.get("all_gates_pass") is True,
        "arb_precision_bits": certificate.get("arb_precision_bits") == 192,
        "input_hashes": (
            inputs.get("auxiliary_sha256") == EXPECTED_AUXILIARY_SHA256
            and inputs.get("protocol_sha256") == EXPECTED_PROTOCOL_SHA256
            and inputs.get("object_sha256") == certifier.EXPECTED_OBJECT_SHA256
        ),
        "object_identity_gate": (
            object_identity.get("path_shape_sha256_and_finiteness") is True
            and object_identity.get("theta0_T_N_B_c_P_bound_to_protocol") is True
        ),
        "protocol_identity_gate": all(protocol_identity.values()),
        "frame_rank_T_gate": (
            frame_T.get("strictly_nonzero") is True
            and positive_decimal_string(frame_T.get("abs_determinant_lower_bound"))
        ),
        "frame_rank_N_gate": (
            frame_N.get("strictly_nonzero") is True
            and positive_decimal_string(frame_N.get("abs_determinant_lower_bound"))
        ),
        "T_N_transversality_gate": (
            transversality.get("strictly_nonzero") is True
            and positive_decimal_string(transversality.get("abs_determinant_lower_bound"))
        ),
        "B_invertibility_gate": (
            B_gate.get("strictly_nonzero") is True
            and B_gate.get("strictly_less_than_one") is True
            and positive_decimal_string(B_gate.get("abs_determinant_lower_bound"))
            and less_than_one_decimal_string(B_gate.get("defect_upper_bound"))
        ),
        "preconditioner_defect_gate": (
            P_gate.get("strictly_nonzero") is True
            and P_gate.get("strictly_less_than_one") is True
            and positive_decimal_string(P_gate.get("abs_determinant_lower_bound"))
            and less_than_one_decimal_string(P_gate.get("defect_upper_bound"))
            and P_gate.get("J_N_definition") == "J_N = B * DR3(theta_0) * N"
        ),
        "name_separation": (
            "response-cost weight" in gates.get("name_separation", {}).get("W_Pi", "")
            and "graph equation" in gates.get("name_separation", {}).get("B", "")
            and "preconditioner" in gates.get("name_separation", {}).get("P", "")
            and gates.get("name_separation", {}).get("distinct_roles_gate") is True
        ),
        "scope_excludes_full_tube_and_r6": (
            scope.get("r5_static_gates_only") is True
            and scope.get("r5_full_tube_certificate_generated") is False
            and scope.get("r5_graph_existence_certified") is False
            and scope.get("r5_exact_response_preservation_certified") is False
            and scope.get("r5_zero_total_cost_certified") is False
            and scope.get("r6_search_performed") is False
            and scope.get("normal_K1_residual_recovery_performed") is False
            and scope.get("binary64_theorem_decision_used") is False
            and scope.get("residual_near_zero_accepted_as_exact_zero") is False
        ),
        "forbidden_keys_absent": not find_forbidden_keys(certificate),
    }
    return checks


def mutation_cases(certificate: dict[str, Any]) -> dict[str, dict[str, Any]]:
    cases: dict[str, dict[str, Any]] = {}

    mutated = copy.deepcopy(certificate)
    mutated["inputs"]["object_sha256"]["T"] = "0" * 64
    cases["object_sha_change_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["gates"]["object_identity"]["path_shape_sha256_and_finiteness"] = False
    cases["dimension_or_finiteness_gate_false_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["gates"]["frame_rank_T"]["strictly_nonzero"] = False
    cases["rank_gate_forged_false_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["gates"]["T_N_transversality"]["abs_determinant_lower_bound"] = "0"
    cases["transversality_zero_lower_bound_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["gates"]["B_strict_invertibility"]["strictly_less_than_one"] = False
    cases["B_invertibility_gate_false_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["gates"]["preconditioner_defect"]["defect_upper_bound"] = "1"
    cases["preconditioner_defect_one_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["gates"]["preconditioner_defect"]["defect_upper_bound"] = "NaN"
    cases["nan_bound_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["gates"]["B_strict_invertibility"]["defect_upper_bound"] = "Infinity"
    cases["infinity_bound_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["scope"]["residual_near_zero_accepted_as_exact_zero"] = True
    cases["residual_near_zero_as_exact_zero_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["scope"]["r5_full_tube_certificate_generated"] = True
    cases["static_as_full_tube_certificate_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["scope"]["r6_search_performed"] = True
    cases["R6_marked_run_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["scope"]["normal_K1_residual_recovery_performed"] = True
    cases["normal_K1_marked_run_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["gates"]["name_separation"]["B"] = mutated["gates"]["name_separation"]["W_Pi"]
    cases["W_Pi_B_P_conflation_fails"] = mutated

    return cases


def run_mutation_tests(certificate: dict[str, Any]) -> dict[str, bool]:
    return {name: not all(verify(case).values()) for name, case in mutation_cases(certificate).items()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mutation-tests", action="store_true")
    args = parser.parse_args()

    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    certificate = read_json(CERT_PATH)
    checks = verify(certificate)
    if args.mutation_tests:
        checks.update(run_mutation_tests(certificate))
    print(json.dumps(checks, indent=2, sort_keys=True))
    if not all(checks.values()):
        print("FAIL")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
