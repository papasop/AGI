#!/usr/bin/env python3
"""
Fast floating-point preflight for a response-fibre geometric flow.

This script does NOT issue a formal theorem.  It tests whether the frozen
v1.3.1 Chebyshev centre curve is ready for a validated ODE/Taylor-model
upgrade.  In the predeclared Euclidean phase metric it checks

    (A) response-fibre tangency,
    (B) positive alignment with the projected negative L6 gradient, and
    (C) strict pointwise L6 descent.

The output deliberately distinguishes:

* GRADIENT_FLOW_FORMAL_CERTIFICATION_READY
* CONTINUOUS_DESCENT_FLOW_CANDIDATE_NOT_GRADIENT_ALIGNED
* CURVE_RECONSTRUCTION_REQUIRED
* PARAMETERIZATION_INTEGRITY_FAILED

An approximate alignment PASS is only a readiness diagnostic.  Exact
parallelism must later be proved as an ODE/DAE existence statement; merely
enclosing a residual around zero is not such a proof.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
from numpy.polynomial import chebyshev as cheb


TITLE = "RESPONSE-FIBRE GEOMETRIC-FLOW ALIGNMENT PREFLIGHT"
VERSION = "0.1.0"

# The metric and every diagnostic gate are frozen before evaluating the curve.
METRIC = "Euclidean metric in the declared fourteen phase coordinates"
EXPECTED_PARAMETERIZATION_SHA256 = (
    "e8ad8a6fbcab626b726082b570f59df6854d4a28259177783e1f5e3274b1cb84"
)
RESPONSE_GAP_GATE = 2.0e-8
TANGENT_RELATIVE_RESIDUAL_GATE = 5.0e-5
MINIMUM_SINGULAR_VALUE_GATE = 2.0e-3
MINIMUM_PROJECTED_GRADIENT_NORM_GATE = 1.0e-6
MINIMUM_ORIENTED_LAMBDA_GATE = 1.0e-6
MINIMUM_ALIGNMENT_COSINE_GATE = 0.99875
MAXIMUM_PARALLEL_RELATIVE_RESIDUAL_GATE = 5.0e-2
MAXIMUM_DL6_DS_GATE = -1.0e-6
DERIVATIVE_CROSSCHECK_RELATIVE_GATE = 5.0e-3

RESPONSE_JACOBIAN_STEP = 2.0e-5
L6_GRADIENT_STEP = 2.0e-5
CURVE_DERIVATIVE_CROSSCHECK_STEP = 1.0e-4

OMEGA = 1.0
TAU = 0.62
CONTROL_DIMENSION = 14
RESPONSE_DIMENSION = 8

REFERENCE_PHASES = np.array(
    [
        3.006797722681818,
        2.7106859720155914,
        1.1306621045783265,
        -2.6568476957176808,
        1.4365241820035193,
        -2.0773016506803064,
        0.16320548211467623,
        3.089644890790571,
        -0.8755338801622679,
        -2.6500043472817922,
        0.9588777193059705,
        -3.1075630669100938,
        0.7072945305932086,
        -0.48362649203822405,
    ],
    dtype=float,
)

FLOW_NODES = np.array(
    [
        [3.0205298334700963, 2.672557855893252, 1.2287347705910372, -2.585812089996734, 1.6156077218714129, -1.9903545457288279, 0.018342179248949615, 3.248305941466115, -0.5506379990622509, -2.650202778530186, 1.1004179447118312, -3.0715843271099477, 0.6908618628784341, -0.5053470390329837],
        [3.0180206895364994, 2.6692158020092327, 1.2550854109255325, -2.578849149200848, 1.6191501634718652, -1.9673620735405895, 0.009676728965377175, 3.250033982646299, -0.5412619215256755, -2.6461863967687758, 1.102070136398153, -3.0809336851409874, 0.6909508188565556, -0.5107271610906394],
        [3.015672240345604, 2.665142579384167, 1.2819661643575662, -2.5713211072979756, 1.6221702596282175, -1.9437256164597883, 0.0023466039713055382, 3.2505998828067275, -0.5330693553190863, -2.641407921867685, 1.104860727069305, -3.0887081213547365, 0.6912540344895083, -0.515268600986809],
        [3.013645177147858, 2.660255570102458, 1.309129627485621, -2.5630346834063693, 1.6250106892880654, -1.919787283322471, -0.0037838668496646254, 3.249909541935888, -0.5260144109112849, -2.635927506934177, 1.108596090829253, -3.095015816215217, 0.6917497687540339, -0.5190245961510166],
        [3.012083137480356, 2.6545111799434182, 1.3363674818948545, -2.553818031868482, 1.627978146674206, -1.8958654515221502, -0.008871915020963437, 3.2478981005198535, -0.5200396153044811, -2.6298240938345625, 1.1130928355962235, -3.1000191138599926, 0.6923847046371968, -0.5220684728154691],
        [3.0111040888927576, 2.64790539865, 1.3635068441211293, -2.543529422233472, 1.6313329694178371, -1.8722520717793314, -0.013079242887669935, 3.244534772877237, -0.515085568766006, -2.623193753174364, 1.1181798415391193, -3.1039216778127154, 0.6930813392323453, -0.5244883520289174],
        [3.0107934389145043, 2.640471300246364, 1.3904127140544176, -2.5320698375331454, 1.6352709633132618, -1.8492112506669518, -0.016567019803742106, 3.2398270207032156, -0.5110920913862655, -2.6161496163935425, 1.1236989214261122, -3.1069491169301524, 0.693749614348016, -0.5263809482690619],
        [3.0112008147478213, 2.6322742042182017, 1.4169851313622397, -2.5193872039265255, 1.6399238734599284, -1.826971105955113, -0.019479825918175406, 3.233819724136135, -0.5080039956568875, -2.60881277081895, 1.129504940010814, -3.1093342459703033, 0.6942981759286697, -0.52784596794792],
        [3.0123384618118534, 2.6234058436124523, 1.4431606012839713, -2.505482806789493, 1.6453547974097789, -1.8057166307719468, -0.021942530099015953, 3.2265931025913632, -0.5057668158313071, -2.6013019235734904, 1.1354701800816682, -3.111297908979576, 0.6946462673504518, -0.5289796091344567],
        [3.0141871560966544, 2.613972693000951, 1.4689099442649445, -2.490404632803783, 1.65156785237466, -1.7855844373586374, -0.024054039424857412, 3.218252486348267, -0.5043302644269975, -2.5937259004870152, 1.1414834295498006, -3.11303512740587, 0.6947322963462942, -0.5298694800130552],
        [3.016703568224395, 2.604086334951333, 1.494233689962464, -2.4742371822080456, 1.6585242033118377, -1.7666600682574403, -0.025883388932136445, 3.208922938809488, -0.5036449592701115, -2.586176981903448, 1.1474528555801007, -3.114704394146617, 0.6945179653319272, -0.5305905010233385],
    ],
    dtype=float,
)


def banner(text: str) -> None:
    print("\n" + "=" * 120)
    print(text)
    print("=" * 120)


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def find_parameterization(explicit: str | None) -> Path:
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit))
    candidates.extend(
        [
            Path("response_fibre_exact_root_descent_v1_3_1_results/global_parameterization.json"),
            Path("response_fibre_exact_root_descent_v1_3_results/global_parameterization.json"),
            Path("response_fibre_parametric_arb_krawczyk_v1_2_2_results/global_parameterization.json"),
            Path("response_fibre_parametric_arb_krawczyk_results/global_parameterization.json"),
            Path("global_parameterization.json"),
        ]
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise FileNotFoundError(
        "global_parameterization.json was not found. Pass "
        "--parameterization /path/to/global_parameterization.json. "
        "Use the file emitted by the complete v1.3.1 run; this preflight "
        "does not rerun the 640-box certificate."
    )


def segment_float(delta: complex, phase: float) -> np.ndarray:
    radius = np.sqrt(OMEGA * OMEGA + delta * delta)
    c = np.cos(0.5 * TAU * radius)
    s = np.sin(0.5 * TAU * radius) / radius
    return np.array(
        [
            [
                c - 1j * s * delta,
                -1j * s * OMEGA * np.exp(-1j * phase),
            ],
            [
                -1j * s * OMEGA * np.exp(1j * phase),
                c + 1j * s * delta,
            ],
        ],
        dtype=complex,
    )


def state_float(phases: np.ndarray, delta: complex) -> np.ndarray:
    state = np.array([1.0 + 0.0j, 0.0 + 0.0j])
    for phase in phases:
        state = segment_float(delta, float(phase)) @ state
    return state


def target_basis_float() -> tuple[np.ndarray, np.ndarray]:
    target = state_float(REFERENCE_PHASES, 0.0)
    target /= np.linalg.norm(target)
    orthogonal = np.array([-np.conj(target[1]), np.conj(target[0])])
    return target, orthogonal


TARGET_FLOAT, ORTHOGONAL_FLOAT = target_basis_float()


def projective_coordinate(phases: np.ndarray, delta: complex) -> complex:
    state = state_float(phases, delta)
    return np.vdot(ORTHOGONAL_FLOAT, state) / np.vdot(TARGET_FLOAT, state)


def response_coefficients(
    phases: np.ndarray,
    order: int = 3,
    radius: float = 0.075,
    points: int = 64,
) -> np.ndarray:
    angles = 2.0 * np.pi * np.arange(points) / points
    roots = np.exp(1j * angles)
    values = np.array(
        [
            projective_coordinate(phases, radius * root)
            for root in roots
        ]
    )
    return np.array(
        [
            np.mean(values * np.exp(-1j * degree * angles))
            / radius**degree
            for degree in range(order + 1)
        ]
    )


def response_feature(phases: np.ndarray) -> np.ndarray:
    coefficients = response_coefficients(phases, order=3)
    return np.concatenate([coefficients.real, coefficients.imag])


TARGET_RESPONSE = response_feature(REFERENCE_PHASES)


def finite_difference_jacobian(
    function,
    point: np.ndarray,
    step: float,
) -> np.ndarray:
    baseline = np.asarray(function(point), dtype=float)
    result = np.empty((baseline.size, point.size), dtype=float)
    for column in range(point.size):
        plus = point.copy()
        minus = point.copy()
        plus[column] += step
        minus[column] -= step
        result[:, column] = (function(plus) - function(minus)) / (2.0 * step)
    return result


def l6_coefficient(phases: np.ndarray) -> float:
    """Extract the sixth symmetric-loss coefficient from a0,...,a6."""
    coefficients = response_coefficients(
        phases, order=6, radius=0.055, points=64
    )
    q = np.zeros(7, dtype=complex)
    for left, a_left in enumerate(coefficients):
        for right, a_right in enumerate(coefficients):
            if left + right <= 6:
                q[left + right] += a_left * np.conj(a_right)

    inverse = np.zeros(7, dtype=complex)
    inverse[0] = 1.0 / (1.0 + q[0])
    for degree in range(1, 7):
        inverse[degree] = -inverse[0] * sum(
            q[k] * inverse[degree - k] for k in range(1, degree + 1)
        )
    loss = np.convolve(q, inverse)[:7]
    return float(loss[6].real)


def l6_gradient(phases: np.ndarray, step: float) -> np.ndarray:
    gradient = np.empty(CONTROL_DIMENSION, dtype=float)
    for column in range(CONTROL_DIMENSION):
        plus = phases.copy()
        minus = phases.copy()
        plus[column] += step
        minus[column] -= step
        gradient[column] = (
            l6_coefficient(plus) - l6_coefficient(minus)
        ) / (2.0 * step)
    return gradient


class FrozenCurve:
    def __init__(self, parameterization: dict[str, Any]):
        self.transverse = np.asarray(
            parameterization["transverse_basis"], dtype=float
        )
        self.coefficients = [
            np.asarray(item, dtype=float)
            for item in parameterization["segment_chebyshev_coefficients"]
        ]
        if self.transverse.shape != (CONTROL_DIMENSION, RESPONSE_DIMENSION):
            raise ValueError(
                f"transverse_basis has shape {self.transverse.shape}, "
                f"expected {(CONTROL_DIMENSION, RESPONSE_DIMENSION)}"
            )
        if len(self.coefficients) != 10:
            raise ValueError(
                f"found {len(self.coefficients)} segments, expected 10"
            )
        for index, coefficients in enumerate(self.coefficients):
            if coefficients.ndim != 2 or coefficients.shape[1] != 8:
                raise ValueError(
                    f"segment {index} coefficients have invalid shape "
                    f"{coefficients.shape}"
                )

    def value(self, segment: int, scalar: float) -> np.ndarray:
        left = FLOW_NODES[segment]
        right = FLOW_NODES[segment + 1]
        correction = np.array(
            [
                cheb.chebval(
                    2.0 * scalar - 1.0,
                    self.coefficients[segment][:, column],
                )
                for column in range(RESPONSE_DIMENSION)
            ]
        )
        return (1.0 - scalar) * left + scalar * right + (
            self.transverse @ correction
        )

    def derivative(self, segment: int, scalar: float) -> np.ndarray:
        correction_derivative = np.array(
            [
                2.0
                * cheb.chebval(
                    2.0 * scalar - 1.0,
                    cheb.chebder(
                        self.coefficients[segment][:, column]
                    ),
                )
                for column in range(RESPONSE_DIMENSION)
            ]
        )
        return (
            FLOW_NODES[segment + 1]
            - FLOW_NODES[segment]
            + self.transverse @ correction_derivative
        )


def curve_l6_derivative_crosscheck(
    curve: FrozenCurve,
    segment: int,
    scalar: float,
    step: float,
) -> float:
    if scalar >= step and scalar <= 1.0 - step:
        return (
            l6_coefficient(curve.value(segment, scalar + step))
            - l6_coefficient(curve.value(segment, scalar - step))
        ) / (2.0 * step)
    if scalar < step:
        f0 = l6_coefficient(curve.value(segment, scalar))
        f1 = l6_coefficient(curve.value(segment, scalar + step))
        f2 = l6_coefficient(curve.value(segment, scalar + 2.0 * step))
        return (-3.0 * f0 + 4.0 * f1 - f2) / (2.0 * step)
    f0 = l6_coefficient(curve.value(segment, scalar))
    f1 = l6_coefficient(curve.value(segment, scalar - step))
    f2 = l6_coefficient(curve.value(segment, scalar - 2.0 * step))
    return (3.0 * f0 - 4.0 * f1 + f2) / (2.0 * step)


def evaluate_point(
    curve: FrozenCurve,
    segment: int,
    scalar: float,
) -> dict[str, Any]:
    phases = curve.value(segment, scalar)
    tangent = curve.derivative(segment, scalar)
    response = response_feature(phases)
    jacobian = finite_difference_jacobian(
        response_feature, phases, RESPONSE_JACOBIAN_STEP
    )
    _, singular_values, vh = np.linalg.svd(jacobian, full_matrices=True)
    rank = int(np.sum(singular_values > 1.0e-9))

    # Under the frozen Euclidean metric the row space of J is normal to the
    # level set, so subtracting its V-basis component is the orthogonal
    # projection into ker(J).
    normal_basis = vh[:RESPONSE_DIMENSION, :]
    gradient = l6_gradient(phases, L6_GRADIENT_STEP)
    fibre_gradient = gradient - normal_basis.T @ (normal_basis @ gradient)
    negative_fibre_gradient = -fibre_gradient

    tangent_norm = float(np.linalg.norm(tangent))
    field_norm = float(np.linalg.norm(negative_fibre_gradient))
    jacobian_norm = float(singular_values[0])
    tangent_linear_residual = float(np.linalg.norm(jacobian @ tangent))
    tangent_relative_residual = tangent_linear_residual / max(
        jacobian_norm * tangent_norm, np.finfo(float).tiny
    )

    if field_norm > 0.0:
        oriented_lambda = float(
            np.dot(tangent, negative_fibre_gradient) / field_norm**2
        )
        alignment_cosine = float(
            np.dot(tangent, negative_fibre_gradient)
            / max(tangent_norm * field_norm, np.finfo(float).tiny)
        )
        parallel_residual = float(
            np.linalg.norm(
                tangent - oriented_lambda * negative_fibre_gradient
            )
            / max(tangent_norm, np.finfo(float).tiny)
        )
    else:
        oriented_lambda = float("nan")
        alignment_cosine = float("nan")
        parallel_residual = float("inf")

    dl6_ds = float(np.dot(gradient, tangent))
    crosscheck = curve_l6_derivative_crosscheck(
        curve,
        segment,
        scalar,
        CURVE_DERIVATIVE_CROSSCHECK_STEP,
    )
    crosscheck_relative_error = abs(dl6_ds - crosscheck) / max(
        abs(dl6_ds), abs(crosscheck), 1.0e-12
    )

    return {
        "segment": segment,
        "local_parameter": scalar,
        "global_parameter": segment + scalar,
        "response_gap": float(np.max(np.abs(response - TARGET_RESPONSE))),
        "response_rank": rank,
        "minimum_singular_value": float(singular_values[-1]),
        "condition_number": float(
            singular_values[0] / singular_values[-1]
        ),
        "curve_speed": tangent_norm,
        "tangent_linear_residual": tangent_linear_residual,
        "tangent_relative_residual": tangent_relative_residual,
        "projected_negative_gradient_norm": field_norm,
        "oriented_lambda": oriented_lambda,
        "alignment_cosine": alignment_cosine,
        "parallel_relative_residual": parallel_residual,
        "L6": l6_coefficient(phases),
        "dL6_ds_inner_product": dl6_ds,
        "dL6_ds_curve_crosscheck": crosscheck,
        "derivative_crosscheck_relative_error": crosscheck_relative_error,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parameterization")
    parser.add_argument(
        "--points-per-segment",
        type=int,
        default=17,
        help="Includes both endpoints of every segment (default: 17).",
    )
    parser.add_argument(
        "--output",
        default="response_fibre_geometric_flow_preflight_v0_1_results",
    )
    parser.add_argument(
        "--allow-unfrozen-input",
        action="store_true",
        help=(
            "Evaluate a parameterization whose canonical SHA-256 differs "
            "from the frozen v1.3.1 object. The status remains diagnostic."
        ),
    )
    args, ignored = parser.parse_known_args()
    if ignored:
        print(f"[notice] ignored notebook arguments: {ignored}")
    if args.points_per_segment < 5:
        raise ValueError("--points-per-segment must be at least 5")

    parameterization_path = find_parameterization(args.parameterization)
    parameterization = json.loads(
        parameterization_path.read_text(encoding="utf-8")
    )
    parameterization_hash = sha256_bytes(canonical_json(parameterization))
    frozen_input = (
        parameterization_hash == EXPECTED_PARAMETERIZATION_SHA256
    )
    if not frozen_input and not args.allow_unfrozen_input:
        raise RuntimeError(
            "The parameterization SHA-256 does not match the frozen v1.3.1 "
            f"object. Observed {parameterization_hash}; expected "
            f"{EXPECTED_PARAMETERIZATION_SHA256}. Use the correct file, or "
            "pass --allow-unfrozen-input for a diagnostic-only run."
        )

    protocol = {
        "title": TITLE,
        "version": VERSION,
        "formal_interval_arithmetic": False,
        "purpose": (
            "floating-point readiness test before a validated geometric-flow "
            "ODE/Taylor-model proof"
        ),
        "model": (
            "14-segment driven qubit with common quasi-static detuning"
        ),
        "metric": METRIC,
        "segments": 10,
        "points_per_segment": args.points_per_segment,
        "declared_points": 10 * args.points_per_segment,
        "parameterization_sha256": parameterization_hash,
        "expected_parameterization_sha256": (
            EXPECTED_PARAMETERIZATION_SHA256
        ),
        "frozen_v1_3_1_input": frozen_input,
        "response_jacobian_step": RESPONSE_JACOBIAN_STEP,
        "L6_gradient_step": L6_GRADIENT_STEP,
        "curve_derivative_crosscheck_step": (
            CURVE_DERIVATIVE_CROSSCHECK_STEP
        ),
        "gates": {
            "maximum_response_gap": RESPONSE_GAP_GATE,
            "maximum_tangent_relative_residual": (
                TANGENT_RELATIVE_RESIDUAL_GATE
            ),
            "minimum_response_singular_value": (
                MINIMUM_SINGULAR_VALUE_GATE
            ),
            "minimum_projected_gradient_norm": (
                MINIMUM_PROJECTED_GRADIENT_NORM_GATE
            ),
            "minimum_oriented_lambda": MINIMUM_ORIENTED_LAMBDA_GATE,
            "minimum_alignment_cosine": MINIMUM_ALIGNMENT_COSINE_GATE,
            "maximum_parallel_relative_residual": (
                MAXIMUM_PARALLEL_RELATIVE_RESIDUAL_GATE
            ),
            "maximum_dL6_ds": MAXIMUM_DL6_DS_GATE,
            "maximum_derivative_crosscheck_relative_error": (
                DERIVATIVE_CROSSCHECK_RELATIVE_GATE
            ),
        },
        "finite_error_outcomes_used": False,
        "uses_cloud_or_qpu": False,
        "uses_pasqal_credentials": False,
    }
    protocol_hash = sha256_bytes(canonical_json(protocol))

    banner(f"{TITLE} v{VERSION}")
    print("No PASQAL account, token, API key, project ID, cloud, or QPU is used.")
    print(json.dumps(protocol, indent=2))
    print(f"protocol_sha256 = {protocol_hash}")

    curve = FrozenCurve(parameterization)
    sample_scalars = np.linspace(0.0, 1.0, args.points_per_segment)
    records: list[dict[str, Any]] = []
    start = time.time()
    for segment in range(10):
        segment_records = []
        for scalar in sample_scalars:
            record = evaluate_point(curve, segment, float(scalar))
            records.append(record)
            segment_records.append(record)
        print(
            f"[segment {segment + 1:02d}/10] "
            f"response={max(x['response_gap'] for x in segment_records):.3e} "
            f"tan_rel={max(x['tangent_relative_residual'] for x in segment_records):.3e} "
            f"cos_min={min(x['alignment_cosine'] for x in segment_records):.6f} "
            f"parallel={max(x['parallel_relative_residual'] for x in segment_records):.3e} "
            f"dL6_max={max(x['dL6_ds_inner_product'] for x in segment_records):.3e}"
        )

    finite_records = all(
        all(
            math.isfinite(float(value))
            for key, value in record.items()
            if key not in {"segment"}
        )
        for record in records
    )
    maximum_response_gap = max(x["response_gap"] for x in records)
    maximum_tangent_relative_residual = max(
        x["tangent_relative_residual"] for x in records
    )
    minimum_singular_value = min(
        x["minimum_singular_value"] for x in records
    )
    minimum_projected_gradient_norm = min(
        x["projected_negative_gradient_norm"] for x in records
    )
    minimum_oriented_lambda = min(x["oriented_lambda"] for x in records)
    minimum_alignment_cosine = min(
        x["alignment_cosine"] for x in records
    )
    maximum_parallel_relative_residual = max(
        x["parallel_relative_residual"] for x in records
    )
    maximum_dl6_ds = max(x["dL6_ds_inner_product"] for x in records)
    maximum_crosscheck_error = max(
        x["derivative_crosscheck_relative_error"] for x in records
    )

    gates = {
        "finite_diagnostics": finite_records,
        "complete_sample_cohort": (
            len(records) == 10 * args.points_per_segment
        ),
        "frozen_v1_3_1_parameterization": frozen_input,
        "response_gap": maximum_response_gap < RESPONSE_GAP_GATE,
        "full_response_rank": all(
            x["response_rank"] == RESPONSE_DIMENSION for x in records
        ),
        "minimum_singular_value": (
            minimum_singular_value > MINIMUM_SINGULAR_VALUE_GATE
        ),
        "fibre_tangency": (
            maximum_tangent_relative_residual
            < TANGENT_RELATIVE_RESIDUAL_GATE
        ),
        "nonstationary_projected_gradient": (
            minimum_projected_gradient_norm
            > MINIMUM_PROJECTED_GRADIENT_NORM_GATE
        ),
        "positive_orientation": (
            minimum_oriented_lambda > MINIMUM_ORIENTED_LAMBDA_GATE
        ),
        "alignment_cosine": (
            minimum_alignment_cosine > MINIMUM_ALIGNMENT_COSINE_GATE
        ),
        "parallel_residual": (
            maximum_parallel_relative_residual
            < MAXIMUM_PARALLEL_RELATIVE_RESIDUAL_GATE
        ),
        "strict_sampled_L6_descent": maximum_dl6_ds < MAXIMUM_DL6_DS_GATE,
        "derivative_crosscheck": (
            maximum_crosscheck_error
            < DERIVATIVE_CROSSCHECK_RELATIVE_GATE
        ),
    }
    integrity_keys = {
        "finite_diagnostics",
        "complete_sample_cohort",
        "frozen_v1_3_1_parameterization",
        "response_gap",
        "full_response_rank",
        "minimum_singular_value",
        "fibre_tangency",
        "nonstationary_projected_gradient",
        "derivative_crosscheck",
    }
    alignment_keys = {
        "positive_orientation",
        "alignment_cosine",
        "parallel_residual",
    }
    integrity_pass = all(gates[key] for key in integrity_keys)
    alignment_pass = all(gates[key] for key in alignment_keys)
    descent_pass = gates["strict_sampled_L6_descent"]

    if not integrity_pass:
        status = "PARAMETERIZATION_INTEGRITY_FAILED"
    elif descent_pass and alignment_pass:
        status = "GRADIENT_FLOW_FORMAL_CERTIFICATION_READY"
    elif descent_pass:
        status = (
            "CONTINUOUS_DESCENT_FLOW_CANDIDATE_NOT_GRADIENT_ALIGNED"
        )
    else:
        status = "CURVE_RECONSTRUCTION_REQUIRED"
    if not frozen_input:
        status = "UNFROZEN_INPUT_DIAGNOSTIC_ONLY"

    report = {
        "scientific_status": status,
        "all_gates_pass": all(gates.values()),
        "formal_interval_arithmetic": False,
        "formal_gradient_flow_claimed": False,
        "sampled_continuous_descent_claimed": False,
        "gates": gates,
        "parameterization_sha256": parameterization_hash,
        "protocol_sha256": protocol_hash,
        "sample_points": len(records),
        "maximum_response_gap": maximum_response_gap,
        "maximum_tangent_relative_residual": (
            maximum_tangent_relative_residual
        ),
        "minimum_response_singular_value": minimum_singular_value,
        "minimum_projected_negative_gradient_norm": (
            minimum_projected_gradient_norm
        ),
        "minimum_oriented_lambda": minimum_oriented_lambda,
        "minimum_alignment_cosine": minimum_alignment_cosine,
        "maximum_parallel_relative_residual": (
            maximum_parallel_relative_residual
        ),
        "maximum_sampled_dL6_ds": maximum_dl6_ds,
        "maximum_derivative_crosscheck_relative_error": (
            maximum_crosscheck_error
        ),
        "elapsed_seconds": time.time() - start,
        "scope": (
            "floating-point sampled readiness diagnostic in the frozen "
            "Euclidean phase metric; not a validated ODE, interval, global "
            "fibre, holonomy, cloud, or QPU theorem"
        ),
    }

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    (output / "protocol.json").write_text(
        json.dumps(protocol, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    with (output / "point_diagnostics.csv").open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    provenance = {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "script_sha256": hashlib.sha256(
            Path(__file__).read_bytes()
        ).hexdigest() if "__file__" in globals() else None,
    }
    (output / "provenance.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    banner("FINAL RESULT")
    print(json.dumps(report, indent=2))
    print("\nInterpretation")
    if status == "GRADIENT_FLOW_FORMAL_CERTIFICATION_READY":
        print(
            "  PASS: the frozen centre curve is tangent to the response "
            "fibre, positively aligned with the projected negative L6 "
            "gradient, and strictly decreases L6 at every declared sample."
        )
        print(
            "  Next: construct a validated ODE/Taylor-model proof. This "
            "floating-point PASS is not itself an exact gradient-flow theorem."
        )
    elif status == (
        "CONTINUOUS_DESCENT_FLOW_CANDIDATE_NOT_GRADIENT_ALIGNED"
    ):
        print(
            "  PARTIAL: the curve is a sampled strict fibre-descent candidate "
            "but fails the predeclared gradient-alignment gate."
        )
        print(
            "  Certify it only as a descent flow, or reconstruct the curve by "
            "integrating the projected-gradient ODE before formal validation."
        )
    elif status == "CURVE_RECONSTRUCTION_REQUIRED":
        print(
            "  FAIL-CLOSED: sampled pointwise L6 descent does not hold over "
            "the complete curve. Reconstruct the curve from the projected "
            "negative-gradient vector field."
        )
    elif status == "UNFROZEN_INPUT_DIAGNOSTIC_ONLY":
        print(
            "  DIAGNOSTIC ONLY: the input hash is not the frozen v1.3.1 "
            "parameterization. No readiness conclusion is issued."
        )
    else:
        print(
            "  FAIL-CLOSED: response, rank, tangency, nonstationarity, or "
            "derivative-consistency integrity failed."
        )


if __name__ == "__main__":
    main()
