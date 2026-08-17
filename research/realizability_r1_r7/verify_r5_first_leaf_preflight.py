#!/usr/bin/env python3
"""Verify the R5-B1a first-leaf preflight certificate."""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import certify_r5_first_leaf_preflight as certifier


HERE = Path(__file__).resolve().parent
CERT_PATH = HERE / "certificates" / "r5_first_leaf_preflight_v1_0.json"
EXPECTED_STATUSES = {
    certifier.EXPECTED_STATUS_CERTIFIED,
    certifier.EXPECTED_STATUS_INCONCLUSIVE,
}
ARB_RE = re.compile(
    r"^\[(?P<mid>[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?) "
    r"\+/- (?P<rad>(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\]$"
)


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


def decimal_bounds(value: Any) -> tuple[Decimal, Decimal] | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = Decimal(value)
    except (InvalidOperation, ValueError, OverflowError):
        match = ARB_RE.match(value)
        if not match:
            return None
        try:
            mid = Decimal(match.group("mid"))
            rad = Decimal(match.group("rad"))
        except (InvalidOperation, ValueError, OverflowError):
            return None
        lower = mid - rad
        upper = mid + rad
    else:
        lower = parsed
        upper = parsed
    if not lower.is_finite() or not upper.is_finite() or lower > upper:
        return None
    return lower, upper


def finite_bound_string(value: Any) -> bool:
    return decimal_bounds(value) is not None


def lower_decimal(value: Any) -> Decimal:
    bounds = decimal_bounds(value)
    if bounds is None:
        raise ValueError(f"not a finite decimal/Arb bound: {value!r}")
    return bounds[0]


def upper_decimal(value: Any) -> Decimal:
    bounds = decimal_bounds(value)
    if bounds is None:
        raise ValueError(f"not a finite decimal/Arb bound: {value!r}")
    return bounds[1]


def positive_decimal_string(value: Any) -> bool:
    return finite_bound_string(value) and lower_decimal(value) > 0


def nonnegative_decimal_string(value: Any) -> bool:
    return finite_bound_string(value) and upper_decimal(value) >= 0


def less_than_one_decimal_string(value: Any) -> bool:
    return finite_bound_string(value) and upper_decimal(value) < 1


def lower_bound_positive(value: Any) -> bool:
    return finite_bound_string(value) and lower_decimal(value) > 0


def comparable(value: dict[str, Any]) -> dict[str, Any]:
    return certifier.certificate_digest_payload(value)


