#!/usr/bin/env python3
"""C4-E2a: Arb certificate for the frozen eight-transition atlas chain.

Every adjacent pair of the nine C4-E0 mixed-trajectory charts is tested using
the C4-E1a positive-volume overlap-box certificate.  This proves a finite
chain of mutually overlapping regular charts and a positive local residence
window at every recentered chart.

It deliberately does not claim validated flowpipe transport from one overlap
box to the next.  Consequently the sum of local residence lower bounds is
reported only as an aggregate local budget, not as a certified trajectory
continuation time.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np

try:
    import c4_arb_recovery_core_certificate_v1_0 as base
    import c4_e0_moving_chart_overlap_preflight_v1_0 as e0
    import c4_e1a_arb_first_chart_overlap_certificate_v1_0 as e1
except ModuleNotFoundError as exc:
    raise RuntimeError(
        "Place C4-E2a beside the C4-B/E0/E1a modules and install "
        "python-flint==0.8.0 and numpy==2.0.2."
    ) from exc


TITLE = "C4-E2a ARB MULTICHART OVERLAP-CHAIN CERTIFICATE"
VERSION = "1.0"
DEFAULT_REPORT = "c4_e2a_arb_multichart_overlap_chain_v1_0.json"


def canonical_sha(value: object) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chart-tangent-half", type=float, default=0.02)
    parser.add_argument("--chart-normal-half", type=float, default=1.0e-4)
    parser.add_argument("--overlap-tangent-half", type=float, default=1.0e-7)
    parser.add_argument("--overlap-normal-half", type=float, default=1.0e-7)
    parser.add_argument("--beta", type=float, default=base.BETA)
    parser.add_argument("--report", default=DEFAULT_REPORT)
    args, unknown = parser.parse_known_args(argv)
    if unknown:
        print("[notice] ignored notebook/kernel arguments:", unknown)
    if min(args.chart_tangent_half, args.chart_normal_half,
           args.overlap_tangent_half, args.overlap_normal_half, args.beta) <= 0:
        raise ValueError("all half-widths and beta must be positive")

    base.ctx.prec = base.PRECISION_BITS
    model = e0.load_model(e0.obtain_model(Path.cwd()))
    charts = e1.frozen_mixed_charts(model, windows=8, steps=4)
    protocol = {
        "version": VERSION,
        "precision_bits": base.PRECISION_BITS,
        "model_sha256": e0.MODEL_SHA256,
        "trajectory": "C4-E0 frozen mixed trajectory",
        "chart_count": 9,
        "transition_count": 8,
        "chart_tangent_half": args.chart_tangent_half,
        "chart_normal_half": args.chart_normal_half,
        "overlap_tangent_half": args.overlap_tangent_half,
        "overlap_normal_half": args.overlap_normal_half,
        "beta": args.beta,
        "criterion": "all eight adjacent chart pairs have certified positive-volume regular overlap boxes",
    }
    print("=" * 100)
    print(f"{TITLE} v{VERSION}")
    print("=" * 100)
    print("scope: rigorous atlas overlap chain; not validated flowpipe continuation/K=1/QPU")
    print("protocol sha256:", canonical_sha(protocol))

    transitions = []
    for index in range(8):
        certificate = e1.certify_transition(
            charts[index], charts[index + 1],
            args.chart_tangent_half, args.chart_normal_half,
            args.overlap_tangent_half, args.overlap_normal_half, args.beta,
        )
        transitions.append(certificate)
        bounds = certificate["bounds"]
        print(
            f"[{index + 1:02d}/08] {index}->{index + 1} "
            f"pass={certificate['all_gates_pass']} "
            f"q_old={bounds['old_chart_neumann_defect_inf_upper']:.6g} "
            f"q_new={bounds['new_chart_neumann_defect_inf_upper']:.6g} "
            f"Tres={bounds['local_residence_time_lower']:.3e}"
        )

    local_times = [
        item["bounds"]["local_residence_time_lower"] for item in transitions
    ]
    gates = {
        "nine_frozen_charts_constructed": len(charts) == 9,
        "eight_adjacent_transitions_evaluated": len(transitions) == 8,
        "all_positive_volume_overlap_boxes_certified": all(
            item["gates"]["positive_volume_overlap_box"] for item in transitions
        ),
        "all_overlap_boxes_inside_both_charts": all(
            item["gates"]["overlap_box_strictly_inside_old_chart"]
            and item["gates"]["overlap_box_strictly_inside_new_chart"]
            for item in transitions
        ),
        "all_projective_denominators_exclude_zero": all(
            item["gates"]["projective_denominators_exclude_zero"]
            for item in transitions
        ),
        "all_old_new_neumann_defects_below_one": all(
            item["gates"]["old_chart_uniform_neumann_defect_below_one"]
            and item["gates"]["new_chart_uniform_neumann_defect_below_one"]
            for item in transitions
        ),
        "all_new_charts_have_positive_local_residence": all(
            value is not None and value > 0 for value in local_times
        ),
        "all_transition_certificates_pass": all(
            item["all_gates_pass"] for item in transitions
        ),
    }
    passed = all(gates.values())
    status = (
        "C4_E2A_ARB_MULTICHART_ATLAS_OVERLAP_CHAIN_CERTIFIED"
        if passed else "C4_E2A_INCONCLUSIVE"
    )
    result = {
        "title": TITLE,
        "version": VERSION,
        "protocol": protocol,
        "protocol_sha256": canonical_sha(protocol),
        "transition_certificates": transitions,
        "summary": {
            "chart_count": len(charts),
            "transition_count": len(transitions),
            "minimum_old_chart_membership_margin": min(
                item["bounds"]["old_chart_membership"]["minimum_margin_lower"]
                for item in transitions
            ),
            "minimum_new_chart_membership_margin": min(
                item["bounds"]["new_chart_membership"]["minimum_margin_lower"]
                for item in transitions
            ),
            "maximum_neumann_defect_upper": max(
                max(item["bounds"]["old_chart_neumann_defect_inf_upper"],
                    item["bounds"]["new_chart_neumann_defect_inf_upper"])
                for item in transitions
            ),
            "minimum_local_residence_time_lower": min(local_times),
            "aggregate_local_residence_budget_lower": sum(local_times),
            "aggregate_budget_is_not_a_continuation_time": True,
        },
        "gates": gates,
        "all_gates_pass": passed,
        "scientific_status": status,
        "claim_boundary": (
            "A 256-bit outward-rounded chain of eight positive-volume regular "
            "overlap boxes is certified for nine frozen charts. Positive local "
            "residence holds at each chart. The calculation does not transport "
            "an interval flowpipe between overlap boxes; the aggregate local "
            "budget is therefore not a certified continuation horizon."
        ),
        "required_next_step": (
            "C4-E2b must use a validated ODE integrator or Taylor-model flowpipe "
            "to prove that an initial interval set reaches each certified "
            "overlap box in sequence. Only then may a finite moving-chart "
            "continuation time be claimed."
        ),
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "python_flint": "0.8.0-compatible",
        },
    }
    Path(args.report).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("\nSUMMARY")
    print(json.dumps({
        "summary": result["summary"],
        "gates": gates,
        "all_gates_pass": passed,
        "scientific_status": status,
    }, indent=2))
    print("report:", args.report)
    return 0 if passed else 2


if __name__ == "__main__":
    code = main()
    if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:
        raise SystemExit(code)
