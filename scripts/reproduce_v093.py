#!/usr/bin/env python3
"""Recompute the frozen v0.9.3 local ODE theorem."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    command = [
        sys.executable,
        "src/response_fibre_intrinsic_picard_microstep_v0_9_3.py",
        "--inputs-zip",
        "inputs/response_fibre_v0_6_2_backend_inputs.zip",
        "--v074-source",
        "src/response_fibre_arb_kkt_witness_alignment_v0_7_4.py",
        "--no-download",
        "--output",
        "results/v0_9_3_reproduction",
    ]
    return subprocess.call(command, cwd=ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
