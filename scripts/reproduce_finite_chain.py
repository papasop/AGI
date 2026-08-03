#!/usr/bin/env python3
"""Print or run the finite-continuation reproduction chain."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHAIN = [
    "archive/milestones/02_second_chart/response_fibre_second_chart_v0_9_10_oneclick.py",
    "archive/milestones/03_endpoint_enclosure/response_fibre_cauchy_norm_correction_v0_9_20_oneclick.py",
    "archive/milestones/03_endpoint_enclosure/response_fibre_signed_field_export_v0_9_22_oneclick.py",
    "archive/milestones/04_third_chart/response_fibre_third_recenter_inclusion_v0_9_23_oneclick.py",
    "archive/milestones/04_third_chart/response_fibre_third_frame_backend_v0_9_25_oneclick.py",
    "archive/milestones/04_third_chart/response_fibre_third_picard_v0_9_26_oneclick.py",
    "archive/milestones/04_third_chart/response_fibre_third_chart_finite_continuation_v0_9_27_oneclick.py",
    "archive/milestones/04_third_chart/response_fibre_third_chart_signed_endpoint_v0_9_28_oneclick.py",
    "archive/milestones/05_fourth_chart/response_fibre_fourth_frame_v0_9_29_oneclick.py",
    "archive/milestones/05_fourth_chart/response_fibre_fourth_picard_v0_9_30_oneclick.py",
    "archive/milestones/05_fourth_chart/response_fibre_fourth_chart_finite_v0_9_31_oneclick.py",
    "archive/milestones/05_fourth_chart/response_fibre_fourth_chart_signed_endpoint_v0_9_32_oneclick.py",
    "archive/milestones/06_taylor_lohner/geometric_flow_active_backend_export_v0_10_1_oneclick.py",
    "archive/milestones/06_taylor_lohner/geometric_flow_scalar_primitives_extract_v0_10_2_oneclick.py",
    "archive/milestones/06_taylor_lohner/geometric_flow_six_variable_jet_lift_v0_10_3_oneclick.py",
    "archive/milestones/06_taylor_lohner/geometric_flow_parametric_normal_graph_jet_v0_10_4_oneclick.py",
    "archive/milestones/06_taylor_lohner/geometric_flow_same_expression_field_dx_v0_10_5_oneclick.py",
    "archive/milestones/06_taylor_lohner/geometric_flow_fourth_chart_qr_lohner_v0_10_6_oneclick.py",
    "archive/milestones/06_taylor_lohner/geometric_flow_reindexed_taylor_chain_v0_10_13_oneclick.py",
    "archive/milestones/06_taylor_lohner/geometric_flow_fifth_frame_inclusion_v0_10_14_oneclick.py",
    "archive/milestones/06_taylor_lohner/geometric_flow_fifth_frame_backend_v0_10_15_oneclick.py",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true", help="execute the chain")
    args = parser.parse_args()

    for script in CHAIN:
        command = [sys.executable, script]
        print(" ".join(command))
        if args.run:
            code = subprocess.call(command, cwd=ROOT)
            if code:
                return code
    if not args.run:
        print("\nPass --run to execute. Some steps require predecessor artifacts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
