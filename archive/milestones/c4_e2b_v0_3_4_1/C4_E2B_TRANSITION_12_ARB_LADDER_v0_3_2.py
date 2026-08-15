#!/usr/bin/env python3
"""C4-E2b transition 1->2 Arb step ladder v0.3.2.

This fail-closed diagnostic reuses the SHA-pinned model, frozen charts,
outward-rounded Picard slabs, correlated quadratic forms, and dynamically
corrected frozen-right-inverse controller of
``C4_E2B_B_EIGHT_CHART_ARB_FLOWPIPE_v0_3.py``.

It certifies transition 0->1 once, transforms that complete endpoint box into
chart 1, freezes the resulting chart-1 starting box, and independently tests
transition 1->2 with a 16/32/64 slab ladder.  Every completed level is written
to the report immediately.  By default the run stops at the first passing
level.

PASS certifies only the finite 1->2 handoff from the frozen incoming chart-1
box.  It is not an eight-chart continuation, global/long-time theorem, K=1,
Pulser, hardware, or QPU claim.

Place this file beside the v0.3 parent and run:

    python C4_E2B_TRANSITION_12_ARB_LADDER_v0_3_2.py

Colab:

    %run C4_E2B_TRANSITION_12_ARB_LADDER_v0_3_2.py
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
import time
from pathlib import Path

import numpy as np


TITLE = "C4-E2b TRANSITION 1->2 ARB STEP LADDER"
VERSION = "0.3.2"
PARENT_NAME = "C4_E2B_B_EIGHT_CHART_ARB_FLOWPIPE_v0_3.py"


def canonical_sha(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def load_parent(path):
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(
            f"{PARENT_NAME} not found at {path}. Upload it beside this v0.3.2 script "
            "or pass --parent /path/to/v0.3.py."
        )
    spec = importlib.util.spec_from_file_location("c4_e2b_parent_v03", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import parent script: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_levels(text):
    values = []
    for token in text.split(","):
        value = int(token.strip())
        if value < 1:
            raise ValueError("all ladder levels must be positive")
        if value not in values:
            values.append(value)
    if not values:
        raise ValueError("at least one ladder level is required")
    return values


def overlap_data(old, cert):
    midpoint = np.asarray(cert["frozen_centres"]["overlap_midpoint"], float)
    centre = old["frame"].T @ (midpoint - old["centre"])
    tangent_half = float(cert["overlap_box"]["tangent_coordinate_half_width"])
    normal_half = float(cert["overlap_box"]["normal_coordinate_half_width"])
    radius = np.r_[np.full(6, tangent_half), np.full(8, normal_half)]
    return centre, radius


def certify_leg(parent, model, old, cert, start_mid, start_rad,
                substeps, leg_time, beta, progress_prefix):
    xm = np.asarray(start_mid, float).copy()
    xr = np.asarray(start_rad, float).copy()
    h = leg_time / substeps
    steps = []
    started = time.time()
    for index in range(substeps):
        xm, xr, rec = parent.picard_step(model, old, xm, xr, h, beta)
        rec.update(
            step=index + 1,
            endpoint_max_radius=float(xr.max()),
            elapsed_seconds=float(time.time() - started),
        )
        steps.append(rec)
        print(
            f"[{progress_prefix} {index+1:03d}/{substeps:03d}] "
            f"picard={rec['iterations']} rad={xr.max():.3e} "
            f"q={rec['inverse_neumann_defect_upper']:.3e} "
            f"dL+={rec['dL_upper']:.3e}",
            flush=True,
        )

    overlap_c, overlap_r = overlap_data(old, cert)
    used = np.abs(xm - overlap_c) + xr
    margin = overlap_r - used
    point_displacement = np.abs(xm - overlap_c)
    point_margin = overlap_r - point_displacement
    chart_half = np.r_[np.full(6, 0.02), np.full(8, 1e-4)]
    worst = int(np.argmin(margin))
    inverse_ok = all(
        rec["regular"] and rec["inverse_neumann_defect_upper"] < 1.0
        for rec in steps
    )
    gates = {
        "all_picard_slabs_self_map": len(steps) == substeps,
        "all_corrected_right_inverses_and_denominators_regular": all(
            rec["regular"] for rec in steps
        ),
        "complete_endpoint_box_strictly_inside_overlap": bool(np.all(margin > 0)),
        "endpoint_centre_strictly_inside_overlap": bool(np.all(point_margin > 0)),
        "endpoint_inside_old_chart": bool(np.all(np.abs(xm) + xr < chart_half)),
        "objective_descent_on_every_slab": all(rec["dL_upper"] < 0 for rec in steps),
        "certified_inverse_neumann_defect_below_one": inverse_ok,
        "exact_response_law_by_controller_identity": inverse_ok and beta > 0,
        "response_lyapunov_exponential_contraction": inverse_ok and beta > 0,
    }
    passed = all(gates.values())
    record = {
        "substeps": substeps,
        "leg_time": leg_time,
        "elapsed_seconds": float(time.time() - started),
        "steps": steps,
        "endpoint_midpoint": xm.tolist(),
        "endpoint_radius": xr.tolist(),
        "bounds": {
            "minimum_overlap_coordinate_margin": float(margin.min()),
            "minimum_point_centre_overlap_margin": float(point_margin.min()),
            "maximum_endpoint_coordinate_radius": float(xr.max()),
            "maximum_endpoint_normalized_overlap_use": float((used / overlap_r).max()),
            "maximum_point_centre_normalized_overlap_use": float(
                (point_displacement / overlap_r).max()
            ),
            "worst_overlap_coordinate": worst,
            "worst_overlap_coordinate_kind": "tangent" if worst < 6 else "normal",
            "worst_coordinate_half_width": float(overlap_r[worst]),
            "worst_coordinate_centre_displacement": float(point_displacement[worst]),
            "worst_coordinate_endpoint_radius": float(xr[worst]),
            "maximum_dL_upper": max(rec["dL_upper"] for rec in steps),
            "maximum_inverse_neumann_defect_upper": max(
                rec["inverse_neumann_defect_upper"] for rec in steps
            ),
            "maximum_expanded_interval_dV_upper_diagnostic": max(
                rec["dV_upper"] for rec in steps
            ),
        },
        "gates": gates,
        "all_gates_pass": passed,
    }
    return xm, xr, record


def convergence_summary(levels):
    rows = []
    for previous, current in zip(levels, levels[1:]):
        rp = previous.get("bounds", {}).get("maximum_endpoint_coordinate_radius")
        rc = current.get("bounds", {}).get("maximum_endpoint_coordinate_radius")
        if rp is None or rc is None or rp <= 0:
            continue
        rows.append({
            "from_substeps": previous["substeps"],
            "to_substeps": current["substeps"],
            "radius_ratio": float(rc / rp),
            "radius_reduction_fraction": float(1.0 - rc / rp),
            "margin_change": float(
                current["bounds"]["minimum_overlap_coordinate_margin"]
                - previous["bounds"]["minimum_overlap_coordinate_margin"]
            ),
        })
    return rows


def write_checkpoint(path, result):
    Path(path).write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    )


def main(argv=None):
    ap = argparse.ArgumentParser()
    script_location = Path(globals().get("__file__", Path.cwd())).resolve()
    script_dir = script_location.parent if script_location.is_file() else script_location
    ap.add_argument("--parent", default=str(script_dir / PARENT_NAME))
    ap.add_argument("--levels", default="16,32,64")
    ap.add_argument("--continue-after-pass", action="store_true")
    ap.add_argument("--initial-half", type=float, default=1e-12)
    ap.add_argument("--first-substeps", type=int, default=8)
    ap.add_argument("--first-leg-time", type=float, default=1.25e-5)
    ap.add_argument("--later-leg-time", type=float, default=2.5e-5)
    ap.add_argument("--beta", type=float, default=100.0)
    ap.add_argument("--report", default="/tmp/c4_e2b_transition_12_arb_ladder_v0_3_2.json")
    args, unknown = ap.parse_known_args(argv)
    if unknown:
        print("# [notice] ignored notebook/kernel arguments:", unknown)
    levels = parse_levels(args.levels)
    if min(args.initial_half, args.first_leg_time, args.later_leg_time, args.beta) <= 0:
        raise ValueError("initial-half, leg times, and beta must be positive")
    if args.first_substeps < 1:
        raise ValueError("first-substeps must be positive")

    parent_path = Path(args.parent).resolve()
    parent = load_parent(parent_path)
    parent.ctx.prec = 256
    workdir = Path("/tmp/c4_e2ba_modules")
    model, charts = parent.setup_objects(workdir)
    e2a = parent.fetch_e2a(workdir)
    certificates = e2a["transition_certificates"]

    protocol = {
        "version": VERSION,
        "parent_script_sha256": parent.digest(parent_path),
        "parent_commit": parent.COMMIT,
        "e2a_sha256": parent.E2A_SHA,
        "precision_bits": 256,
        "prerequisite_transition": [0, 1],
        "target_transition": [1, 2],
        "first_substeps": args.first_substeps,
        "ladder_levels": levels,
        "initial_coordinate_half": args.initial_half,
        "first_leg_time": args.first_leg_time,
        "target_leg_time": args.later_leg_time,
        "beta": args.beta,
        "stop_at_first_pass": not args.continue_after_pass,
        "controller": "Y=Y0[J(theta)Y0]^-1; P=I-YJ; theta_dot=-P gradL-beta Y e",
        "integrator": "outward-rounded Picard slabs; correlated quadratic forms",
    }
    result = {
        "title": TITLE,
        "version": VERSION,
        "protocol": protocol,
        "protocol_sha256": canonical_sha(protocol),
        "prerequisite_0_to_1": None,
        "ladder_1_to_2": [],
        "convergence": [],
        "gates": {},
        "all_gates_pass": False,
        "scientific_status": "C4_E2B_TRANSITION_12_LADDER_RUNNING",
        "claim_boundary": (
            "Transition 1->2 from one frozen incoming chart-1 box only; not an eight-chart, "
            "global/long-time, K=1, Pulser, hardware, or QPU certificate."
        ),
    }
    write_checkpoint(args.report, result)

    print("=" * 100)
    print(TITLE, "v" + VERSION)
    print("=" * 100)
    print("protocol_sha256:", result["protocol_sha256"])
    print("boundary: transition 1->2 only after one certified 0->1 prerequisite")
    print("checkpoint:", args.report)

    try:
        initial_mid = np.zeros(14)
        initial_rad = np.full(14, args.initial_half)
        end0_mid, end0_rad, prerequisite = certify_leg(
            parent, model, charts[0], certificates[0], initial_mid, initial_rad,
            args.first_substeps, args.first_leg_time, args.beta, "0->1",
        )
        result["prerequisite_0_to_1"] = prerequisite
        if not prerequisite["all_gates_pass"]:
            raise RuntimeError("frozen 0->1 prerequisite failed")
        start1_mid, start1_rad = parent.transform_box_between_frames(
            end0_mid, end0_rad, charts[0], charts[1]
        )
        result["incoming_chart_1_box"] = {
            "coordinate_midpoint": start1_mid.tolist(),
            "coordinate_radius": start1_rad.tolist(),
            "coordinate_midpoint_inf": float(np.max(np.abs(start1_mid))),
            "coordinate_radius_inf": float(np.max(start1_rad)),
        }
        write_checkpoint(args.report, result)
        print(
            f"[0->1 PASS] incoming chart-1 midpoint_inf={np.max(np.abs(start1_mid)):.3e} "
            f"radius_inf={np.max(start1_rad):.3e}",
            flush=True,
        )

        first_pass = None
        for substeps in levels:
            print("-" * 100)
            print(f"[1->2] starting {substeps}-slab level", flush=True)
            try:
                _, _, record = certify_leg(
                    parent, model, charts[1], certificates[1], start1_mid, start1_rad,
                    substeps, args.later_leg_time, args.beta, f"1->2 n={substeps}",
                )
            except Exception as exc:
                record = {
                    "substeps": substeps,
                    "all_gates_pass": False,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
            result["ladder_1_to_2"].append(record)
            result["convergence"] = convergence_summary(result["ladder_1_to_2"])
            write_checkpoint(args.report, result)
            if "bounds" in record:
                b = record["bounds"]
                print(
                    f"[1->2 n={substeps}] pass={record['all_gates_pass']} "
                    f"margin={b['minimum_overlap_coordinate_margin']:.3e} "
                    f"centre_margin={b['minimum_point_centre_overlap_margin']:.3e} "
                    f"use={b['maximum_endpoint_normalized_overlap_use']:.3f} "
                    f"rad={b['maximum_endpoint_coordinate_radius']:.3e}",
                    flush=True,
                )
            else:
                print(f"[1->2 n={substeps}] ERROR: {record['error']}", flush=True)
            if record["all_gates_pass"]:
                first_pass = substeps
                if not args.continue_after_pass:
                    break

        completed = result["ladder_1_to_2"]
        result["convergence"] = convergence_summary(completed)
        result["gates"] = {
            "frozen_0_to_1_prerequisite_passes": bool(prerequisite["all_gates_pass"]),
            "at_least_one_target_level_completed": bool(completed),
            "at_least_one_1_to_2_complete_endpoint_box_inside_overlap": bool(
                any(row.get("all_gates_pass", False) for row in completed)
            ),
        }
        passed = all(result["gates"].values())
        result["all_gates_pass"] = passed
        result["scientific_status"] = (
            "C4_E2B_TRANSITION_12_FLOWPIPE_CERTIFIED"
            if passed else "C4_E2B_TRANSITION_12_LADDER_INCONCLUSIVE"
        )
        result["first_passing_substeps"] = first_pass
        result["required_next_step"] = (
            "Freeze this transition-level script/report and independently replay it; then continue to 2->3."
            if passed else
            "If radius reduction is flattening, preserve affine correlations across the 0->1 frame transform instead of brute-force subdivision."
        )
    except Exception as exc:
        result["all_gates_pass"] = False
        result["scientific_status"] = "C4_E2B_TRANSITION_12_LADDER_INCONCLUSIVE"
        result["error_type"] = type(exc).__name__
        result["error"] = str(exc)

    write_checkpoint(args.report, result)
    print("=" * 100)
    print(json.dumps({
        "scientific_status": result["scientific_status"],
        "all_gates_pass": result["all_gates_pass"],
        "first_passing_substeps": result.get("first_passing_substeps"),
        "convergence": result.get("convergence", []),
        "gates": result.get("gates", {}),
        "error_type": result.get("error_type"),
        "error": result.get("error"),
    }, indent=2))
    print("report:", args.report)
    return 0 if result["all_gates_pass"] else 2


if __name__ == "__main__":
    code = main()
    if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:
        raise SystemExit(code)
