#!/usr/bin/env python3
"""Single-instance semantic certificate verifier.

This verifier recomputes declared gate predicates from frozen protocol
thresholds and recorded certificate/report values. It does not import the
frozen scientific generators, rerun Arb interval computations, or independently
prove the recorded enclosures.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


class UsageError(Exception):
    """Schema or usage error."""


@dataclass(frozen=True)
class GateResult:
    name: str
    value: str
    relation: str
    threshold: str
    passed: bool

    def render(self) -> str:
        result = "PASS" if self.passed else "FAIL"
        return (
            f"{self.name}: value={self.value} relation={self.relation} "
            f"threshold={self.threshold} result={result}"
        )


def load_json(root: Path, rel: str) -> Any:
    path = root / rel
    if not path.is_file():
        raise UsageError(f"missing JSON artifact: {rel}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise UsageError(f"malformed JSON in {rel}: {exc}") from exc


def get_path(data: Any, dotted: str) -> Any:
    cursor = data
    for part in dotted.split("."):
        if not isinstance(cursor, dict) or part not in cursor:
            raise UsageError(f"missing required field: {dotted}")
        cursor = cursor[part]
    return cursor


def finite_decimal(data: Any, dotted: str, *, allow_string: bool = False) -> Decimal:
    value = get_path(data, dotted)
    allowed = (int, float, str) if allow_string else (int, float)
    if isinstance(value, bool) or not isinstance(value, allowed):
        raise UsageError(f"{dotted} must be a finite numeric value, got {type(value).__name__}")
    if isinstance(value, str):
        text = value
    else:
        if isinstance(value, float) and not math.isfinite(value):
            raise UsageError(f"{dotted} must be finite, got {value!r}")
        text = repr(value)
    try:
        dec = Decimal(text)
    except InvalidOperation as exc:
        raise UsageError(f"{dotted} is not a valid decimal: {value!r}") from exc
    if not dec.is_finite():
        raise UsageError(f"{dotted} must be finite, got {value!r}")
    return dec


def require_bool(data: Any, dotted: str) -> bool:
    value = get_path(data, dotted)
    if not isinstance(value, bool):
        raise UsageError(f"{dotted} must be a JSON boolean, got {type(value).__name__}")
    return value


def bool_gate(name: str, value: bool, expected: bool) -> GateResult:
    return GateResult(name, str(value), "is", str(expected), value is expected)


def compare_gate(name: str, value: Decimal, relation: str, threshold: Decimal) -> GateResult:
    if relation == "<=":
        passed = value <= threshold
    elif relation == ">=":
        passed = value >= threshold
    elif relation == "==":
        passed = value == threshold
    else:  # pragma: no cover - internal guard
        raise AssertionError(relation)
    return GateResult(name, str(value), relation, str(threshold), passed)


def gates_match(name: str, data: dict[str, Any], expected: dict[str, bool]) -> list[GateResult]:
    gates = get_path(data, "gates")
    if not isinstance(gates, dict):
        raise UsageError(f"{name}.gates must be an object")
    results: list[GateResult] = []
    for gate_name, expected_value in expected.items():
        actual = require_bool(gates, gate_name)
        results.append(bool_gate(f"{name}.gates.{gate_name}", actual, expected_value))
    extra = sorted(set(gates) - set(expected))
    for gate_name in extra:
        require_bool(gates, gate_name)
    return results


def check_aggregation(name: str, data: dict[str, Any]) -> GateResult:
    gates = get_path(data, "gates")
    if not isinstance(gates, dict):
        raise UsageError(f"{name}.gates must be an object")
    all_gates = require_bool(data, "all_gates_pass")
    aggregate = all(require_bool(gates, key) for key in sorted(gates))
    return bool_gate(f"{name}.all_gates_pass_equals_all_gates", all_gates, aggregate)


def compare_report_consistency(
    name: str,
    certificate: dict[str, Any],
    report: dict[str, Any],
    fields: list[str],
) -> list[GateResult]:
    results: list[GateResult] = []
    for field in fields:
        cert_value = get_path(certificate, field)
        report_value = get_path(report, field)
        results.append(GateResult(
            f"{name}.report_consistency.{field}",
            repr(report_value),
            "== certificate",
            repr(cert_value),
            report_value == cert_value,
        ))
    if "gates" in report:
        results.append(GateResult(
            f"{name}.report_consistency.gates",
            "report.gates",
            "== certificate.gates",
            "certificate.gates",
            report.get("gates") == certificate.get("gates"),
        ))
    if "all_gates_pass" in report:
        results.append(GateResult(
            f"{name}.report_consistency.all_gates_pass",
            repr(report.get("all_gates_pass")),
            "== certificate.all_gates_pass",
            repr(certificate.get("all_gates_pass")),
            report.get("all_gates_pass") == certificate.get("all_gates_pass"),
        ))
    return results


def verify_v093(root: Path) -> list[GateResult]:
    protocol = load_json(root, "results/v0_9_3_reference/protocol.json")
    certificate = load_json(root, "results/v0_9_3_reference/intrinsic_picard_microstep_certificate.json")
    report = load_json(root, "results/v0_9_3_reference/report.json")
    if not isinstance(protocol, dict) or not isinstance(certificate, dict) or not isinstance(report, dict):
        raise UsageError("v0.9.3 protocol, certificate, and report must be JSON objects")

    thresholds = get_path(protocol, "gates")
    if not isinstance(thresholds, dict):
        raise UsageError("v0.9.3 protocol.gates must be an object")

    results = [
        compare_gate(
            "v0.9.3.uniform_strict_L6_descent",
            finite_decimal(certificate, "uniform_dL6_dt_upper"),
            "<=",
            finite_decimal(protocol, "gates.maximum_L6_derivative"),
        ),
        compare_gate(
            "v0.9.3.projected_gradient_nonstationary",
            finite_decimal(certificate, "intrinsic_projected_gradient_norm_lower"),
            ">=",
            finite_decimal(protocol, "gates.minimum_projected_gradient_norm"),
        ),
        compare_gate(
            "v0.9.3.picard_contraction",
            finite_decimal(certificate, "picard_contraction_factor"),
            "<=",
            finite_decimal(protocol, "gates.maximum_picard_contraction"),
        ),
        compare_gate(
            "v0.9.3.picard_self_mapping",
            finite_decimal(certificate, "picard_self_mapping_utilization"),
            "<=",
            finite_decimal(protocol, "gates.maximum_picard_self_mapping_utilization"),
        ),
        compare_gate(
            "v0.9.3.complex_parametric_fibre_graph",
            finite_decimal(certificate, "complex_graph_krawczyk_utilization"),
            "<=",
            finite_decimal(protocol, "gates.maximum_graph_utilization"),
        ),
        compare_gate(
            "v0.9.3.implicit_graph_derivative_enclosed",
            finite_decimal(certificate, "implicit_derivative_neumann_defect_upper"),
            "<=",
            finite_decimal(protocol, "gates.maximum_graph_derivative_defect"),
        ),
        compare_gate(
            "v0.9.3.pullback_metric_positive_definite",
            finite_decimal(certificate, "pullback_metric_neumann_defect_upper"),
            "<=",
            finite_decimal(protocol, "gates.maximum_pullback_metric_defect"),
        ),
        compare_gate(
            "v0.9.3.certified_time_step",
            finite_decimal(certificate, "certified_time_step"),
            "==",
            finite_decimal(protocol, "time_step", allow_string=True),
        ),
        compare_gate(
            "v0.9.3.inner_real_picard_radius",
            finite_decimal(certificate, "inner_real_picard_radius"),
            "==",
            finite_decimal(protocol, "inner_real_picard_radius", allow_string=True),
        ),
        bool_gate("v0.9.3.validated_ODE_claimed", require_bool(certificate, "validated_ODE_claimed"), True),
        bool_gate("v0.9.3.ODE_existence_certified", require_bool(certificate, "ODE_existence_certified"), True),
        bool_gate("v0.9.3.ODE_uniqueness_certified", require_bool(certificate, "ODE_uniqueness_certified"), True),
        bool_gate(
            "v0.9.3.exact_response_preservation_certified",
            require_bool(certificate, "exact_response_preservation_certified"),
            True,
        ),
        bool_gate(
            "v0.9.3.uniform_L6_descent_certified_for_validated_solution",
            require_bool(certificate, "uniform_L6_descent_certified_for_validated_solution"),
            True,
        ),
        bool_gate("v0.9.3.global_flow_claimed", require_bool(certificate, "global_flow_claimed"), False),
    ]

    expected_gates = {
        "analytic_normalization_branch": True,
        "cauchy_lipschitz_resolved": True,
        "complex_parametric_fibre_graph": results[4].passed,
        "exact_response_preservation": True,
        "frozen_child_stage_a": True,
        "implicit_graph_derivative_enclosed": results[5].passed,
        "intrinsic_projected_gradient_nonstationary": results[1].passed,
        "picard_contraction": results[2].passed,
        "picard_self_mapping": results[3].passed,
        "pullback_metric_positive_definite": results[6].passed,
        "uniform_strict_L6_descent": results[0].passed,
    }
    results.extend(gates_match("v0.9.3", certificate, expected_gates))
    results.append(check_aggregation("v0.9.3", certificate))
    results.extend(compare_report_consistency(
        "v0.9.3",
        certificate,
        report,
        [
            "certified_time_step",
            "uniform_dL6_dt_upper",
            "intrinsic_projected_gradient_norm_lower",
            "picard_contraction_factor",
            "picard_self_mapping_utilization",
            "global_flow_claimed",
            "validated_ODE_claimed",
        ],
    ))
    return results


def verify_v074(root: Path) -> list[GateResult]:
    protocol = load_json(root, "results/reference/protocol.json")
    certificate = load_json(root, "results/reference/certificate.json")
    report = load_json(root, "results/reference/report.json")
    summary = load_json(root, "results/reference_run_summary.json")
    if not all(isinstance(item, dict) for item in (protocol, certificate, report, summary)):
        raise UsageError("v0.7.4 protocol, certificate, report, and summary must be JSON objects")
    cert_report = get_path(certificate, "report")
    if not isinstance(cert_report, dict):
        raise UsageError("v0.7.4 certificate.report must be an object")
    child_records = get_path(certificate, "child_box_records")
    if not isinstance(child_records, list):
        raise UsageError("v0.7.4 child_box_records must be a list")

    child_count = int(finite_decimal(protocol, "child_boxes"))
    stage_a_count = sum(1 for child in child_records if isinstance(child, dict) and child.get("stage_a_pass") is True)
    stage_b_count = sum(1 for child in child_records if isinstance(child, dict) and child.get("stage_b_pass") is True)
    pass_count = sum(1 for child in child_records if isinstance(child, dict) and child.get("pass") is True)

    results = [
        compare_gate(
            "v0.7.4.maximum_right_inverse_defect",
            finite_decimal(report, "maximum_right_inverse_defect_upper"),
            "<=",
            finite_decimal(protocol, "gates.maximum_right_inverse_defect"),
        ),
        compare_gate(
            "v0.7.4.minimum_projected_gradient_norm",
            finite_decimal(report, "minimum_projected_gradient_norm_lower"),
            ">=",
            finite_decimal(protocol, "gates.minimum_projected_gradient_norm"),
        ),
        compare_gate(
            "v0.7.4.minimum_alignment_scale",
            finite_decimal(report, "minimum_alignment_scale"),
            ">=",
            finite_decimal(protocol, "gates.minimum_alignment_scale"),
        ),
        compare_gate(
            "v0.7.4.maximum_response_tangency_norm",
            finite_decimal(report, "maximum_response_tangency_norm_upper"),
            "<=",
            finite_decimal(protocol, "gates.maximum_response_tangency_norm"),
        ),
        compare_gate(
            "v0.7.4.maximum_dL6_dell",
            finite_decimal(report, "maximum_dL6_dell_upper"),
            "<=",
            finite_decimal(protocol, "gates.maximum_dL6_dell"),
        ),
        compare_gate(
            "v0.7.4.kkt_witness_residual_remains_inconclusive",
            finite_decimal(report, "maximum_parallel_relative_residual_upper"),
            ">=",
            finite_decimal(protocol, "gates.maximum_parallel_relative_residual"),
        ),
        compare_gate("v0.7.4.child_records_count", Decimal(len(child_records)), "==", Decimal(child_count)),
        compare_gate(
            "v0.7.4.child_boxes_passing_stage_a",
            Decimal(stage_a_count),
            "==",
            finite_decimal(report, "child_boxes_declared"),
        ),
        compare_gate("v0.7.4.child_boxes_passing_stage_b", Decimal(stage_b_count), "==", Decimal(0)),
        compare_gate("v0.7.4.child_boxes_passing", Decimal(pass_count), "==", Decimal(0)),
        bool_gate("v0.7.4.cover_is_exact_and_contiguous", require_bool(report, "cover_is_exact_and_contiguous"), True),
        bool_gate("v0.7.4.stage_a_rank_descent_cover_certified", require_bool(report, "stage_a_rank_descent_cover_certified"), True),
        bool_gate("v0.7.4.uniform_single_box_L6_descent_certified", require_bool(report, "uniform_single_box_L6_descent_certified"), True),
        bool_gate("v0.7.4.kkt_witness_alignment_cover_certified", require_bool(report, "kkt_witness_alignment_cover_certified"), False),
        bool_gate("v0.7.4.validated_ODE_claimed", require_bool(report, "validated_ODE_claimed"), False),
        bool_gate("v0.7.4.global_flow_claimed", require_bool(report, "global_flow_claimed"), False),
        bool_gate("v0.7.4.all_gates_pass_expected_false", require_bool(report, "all_gates_pass"), False),
    ]
    results.append(GateResult(
        "v0.7.4.stage_b_inconclusive_consistency",
        "residual_above_threshold",
        "matches",
        "kkt_witness_alignment_cover_certified=false",
        results[5].passed and require_bool(report, "kkt_witness_alignment_cover_certified") is False,
    ))

    for field in [
        "all_gates_pass",
        "stage_a_rank_descent_cover_certified",
        "uniform_single_box_L6_descent_certified",
        "kkt_witness_alignment_cover_certified",
        "global_flow_claimed",
        "validated_ODE_claimed",
        "child_boxes_declared",
        "child_boxes_passing_stage_a",
        "child_boxes_passing_stage_b",
        "maximum_dL6_dell_upper",
        "minimum_projected_gradient_norm_lower",
    ]:
        results.append(GateResult(
            f"v0.7.4.certificate_report_consistency.{field}",
            repr(cert_report.get(field)),
            "== report",
            repr(report.get(field)),
            cert_report.get(field) == report.get(field),
        ))
        results.append(GateResult(
            f"v0.7.4.summary_consistency.{field}",
            repr(summary.get(field)),
            "== report",
            repr(report.get(field)),
            summary.get(field) == report.get(field),
        ))
    return results


def run(root: Path) -> list[GateResult]:
    return verify_v074(root) + verify_v093(root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(ROOT), help="repository root")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    print("single-instance semantic certificate verifier")
    print("mode: recorded-threshold gate recomputation; no Arb rerun")
    try:
        results = run(root)
    except UsageError as exc:
        print(f"SCHEMA ERROR: {exc}", file=sys.stderr)
        return 2
    for result in results:
        print(result.render())
    passed = all(result.passed for result in results)
    print("PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
