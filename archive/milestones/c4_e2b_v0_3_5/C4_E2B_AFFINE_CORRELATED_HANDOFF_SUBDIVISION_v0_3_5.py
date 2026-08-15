#!/usr/bin/env python3
"""C4-E2b affine-correlation-preserving handoff subdivision v0.3.5.

This fail-closed certificate consumes the frozen v0.3.2 level-32 endpoint,
the v0.3.3 bridge candidate, and the v0.3.4.1 cause-separation report.  It
keeps the endpoint enclosure in the *source-chart affine generators* while
testing the target-centred corrected controller.  Therefore it never replaces
the source affine image by a target-axis-aligned hull before evaluating the
Jacobian, inverse, or objective derivative.

If a complete source-parameter box is too wide for the descent test, only that
parameter box is bisected.  The union of accepted leaves covers the complete
frozen endpoint enclosure.  PASS certifies a zero-time chart handoff with
regular corrected controller, exact response identity, target-domain
containment, and strict objective descent on every leaf.  It does not certify
a positive-time target-chart Picard slab, transition 2->3, an eight-chart
chain, a global flow, K=1, Pulser, hardware, or QPU behaviour.
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


TITLE = "C4-E2b AFFINE-CORRELATED HANDOFF SUBDIVISION"
VERSION = "0.3.5"
PARENT_NAME = "C4_E2B_B_EIGHT_CHART_ARB_FLOWPIPE_v0_3.py"
CHECKPOINT_NAME = "c4_e2b_transition_12_arb_ladder_v0_3_2.json"
CANDIDATE_NAME = "c4_e2b_local_bridge_candidate_v0_3_3.json"
DIAGNOSTIC_NAME = "c4_e2b_handoff_controller_covariance_v0_3_4_1.json"


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
    roots = (Path.cwd(), Path("/content"), Path("/tmp"))
    for root in roots:
        for name in names:
            direct = root / name
            if direct.is_file():
                return direct.resolve()
            for relative in (
                Path("archive/milestones/c4_e2b_v0_3_4_1") / name,
                Path("results/c4_e2b") / name,
            ):
                path = root / relative
                if path.is_file():
                    return path.resolve()
    raise FileNotFoundError("Could not find " + " or ".join(names))


def load_parent(path):
    spec = importlib.util.spec_from_file_location("c4_parent_v035", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_self_hash(obj, field):
    claimed = obj.get(field)
    payload = dict(obj)
    payload.pop(field, None)
    if not claimed or canonical_sha(payload) != claimed:
        raise RuntimeError(f"canonical hash mismatch: {field}")


def completed_level(checkpoint, level):
    rows = [r for r in checkpoint.get("ladder_1_to_2", [])
            if int(r.get("substeps", -1)) == level
            and "endpoint_midpoint" in r and "endpoint_radius" in r]
    if not rows:
        raise RuntimeError(f"no completed {level}-slab checkpoint level")
    return rows[-1]


def interval_field(parent, model, parameter_chart, mid, rad, beta,
                   controller_centre):
    """Evaluate on source affine generators with an explicit ambient Y0."""
    ambient_centre = parameter_chart["centre"] + parameter_chart["frame"] @ mid
    half = np.maximum(rad, 0.0)
    parent.e1.configure_interval_engine()
    forms = parent.e1.ambient_phase_forms(
        ambient_centre, parameter_chart["frame"], half
    )
    J, g, err, den, denb = parent.quadratic_data(forms)
    den_ok = parent.lo(abs(den)) > 0 and parent.lo(abs(denb)) > 0

    _, J0, _, _ = model.response_jacobian_gradient_loss(controller_centre)
    J0 = np.asarray(J0, float)
    Y0 = J0.T @ np.linalg.inv(J0 @ J0.T)
    Q = parent.qengine.Quadratic
    Y0q = [[Q(parent.exact(float(v))) for v in row] for row in Y0]
    A = parent.qmatmul(J, Y0q)
    Ainv, q, tail = parent.qneumann_inverse_near_identity(A, terms=3)
    Y = parent.qmatmul(Y0q, Ainv)
    Jg = parent.qmatmul(J, g)
    normal_grad = parent.qmatmul(Y, Jg)
    pgrad = [[g[i][0] - normal_grad[i][0]] for i in range(14)]
    recovery = parent.qmatmul(Y, err)
    ftheta = [[-pgrad[i][0] - parent.exact(beta) * recovery[i][0]]
              for i in range(14)]
    dL = parent.qmatmul(parent.qtranspose(g), ftheta)[0][0].enclosure().real
    dV = parent.qmatmul(
        parent.qtranspose(err), parent.qmatmul(J, ftheta)
    )[0][0].enclosure().real
    finite = den_ok and parent.finite_ball(dL) and parent.finite_ball(dV)
    return dL, dV, bool(finite), float(q), float(tail)


def target_hull(source, target, mid, rad):
    """One outward-padded affine hull, used only for domain containment."""
    ambient_mid = source["centre"] + source["frame"] @ mid
    transform = target["frame"].T @ source["frame"]
    target_mid = target["frame"].T @ (ambient_mid - target["centre"])
    target_rad = np.abs(transform) @ rad
    target_rad = np.nextafter(target_rad, np.inf)
    return target_mid, target_rad


def split_box(mid, rad, index):
    """Outward-covering binary split of one exact-binary64 parameter box."""
    lower = np.nextafter(mid[index] - rad[index], -np.inf)
    upper = np.nextafter(mid[index] + rad[index], np.inf)
    cut = mid[index]
    children = []
    for lo, hi in ((lower, cut), (cut, upper)):
        centre = (lo + hi) / 2.0
        radius = np.nextafter(max(centre - lo, hi - centre), np.inf)
        cm, cr = mid.copy(), rad.copy()
        cm[index], cr[index] = centre, radius
        children.append((cm, cr))
    return children


def leaf_record(parent, model, source, target, mid, rad, beta, depth,
                controller_centre, standard_half):
    dL, dV, regular, q, tail = interval_field(
        parent, model, source, mid, rad, beta, controller_centre
    )
    tm, tr = target_hull(source, target, mid, rad)
    use = (np.abs(tm) + tr) / standard_half
    finite = (regular and math.isfinite(q) and math.isfinite(tail)
              and np.all(np.isfinite(use)))
    return {
        "depth": int(depth),
        "source_parameter_midpoint": mid.tolist(),
        "source_parameter_radius": rad.tolist(),
        "maximum_source_parameter_radius": float(np.max(rad)),
        "target_domain_maximum_use": float(np.max(use)),
        "target_domain_strictly_inside": bool(np.all(use < 1.0)),
        "inverse_neumann_defect_upper": q,
        "inverse_neumann_tail_upper": tail,
        "inverse_neumann_defect_below_one": bool(finite and q < 1.0),
        "dL_lower": float(parent.lo(dL)),
        "dL_upper": float(parent.hi(dL)),
        "objective_descent_certified": bool(finite and parent.hi(dL) < 0.0),
        "expanded_dV_upper_diagnostic": float(parent.hi(dV)),
        "exact_response_identity_available": bool(finite and q < 1.0),
        "finite": bool(finite),
    }


def choose_split(rad, source, target, standard_half):
    influence = (np.abs(target["frame"].T @ source["frame"])
                 / standard_half[:, None])
    score = rad * np.max(influence, axis=0)
    return int(np.argmax(score))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--parent")
    ap.add_argument("--checkpoint")
    ap.add_argument("--candidate")
    ap.add_argument("--diagnostic")
    ap.add_argument("--level", type=int, default=32)
    ap.add_argument("--beta", type=float, default=100.0)
    ap.add_argument("--max-depth", type=int, default=8)
    ap.add_argument("--max-leaves", type=int, default=256)
    ap.add_argument("--report", default="/tmp/c4_e2b_affine_correlated_handoff_v0_3_5.json")
    args, unknown = ap.parse_known_args(argv)
    if unknown:
        print("# [notice] ignored notebook/kernel arguments:", unknown)
    if args.level < 1 or args.beta <= 0 or args.max_depth < 0 or args.max_leaves < 1:
        raise ValueError("invalid positive protocol parameter")

    parent_path = locate(args.parent, [PARENT_NAME])
    checkpoint_path = locate(args.checkpoint, [CHECKPOINT_NAME])
    candidate_path = locate(args.candidate, [CANDIDATE_NAME])
    diagnostic_path = locate(args.diagnostic, [DIAGNOSTIC_NAME])
    checkpoint = json.loads(checkpoint_path.read_text())
    candidate = json.loads(candidate_path.read_text())
    diagnostic = json.loads(diagnostic_path.read_text())
    verify_self_hash(candidate, "candidate_sha256_without_self")
    verify_self_hash(diagnostic, "report_sha256_without_self")
    parent_sha = digest(parent_path)
    checkpoint_sha = digest(checkpoint_path)
    candidate_sha = digest(candidate_path)
    diagnostic_sha = digest(diagnostic_path)
    if candidate.get("source_parent_sha256") != parent_sha:
        raise RuntimeError("candidate-parent binding mismatch")
    if candidate.get("source_checkpoint_sha256") != checkpoint_sha:
        raise RuntimeError("candidate-checkpoint binding mismatch")
    dp = diagnostic.get("protocol", {})
    if dp.get("parent_script_sha256") != parent_sha:
        raise RuntimeError("diagnostic-parent binding mismatch")
    if dp.get("checkpoint_sha256") != checkpoint_sha:
        raise RuntimeError("diagnostic-checkpoint binding mismatch")
    if dp.get("candidate_sha256") != candidate_sha:
        raise RuntimeError("diagnostic-candidate binding mismatch")
    if diagnostic.get("scientific_status") != "INTERVAL_DEPENDENCY_DOMINATES_DESCENT_TEST":
        raise RuntimeError("v0.3.4.1 does not authorize affine subdivision")
    if not (checkpoint.get("prerequisite_0_to_1") or {}).get("all_gates_pass"):
        raise RuntimeError("0->1 prerequisite is not passing")

    parent = load_parent(parent_path)
    parent.ctx.prec = 256
    workdir = Path("/tmp/c4_e2ba_modules")
    model, charts = parent.setup_objects(workdir)
    parent.fetch_e2a(workdir)
    source, target = charts[1], charts[2]
    level = completed_level(checkpoint, args.level)
    root_mid = np.asarray(level["endpoint_midpoint"], float)
    root_rad = np.asarray(level["endpoint_radius"], float)
    standard_half = np.r_[np.full(6, 0.02), np.full(8, 1e-4)]
    controller_centre = np.asarray(target["centre"], float)

    started = time.time()
    pending = [(root_mid, root_rad, 0)]
    accepted, blocked = [], []
    evaluations = 0
    while pending:
        mid, rad, depth = pending.pop()
        row = leaf_record(parent, model, source, target, mid, rad, args.beta,
                          depth, controller_centre, standard_half)
        evaluations += 1
        passed = (row["target_domain_strictly_inside"]
                  and row["inverse_neumann_defect_below_one"]
                  and row["objective_descent_certified"]
                  and row["exact_response_identity_available"])
        if passed:
            accepted.append(row)
            print(f"[leaf PASS d={depth}] q={row['inverse_neumann_defect_upper']:.3e} "
                  f"dL+={row['dL_upper']:+.3e} use={row['target_domain_maximum_use']:.3e}",
                  flush=True)
            continue
        projected_leaf_count = len(accepted) + len(blocked) + len(pending) + 2
        if depth >= args.max_depth or projected_leaf_count > args.max_leaves:
            row["blocking_reason"] = (
                "nonfinite" if not row["finite"] else
                "target_domain" if not row["target_domain_strictly_inside"] else
                "inverse_regular" if not row["inverse_neumann_defect_below_one"] else
                "objective_descent"
            )
            blocked.append(row)
            print(f"[leaf BLOCK d={depth}] reason={row['blocking_reason']} "
                  f"q={row['inverse_neumann_defect_upper']:.3e} "
                  f"dL+={row['dL_upper']:+.3e}", flush=True)
            continue
        index = choose_split(rad, source, target, standard_half)
        for cm, cr in reversed(split_box(mid, rad, index)):
            pending.append((cm, cr, depth + 1))
        print(f"[split d={depth}] coordinate={index} dL+={row['dL_upper']:+.3e}",
              flush=True)

    all_pass = len(blocked) == 0 and len(accepted) > 0
    protocol = {
        "version": VERSION,
        "precision_bits": 256,
        "parent_script_sha256": parent_sha,
        "checkpoint_sha256": checkpoint_sha,
        "candidate_sha256": candidate_sha,
        "diagnostic_sha256": diagnostic_sha,
        "level": args.level,
        "beta": args.beta,
        "max_depth": args.max_depth,
        "max_leaves": args.max_leaves,
        "parameterization": "source-chart affine generators retained on every leaf",
        "split_rule": "largest normalized target-domain generator influence",
        "controller": "target-centred Y0 with dynamically corrected Y=Y0(JY0)^-1",
    }
    gates = {
        "frozen_0_to_1_prerequisite_passes": True,
        "requested_level_complete": True,
        "v0_3_4_1_interval_dependency_diagnosis_bound": True,
        "complete_endpoint_partition_covered": bool(len(accepted) + len(blocked) > 0),
        "all_leaves_strictly_inside_target_domain": bool(
            all(r["target_domain_strictly_inside"] for r in accepted) and not blocked
        ),
        "all_leaf_inverse_neumann_defects_below_one": bool(
            all(r["inverse_neumann_defect_below_one"] for r in accepted) and not blocked
        ),
        "strict_objective_descent_on_every_leaf": bool(
            all(r["objective_descent_certified"] for r in accepted) and not blocked
        ),
        "exact_response_identity_available_on_every_leaf": bool(
            all(r["exact_response_identity_available"] for r in accepted) and not blocked
        ),
    }
    all_pass = bool(all_pass and all(gates.values()))
    status = ("C4_E2B_AFFINE_CORRELATED_HANDOFF_CERTIFIED"
              if all_pass else "C4_E2B_AFFINE_CORRELATED_HANDOFF_INCONCLUSIVE")
    report = {
        "title": TITLE,
        "version": VERSION,
        "protocol": protocol,
        "protocol_sha256": canonical_sha(protocol),
        "scientific_status": status,
        "all_gates_pass": all_pass,
        "gates": gates,
        "summary": {
            "evaluations": evaluations,
            "accepted_leaves": len(accepted),
            "blocked_leaves": len(blocked),
            "maximum_leaf_depth": max([r["depth"] for r in accepted + blocked], default=0),
            "maximum_accepted_dL_upper": max(
                [r["dL_upper"] for r in accepted], default=None
            ),
            "maximum_accepted_inverse_neumann_defect": max(
                [r["inverse_neumann_defect_upper"] for r in accepted], default=None
            ),
            "maximum_accepted_target_domain_use": max(
                [r["target_domain_maximum_use"] for r in accepted], default=None
            ),
            "elapsed_seconds": float(time.time() - started),
        },
        "accepted_leaves": accepted,
        "blocked_leaves": blocked,
        "required_next_step": (
            "Freeze this zero-time handoff certificate and start one target-chart positive-time Picard slab."
            if all_pass else
            "Inspect the first blocked leaf; increase subdivision only if the obstruction is interval width, never by relaxing a gate."
        ),
        "claim_boundary": (
            "Zero-time affine-correlated chart handoff only; not a positive-time flowpipe, "
            "complete transition 1->2 continuation, later chart transition, or global flow."
        ),
    }
    report["report_sha256_without_self"] = canonical_sha(report)
    Path(args.report).write_text(json.dumps(
        report, indent=2, sort_keys=True, allow_nan=False
    ) + "\n")
    print("=" * 100)
    print(TITLE, "v" + VERSION)
    print("=" * 100)
    print(json.dumps({
        "scientific_status": status,
        "all_gates_pass": all_pass,
        "summary": report["summary"],
        "required_next_step": report["required_next_step"],
    }, indent=2))
    print("report:", args.report)
    return 0 if all_pass else 2


if __name__ == "__main__":
    _code = main()
    if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:
        raise SystemExit(_code)
