#!/usr/bin/env python3
"""Pulser shot-delay stability map v1.3 (W1).

Maps the dimensionless response-fibre recovery diagnostic K_rec across frozen
finite-shot budgets and estimator-memory delays.  Multiple RNG seeds and
held-out systematic disturbances are used.  The controller and independent
evaluation streams are disjoint; exact emulator probabilities are audit truth
only and are never supplied to the controller.

Requires the sibling frozen model file
``pulser_finite_shot_unit_recovery_law_audit_v1_1.py``.

This is QutipBackendV2 iterative full-sequence recalibration.  It is not
within-shot feedback, a QPU/hardware result, Arb/C4, K=1 physics, or
process-time evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import platform
import sys
from collections import Counter
from pathlib import Path


BASE_NAME = "pulser_finite_shot_unit_recovery_law_audit_v1_1.py"
_THIS_FILE = globals().get("__file__")
BASE_PATH = (
    Path(_THIS_FILE).resolve().with_name(BASE_NAME)
    if _THIS_FILE else Path.cwd() / BASE_NAME
)
if not BASE_PATH.is_file():
    raise RuntimeError(
        f"Place {BASE_NAME} beside this v1.3 script. In Colab, use the "
        "provided v1.3 bundle instead of pasting this file alone."
    )
_spec = importlib.util.spec_from_file_location("unit_law_v11", BASE_PATH)
if _spec is None or _spec.loader is None:
    raise RuntimeError("could not load frozen v1.1 model")
base = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = base
_spec.loader.exec_module(base)

import numpy as np  # noqa: E402


TITLE = "PULSER SHOT-DELAY RESPONSE-FIBRE STABILITY MAP"
VERSION = "1.3"
DEFAULT_REPORT = "pulser_shot_delay_stability_map_v1_3.json"
DEFAULT_SHOTS = (3000, 12000, 48000)
DEFAULT_DELAYS = (0, 1, 2, 3)
DEFAULT_SEEDS = (20260813, 20260829)


def canonical_sha(value: object) -> str:
    raw = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def parse_ints(value: str) -> tuple[int, ...]:
    result = tuple(int(x.strip()) for x in value.split(",") if x.strip())
    if not result:
        raise argparse.ArgumentTypeError("expected comma-separated integers")
    return result


def estimate(model, phases, case, shot_budget, args, key):
    measured = model.shot_response(
        phases, case, shot_budget,
        base.stable_seed(*key, "residual"),
    )
    jac_shots = max(2000, int(round(2.0 * shot_budget)))
    jac = np.empty((3, phases.size))
    for axis in range(phases.size):
        offset = np.zeros(phases.size)
        offset[axis] = args.finite_difference_step
        plus = model.shot_response(
            phases + offset, case, jac_shots,
            base.stable_seed(*key, "jac", axis, "+"),
        )
        minus = model.shot_response(
            phases - offset, case, jac_shots,
            base.stable_seed(*key, "jac", axis, "-"),
        )
        jac[:, axis] = (
            plus - minus
        ) / (2.0 * args.finite_difference_step)
    return measured, jac, jac_shots


def run_cell(model, case, seed, shot_budget, delay, target_exact, args):
    phases = base.REFERENCE_PHASES.copy()
    nominal = base.Disturbance(
        f"nominal_s{seed}_n{shot_budget}", 1.0, 0.0,
        tuple(0.0 for _ in base.REFERENCE_PHASES), 0.0,
    )
    target_measured = model.shot_response(
        base.REFERENCE_PHASES, nominal, shot_budget,
        base.stable_seed(seed, shot_budget, "target"),
    )
    initial_error = base.safe_error(
        model.exact_response(phases, case), target_exact, shot_budget
    )
    history = []
    records = []
    minimum_sigma = math.inf
    total_path = 0.0

    for iteration in range(args.iterations):
        key = (seed, case.name, shot_budget, delay, iteration)
        measured, jac, jac_shots = estimate(
            model, phases, case, shot_budget, args, key
        )
        history.append((measured - target_measured, jac.copy()))
        used_index = max(0, len(history) - 1 - delay)
        residual_used, jac_used = history[used_index]
        estimator_age = iteration - used_index
        singular = np.linalg.svd(jac_used, compute_uv=False)
        minimum_sigma = min(minimum_sigma, float(singular[-1]))
        gram = jac_used @ jac_used.T
        right_inverse = jac_used.T @ np.linalg.inv(
            gram + args.right_inverse_regularisation * np.eye(3)
        )
        projector = np.eye(phases.size) - right_inverse @ jac_used
        gradient = base.objective_gradient(phases, args.objective_weight)
        velocity = (
            -projector @ gradient
            - args.feedback_gain * right_inverse @ residual_used
        )
        raw_step = args.learning_rate * velocity
        raw_norm = float(np.linalg.norm(raw_step))
        clip_scale = min(
            1.0, args.maximum_step_norm / max(raw_norm, 1e-30)
        )
        step = clip_scale * raw_step

        true_before = model.exact_response(phases, case)
        error_before = base.safe_error(
            true_before, target_exact, args.evaluation_shots
        )
        evaluation_before = model.shot_response(
            phases, case, args.evaluation_shots,
            base.stable_seed(*key, "evaluation_before"),
        )
        phases = base.wrap_phase(phases + step)
        true_after = model.exact_response(phases, case)
        error_after = base.safe_error(
            true_after, target_exact, args.evaluation_shots
        )
        evaluation_after = model.shot_response(
            phases, case, args.evaluation_shots,
            base.stable_seed(*key, "evaluation_after"),
        )
        measured_e0 = base.safe_error(
            evaluation_before, target_measured, args.evaluation_shots
        )
        measured_e1 = base.safe_error(
            evaluation_after, target_measured, args.evaluation_shots
        )
        delta_tau = args.feedback_gain * args.learning_rate * clip_scale
        tkc, tkd, tdk = base.recovery_laws(
            error_before, error_after, delta_tau
        )
        mkc, mkd, mdk = base.recovery_laws(
            measured_e0, measured_e1, delta_tau
        )
        total_path += float(np.linalg.norm(step))
        records.append({
            "iteration": iteration,
            "estimator_age_rounds": estimator_age,
            "true_error_before": error_before,
            "true_error_after": error_after,
            "measured_error_before": measured_e0,
            "measured_error_after": measured_e1,
            "truth_K_rec_continuous": tkc,
            "truth_K_rec_discrete_corrected": tkd,
            "truth_delta_K": tdk,
            "measured_K_rec_continuous": mkc,
            "measured_K_rec_discrete_corrected": mkd,
            "measured_delta_K": mdk,
            "clip_scale": clip_scale,
            "effective_delta_tau": delta_tau,
            "step_norm": float(np.linalg.norm(step)),
            "estimated_minimum_jacobian_singular_value": float(singular[-1]),
            "jacobian_shots_per_side": jac_shots,
        })

    final_error = base.safe_error(
        model.exact_response(phases, case), target_exact,
        args.evaluation_shots,
    )
    truth_k = base.finite_values(
        row["truth_K_rec_continuous"] for row in records
    )
    measured_k = base.finite_values(
        row["measured_K_rec_continuous"] for row in records
    )
    return {
        "seed": seed,
        "case": case.name,
        "shot_budget": shot_budget,
        "delay_rounds": delay,
        "initial_true_error": initial_error,
        "final_true_error": final_error,
        "true_response_reduction": 1.0 - final_error / initial_error,
        "median_truth_K_rec": float(np.median(truth_k)),
        "median_measured_K_rec": float(np.median(measured_k)),
        "median_abs_truth_delta_K": float(
            np.median(np.abs(np.asarray(truth_k) - 1.0))
        ),
        "positive_truth_K_fraction": float(np.mean(np.asarray(truth_k) > 0)),
        "minimum_estimated_jacobian_singular_value": minimum_sigma,
        "control_path_length": total_path,
        "records": records,
    }


def summarise_grid(rows, shots_grid, delays_grid):
    grid = {}
    for shot_budget in shots_grid:
        grid[str(shot_budget)] = {}
        for delay in delays_grid:
            selected = [
                x for x in rows
                if x["shot_budget"] == shot_budget
                and x["delay_rounds"] == delay
            ]
            grid[str(shot_budget)][str(delay)] = {
                "replicate_count": len(selected),
                "median_truth_K_rec": float(np.median([
                    x["median_truth_K_rec"] for x in selected
                ])),
                "median_measured_K_rec": float(np.median([
                    x["median_measured_K_rec"] for x in selected
                ])),
                "median_true_response_reduction": float(np.median([
                    x["true_response_reduction"] for x in selected
                ])),
                "median_positive_truth_K_fraction": float(np.median([
                    x["positive_truth_K_fraction"] for x in selected
                ])),
                "minimum_estimated_jacobian_singular_value": float(min(
                    x["minimum_estimated_jacobian_singular_value"]
                    for x in selected
                )),
            }
    return grid


def optimal_delays(rows, seeds, shots_grid, delays_grid):
    by_seed = {}
    for seed in seeds:
        by_seed[str(seed)] = {}
        for shot_budget in shots_grid:
            scores = {}
            for delay in delays_grid:
                values = [
                    x["median_truth_K_rec"] for x in rows
                    if x["seed"] == seed
                    and x["shot_budget"] == shot_budget
                    and x["delay_rounds"] == delay
                ]
                scores[delay] = float(np.median(values))
            best = max(scores, key=lambda d: (scores[d], -d))
            by_seed[str(seed)][str(shot_budget)] = {
                "optimal_delay_rounds": best,
                "optimal_median_truth_K_rec": scores[best],
                "delay_scores": {str(k): v for k, v in scores.items()},
            }
    consensus = {}
    for shot_budget in shots_grid:
        choices = [
            by_seed[str(seed)][str(shot_budget)]["optimal_delay_rounds"]
            for seed in seeds
        ]
        counts = Counter(choices)
        mode_delay, mode_count = sorted(
            counts.items(), key=lambda x: (-x[1], x[0])
        )[0]
        consensus[str(shot_budget)] = {
            "modal_optimal_delay_rounds": mode_delay,
            "agreement_fraction": mode_count / len(seeds),
            "seed_choices": choices,
        }
    return by_seed, consensus


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--report", default=DEFAULT_REPORT)
    p.add_argument("--seeds", type=parse_ints, default=DEFAULT_SEEDS)
    p.add_argument("--shots-grid", type=parse_ints, default=DEFAULT_SHOTS)
    p.add_argument("--delays-grid", type=parse_ints, default=DEFAULT_DELAYS)
    p.add_argument("--cases-per-seed", type=int, default=2)
    p.add_argument("--iterations", type=int, default=4)
    p.add_argument("--evaluation-shots", type=int, default=30000)
    p.add_argument("--finite-difference-step", type=float, default=0.04)
    p.add_argument("--duration-ns", type=int, default=160)
    p.add_argument("--amplitude", type=float, default=5.0)
    p.add_argument("--detuning", type=float, default=-1.0)
    p.add_argument("--spacing-um", type=float, default=7.0)
    p.add_argument("--dephasing-rate", type=float, default=0.02)
    p.add_argument("--objective-weight", type=float, default=0.02)
    p.add_argument("--learning-rate", type=float, default=0.10)
    p.add_argument("--maximum-step-norm", type=float, default=0.12)
    p.add_argument("--feedback-gain", type=float, default=3.0)
    p.add_argument("--right-inverse-regularisation", type=float, default=2e-4)
    args, unknown = p.parse_known_args(argv)
    if unknown:
        print("# [notice] ignored notebook/kernel arguments:", unknown)
    seeds = tuple(args.seeds)
    shots_grid = tuple(sorted(set(args.shots_grid)))
    delays_grid = tuple(sorted(set(args.delays_grid)))
    if len(seeds) < 2 or args.cases_per_seed < 1:
        raise ValueError("use at least two seeds and one case per seed")
    if min(shots_grid) < 1000 or min(delays_grid) < 0:
        raise ValueError("invalid shot or delay grid")
    if args.iterations <= max(delays_grid):
        raise ValueError("iterations must exceed maximum delay")

    protocol = {
        "version": VERSION,
        "base_model_file": BASE_NAME,
        "base_model_sha256": hashlib.sha256(BASE_PATH.read_bytes()).hexdigest(),
        "seeds": list(seeds),
        "cases_per_seed": args.cases_per_seed,
        "shots_grid": list(shots_grid),
        "delays_grid": list(delays_grid),
        "iterations": args.iterations,
        "evaluation_shots": args.evaluation_shots,
        "jacobian_shots_rule": "max(2000, 2*shot_budget) per side",
        "finite_difference_step": args.finite_difference_step,
        "learning_rate": args.learning_rate,
        "maximum_step_norm": args.maximum_step_norm,
        "feedback_gain": args.feedback_gain,
        "right_inverse_regularisation": args.right_inverse_regularisation,
        "selection_rule": (
            "Within each seed and shot budget, choose delay maximizing median "
            "truth K_rec across held-out cases; ties prefer smaller delay."
        ),
        "predeclared_gates": {
            "minimum_jacobian_singular_value": 1e-3,
            "high_shot_zero_delay_K_positive": True,
            "grid_positive_net_recovery_fraction": 0.75,
            "low_shot_memory_benefit_min": 0.03,
            "low_shot_memory_benefit_seed_fraction": 0.50,
        },
    }
    print("=" * 104)
    print(f"{TITLE} v{VERSION}")
    print("=" * 104)
    print(
        "scope: multi-seed Pulser shot-delay stability map; not "
        "within-shot/QPU/Arb/C4/K=1/process-time evidence"
    )
    print("protocol sha256:", canonical_sha(protocol))

    model = base.PulserModel(args)
    nominal = base.Disturbance(
        "nominal_exact", 1.0, 0.0,
        tuple(0.0 for _ in base.REFERENCE_PHASES), 0.0,
    )
    target_exact = model.exact_response(base.REFERENCE_PHASES, nominal)
    rows = []
    total = len(seeds) * args.cases_per_seed * len(shots_grid) * len(delays_grid)
    counter = 0
    for seed in seeds:
        cohort = base.frozen_disturbances(
            seed, args.cases_per_seed, args.dephasing_rate
        )
        for case in cohort:
            for shot_budget in shots_grid:
                for delay in delays_grid:
                    counter += 1
                    row = run_cell(
                        model, case, seed, shot_budget, delay,
                        target_exact, args,
                    )
                    rows.append(row)
                    print(
                        f"[{counter:03d}/{total:03d}] seed={seed} "
                        f"{case.name} shots={shot_budget:5d} d={delay} "
                        f"K={row['median_truth_K_rec']:+.4f} "
                        f"red={row['true_response_reduction']:+.4f} "
                        f"pos={row['positive_truth_K_fraction']:.2f}"
                    )

    grid = summarise_grid(rows, shots_grid, delays_grid)
    seed_optima, consensus = optimal_delays(
        rows, seeds, shots_grid, delays_grid
    )
    low_shots = min(shots_grid)
    high_shots = max(shots_grid)
    zero_delay = min(delays_grid)
    low_benefit_by_seed = {}
    for seed in seeds:
        scores = seed_optima[str(seed)][str(low_shots)]["delay_scores"]
        baseline_score = scores[str(zero_delay)]
        memory_candidates = [
            (int(delay), float(score))
            for delay, score in scores.items() if int(delay) > 0
        ]
        best_memory = max(memory_candidates, key=lambda x: (x[1], -x[0]))
        benefit = best_memory[1] - baseline_score
        low_benefit_by_seed[str(seed)] = {
            "best_positive_delay": best_memory[0],
            "K_improvement_over_zero_delay": benefit,
            "benefit_at_least_0p03": benefit >= 0.03,
        }
    benefit_fraction = float(np.mean([
        x["benefit_at_least_0p03"] for x in low_benefit_by_seed.values()
    ]))
    positive_recovery_fraction = float(np.mean([
        x["true_response_reduction"] > 0 for x in rows
    ]))
    minimum_sigma = min(
        x["minimum_estimated_jacobian_singular_value"] for x in rows
    )
    high_zero_k = grid[str(high_shots)][str(zero_delay)][
        "median_truth_K_rec"
    ]
    k_values = [x["median_truth_K_rec"] for x in rows]
    signs_present = {
        "positive_K_observed": any(x > 0 for x in k_values),
        "nonpositive_K_observed": any(x <= 0 for x in k_values),
    }
    gates = {
        "all_grid_cells_completed": len(rows) == total,
        "all_values_finite": bool(all(
            math.isfinite(x["median_truth_K_rec"])
            and math.isfinite(x["true_response_reduction"])
            for x in rows
        )),
        "estimated_jacobians_retain_rank_margin": minimum_sigma > 1e-3,
        "high_shot_zero_delay_K_is_positive": high_zero_k > 0,
        "at_least_75pct_replicates_have_positive_net_recovery": (
            positive_recovery_fraction >= 0.75
        ),
        "low_shot_memory_benefit_replicates_in_at_least_half_seeds": (
            benefit_fraction >= 0.50
        ),
    }
    passed = all(gates.values())
    status = (
        "SHOT_DELAY_MEMORY_STABILITY_MAP_SUPPORTED"
        if passed else "SHOT_DELAY_MEMORY_STABILITY_MAP_INCONCLUSIVE"
    )
    summary = {
        "grid_cell_count": len(shots_grid) * len(delays_grid),
        "replicate_run_count": len(rows),
        "backend_exact_probability_executions": model.backend_executions,
        "minimum_estimated_jacobian_singular_value": minimum_sigma,
        "positive_net_recovery_fraction": positive_recovery_fraction,
        "low_shot_memory_benefit_seed_fraction": benefit_fraction,
        "low_shot_memory_benefit_by_seed": low_benefit_by_seed,
        "K_signs": signs_present,
        "K_range": [float(min(k_values)), float(max(k_values))],
    }
    report = {
        "title": TITLE,
        "version": VERSION,
        "protocol": protocol,
        "protocol_sha256": canonical_sha(protocol),
        "grid_summary": grid,
        "seedwise_optimal_delays": seed_optima,
        "cross_seed_delay_consensus": consensus,
        "summary": summary,
        "replicate_results": rows,
        "gates": gates,
        "all_gates_pass": passed,
        "scientific_status": status,
        "claim_boundary": (
            "This is an operational memory-noise map in one declared Pulser "
            "emulator pulse family. A positive-delay optimum is not universal "
            "Wiener optimality and K_rec is not the broader K=1 physical law."
        ),
        "required_next_step": (
            "If a low-shot memory benefit replicates, compare hard delay with "
            "an exponential-memory estimator and map the local K=0 boundary."
        ),
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
    }
    Path(args.report).write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print("\nSUMMARY")
    print(json.dumps({
        "grid_summary": grid,
        "cross_seed_delay_consensus": consensus,
        "summary": summary,
        "gates": gates,
        "all_gates_pass": passed,
        "scientific_status": status,
    }, indent=2))
    print("report:", args.report)
    return 0 if passed else 2


if __name__ == "__main__":
    code = main()
    if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:
        raise SystemExit(code)