def verify(certificate: dict[str, Any]) -> dict[str, bool]:
    expected = certifier.build_certificate()
    gates = certificate.get("gates", {})
    inputs = certificate.get("inputs", {})
    scope = certificate.get("scope", {})
    leaf = gates.get("leaf_identity", {})
    parameter = gates.get("parameter_to_intrinsic_line", {})
    chart = gates.get("chart_residence", {})
    nowrap = gates.get("no_phase_wrap", {})
    B_gate = gates.get("B_strict_invertibility_on_leaf", {})
    J_gate = gates.get("normal_jacobian_invertibility_on_leaf", {})
    P_gate = gates.get("preconditioner_defect_on_leaf", {})
    K_gate = gates.get("krawczyk_self_map", {})
    contraction = gates.get("krawczyk_contraction", {})
    residual = gates.get("response_residual_enclosure", {})
    unique = gates.get("unique_root", {})
    exact = gates.get("exact_response_implication", {})
    names = gates.get("name_separation", {})

    recomputed_match = comparable(certificate) == comparable(expected)
    status = certificate.get("scientific_status")
    all_pass = certificate.get("all_gates_pass")
    expected_all_pass = status == certifier.EXPECTED_STATUS_CERTIFIED

    checks = {
        "certificate_matches_recomputed_arb_preflight": recomputed_match,
        "certificate_sha256": (
            certificate.get("certificate_sha256")
            == certifier.sha256_bytes(certifier.canonical_json(comparable(certificate)))
        ),
        "schema_version": certificate.get("schema_version") == "1.0",
        "certificate_id": certificate.get("certificate_id") == "r5_first_leaf_preflight_v1_0",
        "certificate_kind": (
            certificate.get("certificate_kind") == "prospective_r5_b1a_first_leaf_preflight"
        ),
        "scientific_status_allowed": status in EXPECTED_STATUSES,
        "all_gates_status_consistent": all_pass is expected_all_pass,
        "arb_precision": certificate.get("arb_precision_bits") == 192,
        "base_commit": certificate.get("base_commit") == certifier.EXPECTED_BASE_COMMIT,
        "input_hashes": (
            inputs.get("parent_protocol_sha256") == certifier.EXPECTED_PARENT_PROTOCOL_SHA256
            and inputs.get("protocol_sha256") == certifier.EXPECTED_PROTOCOL_SHA256
            and inputs.get("auxiliary_sha256") == certifier.EXPECTED_AUXILIARY_SHA256
            and inputs.get("static_certificate_sha256") == certifier.EXPECTED_STATIC_CERT_SHA256
            and inputs.get("v0_7_4_source_sha256") == certifier.EXPECTED_V074_SOURCE_SHA256
            and inputs.get("object_sha256") == certifier.EXPECTED_OBJECT_SHA256
        ),
        "leaf_identity": (
            leaf.get("leaf_index") == 0
            and leaf.get("leaf_interval") == certifier.LEAF_INTERVAL
            and leaf.get("matches_protocol_first_leaf") is True
            and leaf.get("subdivision_count") == 16
            and leaf.get("maximum_refinement_depth") == 8
        ),
        "parameter_interval": (
            parameter.get("v") == ["1", "0", "0", "0", "0", "0"]
            and parameter.get("a_equals_t_times_v") is True
            and finite_bound_string(parameter.get("t_box_lower"))
            and finite_bound_string(parameter.get("t_box_upper"))
            and lower_decimal(parameter.get("t_box_lower")) <= Decimal("-1e-12")
            and upper_decimal(parameter.get("t_box_upper")) >= Decimal("-8.75e-13")
        ),
        "chart_gate": (
            chart.get("gate") is True
            and lower_bound_positive(chart.get("margin_lower_bound"))
            and nonnegative_decimal_string(chart.get("max_phase_displacement_abs_upper"))
        ),
        "nowrap_gate": (
            nowrap.get("gate") is True
            and lower_bound_positive(nowrap.get("margin_lower_bound"))
            and nonnegative_decimal_string(nowrap.get("max_phase_displacement_abs_upper"))
        ),
        "B_invertibility_gate": (
            B_gate.get("gate") is True
            and less_than_one_decimal_string(B_gate.get("defect_upper_bound"))
        ),
        "normal_jacobian_gate": (
            J_gate.get("strictly_nonzero") is True
            and positive_decimal_string(J_gate.get("abs_determinant_lower_bound"))
            and "B*DR3" in J_gate.get("J_N_definition", "")
        ),
        "preconditioner_defect_gate": (
            P_gate.get("gate") is True
            and less_than_one_decimal_string(P_gate.get("defect_upper_bound"))
            and P_gate.get("P_source") == "frozen auxiliary object P"
        ),
        "self_map_logic": (
            K_gate.get("b_box_radius") == certifier.B_BOX_RADIUS
            and positive_decimal_string(K_gate.get("b_box_radius"))
            and nonnegative_decimal_string(K_gate.get("correction_norm_upper_bound"))
            and nonnegative_decimal_string(K_gate.get("image_radius_upper_bound"))
            and finite_bound_string(K_gate.get("strict_interior_margin_lower_bound"))
            and K_gate.get("gate") is (
                lower_decimal(K_gate.get("strict_interior_margin_lower_bound")) > 0
            )
        ),
        "contraction_gate": (
            contraction.get("gate") is True
            and less_than_one_decimal_string(contraction.get("contraction_upper_bound"))
        ),
        "residual_not_exact_zero": (
            residual.get("residual_near_zero_accepted_as_exact_response") is False
            and nonnegative_decimal_string(residual.get("residual_abs_upper_bound"))
        ),
        "unique_root_consistency": (
            unique.get("gate") is (
                K_gate.get("gate") is True and contraction.get("gate") is True
            )
        ),
        "exact_response_logic": (
            exact.get("gate") is True
            and exact.get("residual_interval_substituted_for_exact_zero") is False
            and "strict invertibility of B" in exact.get("logic", "")
        ),
        "name_separation": (
            "response-cost weight" in names.get("W_Pi", "")
            and "graph equation" in names.get("B", "")
            and "preconditioner" in names.get("P", "")
            and names.get("distinct_roles_gate") is True
        ),
        "scope_exclusions": (
            scope.get("first_leaf_preflight_only") is True
            and scope.get("r5_full_tube_certificate_generated") is False
            and scope.get("r5_full_tube_certified") is False
            and scope.get("r5_certified") is False
            and scope.get("r6_search_performed") is False
            and scope.get("normal_K1_residual_recovery_performed") is False
            and scope.get("binary64_theorem_decision_used") is False
            and scope.get("residual_near_zero_accepted_as_exact_zero") is False
        ),
    }
    return checks


