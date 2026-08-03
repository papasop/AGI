#!/usr/bin/env python3
"""Audit the implementation-open fifth-frame harness without upgrading claims."""

from __future__ import annotations

import argparse
import sys

from _entrypoint_utils import fail_closed_sha256, run_python_script


ARTIFACTS = [
    "src/geometric_flow_fifth_frame_inclusion_v0_10_14_oneclick.py",
    "src/geometric_flow_fifth_frame_backend_v0_10_15_oneclick.py",
]
TARGET = "src/geometric_flow_fifth_frame_backend_v0_10_15_oneclick.py"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-backend",
        action="store_true",
        help="execute the fail-closed v0.10.15 backend harness",
    )
    args, passthrough = parser.parse_known_args(argv)
    fail_closed_sha256(ARTIFACTS)
    if not args.run_backend:
        print("v0.10.14/v0.10.15 fifth-frame harness artifacts verified")
        print("status: implementation-open fail-closed harness")
        print("claim: no fifth frame, complete-child traversal, or global flow is certified")
        print("pass --run-backend to execute the underlying v0.10.15 harness")
        return 0
    return run_python_script(TARGET, passthrough)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
