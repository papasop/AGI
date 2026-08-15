#!/usr/bin/env python3
"""Fail-closed Colab/local resume entrypoint for the C4-E2b 1->2 handoff work."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "archive" / "milestones" / "c4_e2b_v0_3_4_1"
RESULTS = ROOT / "results" / "c4_e2b"
PARENT = ARCHIVE / "C4_E2B_B_EIGHT_CHART_ARB_FLOWPIPE_v0_3.py"
LADDER = ARCHIVE / "C4_E2B_TRANSITION_12_ARB_LADDER_v0_3_2.py"
RECENTER = ARCHIVE / "C4_E2B_LOCAL_RECENTER_AFFINE_HANDOFF_v0_3_3.py"
DIAGNOSTIC = ARCHIVE / "C4_E2B_HANDOFF_CONTROLLER_COVARIANCE_DIAGNOSTIC_v0_3_4_1.py"
CHECKPOINT = RESULTS / "c4_e2b_transition_12_arb_ladder_v0_3_2.json"
CANDIDATE = RESULTS / "c4_e2b_local_bridge_candidate_v0_3_3.json"
RECENTER_REPORT = RESULTS / "c4_e2b_local_recenter_affine_handoff_v0_3_3.json"
DIAGNOSTIC_REPORT = RESULTS / "c4_e2b_handoff_controller_covariance_v0_3_4_1.json"


def run(command: list[str]) -> None:
    print("[run]", " ".join(command), flush=True)
    subprocess.run(command, check=True)


def require(path: Path, message: str) -> None:
    if not path.is_file():
        raise SystemExit(f"[blocked] {message}: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=("ladder", "recenter", "diagnose", "continue"))
    parser.add_argument("--level", type=int, default=32)
    parser.add_argument("--levels", default="16,32,64")
    parser.add_argument("--install", action="store_true",
                        help="install the frozen Colab dependencies first")
    args = parser.parse_args()
    RESULTS.mkdir(parents=True, exist_ok=True)
    if args.install:
        run([sys.executable, "-m", "pip", "install", "python-flint==0.8.0", "numpy==2.0.2"])

    if args.stage == "ladder":
        run([sys.executable, "-u", str(LADDER), "--parent", str(PARENT),
             "--levels", args.levels, "--report", str(CHECKPOINT)])
        return

    require(CHECKPOINT, "run the ladder stage first")
    if args.stage in ("recenter", "continue"):
        run([sys.executable, "-u", str(RECENTER), "--parent", str(PARENT),
             "--checkpoint", str(CHECKPOINT), "--level", str(args.level),
             "--candidate", str(CANDIDATE), "--report", str(RECENTER_REPORT)])
        if args.stage == "recenter":
            return

    require(CANDIDATE, "run the recenter stage first")
    run([sys.executable, "-u", str(DIAGNOSTIC), "--parent", str(PARENT),
         "--checkpoint", str(CHECKPOINT), "--candidate", str(CANDIDATE),
         "--level", str(args.level), "--report", str(DIAGNOSTIC_REPORT)])


if __name__ == "__main__":
    main()
