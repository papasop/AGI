#!/usr/bin/env python3
"""Stable entry point for the finite-continuation reproduction chain."""

from __future__ import annotations

import sys

from _entrypoint_utils import fail_closed_sha256, run_python_script, stable_parser


ARTIFACTS = [
    "response_fibre_second_chart_v0_9_10_oneclick.py",
    "response_fibre_fourth_chart_signed_endpoint_v0_9_32_oneclick.py",
    "src/geometric_flow_reindexed_taylor_chain_v0_10_13_oneclick.py",
]
TARGET = "scripts/reproduce_finite_chain.py"


def main(argv: list[str] | None = None) -> int:
    parser = stable_parser(__doc__ or "")
    args, passthrough = parser.parse_known_args(argv)
    fail_closed_sha256(ARTIFACTS)
    if args.check_only:
        print("finite-continuation chain artifacts verified")
        return 0
    return run_python_script(TARGET, passthrough)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
