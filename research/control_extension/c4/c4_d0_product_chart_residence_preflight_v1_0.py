#!/usr/bin/env python3
"""C4-D0: product-chart residence-time preflight.

This numerical diagnostic repairs an important domain mismatch in C4-C.  The
C4-B/C Arb domain is an eight-dimensional normal slice, while the controlled
flow also has a six-dimensional tangent component.  Here we introduce the
fixed product chart

    theta = theta_ref + T0 xi + N0 z,

and measure residence in a declared 6D x 8D box under the full, unsaturated,
dynamic Moore--Penrose controlled flow.

This is a floating-point preflight used to freeze a feasible tube for a later
Arb proof (C4-D1).  It is not itself an interval certificate, an invariant-set
proof, a K=1 result, or hardware/QPU evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
from pathlib import Path

import numpy as np

try:
    import normally_attracting_response_fibre_real_model_v1_1 as model
except ModuleNotFoundError as exc:
    raise RuntimeError(
        "Place normally_attracting_response_fibre_real_model_v1_1.py "
        "beside this script."
    ) from exc


TITLE = "C4-D0 PRODUCT-CHART RESIDENCE-TIME PREFLIGHT"
VERSION = "1.0"
DEFAULT_REPORT = "c4_d0_product_chart_residence_preflight_v1_0.json"
SEED = 20260809


def unit(x):
    n = float(np.linalg.norm(x))
    if not np.isfinite(n) or n == 0:
        raise FloatingPointError("cannot normalize vector")
    return x / n


def frozen_chart():
    _, j0, _, _ = model.response_jacobian_gradient_loss(model.REFERENCE_PHASES)
    _, singular, vh = np.linalg.svd(j0, full_matrices=True)
    n0 = vh[: model.RESPONSE_DIM].T
    t0 = vh[model.RESPONSE_DIM :].T
    return t0, n0, singular


def coordinates(theta, t0, n0):
    displacement = np.asarray(theta) - model.REFERENCE_PHASES
    return t0.T @ displacement, n0.T @ displacement


def geometry(theta, beta):
    response, jacobian, gradient, loss = model.response_jacobian_gradient_loss(theta)
    u, singular, vh = np.linalg.svd(jacobian, full_matrices=False)
    if singular[-1] <= model.SVD_RCOND * singular[0]:
        raise FloatingPointError("response Jacobian lost numerical row rank")
    right_inverse = (vh.T / singular) @ u.T
    projector = np.eye(model.NPHASE) - right_inverse @ jacobian
    error = response - model.R_STAR
    field = -projector @ gradient - beta * (right_inverse @ error)
    return field, error, singular, loss


def direction_bank(t0, n0, rng):
    directions = []
    for index in range(1):
        tangent = unit(t0 @ rng.normal(size=t0.shape[1]))
        normal = unit(n0 @ rng.normal(size=n0.shape[1]))
        directions.extend(
            [
                (f"tangent_{index}", tangent),
                (f"normal_{index}", normal),
                (f"mixed_{index}", unit(tangent + normal)),
            ]
        )
    return directions


def integrate_trial(start, t0, n0, beta, duration, steps):
    """Deterministic explicit-midpoint integration for the preflight only."""
    dt = duration / steps
    times = [0.0]
    states = [np.asarray(start, dtype=float).copy()]
    theta = states[0]
    for index in range(steps):
        k1 = geometry(theta, beta)[0]
        midpoint = theta + 0.5 * dt * k1
        k2 = geometry(midpoint, beta)[0]
        theta = theta + dt * k2
        times.append((index + 1) * dt)
        states.append(theta.copy())
    solution = {
        "success": bool(np.all(np.isfinite(states))),
        "message": "fixed-step explicit midpoint",
        "t": np.asarray(times),
        "y": np.asarray(states).T,
    }
    samples = []
    for time, theta in zip(solution["t"], solution["y"].T):
        xi, z = coordinates(theta, t0, n0)
        _, error, singular, loss = geometry(theta, beta)
        samples.append(
            {
                "time": float(time),
                "xi_inf": float(np.linalg.norm(xi, ord=np.inf)),
                "z_inf": float(np.linalg.norm(z, ord=np.inf)),
                "response_norm": float(np.linalg.norm(error)),
                "sigma_min": float(singular[-1]),
                "loss": float(loss),
            }
        )
    return solution, samples


def first_exit(samples, tangent_half, normal_half):
    for row in samples:
        if row["xi_inf"] >= tangent_half or row["z_inf"] >= normal_half:
            return row["time"]
    return None


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--normal-radius", type=float, default=3.25e-4)
    parser.add_argument("--tangent-half-width", type=float, default=2.0e-2)
    parser.add_argument("--initial-fraction", type=float, default=0.25)
    parser.add_argument("--duration", type=float, default=2.0e-3)
    parser.add_argument("--beta", type=float, default=model.BETA)
    parser.add_argument("--rtol", type=float, default=1e-10)
    parser.add_argument("--atol", type=float, default=1e-12)
    parser.add_argument("--report", default=DEFAULT_REPORT)
    args, unknown = parser.parse_known_args(argv)
    if unknown:
        print("[notice] ignored notebook/kernel arguments:", unknown)
    if not (0 < args.normal_radius <= 3.25e-4):
        raise ValueError("normal-radius must be in (0, 3.25e-4]")
    if not (args.tangent_half_width > 0 and args.duration > 0 and args.beta > 0):
        raise ValueError("tangent width, duration, and beta must be positive")
    if not (0 < args.initial_fraction < 1):
        raise ValueError("initial-fraction must lie strictly between 0 and 1")

    normal_half = args.normal_radius / math.sqrt(model.RESPONSE_DIM)
    t0, n0, singular0 = frozen_chart()
    protocol = {
        "version": VERSION,
        "seed": SEED,
        "chart": "theta_ref+T0*xi+N0*z",
        "tangent_dimension": int(t0.shape[1]),
        "normal_dimension": int(n0.shape[1]),
        "tangent_half_width": args.tangent_half_width,
        "normal_radius": args.normal_radius,
        "normal_coordinate_half_width": normal_half,
        "initial_fraction": args.initial_fraction,
        "duration": args.duration,
        "beta": args.beta,
        "solver": "deterministic explicit midpoint; 10/20-step convergence pair",
        "declared_rtol_metadata": args.rtol,
        "declared_atol_metadata": args.atol,
    }
    phash = hashlib.sha256(
        json.dumps(protocol, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()

    print("=" * 100)
    print(f"{TITLE} v{VERSION}")
    print("=" * 100)
    print("scope: numerical product-chart preflight; not Arb/invariance/K=1/QPU evidence")
    print("protocol sha256:", phash)
    print("chart dimensions:", t0.shape[1], "+", n0.shape[1])
    print("normal coordinate half-width:", normal_half)
    print("tangent coordinate half-width:", args.tangent_half_width)

    rng = np.random.default_rng(SEED)
    trials = []
    directions = direction_bank(t0, n0, rng)
    for index, (name, direction) in enumerate(directions, 1):
        # Scale by Euclidean norm.  Coordinate gates below decide membership.
        if name.startswith("tangent"):
            scale = args.initial_fraction * args.tangent_half_width
        elif name.startswith("normal"):
            scale = args.initial_fraction * normal_half
        else:
            scale = args.initial_fraction * min(args.tangent_half_width, normal_half)
        start = model.REFERENCE_PHASES + scale * direction
        solution, samples = integrate_trial(
            start,
            t0,
            n0,
            args.beta,
            args.duration,
            10,
        )
        exit_time = first_exit(samples, args.tangent_half_width, normal_half)
        row = {
            "name": name,
            "success": bool(solution["success"]),
            "message": solution["message"],
            "steps": len(solution["t"]),
            "first_exit_time": exit_time,
            "resided_for_full_duration": exit_time is None,
            "initial_response_norm": samples[0]["response_norm"],
            "final_response_norm": samples[-1]["response_norm"],
            "maximum_xi_inf": max(x["xi_inf"] for x in samples),
            "maximum_z_inf": max(x["z_inf"] for x in samples),
            "minimum_sigma": min(x["sigma_min"] for x in samples),
            "initial_loss": samples[0]["loss"],
            "final_loss": samples[-1]["loss"],
        }
        trials.append(row)
        print(
            f"[{index:02d}/{len(directions):02d}] {name:10s} "
            f"resident={row['resided_for_full_duration']} "
            f"zmax={row['maximum_z_inf']:.3e} "
            f"ximax={row['maximum_xi_inf']:.3e} "
            f"sigma={row['minimum_sigma']:.3e}"
        )

    # Reintegrate one mixed case with a halved max_step.  This is a solver
    # convergence check, not a replacement for interval arithmetic.
    probe_name, probe_direction = directions[-1]
    probe_scale = args.initial_fraction * min(args.tangent_half_width, normal_half)
    probe_start = model.REFERENCE_PHASES + probe_scale * probe_direction
    coarse, coarse_samples = integrate_trial(
        probe_start, t0, n0, args.beta, args.duration, 10,
    )
    fine, fine_samples = integrate_trial(
        probe_start, t0, n0, args.beta, args.duration, 20,
    )
    endpoint_difference = float(np.linalg.norm(coarse["y"][:, -1] - fine["y"][:, -1]))

    full_residence = all(row["resided_for_full_duration"] for row in trials)
    all_finite = all(
        np.isfinite(value)
        for row in trials
        for key, value in row.items()
        if isinstance(value, (float, int))
    )
    minimum_sigma = min(row["minimum_sigma"] for row in trials)
    gates = {
        "reference_full_row_rank": bool(singular0[-1] > 1e-3),
        "all_integrations_successful": all(row["success"] for row in trials),
        "all_values_finite": bool(all_finite),
        "all_trials_reside_for_declared_duration": bool(full_residence),
        "trajectory_rank_margin_positive": bool(minimum_sigma > 1e-3),
        "step_halving_endpoint_converged": bool(endpoint_difference < 1e-8),
    }
    passed = all(gates.values())
    result = {
        "title": TITLE,
        "version": VERSION,
        "protocol": protocol,
        "protocol_sha256": phash,
        "reference_minimum_singular_value": float(singular0[-1]),
        "trials": trials,
        "convergence": {
            "probe": probe_name,
            "coarse_success": bool(coarse["success"]),
            "fine_success": bool(fine["success"]),
            "endpoint_difference": endpoint_difference,
            "coarse_final_response": coarse_samples[-1]["response_norm"],
            "fine_final_response": fine_samples[-1]["response_norm"],
        },
        "summary": {
            "minimum_observed_singular_value": minimum_sigma,
            "minimum_observed_residence_time_lower_bound": (
                args.duration if full_residence else min(
                    row["first_exit_time"] for row in trials
                    if row["first_exit_time"] is not None
                )
            ),
            "full_residence_fraction": sum(
                row["resided_for_full_duration"] for row in trials
            ) / len(trials),
        },
        "gates": gates,
        "all_gates_pass": passed,
        "scientific_status": (
            "C4_D0_PRODUCT_CHART_PREFLIGHT_SUPPORTED" if passed
            else "C4_D0_PRODUCT_CHART_PREFLIGHT_INCONCLUSIVE"
        ),
        "required_next_step": (
            "C4-D1 must replace sampled trajectories by outward-rounded bounds "
            "over the full 6D tangent x 8D normal product tube and derive a "
            "certified residence time or moving-chart continuation theorem."
        ),
        "claim_boundary": (
            "Floating-point sampled-ray residence diagnostic only. It neither "
            "proves positive invariance nor certifies unsampled initial data."
        ),
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
    }
    Path(args.report).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("\nSUMMARY")
    print(json.dumps({k: result[k] for k in (
        "summary", "convergence", "gates", "all_gates_pass",
        "scientific_status", "required_next_step")}, indent=2))
    print("report:", args.report)
    return 0 if passed else 2


if __name__ == "__main__":
    code = main()
    if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:
        raise SystemExit(code)
