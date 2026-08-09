#!/usr/bin/env python3
"""C4-E0 numerical moving-chart overlap/recentring preflight.

This is a floating-point preflight on the committed real 14-phase model.  It
does not constitute Arb tube invariance, global continuation, K=1, or QPU
evidence.  The next rigorous step is C4-E1: outward-rounded bounds over whole
chart tubes and their overlaps.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
import urllib.request
from pathlib import Path

import numpy as np


TITLE = "C4-E0 MOVING-CHART RECENTRING AND OVERLAP PREFLIGHT v1.0"
MODEL_COMMIT = "784ba5523cb3e1e2be7def3362c1722149df7360"
MODEL_NAME = "normally_attracting_response_fibre_real_model_v1_1.py"
MODEL_SHA256 = "2ba9e8739c328d97e4074f6f2ce8c0adbdf678c6f18e37bfb72cba2919b81529"
MODEL_URL = (
    "https://raw.githubusercontent.com/papasop/Geometric-Flow/"
    f"{MODEL_COMMIT}/research/control_extension/c4/{MODEL_NAME}"
)

DEFAULT_REPORT = "c4_e0_moving_chart_overlap_preflight_v1_0_report.json"


def canonical_json(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def obtain_model(directory: Path) -> Path:
    path = directory / MODEL_NAME
    if not path.exists() or sha256_file(path) != MODEL_SHA256:
        print(f"[setup] fetching frozen model @ {MODEL_COMMIT[:12]}")
        try:
            with urllib.request.urlopen(MODEL_URL, timeout=60) as response:
                payload = response.read()
        except Exception as exc:
            raise RuntimeError(
                f"Could not fetch {MODEL_URL}. Place {MODEL_NAME} beside this script."
            ) from exc
        path.write_bytes(payload)
    actual = sha256_file(path)
    if actual != MODEL_SHA256:
        raise RuntimeError(
            f"Frozen model SHA mismatch: expected {MODEL_SHA256}, obtained {actual}"
        )
    return path


def load_model(path: Path):
    spec = importlib.util.spec_from_file_location("c4_real_model", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import model from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def frames(jacobian: np.ndarray, response_dim: int, rcond: float):
    u, singular, vh = np.linalg.svd(jacobian, full_matrices=True)
    cutoff = rcond * singular[0]
    if singular[-1] <= cutoff:
        raise np.linalg.LinAlgError("response Jacobian is numerically rank deficient")
    normal = vh[:response_dim].T
    tangent = vh[response_dim:].T
    right_inverse = (vh[:response_dim].T / singular) @ u.T
    return tangent, normal, right_inverse, singular


def geometry(model, theta: np.ndarray, beta: float):
    response, jacobian, gradient, loss = model.response_jacobian_gradient_loss(theta)
    tangent, normal, right_inverse, singular = frames(
        jacobian, model.RESPONSE_DIM, model.SVD_RCOND
    )
    projector = np.eye(model.NPHASE) - right_inverse @ jacobian
    error = response - model.R_STAR
    field = -projector @ gradient - beta * (right_inverse @ error)
    return {
        "response": response,
        "jacobian": jacobian,
        "gradient": gradient,
        "loss": float(loss),
        "error": error,
        "field": field,
        "tangent": tangent,
        "normal": normal,
        "singular": singular,
    }


def midpoint_step(model, theta: np.ndarray, dt: float, beta: float) -> np.ndarray:
    k1 = geometry(model, theta, beta)["field"]
    k2 = geometry(model, theta + 0.5 * dt * k1, beta)["field"]
    return theta + dt * k2


def integrate_window(
    model, theta: np.ndarray, duration: float, steps: int, beta: float
) -> tuple[np.ndarray, dict]:
    dt = duration / steps
    current = theta.copy()
    minimum_sigma = math.inf
    maximum_error = 0.0
    all_finite = True
    for _ in range(steps):
        current = midpoint_step(model, current, dt, beta)
        state = geometry(model, current, beta)
        minimum_sigma = min(minimum_sigma, float(state["singular"][-1]))
        maximum_error = max(maximum_error, float(np.linalg.norm(state["error"])))
        all_finite = all_finite and bool(np.all(np.isfinite(current)))
    return current, {
        "minimum_sigma": minimum_sigma,
        "maximum_response_error": maximum_error,
        "all_finite": all_finite,
    }


def overlap_witness(old: dict, new: dict, tangent_half: float, normal_half: float):
    midpoint = 0.5 * (old["centre"] + new["centre"])
    records = []
    reconstruction_errors = []
    for chart in (old, new):
        delta = midpoint - chart["centre"]
        xi = chart["tangent"].T @ delta
        zeta = chart["normal"].T @ delta
        reconstructed = (
            chart["centre"] + chart["tangent"] @ xi + chart["normal"] @ zeta
        )
        reconstruction_errors.append(float(np.linalg.norm(reconstructed - midpoint)))
        records.append(
            {
                "tangent_coordinate_inf": float(np.linalg.norm(xi, ord=np.inf)),
                "normal_coordinate_inf": float(np.linalg.norm(zeta, ord=np.inf)),
            }
        )
    tangent_alignment = np.linalg.svd(
        old["tangent"].T @ new["tangent"], compute_uv=False
    )
    normal_alignment = np.linalg.svd(
        old["normal"].T @ new["normal"], compute_uv=False
    )
    overlap = all(
        record["tangent_coordinate_inf"] < tangent_half
        and record["normal_coordinate_inf"] < normal_half
        for record in records
    )
    return {
        "midpoint_in_both_charts": overlap,
        "old_chart_coordinates": records[0],
        "new_chart_coordinates": records[1],
        "maximum_reconstruction_error": max(reconstruction_errors),
        "minimum_tangent_frame_alignment": float(tangent_alignment[-1]),
        "minimum_normal_frame_alignment": float(normal_alignment[-1]),
    }


def deterministic_directions(model, seed: int):
    reference = np.asarray(model.REFERENCE_PHASES, dtype=float)
    state = geometry(model, reference, model.BETA)
    rng = np.random.default_rng(seed)
    tangent_vector = state["tangent"] @ rng.normal(size=state["tangent"].shape[1])
    normal_vector = state["normal"] @ rng.normal(size=state["normal"].shape[1])
    tangent_vector /= np.linalg.norm(tangent_vector)
    normal_vector /= np.linalg.norm(normal_vector)
    return reference, tangent_vector, normal_vector


def run_trial(model, name: str, theta0: np.ndarray, config: dict, steps: int):
    initial = geometry(model, theta0, config["beta"])
    theta = theta0.copy()
    charts = []
    overlaps = []
    minimum_sigma = float(initial["singular"][-1])
    maximum_response_error = float(np.linalg.norm(initial["error"]))
    all_finite = True

    for index in range(config["windows"] + 1):
        state = geometry(model, theta, config["beta"])
        chart = {
            "index": index,
            "centre": theta.copy(),
            "tangent": state["tangent"],
            "normal": state["normal"],
            "response_error": float(np.linalg.norm(state["error"])),
            "loss": state["loss"],
            "minimum_singular_value": float(state["singular"][-1]),
        }
        if charts:
            overlaps.append(
                overlap_witness(
                    charts[-1], chart,
                    config["tangent_half"], config["normal_half"]
                )
            )
        charts.append(chart)
        if index == config["windows"]:
            break
        theta, window_stats = integrate_window(
            model, theta, config["window_duration"], steps, config["beta"]
        )
        minimum_sigma = min(minimum_sigma, window_stats["minimum_sigma"])
        maximum_response_error = max(
            maximum_response_error, window_stats["maximum_response_error"]
        )
        all_finite = all_finite and window_stats["all_finite"]

    final = geometry(model, theta, config["beta"])
    initial_error = float(np.linalg.norm(initial["error"]))
    final_error = float(np.linalg.norm(final["error"]))
    reduction = 1.0 - final_error / max(initial_error, 1e-30)
    return {
        "name": name,
        "steps_per_window": steps,
        "initial_response_error": initial_error,
        "final_response_error": final_error,
        "response_reduction": reduction,
        "initial_loss": initial["loss"],
        "final_loss": final["loss"],
        "minimum_singular_value": minimum_sigma,
        "maximum_response_error": maximum_response_error,
        "all_finite": all_finite,
        "chart_count": len(charts),
        "transition_count": len(overlaps),
        "all_midpoint_overlaps": all(x["midpoint_in_both_charts"] for x in overlaps),
        "minimum_tangent_alignment": min(
            x["minimum_tangent_frame_alignment"] for x in overlaps
        ),
        "minimum_normal_alignment": min(
            x["minimum_normal_frame_alignment"] for x in overlaps
        ),
        "maximum_reconstruction_error": max(
            x["maximum_reconstruction_error"] for x in overlaps
        ),
        "overlaps": overlaps,
        "final_theta": theta,
    }


def serialisable_trial(trial: dict) -> dict:
    return {key: value for key, value in trial.items() if key != "final_theta"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", default=DEFAULT_REPORT)
    parser.add_argument("--seed", type=int, default=20260809)
    parser.add_argument("--windows", type=int, default=8)
    parser.add_argument("--window-duration", type=float, default=2.5e-5)
    parser.add_argument("--steps", type=int, default=4)
    parser.add_argument("--beta", type=float, default=100.0)
    parser.add_argument("--tangent-half", type=float, default=0.02)
    parser.add_argument("--normal-half", type=float, default=1.0e-4)
    args, unknown = parser.parse_known_args(argv)
    if unknown:
        print(f"# [notice] ignored notebook/kernel arguments: {unknown}")

    config = {
        "model_commit": MODEL_COMMIT,
        "model_sha256": MODEL_SHA256,
        "seed": args.seed,
        "windows": args.windows,
        "window_duration": args.window_duration,
        "steps_per_window": args.steps,
        "beta": args.beta,
        "tangent_half": args.tangent_half,
        "normal_half": args.normal_half,
        "perturbation_scale": 2.5e-5,
    }
    protocol_sha = hashlib.sha256(canonical_json(config)).hexdigest()

    workdir = Path.cwd()
    model = load_model(obtain_model(workdir))
    reference, tangent_direction, normal_direction = deterministic_directions(
        model, args.seed
    )
    scale = config["perturbation_scale"]
    starts = [
        ("tangent", reference + scale * tangent_direction),
        ("normal", reference + scale * normal_direction),
        (
            "mixed",
            reference
            + scale / math.sqrt(2.0) * (tangent_direction + normal_direction),
        ),
    ]

    print("=" * 100)
    print(TITLE)
    print("=" * 100)
    print(
        "scope: floating-point moving-chart overlap preflight; "
        "not Arb/invariance/global/K=1/QPU evidence"
    )
    print("protocol sha256:", protocol_sha)
    print("model commit:", MODEL_COMMIT)

    trials = []
    convergence = []
    for index, (name, start) in enumerate(starts, 1):
        trial = run_trial(model, name, start, config, args.steps)
        # The mixed trajectory exercises both bundles and is the frozen
        # step-halving probe.  Repeating this relatively expensive diagnostic
        # for the pure tangent/normal probes adds runtime but no new gate.
        if name == "mixed":
            fine = run_trial(model, name, start, config, 2 * args.steps)
            endpoint_difference = float(
                np.linalg.norm(trial["final_theta"] - fine["final_theta"])
            )
            convergence.append({"name": name, "endpoint_difference": endpoint_difference})
            convergence_text = f"{endpoint_difference:.3e}"
        else:
            endpoint_difference = None
            convergence_text = "n/a"
        trials.append(trial)
        print(
            f"[{index:02d}/{len(starts):02d}] {name:7s} "
            f"charts={trial['chart_count']} overlaps={trial['transition_count']} "
            f"e0={trial['initial_response_error']:.3e} "
            f"ef={trial['final_response_error']:.3e} "
            f"red={trial['response_reduction']:+.6f} "
            f"sigma={trial['minimum_singular_value']:.3e} "
            f"conv={convergence_text}"
        )

    gates = {
        "all_finite": all(t["all_finite"] for t in trials),
        "multi_chart_recentring_completed": all(t["transition_count"] >= 8 for t in trials),
        "explicit_overlap_witness_for_every_transition": all(
            t["all_midpoint_overlaps"] for t in trials
        ),
        "coordinate_reconstruction_accurate": max(
            t["maximum_reconstruction_error"] for t in trials
        ) < 1e-12,
        "chart_frames_remain_compatible": min(
            min(t["minimum_tangent_alignment"], t["minimum_normal_alignment"])
            for t in trials
        ) > 0.999,
        "trajectory_rank_margin_positive": min(
            t["minimum_singular_value"] for t in trials
        ) > 1e-4,
        "normal_and_mixed_recovery_matches_finite_horizon_rate": all(
            t["response_reduction"]
            > 0.95
            * (1.0 - math.exp(-config["beta"] * config["windows"]
                              * config["window_duration"]))
            for t in trials
            if t["name"] in {"normal", "mixed"}
        ),
        "objective_not_spoiled": all(
            t["final_loss"] <= t["initial_loss"] + 1e-8 for t in trials
        ),
        "step_halving_endpoint_converged": max(
            item["endpoint_difference"] for item in convergence
        ) < 1e-8,
    }
    all_pass = all(gates.values())
    status = (
        "C4_E0_MOVING_CHART_OVERLAP_PREFLIGHT_SUPPORTED"
        if all_pass
        else "C4_E0_MOVING_CHART_PREFLIGHT_INCONCLUSIVE"
    )
    report = {
        "title": TITLE,
        "scope": (
            "floating-point moving-chart overlap/recentring preflight on the frozen "
            "real 14-phase model; not Arb tube invariance, global continuation, K=1, "
            "Pulser, or QPU evidence"
        ),
        "protocol": config,
        "protocol_sha256": protocol_sha,
        "trials": [serialisable_trial(t) for t in trials],
        "convergence": convergence,
        "summary": {
            "trial_count": len(trials),
            "minimum_singular_value": min(t["minimum_singular_value"] for t in trials),
            "minimum_frame_alignment": min(
                min(t["minimum_tangent_alignment"], t["minimum_normal_alignment"])
                for t in trials
            ),
            "maximum_coordinate_reconstruction_error": max(
                t["maximum_reconstruction_error"] for t in trials
            ),
            "minimum_normal_mixed_response_reduction": min(
                t["response_reduction"]
                for t in trials
                if t["name"] in {"normal", "mixed"}
            ),
            "linearised_finite_horizon_reduction": 1.0
            - math.exp(
                -config["beta"] * config["windows"] * config["window_duration"]
            ),
            "maximum_step_halving_endpoint_difference": max(
                item["endpoint_difference"] for item in convergence
            ),
        },
        "gates": gates,
        "all_gates_pass": all_pass,
        "scientific_status": status,
        "required_next_step": (
            "C4-E1 must replace sampled trajectories and pointwise midpoint-overlap "
            "witnesses with outward-rounded full-tube chart-overlap/recentring bounds, "
            "then certify a finite moving-chart continuation horizon."
        ),
    }
    Path(args.report).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print("\nSUMMARY")
    print(json.dumps({"summary": report["summary"], "gates": gates, "all_gates_pass": all_pass,
                      "scientific_status": status}, indent=2, ensure_ascii=False))
    print("report:", args.report)
    return 0 if all_pass else 1


if __name__ == "__main__":
    exit_code = main()
    if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:
        raise SystemExit(exit_code)
