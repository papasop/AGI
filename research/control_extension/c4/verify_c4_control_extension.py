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


if __name__ == "__main__":
    main()

