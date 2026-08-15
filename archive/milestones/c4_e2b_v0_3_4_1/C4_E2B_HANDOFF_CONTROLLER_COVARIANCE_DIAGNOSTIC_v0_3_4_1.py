#!/usr/bin/env python3
"""C4-E2b handoff controller-covariance diagnostic v0.3.4.1.

Separates the sole failed v0.3.4 gate into two causes:

  (i) repeated axis-aligned wrapping (source -> bridge -> target), and
 (ii) changing the frozen ambient right inverse Y0 when a chart is changed.

Five core evaluations are compared on rigorously enclosed Arb boxes:

 A  source chart, source box, source-centred Y0;
 B  bridge chart, bridge box, bridge-centred Y0;
 C  target chart, direct source->target box, target-centred Y0;
 D  target chart, via-bridge box, target-centred Y0;
 E  bridge/target boxes with the SAME source-centred ambient Y0 transported.

The script is diagnostic.  It does not certify a positive-time continuation,
modify the controller, or relax any theorem gate.
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


TITLE = "C4-E2b HANDOFF CONTROLLER-COVARIANCE DIAGNOSTIC"
VERSION = "0.3.4.1"
PARENT_NAME = "C4_E2B_B_EIGHT_CHART_ARB_FLOWPIPE_v0_3.py"
CHECKPOINT_NAME = "c4_e2b_transition_12_arb_ladder_v0_3_2.json"
CANDIDATE_NAME = "c4_e2b_local_bridge_candidate_v0_3_3.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(obj) -> str:
    return hashlib.sha256(json.dumps(
        obj, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()).hexdigest()


def locate(explicit, names):
    if explicit:
        path = Path(explicit).expanduser().resolve()
        if path.is_file():
            return path
        raise FileNotFoundError(path)
    for root in (Path.cwd(), Path("/content"), Path("/tmp")):
        for name in names:
            path = root / name
            if path.is_file():
                return path.resolve()
    raise FileNotFoundError("Could not find " + " or ".join(names))


def load_parent(path):
    spec = importlib.util.spec_from_file_location("c4_parent_v0341", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_candidate(candidate):
    claimed = candidate.get("candidate_sha256_without_self")
    payload = dict(candidate)
    payload.pop("candidate_sha256_without_self", None)
    if not claimed or canonical_sha(payload) != claimed:
        raise RuntimeError("candidate canonical hash mismatch")


def completed_level(checkpoint, level):
    rows = [r for r in checkpoint.get("ladder_1_to_2", [])
            if int(r.get("substeps", -1)) == level
            and "endpoint_midpoint" in r and "endpoint_radius" in r]
    if not rows:
        raise RuntimeError(f"no completed {level}-slab checkpoint level")
    return rows[-1]


def interval_field_with_controller_centre(parent, model, chart, u_mid, u_rad,
                                          beta, controller_centre):
    """Parent interval field with Y0 frozen at an explicit ambient centre."""
    ambient_centre = chart["centre"] + chart["frame"] @ u_mid
    half = np.maximum(u_rad, 0.0)
    parent.e1.configure_interval_engine()
    forms = parent.e1.ambient_phase_forms(ambient_centre, chart["frame"], half)
    J, g, err, den, denb = parent.quadratic_data(forms)
    den_ok = parent.lo(abs(den)) > 0 and parent.lo(abs(denb)) > 0

    _, J0, _, _ = model.response_jacobian_gradient_loss(controller_centre)
    Y0 = J0.T @ np.linalg.inv(J0 @ J0.T)
    Y0q = [[parent.qengine.Quadratic(parent.exact(float(v))) for v in row]
           for row in Y0]
    A = parent.qmatmul(J, Y0q)
    Ainv, inv_q, inv_tail = parent.qneumann_inverse_near_identity(A, terms=3)
    Y = parent.qmatmul(Y0q, Ainv)
    Jg = parent.qmatmul(J, g)
    normal_grad = parent.qmatmul(Y, Jg)
    pgrad = [[g[i][0] - normal_grad[i][0]] for i in range(14)]
    recovery = parent.qmatmul(Y, err)
    ftheta = [[-pgrad[i][0] - parent.exact(beta) * recovery[i][0]]
              for i in range(14)]
    frameq = [[parent.qengine.Quadratic(parent.exact(float(v))) for v in row]
              for row in chart["frame"].T]
    fuq = parent.qmatmul(frameq, ftheta)
    fu = parent.arb_mat([[fuq[i][0].enclosure().real] for i in range(14)])
    finite = den_ok and all(parent.finite_ball(fu[i, 0]) for i in range(14))
    dLq = parent.qmatmul(parent.qtranspose(g), ftheta)[0][0]
    dVq = parent.qmatmul(
        parent.qtranspose(err), parent.qmatmul(J, ftheta)
    )[0][0]
    return fu, dLq.enclosure().real, dVq.enclosure().real, finite, inv_q, inv_tail


def midpoint_evaluation(model, theta, controller_centre, beta):
    response, J, gradient, loss = model.response_jacobian_gradient_loss(theta)
    _, J0, _, _ = model.response_jacobian_gradient_loss(controller_centre)
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
    return {
        "dL": float(gradient @ field),
        "dV": float(error @ (J @ field)),
        "loss": float(loss),
        "inverse_condition": float(np.linalg.cond(A)),
        "field_norm": float(np.linalg.norm(field)),
    }


def evaluate(parent, model, chart, mid, rad, beta, controller_centre,
             label, box_route, controller_label):
    fu, dL, dV, regular, q, tail = interval_field_with_controller_centre(
        parent, model, chart, np.asarray(mid, float), np.asarray(rad, float),
        beta, np.asarray(controller_centre, float)
    )
    theta_mid = chart["centre"] + chart["frame"] @ np.asarray(mid, float)
    point = midpoint_evaluation(model, theta_mid, controller_centre, beta)
    return {
        "label": label,
        "box_route": box_route,
        "controller": controller_label,
        "box_maximum_radius": float(np.max(rad)),
        "regular": bool(regular),
        "inverse_neumann_defect_upper": float(q),
        "inverse_neumann_tail_upper": float(tail),
        "inverse_neumann_defect_below_one": bool(regular and q < 1.0),
        "dL_lower": float(parent.lo(dL)),
        "dL_upper": float(parent.hi(dL)),
        "objective_descent_certified": bool(parent.hi(dL) < 0.0),
        "expanded_dV_upper_diagnostic": float(parent.hi(dV)),
        "exact_response_identity_available": bool(regular and q < 1.0),
        "midpoint": point,
    }


def classify(cases):
    A = cases["A_source_native"]
    C = cases["C_target_direct_native"]
    D = cases["D_target_via_native"]
    Et = cases["E_target_direct_source_controller"]
    Eb = cases["E_bridge_source_controller"]
    if not A["objective_descent_certified"]:
        return (
            "SOURCE_ENDPOINT_DESCENT_NOT_REPRODUCED",
            "Reconcile the endpoint box with the final v0.3.2 Picard slab before changing the atlas."
        )
    if C["objective_descent_certified"] and not D["objective_descent_certified"]:
        return (
            "DOUBLE_HULL_WRAPPING_IDENTIFIED",
            "Use the direct source-to-target Arb transform; do not gate on the twice-hulled target box."
        )
    if (not C["objective_descent_certified"]
            and Et["objective_descent_certified"]):
        return (
            "CHART_DEPENDENT_CONTROLLER_REFREEZE_IDENTIFIED",
            "Transport one frozen ambient Y0 across the handoff instead of recomputing Y0 at each chart centre."
        )
    if C["objective_descent_certified"] and D["objective_descent_certified"]:
        return (
            "NATIVE_TARGET_DESCENT_SUPPORTED",
            "The direct target box is sufficient; continue with a target-chart positive-time slab."
        )
    if Eb["objective_descent_certified"] or Et["objective_descent_certified"]:
        return (
            "PARTIAL_TRANSPORTED_CONTROLLER_SUPPORT",
            "Split the bridge or preserve affine correlations before promotion."
        )
    # Midpoint signs distinguish a real local controller issue from interval inflation.
    native_midpoint_negative = C["midpoint"]["dL"] < 0.0
    transported_midpoint_negative = Et["midpoint"]["dL"] < 0.0
    if native_midpoint_negative or transported_midpoint_negative:
        return (
            "INTERVAL_DEPENDENCY_DOMINATES_DESCENT_TEST",
            "Preserve affine correlations or subdivide only the handoff box; the midpoint still descends."
        )
    return (
        "ACTUAL_LOCAL_DESCENT_LOSS_INDICATED",
        "Redesign the controller/Lyapunov objective or move the handoff; do not continue the formal chain."
    )


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--parent")
    ap.add_argument("--checkpoint")
    ap.add_argument("--candidate")
    ap.add_argument("--level", type=int, default=32)
    ap.add_argument("--beta", type=float, default=100.0)
    ap.add_argument("--report", default="/tmp/c4_e2b_handoff_controller_covariance_v0_3_4_1.json")
    args, unknown = ap.parse_known_args(argv)
    if unknown:
        print("# [notice] ignored notebook/kernel arguments:", unknown)

    parent_path = locate(args.parent, [PARENT_NAME])
    checkpoint_path = locate(args.checkpoint, [CHECKPOINT_NAME])
    candidate_path = locate(args.candidate, [CANDIDATE_NAME])
    checkpoint = json.loads(checkpoint_path.read_text())
    candidate = json.loads(candidate_path.read_text())
    verify_candidate(candidate)
    parent_sha, checkpoint_sha = digest(parent_path), digest(checkpoint_path)
    if candidate.get("source_parent_sha256") != parent_sha:
        raise RuntimeError("candidate-parent binding mismatch")
    if candidate.get("source_checkpoint_sha256") != checkpoint_sha:
        raise RuntimeError("candidate-checkpoint binding mismatch")
    if int(candidate.get("source_ladder_level", -1)) != args.level:
        raise RuntimeError("candidate-level binding mismatch")
    if not (checkpoint.get("prerequisite_0_to_1") or {}).get("all_gates_pass"):
        raise RuntimeError("0->1 prerequisite is not passing")

    parent = load_parent(parent_path)
    parent.ctx.prec = 256
    workdir = Path("/tmp/c4_e2ba_modules")
    model, charts = parent.setup_objects(workdir)
    parent.fetch_e2a(workdir)
    source, target = charts[1], charts[2]
    bridge = {
        "centre": np.asarray(candidate["centre"], float),
        "frame": np.asarray(candidate["frame_columns_tangent_then_normal"], float),
    }
    level = completed_level(checkpoint, args.level)
    sm = np.asarray(level["endpoint_midpoint"], float)
    sr = np.asarray(level["endpoint_radius"], float)
    bm, br = parent.transform_box_between_frames(sm, sr, source, bridge)
    td_m, td_r = parent.transform_box_between_frames(sm, sr, source, target)
    tv_m, tv_r = parent.transform_box_between_frames(bm, br, bridge, target)

    cases = {
        "A_source_native": evaluate(
            parent, model, source, sm, sr, args.beta, source["centre"],
            "A", "source endpoint", "source-centred Y0"
        ),
        "B_bridge_native": evaluate(
            parent, model, bridge, bm, br, args.beta, bridge["centre"],
            "B", "source->bridge", "bridge-centred Y0"
        ),
        "C_target_direct_native": evaluate(
            parent, model, target, td_m, td_r, args.beta, target["centre"],
            "C", "direct source->target", "target-centred Y0"
        ),
        "D_target_via_native": evaluate(
            parent, model, target, tv_m, tv_r, args.beta, target["centre"],
            "D", "source->bridge->target", "target-centred Y0"
        ),
        "E_bridge_source_controller": evaluate(
            parent, model, bridge, bm, br, args.beta, source["centre"],
            "E_bridge", "source->bridge", "transported source-centred Y0"
        ),
        "E_target_direct_source_controller": evaluate(
            parent, model, target, td_m, td_r, args.beta, source["centre"],
            "E_target_direct", "direct source->target", "transported source-centred Y0"
        ),
        "E_target_via_source_controller": evaluate(
            parent, model, target, tv_m, tv_r, args.beta, source["centre"],
            "E_target_via", "source->bridge->target", "transported source-centred Y0"
        ),
    }
    status, next_step = classify(cases)
    all_regular = all(row["inverse_neumann_defect_below_one"] for row in cases.values())
    wrapping_ratio = float(np.max(tv_r / np.maximum(td_r, np.finfo(float).tiny)))
    protocol = {
        "version": VERSION,
        "precision_bits": 256,
        "parent_script_sha256": parent_sha,
        "checkpoint_sha256": checkpoint_sha,
        "candidate_sha256": digest(candidate_path),
        "level": args.level,
        "beta": args.beta,
        "comparison": "native per-chart Y0 versus transported source-centred ambient Y0",
    }
    report = {
        "title": TITLE,
        "version": VERSION,
        "protocol": protocol,
        "protocol_sha256": canonical_sha(protocol),
        "scientific_status": status,
        "diagnostic_complete": bool(all_regular),
        "all_gates_pass": None,
        "cases": cases,
        "summary": {
            "via_to_direct_target_radius_ratio": wrapping_ratio,
            "source_native_dL_upper": cases["A_source_native"]["dL_upper"],
            "bridge_native_dL_upper": cases["B_bridge_native"]["dL_upper"],
            "target_direct_native_dL_upper": cases["C_target_direct_native"]["dL_upper"],
            "target_via_native_dL_upper": cases["D_target_via_native"]["dL_upper"],
            "bridge_transported_Y0_dL_upper": cases[
                "E_bridge_source_controller"
            ]["dL_upper"],
            "target_direct_transported_Y0_dL_upper": cases[
                "E_target_direct_source_controller"
            ]["dL_upper"],
            "all_case_inverse_defects_below_one": all_regular,
        },
        "required_next_step": next_step,
        "claim_boundary": (
            "Cause-separation diagnostic only; not a positive-time flowpipe or revised handoff certificate."
        ),
    }
    report["report_sha256_without_self"] = canonical_sha(report)
    Path(args.report).write_text(json.dumps(
        report, indent=2, sort_keys=True, allow_nan=False
    ) + "\n")

    print("=" * 100)
    print(TITLE, "v" + VERSION)
    print("=" * 100)
    print("protocol_sha256:", report["protocol_sha256"])
    print("boundary: cause-separation diagnostic; not a new certificate")
    for key, row in cases.items():
        print(f"[{row['label']:<15}] q={row['inverse_neumann_defect_upper']:.3e} "
              f"dL=[{row['dL_lower']:+.3e},{row['dL_upper']:+.3e}] "
              f"mid={row['midpoint']['dL']:+.3e} "
              f"descent={row['objective_descent_certified']}")
    print(json.dumps({
        "scientific_status": status,
        "diagnostic_complete": all_regular,
        "via_to_direct_target_radius_ratio": wrapping_ratio,
        "required_next_step": next_step,
    }, indent=2))
    print("report:", args.report)
    return 0 if all_regular else 2


if __name__ == "__main__":
    _code = main()
    if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:
        raise SystemExit(_code)
