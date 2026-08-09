#!/usr/bin/env python3
"""Fail-closed semantic verifier for the post-publication C4 artifacts."""
import argparse
import json
from pathlib import Path


def load(path):
    return json.loads(Path(path).read_text())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--d0", required=True)
    parser.add_argument("--d1", required=True)
    parser.add_argument("--e2a")
    args = parser.parse_args()
    d0, d1 = load(args.d0), load(args.d1)

    if d0.get("scientific_status") != "C4_D0_PRODUCT_CHART_PREFLIGHT_SUPPORTED":
        raise SystemExit("D0 sampled preflight did not pass")
    if not d0.get("all_gates_pass"):
        raise SystemExit("D0 all_gates_pass is false")

    if d1.get("scientific_status") != "C4_D1_FINITE_RESIDENCE_CERTIFIED":
        raise SystemExit("D1 finite-residence certificate did not pass")
    if not d1.get("all_gates_pass"):
        raise SystemExit("D1 all_gates_pass is false")
    bounds = d1.get("bounds", {})
    q = bounds.get("neumann_defect_inf_norm", {}).get("upper")
    residence = bounds.get("certified_residence_time_lower_bound")
    if q is None or not q < 1.0:
        raise SystemExit("D1 requires q_upper < 1")
    if residence is None or not residence > 0.0:
        raise SystemExit("D1 requires a positive residence-time lower bound")

    forbidden = "positive invariance global K=1 QPU"
    boundary = (d1.get("claim_boundary") or "").lower()
    if "does not prove positive invariance" not in boundary:
        raise SystemExit("D1 claim boundary must exclude positive invariance")
    print("C4 control-extension artifacts verified")
    print(f"q_upper={q:.17g}")
    print(f"T_cert={residence:.17g}")
    print("forbidden claims:", forbidden)

    if args.e2a:
        e2a = load(args.e2a)
        if e2a.get("scientific_status") != (
            "C4_E2A_ARB_MULTICHART_ATLAS_OVERLAP_CHAIN_CERTIFIED"
        ):
            raise SystemExit("E2a overlap-chain certificate did not pass")
        if not e2a.get("all_gates_pass"):
            raise SystemExit("E2a all_gates_pass is false")
        summary = e2a.get("summary", {})
        gates = e2a.get("gates", {})
        transitions = e2a.get("transition_certificates", [])
        if summary.get("chart_count") != 9:
            raise SystemExit("E2a must record nine frozen charts")
        if summary.get("transition_count") != 8 or len(transitions) != 8:
            raise SystemExit("E2a must record eight adjacent transitions")
        if summary.get("aggregate_budget_is_not_a_continuation_time") is not True:
            raise SystemExit("E2a must disclaim aggregate budget as continuation time")
        if summary.get("maximum_neumann_defect_upper") != 0.018601705183309603:
            raise SystemExit("E2a maximum Neumann-defect bound changed")
        if summary.get("minimum_local_residence_time_lower") != 6.050195285542712e-10:
            raise SystemExit("E2a minimum local residence bound changed")
        if summary.get("aggregate_local_residence_budget_lower") != 4.844642545380921e-09:
            raise SystemExit("E2a aggregate local residence budget changed")
        required_gates = {
            "nine_frozen_charts_constructed",
            "eight_adjacent_transitions_evaluated",
            "all_positive_volume_overlap_boxes_certified",
            "all_overlap_boxes_inside_both_charts",
            "all_projective_denominators_exclude_zero",
            "all_old_new_neumann_defects_below_one",
            "all_new_charts_have_positive_local_residence",
            "all_transition_certificates_pass",
        }
        if not all(gates.get(name) is True for name in required_gates):
            raise SystemExit("E2a required gates are not all true")
        positive_boxes = sum(
            1
            for item in transitions
            if item.get("gates", {}).get("positive_volume_overlap_box") is True
        )
        if positive_boxes != 8:
            raise SystemExit("E2a must certify 8/8 positive-volume overlap boxes")
        boundary = (e2a.get("claim_boundary") or "").lower()
        next_step = (e2a.get("required_next_step") or "").lower()
        if "does not transport an interval flowpipe" not in boundary:
            raise SystemExit("E2a boundary must reject flowpipe transport")
        if "not a certified continuation horizon" not in boundary:
            raise SystemExit("E2a boundary must reject continuation horizon")
        if "c4-e2b" not in next_step or "validated" not in next_step:
            raise SystemExit("E2a next step must be C4-E2b validated flowpipe work")
        print("E2a overlap-chain artifact verified")
        print("charts=9 transitions=8 positive_volume_overlap_boxes=8/8")
        print("aggregate_budget_is_not_a_continuation_time=true")


if __name__ == "__main__":
    main()
