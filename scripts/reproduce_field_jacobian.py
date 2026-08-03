#!/usr/bin/env python3
"""Stable entry point for the v0.10.5 same-expression X/DX certificate."""

from __future__ import annotations

import sys

from _entrypoint_utils import fail_closed_sha256, run_python_script, stable_parser


ARTIFACTS = [
    "src/geometric_flow_same_expression_field_dx_v0_10_5_oneclick.py",
    "results/v0_10_5/same_expression_X_DX_arb_certificate.json",
]
TARGET = "src/geometric_flow_same_expression_field_dx_v0_10_5_oneclick.py"


def main(argv: list[str] | None = None) -> int:
    parser = stable_parser(__doc__ or "")
    args, passthrough = parser.parse_known_args(argv)
    fail_closed_sha256(ARTIFACTS)
    if args.check_only:
        print("v0.10.5 same-expression X/DX artifacts verified")
        return 0
    return run_python_script(TARGET, passthrough)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
