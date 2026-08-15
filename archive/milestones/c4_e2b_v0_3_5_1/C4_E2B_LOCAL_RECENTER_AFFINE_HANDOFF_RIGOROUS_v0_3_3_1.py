#!/usr/bin/env python3
"""C4-E2b local recentering / affine-handoff preflight v0.3.3.

This script consumes a completed v0.3.2 checkpoint and designs a local,
response-adapted bridge chart for the failed 1->2 handoff.  It does not rerun
the expensive 16/32/64 Arb ladder.  The complete endpoint box is transformed
conservatively from frozen chart 1 into candidate orthonormal frames.  Frames
are constructed from the local response Jacobian, while preserving the
six-dimensional tangent / eight-dimensional normal split.

PASS means that a finite, well-conditioned local bridge candidate has been
found and is worth promotion to a fresh Arb certificate.  It is NOT an Arb
handoff certificate, an eight-chart continuation, a global/long-time theorem,
K=1 evidence, Pulser evidence, hardware evidence, or QPU evidence.  Because
the v0.3.2 checkpoint stores an axis-aligned hull, correlations discarded by
that earlier hull cannot be recovered here.

Colab: upload this file, the v0.3 parent, and the v0.3.2 checkpoint, then run

    %run C4_E2B_LOCAL_RECENTER_AFFINE_HANDOFF_v0_3_3.py

The script searches /content, /tmp, and the current directory automatically.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np


TITLE = "C4-E2b LOCAL RECENTERING / AFFINE HANDOFF PREFLIGHT RIGOROUS"
VERSION = "0.3.3.1"
PARENT_NAME = "C4_E2B_B_EIGHT_CHART_ARB_FLOWPIPE_RIGOROUS_v0_3_5_1.py"
CHECKPOINT_NAME = "c4_e2b_transition_12_arb_ladder_v0_3_2_1.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(obj) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":"),
                   allow_nan=False).encode()
    ).hexdigest()


def jsonable(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.floating, np.integer)):
        return obj.item()
    if isinstance(obj, np.bool_):
        return bool(obj)
    raise TypeError(type(obj).__name__)


def locate(explicit: str | None, names: list[str]) -> Path:
    if explicit:
        path = Path(explicit).expanduser().resolve()
        if path.is_file():
            return path
        raise FileNotFoundError(path)
    roots = [Path.cwd(), Path("/content"), Path("/tmp")]
    for root in roots:
        for name in names:
            path = root / name
            if path.is_file():
                return path.resolve()
            for relative in (
                Path("archive/milestones/c4_e2b_v0_3_5_1") / name,
                Path("results/c4_e2b") / name,
            ):
                path = root / relative
                if path.is_file():
                    return path.resolve()
    wanted = " or ".join(names)
    raise FileNotFoundError(
        f"Could not find {wanted}. Upload it to Colab or pass an explicit path."
    )


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("c4_e2b_parent_v03_for_v033", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def procrustes_align(raw: np.ndarray, reference: np.ndarray) -> np.ndarray:
    """Rotate an orthonormal subspace basis toward a reference basis."""
    u, _, vt = np.linalg.svd(raw.T @ reference, full_matrices=False)
    return raw @ (u @ vt)


def response_frame(model, centre: np.ndarray, reference: np.ndarray):
    """Return a response-adapted 6+8 orthonormal frame at centre."""
    _, J, _, _ = model.response_jacobian_gradient_loss(centre)
    J = np.asarray(J, float)
    _, singular, vt = np.linalg.svd(J, full_matrices=True)
    rank = int(np.sum(singular > singular[0] * 1e-12))
    if J.shape != (8, 14) or rank != 8:
        raise RuntimeError(f"response Jacobian shape/rank is {J.shape}/{rank}, expected (8,14)/8")
    normal = vt[:8].T
    tangent = vt[8:].T
    tangent = procrustes_align(tangent, reference[:, :6])
    normal = procrustes_align(normal, reference[:, 6:])
    frame = np.column_stack([tangent, normal])
    # Remove roundoff without mixing tangent and normal blocks.
    qt, _ = np.linalg.qr(frame[:, :6])
    qn0 = frame[:, 6:] - qt @ (qt.T @ frame[:, 6:])
    qn, _ = np.linalg.qr(qn0)
    frame = np.column_stack([
        procrustes_align(qt, reference[:, :6]),
        procrustes_align(qn, reference[:, 6:]),
    ])
    return frame, J, singular


def transform_hull(ambient_mid, ambient_generator, centre, frame):
    """Conservative image of an affine generator hull in a new frame."""
    mid = frame.T @ (ambient_mid - centre)
    radius = np.abs(frame.T @ ambient_generator).sum(axis=1)
    return mid, radius


def corrected_field(model, theta, frozen_centre, beta):
    response, J, gradient, loss = model.response_jacobian_gradient_loss(theta)
    _, J0, _, _ = model.response_jacobian_gradient_loss(frozen_centre)
    response = np.asarray(response, float)
    J = np.asarray(J, float)
    gradient = np.asarray(gradient, float)
    J0 = np.asarray(J0, float)
    Y0 = J0.T @ np.linalg.inv(J0 @ J0.T)
    A = J @ Y0
    Y = Y0 @ np.linalg.inv(A)
    P = np.eye(14) - Y @ J
    error = response - np.asarray(model.R_STAR, float)
    field = -P @ gradient - beta * (Y @ error)
    s = np.linalg.svd(J, compute_uv=False)
    return {
        "finite": bool(np.all(np.isfinite(field))),
        "relative_smallest_singular_value": float(s[-1] / s[0]),
        "minimum_singular_value": float(s[-1]),
        "controller_condition": float(np.linalg.cond(A)),
        "field_norm": float(np.linalg.norm(field)),
        "loss": float(loss),
    }


def completed_level(checkpoint, requested: int | None):
    rows = [r for r in checkpoint.get("ladder_1_to_2", [])
            if "endpoint_midpoint" in r and "endpoint_radius" in r]
    if requested is not None:
        rows = [r for r in rows if int(r.get("substeps", -1)) == requested]
    if not rows:
        raise RuntimeError("checkpoint contains no completed requested ladder level")
    return max(rows, key=lambda r: int(r["substeps"]))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--parent")
    ap.add_argument("--checkpoint")
    ap.add_argument("--level", type=int, default=32,
                    help="completed v0.3.2 level to consume (default: 32)")
    ap.add_argument("--centres", type=int, default=41)
    ap.add_argument("--beta", type=float, default=100.0)
    ap.add_argument("--report", default="/tmp/c4_e2b_local_recenter_affine_handoff_v0_3_3_1.json")
    ap.add_argument("--candidate", default="/tmp/c4_e2b_local_recenter_affine_handoff_v0_3_3_1.json")
    args, unknown = ap.parse_known_args(argv)
    if unknown:
        print("# [notice] ignored notebook/kernel arguments:", unknown)
    if args.centres < 3 or args.beta <= 0:
        raise ValueError("centres must be >=3 and beta must be positive")

    parent_path = locate(args.parent, [PARENT_NAME])
    checkpoint_path = locate(args.checkpoint, [CHECKPOINT_NAME,
        "c4_e2b_transition_12_arb_ladder_v0_3_2.json"])
    checkpoint = json.loads(checkpoint_path.read_text())
    level = completed_level(checkpoint, args.level)

    parent = load_module(parent_path)
    parent.ctx.prec = 256
    model, charts = parent.setup_objects(Path("/tmp/c4_e2ba_modules"))
    e2a = parent.fetch_e2a(Path("/tmp/c4_e2ba_modules"))
    old, target = charts[1], charts[2]
    cert = e2a["transition_certificates"][1]

    declared_parent_sha = checkpoint.get("protocol", {}).get("parent_script_sha256")
    actual_parent_sha = digest(parent_path)
    if declared_parent_sha and declared_parent_sha != actual_parent_sha:
        raise RuntimeError(
            f"parent SHA mismatch: checkpoint={declared_parent_sha}, file={actual_parent_sha}"
        )
    prereq = checkpoint.get("prerequisite_0_to_1") or {}
    if not prereq.get("all_gates_pass", False):
        raise RuntimeError("checkpoint does not contain a passing 0->1 prerequisite")

    xm = np.asarray(level["endpoint_midpoint"], float)
    xr = np.asarray(level["endpoint_radius"], float)
    ambient_mid = old["centre"] + old["frame"] @ xm
    ambient_generator = old["frame"] @ np.diag(xr)
    overlap_mid = np.asarray(cert["frozen_centres"]["overlap_midpoint"], float)
    standard_half = np.r_[np.full(6, 0.02), np.full(8, 1e-4)]

    response_at_endpoint, J_endpoint, singular = response_frame(
        model, ambient_mid, target["frame"]
    )
    frames = {
        "frozen_chart_1": old["frame"],
        "frozen_chart_2": target["frame"],
        "response_adapted": response_at_endpoint,
    }
    centre_targets = {
        "overlap": overlap_mid,
        "target_chart": target["centre"],
    }

    rows = []
    for frame_name, frame in frames.items():
        orth = float(np.linalg.norm(frame.T @ frame - np.eye(14), ord=np.inf))
        for destination_name, destination in centre_targets.items():
            for alpha in np.linspace(0.0, 1.0, args.centres):
                centre = ambient_mid + float(alpha) * (destination - ambient_mid)
                cm, cr = transform_hull(
                    ambient_mid, ambient_generator, centre, frame
                )
                incoming_use = float(np.max((np.abs(cm) + cr) / standard_half))
                target_in_bridge = frame.T @ (target["centre"] - centre)
                target_centre_use = float(np.max(np.abs(target_in_bridge) / standard_half))
                bridge_in_target = target["frame"].T @ (centre - target["centre"])
                bridge_centre_target_use = float(
                    np.max(np.abs(bridge_in_target) / standard_half)
                )
                score = max(incoming_use, target_centre_use,
                            bridge_centre_target_use)
                rows.append({
                    "frame": frame_name,
                    "destination": destination_name,
                    "alpha": float(alpha),
                    "score": score,
                    "incoming_standard_chart_use": incoming_use,
                    "target_centre_in_bridge_use": target_centre_use,
                    "bridge_centre_in_target_use": bridge_centre_target_use,
                    "maximum_incoming_coordinate_radius": float(cr.max()),
                    "centre": centre,
                    "coordinate_midpoint": cm,
                    "coordinate_radius": cr,
                    "orthonormal_residual": orth,
                })
    best = min(rows, key=lambda r: r["score"])

    # Diagnostic local regularity at the midpoint and all +/- generator axes.
    samples = [best["centre"]]
    for j in range(ambient_generator.shape[1]):
        samples.append(ambient_mid + ambient_generator[:, j])
        samples.append(ambient_mid - ambient_generator[:, j])
    diagnostics = [corrected_field(model, x, best["centre"], args.beta)
                   for x in samples]
    min_rel_s = min(d["relative_smallest_singular_value"] for d in diagnostics)
    max_cond = max(d["controller_condition"] for d in diagnostics)

    # Report the old frozen-overlap failure, but never use it as the new-chart gate.
    tangent_half = float(cert["overlap_box"]["tangent_coordinate_half_width"])
    normal_half = float(cert["overlap_box"]["normal_coordinate_half_width"])
    frozen_half = np.r_[np.full(6, tangent_half), np.full(8, normal_half)]
    frozen_c = old["frame"].T @ (overlap_mid - old["centre"])
    frozen_use = float(np.max((np.abs(xm - frozen_c) + xr) / frozen_half))

    baseline = next(r for r in rows if r["frame"] == "frozen_chart_2"
                    and r["destination"] == "target_chart" and r["alpha"] == 0.0)
    gates = {
        "frozen_0_to_1_prerequisite_passes": True,
        "requested_ladder_level_complete": True,
        "all_candidate_values_finite": bool(all(
            math.isfinite(float(v))
            for r in rows for v in (r["score"], r["maximum_incoming_coordinate_radius"])
        )),
        "response_adapted_frame_orthonormal": bool(
            np.linalg.norm(response_at_endpoint.T @ response_at_endpoint - np.eye(14),
                           ord=np.inf) < 1e-10
        ),
        "sampled_response_jacobian_full_row_rank": bool(min_rel_s > 1e-10),
        "sampled_corrected_controller_well_conditioned": bool(max_cond < 2.0),
        "complete_incoming_hull_inside_candidate_standard_chart": bool(
            best["incoming_standard_chart_use"] < 1.0
        ),
        "candidate_and_target_centres_mutually_inside_standard_domains": bool(
            best["target_centre_in_bridge_use"] < 1.0
            and best["bridge_centre_in_target_use"] < 1.0
        ),
        "candidate_improves_target_frame_hull_score": bool(
            best["score"] < baseline["score"]
        ),
    }
    passed = all(gates.values())

    candidate = {
        "title": "C4-E2b response-adapted local bridge candidate",
        "version": VERSION,
        "source_checkpoint_sha256": digest(checkpoint_path),
        "source_parent_sha256": actual_parent_sha,
        "source_ladder_level": int(level["substeps"]),
        "frame_kind": best["frame"],
        "centre_destination": best["destination"],
        "centre_alpha": best["alpha"],
        "centre": best["centre"],
        "frame_columns_tangent_then_normal": frames[best["frame"]],
        "incoming_coordinate_midpoint": best["coordinate_midpoint"],
        "incoming_coordinate_radius": best["coordinate_radius"],
        "standard_coordinate_half_width": standard_half,
        "claim_boundary": "candidate chart data only; requires fresh Arb certification",
    }
    candidate_plain = json.loads(json.dumps(candidate, default=jsonable, allow_nan=False))
    candidate_plain["candidate_sha256_without_self"] = canonical_sha(candidate_plain)
    Path(args.candidate).write_text(json.dumps(candidate_plain, indent=2,
                                                sort_keys=True) + "\n")

    protocol = {
        "version": VERSION,
        "parent_script_sha256": actual_parent_sha,
        "checkpoint_sha256": digest(checkpoint_path),
        "ladder_level": int(level["substeps"]),
        "centre_candidates_per_destination": args.centres,
        "frame_candidates": list(frames),
        "beta": args.beta,
        "selection_rule": "minimize maximum standard-domain use across incoming hull and mutual centres",
    }
    report = {
        "title": TITLE,
        "version": VERSION,
        "protocol": protocol,
        "protocol_sha256": canonical_sha(protocol),
        "scientific_status": (
            "C4_E2B_LOCAL_AFFINE_BRIDGE_PROMOTION_WARRANTED"
            if passed else "C4_E2B_LOCAL_AFFINE_BRIDGE_NOT_YET_SUPPORTED"
        ),
        "all_gates_pass": passed,
        "selected_candidate": candidate_plain,
        "summary": {
            "source_level": int(level["substeps"]),
            "old_frozen_overlap_normalized_use_diagnostic": frozen_use,
            "old_frozen_overlap_still_fails": bool(frozen_use >= 1.0),
            "baseline_target_frame_score": baseline["score"],
            "selected_score": best["score"],
            "selected_incoming_use": best["incoming_standard_chart_use"],
            "selected_target_centre_in_bridge_use": best["target_centre_in_bridge_use"],
            "selected_bridge_centre_in_target_use": best["bridge_centre_in_target_use"],
            "minimum_sampled_relative_jacobian_singular_value": min_rel_s,
            "maximum_sampled_controller_condition": max_cond,
            "endpoint_jacobian_singular_values": singular,
        },
        "gates": gates,
        "claim_boundary": (
            "Binary64 local-chart design using a rigorously enclosed incoming hull; "
            "not a new Arb overlap or flowpipe certificate."
        ),
        "required_next_step": (
            "Freeze this bridge candidate, certify its full box Jacobian rank and controller "
            "regularity with Arb, then propagate directly from chart 1 through the bridge into chart 2."
            if passed else
            "Do not resume brute-force subdivision; inspect the failed gate and enlarge or split the local bridge atlas."
        ),
    }
    report_plain = json.loads(json.dumps(report, default=jsonable, allow_nan=False))
    report_plain["report_sha256_without_self"] = canonical_sha(report_plain)
    Path(args.report).write_text(json.dumps(report_plain, indent=2,
                                            sort_keys=True) + "\n")

    print("=" * 100)
    print(TITLE, "v" + VERSION)
    print("=" * 100)
    print("protocol_sha256:", report_plain["protocol_sha256"])
    print("boundary: local bridge candidate only; not a fresh Arb certificate")
    print(json.dumps({
        "scientific_status": report_plain["scientific_status"],
        "all_gates_pass": passed,
        "selected_frame": best["frame"],
        "selected_destination": best["destination"],
        "selected_alpha": best["alpha"],
        "old_frozen_overlap_use": frozen_use,
        "baseline_score": baseline["score"],
        "selected_score": best["score"],
        "gates": gates,
    }, indent=2))
    print("candidate:", args.candidate)
    print("report:", args.report)
    # Avoid the noisy SystemExit traceback in notebooks.
    return 0 if passed else 2


if __name__ == "__main__":
    _code = main()
    if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:
        raise SystemExit(_code)
