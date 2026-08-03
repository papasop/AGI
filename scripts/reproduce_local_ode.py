#!/usr/bin/env python3
"""Stable entry point for the frozen v0.9.3 local ODE theorem."""

from __future__ import annotations

import sys

from _entrypoint_utils import fail_closed_sha256, run_python_script, stable_parser


ARTIFACTS = [
    "src/response_fibre_intrinsic_picard_microstep_v0_9_3.py",
    "inputs/response_fibre_v0_6_2_backend_inputs.zip",
]
TARGET = "scripts/reproduce_v093.py"


def main(argv: list[str] | None = None) -> int:
    parser = stable_parser(__doc__ or "")
    args, passthrough = parser.parse_known_args(argv)
    fail_closed_sha256(ARTIFACTS)
    if args.check_only:
        print("v0.9.3 local ODE artifacts verified")
        return 0
    return run_python_script(TARGET, passthrough)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