def mutation_cases(certificate: dict[str, Any]) -> dict[str, dict[str, Any]]:
    cases: dict[str, dict[str, Any]] = {}

    mutated = copy.deepcopy(certificate)
    mutated["inputs"]["protocol_sha256"] = "0" * 64
    cases["upstream_sha_change_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["gates"]["leaf_identity"]["leaf_index"] = 1
    cases["leaf_index_change_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["gates"]["leaf_identity"]["leaf_interval"] = ["-9e-13", "-8.75e-13"]
    cases["leaf_interval_shrink_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["arb_precision_bits"] = 128
    cases["arb_precision_change_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["inputs"]["object_sha256"]["P"] = "f" * 64
    cases["object_sha_change_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["gates"]["chart_residence"]["margin_lower_bound"] = "NaN"
    cases["nan_bound_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["gates"]["no_phase_wrap"]["margin_lower_bound"] = "Infinity"
    cases["infinity_bound_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["gates"]["chart_residence"]["gate"] = False
    cases["chart_gate_forgery_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["gates"]["no_phase_wrap"]["gate"] = False
    cases["nowrap_gate_forgery_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["gates"]["B_strict_invertibility_on_leaf"]["gate"] = False
    cases["B_gate_forgery_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["gates"]["normal_jacobian_invertibility_on_leaf"]["strictly_nonzero"] = False
    cases["JN_gate_forgery_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["gates"]["preconditioner_defect_on_leaf"]["defect_upper_bound"] = "1"
    cases["defect_ge_one_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["gates"]["krawczyk_contraction"]["contraction_upper_bound"] = "1"
    cases["contraction_ge_one_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["gates"]["krawczyk_self_map"]["strict_interior_margin_lower_bound"] = "0"
    mutated["gates"]["krawczyk_self_map"]["gate"] = True
    cases["non_strict_self_map_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["gates"]["response_residual_enclosure"]["residual_near_zero_accepted_as_exact_response"] = True
    cases["residual_near_zero_as_exact_response_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["gates"]["unique_root"]["gate"] = True
    cases["forged_unique_root_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["all_gates_pass"] = True
    cases["forged_all_gates_pass_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["scientific_status"] = "R5_FULL_TUBE_CERTIFIED"
    cases["full_tube_status_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["scope"]["r6_search_performed"] = True
    cases["R6_marked_run_fails"] = mutated

    mutated = copy.deepcopy(certificate)
    mutated["scope"]["normal_K1_residual_recovery_performed"] = True
    cases["normal_K1_marked_run_fails"] = mutated

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
