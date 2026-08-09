#!/usr/bin/env python3
"""Pulser finite-shot unit-recovery-law audit v1.1.

Tests how the local right-inverse law departs from unit recovery under finite
shots, nonlinear finite steps, saturation, dephasing, and held-out systematic
disturbances.  Controller shots and evaluation shots use disjoint frozen RNG
streams.  Exact emulator probabilities are retained only as an audit truth
channel and are never supplied to the controller.

This is iterative full-sequence recalibration on QutipBackendV2.  It is not
within-shot feedback, QPU/hardware, Arb/C4, K=1 physics, or process-time
evidence.  Pulser 1.8.0 is installed automatically when absent.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata
import json
import math
import os
import platform
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


TITLE = "PULSER FINITE-SHOT UNIT-RECOVERY-LAW AUDIT"
VERSION = "1.1"
PULSER_VERSION = "1.8.0"
DEFAULT_REPORT = "pulser_finite_shot_unit_recovery_law_audit_v1_1.json"
REFERENCE_PHASES_LIST = [
    0.44700291, 3.23777603, 1.34003555,
    2.59344604, 6.01771251, 0.10582154,
]
RESPONSE_KEYS = ("gg", "gr", "rg")


def ensure_pulser() -> None:
    try:
        importlib.import_module("pulser")
        importlib.import_module("pulser_simulation")
        return
    except ModuleNotFoundError as exc:
        if os.environ.get("PULSER_PREFLIGHT_NO_INSTALL") == "1":
            raise RuntimeError(f"Install pulser=={PULSER_VERSION}") from exc
    print(f"[setup] installing pulser=={PULSER_VERSION}")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "-q",
        f"pulser=={PULSER_VERSION}",
    ])
    importlib.invalidate_caches()


ensure_pulser()
import numpy as np  # noqa: E402
from pulser import NoiseModel, Pulse, Register, Sequence  # noqa: E402
from pulser.devices import DigitalAnalogDevice  # noqa: E402
from pulser_simulation import QutipBackendV2  # noqa: E402

REFERENCE_PHASES = np.array(REFERENCE_PHASES_LIST, dtype=float)


def canonical_sha(value: object) -> str:
    raw = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def wrap_phase(value: np.ndarray) -> np.ndarray:
    return np.mod(value, 2.0 * np.pi)


def stable_seed(*parts: object) -> int:
    raw = "|".join(map(str, parts)).encode("utf-8")
    return int.from_bytes(hashlib.sha256(raw).digest()[:8], "little")


@dataclass(frozen=True)
class Disturbance:
    name: str
    amplitude_scale: float
    detuning_offset: float
    phase_bias: tuple[float, ...]
    dephasing_rate: float

    def serialise(self) -> dict:
        return {
            "name": self.name,
            "amplitude_scale": self.amplitude_scale,
            "detuning_offset": self.detuning_offset,
            "phase_bias": list(self.phase_bias),
            "dephasing_rate": self.dephasing_rate,
        }


def frozen_disturbances(seed: int, count: int,
                        dephasing_rate: float) -> list[Disturbance]:
    rng = np.random.default_rng(seed)
    result = []
    for index in range(count):
        phase_bias = rng.normal(0.0, 0.025, REFERENCE_PHASES.size)
        phase_bias -= phase_bias.mean()
        result.append(Disturbance(
            f"heldout_{index:02d}",
            float(np.clip(1.0 + rng.normal(0.0, 0.035), 0.93, 1.07)),
            float(np.clip(rng.normal(0.0, 0.12), -0.24, 0.24)),
            tuple(map(float, phase_bias)),
            dephasing_rate,
        ))
    return result


class PulserModel:
    def __init__(self, args):
        self.args = args
        self.cache: dict[tuple, np.ndarray] = {}
        self.backend_executions = 0

    def sequence(self, phases: np.ndarray, case: Disturbance) -> Sequence:
        reg = Register({
            "q0": (-0.5 * self.args.spacing_um, 0.0),
            "q1": (+0.5 * self.args.spacing_um, 0.0),
        })
        seq = Sequence(reg, DigitalAnalogDevice)
        seq.declare_channel("rydberg", "rydberg_local", initial_target="q0")
        physical = wrap_phase(phases + np.asarray(case.phase_bias))
        for index, phase in enumerate(physical):
            seq.target("q0" if index % 2 == 0 else "q1", "rydberg")
            seq.add(Pulse.ConstantPulse(
                self.args.duration_ns,
                self.args.amplitude * case.amplitude_scale,
                self.args.detuning + case.detuning_offset,
                float(phase),
            ), "rydberg")
        seq.measure("ground-rydberg")
        return seq

    def exact_response(self, phases: np.ndarray,
                       case: Disturbance) -> np.ndarray:
        phases = wrap_phase(np.asarray(phases, dtype=float))
        key = (
            tuple(np.round(phases, 13)), case.name, case.amplitude_scale,
            case.detuning_offset, case.phase_bias, case.dephasing_rate,
        )
        if key in self.cache:
            return self.cache[key].copy()
        config = QutipBackendV2.default_config.with_changes(
            noise_model=NoiseModel(dephasing_rate=case.dephasing_rate)
        )
        out = QutipBackendV2(
            self.sequence(phases, case), config=config
        ).run().final_state.probabilities()
        response = np.array([float(out.get(k, 0.0)) for k in RESPONSE_KEYS])
        if not np.all(np.isfinite(response)) or response.sum() > 1.0 + 1e-9:
            raise RuntimeError("invalid emulator probability response")
        self.backend_executions += 1
        self.cache[key] = response.copy()
        return response

    def shot_response(self, phases: np.ndarray, case: Disturbance,
                      shots: int, seed: int) -> np.ndarray:
        response = self.exact_response(phases, case)
        probabilities = np.append(response, max(0.0, 1.0 - response.sum()))
        probabilities /= probabilities.sum()
        counts = np.random.default_rng(seed).multinomial(shots, probabilities)
        return counts[:3].astype(float) / shots


def objective(phases: np.ndarray, weight: float) -> float:
    delta = phases - np.roll(phases, 1)
    return float(weight * np.sum(1.0 - np.cos(delta)))


def objective_gradient(phases: np.ndarray, weight: float) -> np.ndarray:
    return weight * (
        np.sin(phases - np.roll(phases, 1))
        + np.sin(phases - np.roll(phases, -1))
    )


def estimated_jacobian(model: PulserModel, phases: np.ndarray,
                       case: Disturbance, args, key: tuple) -> np.ndarray:
    jac = np.empty((3, phases.size))
    for axis in range(phases.size):
        offset = np.zeros(phases.size)
        offset[axis] = args.finite_difference_step
        plus = model.shot_response(
            phases + offset, case, args.jacobian_shots,
            stable_seed(*key, "jac", axis, "+"),
        )
        minus = model.shot_response(
            phases - offset, case, args.jacobian_shots,
            stable_seed(*key, "jac", axis, "-"),
        )
        jac[:, axis] = (plus - minus) / (2 * args.finite_difference_step)
    return jac


def safe_error(response: np.ndarray, target: np.ndarray,
               shots: int) -> float:
    # Half a count prevents log(0) without materially changing resolved errors.
    return max(float(np.linalg.norm(response - target)), 0.5 / shots)


def recovery_laws(error_before: float, error_after: float,
                  delta_tau: float) -> tuple[float, float, float]:
    if delta_tau <= 0 or delta_tau >= 1:
        return math.nan, math.nan, math.nan
    ratio = max(error_after, 1e-30) / max(error_before, 1e-30)
    k_cont = -math.log(ratio) / delta_tau
    k_disc = math.log(ratio) / math.log(1.0 - delta_tau)
    return k_cont, k_disc, k_cont - 1.0


def run_controller(model: PulserModel, kind: str, case: Disturbance,
                   target_exact: np.ndarray, target_shot: np.ndarray,
                   args) -> dict:
    phases = REFERENCE_PHASES.copy()
    initial_true_error = safe_error(
        model.exact_response(phases, case), target_exact, args.evaluation_shots
    )
    records = []
    minimum_sigma = math.inf
    total_path = 0.0

    for iteration in range(args.iterations):
        key = (args.seed, case.name, kind, iteration)
        measured_before = model.shot_response(
            phases, case, args.controller_shots,
            stable_seed(*key, "control_before"),
        )
        eval_before = model.shot_response(
            phases, case, args.evaluation_shots,
            stable_seed(*key, "eval_before"),
        )
        true_before = model.exact_response(phases, case)
        residual = measured_before - target_shot
        jac = estimated_jacobian(model, phases, case, args, key)
        singular = np.linalg.svd(jac, compute_uv=False)
        minimum_sigma = min(minimum_sigma, float(singular[-1]))
        gram = jac @ jac.T
        right_inverse = jac.T @ np.linalg.inv(
            gram + args.right_inverse_regularisation * np.eye(3)
        )
        projector = np.eye(phases.size) - right_inverse @ jac
        gradient = objective_gradient(phases, args.objective_weight)
        if kind == "feedback":
            tangent_velocity = -projector @ gradient
            normal_velocity = -args.feedback_gain * right_inverse @ residual
            velocity = tangent_velocity + normal_velocity
        elif kind == "tangent":
            normal_velocity = np.zeros_like(phases)
            velocity = -projector @ gradient
        elif kind == "penalty":
            normal_velocity = -args.penalty_gain * jac.T @ residual
            velocity = -gradient + normal_velocity
        else:
            raise ValueError(kind)

        raw_step = args.learning_rate * velocity
        raw_norm = float(np.linalg.norm(raw_step))
        clip_scale = min(1.0, args.maximum_step_norm / max(raw_norm, 1e-30))
        step = clip_scale * raw_step
        phases = wrap_phase(phases + step)
        total_path += float(np.linalg.norm(step))

        eval_after = model.shot_response(
            phases, case, args.evaluation_shots,
            stable_seed(*key, "eval_after"),
        )
        true_after = model.exact_response(phases, case)
        measured_e0 = safe_error(eval_before, target_shot, args.evaluation_shots)
        measured_e1 = safe_error(eval_after, target_shot, args.evaluation_shots)
        true_e0 = safe_error(true_before, target_exact, args.evaluation_shots)
        true_e1 = safe_error(true_after, target_exact, args.evaluation_shots)
        delta_tau = (
            args.feedback_gain * args.learning_rate * clip_scale
            if kind == "feedback" else math.nan
        )
        mkc, mkd, mdk = recovery_laws(measured_e0, measured_e1, delta_tau)
        tkc, tkd, tdk = recovery_laws(true_e0, true_e1, delta_tau)
        records.append({
            "iteration": iteration,
            "measured_error_before": measured_e0,
            "measured_error_after": measured_e1,
            "true_error_before": true_e0,
            "true_error_after": true_e1,
            "minimum_estimated_jacobian_singular_value": float(singular[-1]),
            "clip_scale": clip_scale,
            "effective_delta_tau": delta_tau,
            "measured_K_rec_continuous": mkc,
            "measured_K_rec_discrete_corrected": mkd,
            "measured_delta_K": mdk,
            "truth_K_rec_continuous": tkc,
            "truth_K_rec_discrete_corrected": tkd,
            "truth_delta_K": tdk,
            "step_norm": float(np.linalg.norm(step)),
            "normal_velocity_norm": float(np.linalg.norm(normal_velocity)),
        })

    final_true_error = safe_error(
        model.exact_response(phases, case), target_exact, args.evaluation_shots
    )
    final_eval = model.shot_response(
        phases, case, args.evaluation_shots,
        stable_seed(args.seed, case.name, kind, "final_eval"),
    )
    final_measured_error = safe_error(
        final_eval, target_shot, args.evaluation_shots
    )
    return {
        "controller": kind,
        "initial_true_error": initial_true_error,
        "final_true_error": final_true_error,
        "final_measured_error": final_measured_error,
        "true_response_reduction": 1.0 - final_true_error / initial_true_error,
        "final_objective": objective(phases, args.objective_weight),
        "control_path_length": total_path,
        "minimum_estimated_jacobian_singular_value": minimum_sigma,
        "records": records,
    }


def finite_values(values) -> list[float]:
    return [float(x) for x in values if math.isfinite(float(x))]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--report", default=DEFAULT_REPORT)
    p.add_argument("--seed", type=int, default=20260811)
    p.add_argument("--cases", type=int, default=4)
    p.add_argument("--iterations", type=int, default=6)
    p.add_argument("--controller-shots", type=int, default=12000)
    p.add_argument("--jacobian-shots", type=int, default=24000)
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
    p.add_argument("--penalty-gain", type=float, default=300.0)
    p.add_argument("--right-inverse-regularisation", type=float, default=2e-4)
    args, unknown = p.parse_known_args(argv)
    if unknown:
        print("# [notice] ignored notebook/kernel arguments:", unknown)
    if args.cases < 2 or args.iterations < 2:
        raise ValueError("need at least two cases and two iterations")
    if min(args.controller_shots, args.jacobian_shots,
           args.evaluation_shots) < 1000:
        raise ValueError("shot budgets must be at least 1000")

    cases = frozen_disturbances(args.seed, args.cases, args.dephasing_rate)
    nominal = Disturbance(
        "nominal", 1.0, 0.0, tuple(0.0 for _ in REFERENCE_PHASES), 0.0
    )
    protocol = {
        "version": VERSION,
        "backend": "Pulser QutipBackendV2",
        "reference_phases": REFERENCE_PHASES.tolist(),
        "response_keys": list(RESPONSE_KEYS),
        "cases": [x.serialise() for x in cases],
        "iterations": args.iterations,
        "shots": {
            "controller": args.controller_shots,
            "jacobian_per_side": args.jacobian_shots,
            "independent_evaluation": args.evaluation_shots,
        },
        "finite_difference_step": args.finite_difference_step,
        "learning_rate": args.learning_rate,
        "maximum_step_norm": args.maximum_step_norm,
        "feedback_gain": args.feedback_gain,
        "penalty_gain": args.penalty_gain,
        "right_inverse_regularisation": args.right_inverse_regularisation,
        "rng_separation": (
            "controller, Jacobian, and evaluation shots use disjoint frozen "
            "SHA-256-derived streams; exact probabilities are audit truth only"
        ),
        "unit_law": {
            "continuous": "-Delta log ||e|| / Delta tau",
            "discrete_corrected": "log(e_after/e_before)/log(1-Delta tau)",
            "Delta_tau": "feedback_gain*learning_rate*clip_scale",
            "delta_K": "K_rec_continuous-1",
        },
        "predeclared_gates": {
            "median_feedback_true_reduction": 0.50,
            "feedback_baseline_win_fraction": 0.75,
            "positive_truth_K_fraction": 0.75,
            "median_abs_truth_delta_K": 0.75,
            "minimum_estimated_jacobian_singular_value": 1e-3,
        },
    }
    print("=" * 104)
    print(f"{TITLE} v{VERSION}")
    print("=" * 104)
    print(
        "scope: finite-shot Pulser emulator iterative calibration and unit-law "
        "deviation audit; not within-shot/QPU/Arb/C4/K=1/process-time evidence"
    )
    print("protocol sha256:", canonical_sha(protocol))

    model = PulserModel(args)
    target_exact = model.exact_response(REFERENCE_PHASES, nominal)
    target_shot = model.shot_response(
        REFERENCE_PHASES, nominal, args.controller_shots,
        stable_seed(args.seed, "frozen_target"),
    )
    print("exact target:", np.array2string(target_exact, precision=9))
    print("shot target :", np.array2string(target_shot, precision=9))

    results = []
    for index, case in enumerate(cases, 1):
        controls = {
            kind: run_controller(
                model, kind, case, target_exact, target_shot, args
            ) for kind in ("tangent", "feedback", "penalty")
        }
        fb = controls["feedback"]
        t = controls["tangent"]
        q = controls["penalty"]
        result = {
            "disturbance": case.serialise(),
            "controllers": controls,
            "feedback_beats_tangent": fb["final_true_error"] < t["final_true_error"],
            "feedback_beats_penalty": fb["final_true_error"] < q["final_true_error"],
        }
        results.append(result)
        ks = finite_values(r["truth_K_rec_continuous"] for r in fb["records"])
        print(
            f"[{index:02d}/{len(cases):02d}] {case.name} "
            f"e0={fb['initial_true_error']:.3e} "
            f"tan={t['final_true_error']:.3e} "
            f"fb={fb['final_true_error']:.3e} "
            f"pen={q['final_true_error']:.3e} "
            f"red={fb['true_response_reduction']:+.6f} "
            f"Kmed={np.median(ks):+.4f}"
        )

    feedback = [x["controllers"]["feedback"] for x in results]
    reductions = [x["true_response_reduction"] for x in feedback]
    truth_k = finite_values(
        r["truth_K_rec_continuous"] for c in feedback for r in c["records"]
    )
    measured_k = finite_values(
        r["measured_K_rec_continuous"] for c in feedback for r in c["records"]
    )
    truth_k_disc = finite_values(
        r["truth_K_rec_discrete_corrected"]
        for c in feedback for r in c["records"]
    )
    min_sigma = min(
        c["minimum_estimated_jacobian_singular_value"]
        for x in results for c in x["controllers"].values()
    )
    tangent_wins = float(np.mean([x["feedback_beats_tangent"] for x in results]))
    penalty_wins = float(np.mean([x["feedback_beats_penalty"] for x in results]))
    positive_fraction = float(np.mean(np.asarray(truth_k) > 0))
    median_abs_delta = float(np.median(np.abs(np.asarray(truth_k) - 1.0)))
    gates = {
        "all_values_finite": bool(all(map(math.isfinite, reductions + truth_k))),
        "finite_shot_streams_are_train_evaluation_separated": True,
        "estimated_response_jacobians_full_row_rank": bool(min_sigma > 1e-3),
        "median_feedback_true_reduction_at_least_50pct": bool(
            np.median(reductions) >= 0.50
        ),
        "feedback_beats_tangent_on_at_least_75pct_cases": bool(
            tangent_wins >= 0.75
        ),
        "feedback_beats_penalty_on_at_least_75pct_cases": bool(
            penalty_wins >= 0.75
        ),
        "positive_truth_K_on_at_least_75pct_steps": bool(
            positive_fraction >= 0.75
        ),
        "median_abs_truth_delta_K_at_most_0p75": bool(
            median_abs_delta <= 0.75
        ),
    }
    passed = all(gates.values())
    summary = {
        "heldout_case_count": len(results),
        "backend_exact_probability_executions": model.backend_executions,
        "controller_shots": args.controller_shots,
        "jacobian_shots_per_side": args.jacobian_shots,
        "evaluation_shots": args.evaluation_shots,
        "median_feedback_true_response_reduction": float(np.median(reductions)),
        "minimum_feedback_true_response_reduction": float(np.min(reductions)),
        "feedback_tangent_win_fraction": tangent_wins,
        "feedback_penalty_win_fraction": penalty_wins,
        "median_truth_K_rec_continuous": float(np.median(truth_k)),
        "median_measured_K_rec_continuous": float(np.median(measured_k)),
        "median_truth_K_rec_discrete_corrected": float(np.median(truth_k_disc)),
        "median_abs_truth_delta_K": median_abs_delta,
        "positive_truth_K_step_fraction": positive_fraction,
        "minimum_estimated_jacobian_singular_value": float(min_sigma),
    }
    status = (
        "FINITE_SHOT_UNIT_RECOVERY_LAW_SUPPORTED_WITH_BOUNDED_DEVIATION"
        if passed else "FINITE_SHOT_UNIT_RECOVERY_LAW_AUDIT_INCONCLUSIVE"
    )
    report = {
        "title": TITLE,
        "version": VERSION,
        "protocol": protocol,
        "protocol_sha256": canonical_sha(protocol),
        "target_exact": target_exact.tolist(),
        "target_shot_estimate": target_shot.tolist(),
        "cases": results,
        "summary": summary,
        "gates": gates,
        "all_gates_pass": passed,
        "scientific_status": status,
        "claim_boundary": (
            "This audit measures a dimensionless local recovery-rate diagnostic "
            "under finite-shot estimation in one declared Pulser emulator model. "
            "K_rec near one is a controller normalisation diagnostic, not proof "
            "of the broader K=1 physical theory or of process-relative time."
        ),
        "required_next_step": (
            "Repeat with frozen SPAM, drift, latency, and actuator saturation, "
            "then run the same protocol on a second model before any QPU pilot."
        ),
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pulser": importlib.metadata.version("pulser"),
            "pulser_simulation": importlib.metadata.version("pulser-simulation"),
        },
    }
    Path(args.report).write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print("\nSUMMARY")
    print(json.dumps({
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
