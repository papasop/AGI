#!/usr/bin/env python3
"""Stable entry point for the v0.10.6 fourth-chart Lohner flowpipe."""

from __future__ import annotations

import sys

from _entrypoint_utils import fail_closed_sha256, run_python_script, stable_parser


ARTIFACTS = [
    "archive/frozen_milestones/06_taylor_lohner/geometric_flow_fourth_chart_qr_lohner_v0_10_6_oneclick.py",
    "results/v0_10_6/fourth_chart_qr_lohner_support_certificate.json",
    "results/v0_10_6/qr_lohner_step_records.json",
]
TARGET = "archive/frozen_milestones/06_taylor_lohner/geometric_flow_fourth_chart_qr_lohner_v0_10_6_oneclick.py"


def main(argv: list[str] | None = None) -> int:
    parser = stable_parser(__doc__ or "")
    args, passthrough = parser.parse_known_args(argv)
    fail_closed_sha256(ARTIFACTS)
    if args.check_only:
        print("v0.10.6 Lohner flowpipe artifacts verified")
        return 0
    return run_python_script(TARGET, passthrough)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
