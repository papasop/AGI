#!/usr/bin/env python3
"""Outward-rounded Stage-A and frozen KKT-witness alignment audit.

v0.7.4 preserves the successful v0.7.0--v0.7.3 Stage-A proof.  Stage B freezes
one least-squares KKT witness (lambda, mu) at each child centre and encloses
the fourteen-dimensional residual g + lambda*gamma_dot - J^T*mu directly.

    w = grad L6 + lambda gamma_dot - DR3^T mu.

Since P DR3^T=0, ||P grad L6 + lambda P gamma_dot|| <= ||w||.  A separate
outward-rounded normal-tangent correction converts alignment with P gamma_dot
to alignment with gamma_dot.  No analytic complex square root is used in the
theorem-bearing Cauchy path.

The following statements are theorem-bearing for the serialized model and
the accepted scalar box:

* the response Jacobian has full row rank;
* the projected L6 gradient is nonzero;
* the serialized atlas curve is uniformly tangent to the response level up
  to the reported outward-rounded residual;
* dL6/dell has a strictly negative uniform interval upper bound; and
* the atlas derivative has the reported uniform residual from the normalized
  projected-negative-gradient field.

This is not yet a validated ODE existence/uniqueness theorem.  It certifies a
uniform local descent box on the serialized atlas, not a transverse
radii-polynomial tube or the complete ten-chart flow.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from typing import Any

import numpy as np


TITLE = "RESPONSE-FIBRE ARB KKT-WITNESS ALIGNMENT AUDIT"
VERSION = "0.7.4"
PRECISION_BITS = 192

EXPECTED_ATLAS_SHA256 = (
    "c02acc1c76e0b670793340150d1a875fdc373e0ac7c46d3360a7824b66a3a5ef"
)
EXPECTED_SOURCE_ATLAS_SHA256 = (
    "de5fd49e09dcb35121b8d17b0ade06caf6af596ad6ef0b455ec4520c4f845a15"
)
EXPECTED_SOURCE_CURVE_SHA256 = (
    "b63827b54311e895a2089610575601a5c79fa43d66ddd40f9cccfb1f37c9d670"
)
EXPECTED_PARAMETERIZATION_SHA256 = (
    "e8ad8a6fbcab626b726082b570f59df6854d4a28259177783e1f5e3274b1cb84"
)

OMEGA = 1.0
TAU = 0.62
CONTROL_DIMENSION = 14
RESPONSE_ORDER = 3
RESPONSE_DIMENSION = 8
DELTA_ORDER = 6
SUBDIVISIONS = 64

DEFAULT_CHART = 9
DEFAULT_SUBDIVISION = 32
BOX_HALF_WIDTH = 1.0 / SUBDIVISIONS
CHILD_BOXES = 16
CAUCHY_POINTS = 64
CAUCHY_ARCS = 64
CAUCHY_SAMPLE_RADIUS_MULTIPLIER = 2.0
CAUCHY_BOUND_RADIUS_MULTIPLIER = 3.0
TAYLOR_ORDER = 24

GATES = {
    "maximum_right_inverse_defect": 0.8,
    "minimum_projected_gradient_norm": 0.60,
    "maximum_response_tangency_norm": 1.0e-6,
    "maximum_parallel_relative_residual": 2.0e-4,
    "minimum_alignment_scale": 0.55,
    "maximum_dL6_dell": -0.55,
}

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


def ensure_flint() -> None:
    try:
        import flint  # noqa: F401
    except ImportError:
        print("[dependencies] installing python-flint==0.8.0")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q",
             "python-flint==0.8.0"],
            check=True,
        )


def script_directory() -> Path:
    value = globals().get("__file__")
    return Path(value).resolve().parent if value else Path.cwd().resolve()


def load_atlas(
    explicit_atlas: str | None, explicit_zip: str | None
) -> tuple[dict[str, Any], str]:
    roots = [Path.cwd(), script_directory(), Path("/content")]
    atlas_candidates = []
    if explicit_atlas:
        atlas_candidates.append(Path(explicit_atlas))
    for root in roots:
        atlas_candidates.extend(
            [
                root / "response_fibre_v0_6_2_backend_inputs"
                / "corrected_atlas.json",
                root / "corrected_atlas.json",
            ]
        )
    for candidate in atlas_candidates:
        if candidate.is_file():
            return json.loads(candidate.read_text(encoding="utf-8")), str(
                candidate.resolve()
            )

    zip_paths = []
    if explicit_zip:
        zip_paths.append(Path(explicit_zip))
    for root in roots:
        zip_paths.extend(
            [
                root / "response_fibre_v0_6_2_backend_inputs.zip",
                root / "response_fibre_v0_6_2_backend_inputs (1).zip",
                root / "response_fibre_v0_6_2_backend_inputs_1.zip",
            ]
        )
    for candidate in zip_paths:
        if not candidate.is_file():
            continue
        with zipfile.ZipFile(candidate) as archive:
            names = [
                name for name in archive.namelist()
                if name.endswith("/corrected_atlas.json")
                or name == "corrected_atlas.json"
            ]
            if len(names) != 1:
                raise RuntimeError(
                    f"{candidate} must contain exactly one corrected_atlas.json"
                )
            return json.loads(archive.read(names[0])), (
                f"{candidate.resolve()}::{names[0]}"
            )
    raise FileNotFoundError(
        "Upload response_fibre_v0_6_2_backend_inputs.zip beside this script "
        "or pass --atlas/--inputs-zip."
    )


def validate_atlas(atlas: dict[str, Any]) -> dict[str, bool]:
    return {
        "corrected_atlas_sha256": (
            sha256_bytes(canonical_json(atlas)) == EXPECTED_ATLAS_SHA256
        ),
        "source_atlas_sha256": (
            atlas.get("source_atlas_sha256") == EXPECTED_SOURCE_ATLAS_SHA256
        ),
        "source_curve_sha256": (
            atlas.get("source_curve_sha256") == EXPECTED_SOURCE_CURVE_SHA256
        ),
        "source_parameterization_sha256": (
            atlas.get("source_parameterization_sha256")
            == EXPECTED_PARAMETERIZATION_SHA256
        ),
        "chart_count": len(atlas.get("charts", [])) == 10,
    }


def midpoint_radius(value) -> tuple[float, float]:
    lo = float(value.lower())
    hi = float(value.upper())
    if not math.isfinite(lo) or not math.isfinite(hi):
        raise ArithmeticError("non-finite Arb enclosure")
    return 0.5 * (lo + hi), 0.5 * (hi - lo)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--atlas")
    parser.add_argument("--inputs-zip")
    parser.add_argument("--chart", type=int, default=DEFAULT_CHART)
    parser.add_argument(
        "--subdivision", type=int, default=DEFAULT_SUBDIVISION
    )
    parser.add_argument(
        "--output",
        default="response_fibre_arb_kkt_witness_v0_7_4_results",
    )
    args, ignored = parser.parse_known_args()
    if ignored:
        print(f"[notice] ignored notebook arguments: {ignored}")
    if not 0 <= args.chart < 10:
        raise ValueError("--chart must be between 0 and 9")
    if not 0 <= args.subdivision < SUBDIVISIONS:
        raise ValueError("--subdivision must be between 0 and 63")

    ensure_flint()
    from flint import acb, arb, ctx

    ctx.prec = PRECISION_BITS

    def ap(value):
        if isinstance(value, arb):
            return value
        if isinstance(value, (np.floating, np.integer)):
            value = value.item()
        return arb(repr(value) if isinstance(value, float) else str(value))

    def upper_point(value):
        if isinstance(value, acb):
            value = value.abs_upper()
        if isinstance(value, arb):
            return arb(str(value.abs_upper().upper()))
        return ap(math.nextafter(abs(float(value)), math.inf))

    def ball(mid, radius):
        midpoint = mid if isinstance(mid, arb) else ap(mid)
        radius_upper = upper_point(radius).upper()
        return midpoint + arb(0, str(radius_upper))

    def upper_float(value) -> float:
        return float(upper_point(value))

    I = acb(0, 1)

    class DeltaJet:
        order = DELTA_ORDER

        def __init__(self, coefficients=0):
            if isinstance(coefficients, DeltaJet):
                self.c = coefficients.c[:]
            elif isinstance(coefficients, (list, tuple)):
                self.c = [acb(item) for item in coefficients]
                self.c += [acb(0)] * (self.order + 1 - len(self.c))
            else:
                self.c = [acb(coefficients)] + [acb(0)] * self.order
            self.c = self.c[: self.order + 1]

        def __add__(self, other):
            other = DeltaJet(other)
            return DeltaJet(
                [self.c[k] + other.c[k] for k in range(self.order + 1)]
            )

        __radd__ = __add__

        def __neg__(self):
            return DeltaJet([-item for item in self.c])

        def __sub__(self, other):
            return self + (-DeltaJet(other))

        def __rsub__(self, other):
            return DeltaJet(other) - self

        def __mul__(self, other):
            other = DeltaJet(other)
            return DeltaJet(
                [
                    sum(
                        (self.c[k] * other.c[n - k]
                         for k in range(n + 1)),
                        acb(0),
                    )
                    for n in range(self.order + 1)
                ]
            )

        __rmul__ = __mul__

        def inv(self):
            if self.c[0].contains(0):
                raise ArithmeticError("DeltaJet centre contains zero")
            result = [1 / self.c[0]]
            for n in range(1, self.order + 1):
                result.append(
                    -result[0]
                    * sum(
                        (self.c[k] * result[n - k]
                         for k in range(1, n + 1)),
                        acb(0),
                    )
                )
            return DeltaJet(result)

        def __truediv__(self, other):
            return self * DeltaJet(other).inv()

        def __rtruediv__(self, other):
            return DeltaJet(other) / self

        def sqrt(self):
            result = [self.c[0].sqrt()]
            if result[0].contains(0):
                raise ArithmeticError("DeltaJet square-root centre contains zero")
            for n in range(1, self.order + 1):
                result.append(
                    (
                        self.c[n]
                        - sum(
                            (result[k] * result[n - k]
                             for k in range(1, n)),
                            acb(0),
                        )
                    )
                    / (2 * result[0])
                )
            return DeltaJet(result)

        def exp(self):
            result = [self.c[0].exp()]
            for n in range(1, self.order + 1):
                result.append(
                    sum(
                        (k * self.c[k] * result[n - k]
                         for k in range(1, n + 1)),
                        acb(0),
                    )
                    / n
                )
            return DeltaJet(result)

        def sin(self):
            value = self * I
            return (value.exp() - (-value).exp()) / (2 * I)

        def cos(self):
            value = self * I
            return (value.exp() + (-value).exp()) / 2

    def jet_matvec(matrix, vector):
        return [
            matrix[0][0] * vector[0] + matrix[0][1] * vector[1],
            matrix[1][0] * vector[0] + matrix[1][1] * vector[1],
        ]

    def nominal_state(phases):
        # Trigonometry is evaluated by Arb from the declared decimals.  No
        # binary64 sine/cosine value enters the theorem-bearing state.
        half_angle = ap(TAU) * ap(OMEGA) / 2
        cosine = acb(half_angle.cos())
        sine = acb(half_angle.sin() / ap(OMEGA))
        state = [acb(1), acb(0)]
        for phase_value in phases:
            phase = acb(phase_value)
            em = (-I * phase).exp()
            ep = (I * phase).exp()
            matrix = [
                [cosine, -I * sine * ap(OMEGA) * em],
                [-I * sine * ap(OMEGA) * ep, cosine],
            ]
            state = [
                matrix[0][0] * state[0] + matrix[0][1] * state[1],
                matrix[1][0] * state[0] + matrix[1][1] * state[1],
            ]
        return state

    target_state = nominal_state([ap(value) for value in REFERENCE_PHASES])
    target_norm = (
        target_state[0].conjugate() * target_state[0]
        + target_state[1].conjugate() * target_state[1]
    ).sqrt()
    target = [item / target_norm for item in target_state]
    orthogonal = [-target[1].conjugate(), target[0].conjugate()]

    def projective_jet_and_derivatives(phases, mirror=False):
        delta = DeltaJet([0, 1])
        radius = (1 + delta * delta).sqrt()
        half_duration = ap(TAU) / 2
        cosine = (radius * half_duration).cos()
        sine = (radius * half_duration).sin() / radius
        state = [DeltaJet(1), DeltaJet(0)]
        derivatives = [
            [DeltaJet(0), DeltaJet(0)]
            for _ in range(CONTROL_DIMENSION)
        ]

        for phase_index, phase_value in enumerate(phases):
            phase = acb(phase_value)
            em = (-I * phase).exp()
            ep = (I * phase).exp()
            if not mirror:
                matrix = [
                    [cosine - I * sine * delta, -I * sine * em],
                    [-I * sine * ep, cosine + I * sine * delta],
                ]
                derivative_matrix = [
                    [DeltaJet(0), -sine * em],
                    [sine * ep, DeltaJet(0)],
                ]
            else:
                matrix = [
                    [cosine + I * sine * delta, I * sine * ep],
                    [I * sine * em, cosine - I * sine * delta],
                ]
                derivative_matrix = [
                    [DeltaJet(0), -sine * ep],
                    [sine * em, DeltaJet(0)],
                ]

            old_state = state
            state = jet_matvec(matrix, old_state)
            updated = []
            for column in range(CONTROL_DIMENSION):
                value = jet_matvec(matrix, derivatives[column])
                if column == phase_index:
                    local = jet_matvec(derivative_matrix, old_state)
                    value = [value[0] + local[0], value[1] + local[1]]
                updated.append(value)
            derivatives = updated

        if not mirror:
            numerator_weights = [item.conjugate() for item in orthogonal]
            denominator_weights = [item.conjugate() for item in target]
        else:
            numerator_weights = orthogonal
            denominator_weights = target

        numerator = (
            DeltaJet(numerator_weights[0]) * state[0]
            + DeltaJet(numerator_weights[1]) * state[1]
        )
        denominator = (
            DeltaJet(denominator_weights[0]) * state[0]
            + DeltaJet(denominator_weights[1]) * state[1]
        )
        coordinate = numerator / denominator
        coordinate_derivatives = []
        for derivative in derivatives:
            dn = (
                DeltaJet(numerator_weights[0]) * derivative[0]
                + DeltaJet(numerator_weights[1]) * derivative[1]
            )
            dd = (
                DeltaJet(denominator_weights[0]) * derivative[0]
                + DeltaJet(denominator_weights[1]) * derivative[1]
            )
            coordinate_derivatives.append(
                (dn * denominator - numerator * dd)
                / (denominator * denominator)
            )
        return coordinate, coordinate_derivatives

    def response_jacobian_and_gradient(phases, analytic_output=False):
        z, dz = projective_jet_and_derivatives(phases, mirror=False)
        zbar, dzbar = projective_jet_and_derivatives(phases, mirror=True)
        jacobian = [
            [arb(0) for _ in range(CONTROL_DIMENSION)]
            for _ in range(RESPONSE_DIMENSION)
        ]
        for order in range(RESPONSE_ORDER + 1):
            for column in range(CONTROL_DIMENSION):
                real_extension = (
                    dz[column].c[order] + dzbar[column].c[order]
                ) / 2
                imaginary_extension = (
                    dz[column].c[order] - dzbar[column].c[order]
                ) / (2 * I)
                jacobian[order][column] = (
                    real_extension
                    if analytic_output else real_extension.real
                )
                jacobian[RESPONSE_ORDER + 1 + order][column] = (
                    imaginary_extension
                    if analytic_output else imaginary_extension.real
                )

        q = z * zbar
        denominator = 1 + q
        gradient = []
        for column in range(CONTROL_DIMENSION):
            dq = dz[column] * zbar + z * dzbar[column]
            derivative_loss = dq / (denominator * denominator)
            coefficient = derivative_loss.c[DELTA_ORDER]
            gradient.append(
                coefficient if analytic_output else coefficient.real
            )
        return jacobian, gradient

    def chebyshev_evaluate(coefficients, scalar):
        b1 = acb(0)
        b2 = acb(0)
        for coefficient in coefficients[:0:-1]:
            b0 = 2 * scalar * b1 - b2 + acb(ap(coefficient))
            b2, b1 = b1, b0
        return scalar * b1 - b2 + acb(ap(coefficients[0]))

    def chebyshev_derivative(coefficients):
        """Differentiate a Chebyshev series using Arb arithmetic only."""
        degree = len(coefficients) - 1
        if degree <= 0:
            return [arb(0)]
        if degree == 1:
            return [coefficients[1]]
        derivative = [arb(0) for _ in range(degree)]
        derivative[degree - 1] = 2 * degree * coefficients[degree]
        if degree >= 2:
            derivative[degree - 2] = (
                2 * (degree - 1) * coefficients[degree - 1]
            )
            for index in range(degree - 3, -1, -1):
                derivative[index] = (
                    derivative[index + 2]
                    + 2 * (index + 1) * coefficients[index + 1]
                )
            derivative[0] /= 2
        return derivative

    def phase_and_derivative_at(chart, local, analytic_output=False):
        serialized = chart["coefficients_degree_first"]
        coefficients = [
            [ap(serialized[degree][column]) for degree in range(len(serialized))]
            for column in range(CONTROL_DIMENSION)
        ]
        derivative_coefficients = [
            chebyshev_derivative(column) for column in coefficients
        ]
        phases = [
            chebyshev_evaluate(coefficients[column], local)
            for column in range(CONTROL_DIMENSION)
        ]
        chart_interval = chart["arclength_interval"]
        chart_length = ap(chart_interval[1]) - ap(chart_interval[0])
        analytic_derivatives = [
            (
                chebyshev_evaluate(
                    derivative_coefficients[column], local
                )
                * 2
                / chart_length
            )
            for column in range(CONTROL_DIMENSION)
        ]
        derivatives = (
            analytic_derivatives
            if analytic_output
            else [item.real for item in analytic_derivatives]
        )
        return phases, derivatives

    def phase_and_derivative(chart, local_center, local_radius):
        return phase_and_derivative_at(
            chart, acb(ball(local_center, local_radius))
        )

    def add_disk(value, radius):
        error = ball(0, radius)
        return value + acb(error, error)

    def analytic_invariants(chart, local):
        phases, curve_derivative = phase_and_derivative_at(
            chart, local, analytic_output=True
        )
        jacobian, gradient = response_jacobian_and_gradient(
            phases, analytic_output=True
        )
        gram = [
            [
                sum(
                    (
                        jacobian[row][column]
                        * jacobian[inner][column]
                        for column in range(CONTROL_DIMENSION)
                    ),
                    acb(0),
                )
                for inner in range(RESPONSE_DIMENSION)
            ]
            for row in range(RESPONSE_DIMENSION)
        ]
        jacobian_gradient = [
            sum(
                (
                    jacobian[row][column] * gradient[column]
                    for column in range(CONTROL_DIMENSION)
                ),
                acb(0),
            )
            for row in range(RESPONSE_DIMENSION)
        ]
        gradient_square = sum(
            (item * item for item in gradient), acb(0)
        )
        response_tangent = [
            sum(
                (
                    jacobian[row][column] * curve_derivative[column]
                    for column in range(CONTROL_DIMENSION)
                ),
                acb(0),
            )
            for row in range(RESPONSE_DIMENSION)
        ]
        loss_derivative = sum(
            (
                gradient[column] * curve_derivative[column]
                for column in range(CONTROL_DIMENSION)
            ),
            acb(0),
        )
        speed_square = sum(
            (item * item for item in curve_derivative), acb(0)
        )
        return (
            [item for row in gram for item in row]
            + jacobian_gradient
            + [gradient_square]
            + response_tangent
            + [loss_derivative, speed_square]
            + [item for row in jacobian for item in row]
            + gradient
            + curve_derivative
        )

    def unpack_raw_invariants(values):
        gram_end = RESPONSE_DIMENSION * RESPONSE_DIMENSION
        gram = [
            values[row * RESPONSE_DIMENSION:(row + 1) * RESPONSE_DIMENSION]
            for row in range(RESPONSE_DIMENSION)
        ]
        cursor = gram_end
        jacobian_gradient = values[cursor:cursor + RESPONSE_DIMENSION]
        cursor += RESPONSE_DIMENSION
        gradient_square = values[cursor]
        cursor += 1
        response_tangent = values[cursor:cursor + RESPONSE_DIMENSION]
        cursor += RESPONSE_DIMENSION
        loss_derivative = values[cursor]
        speed_square = values[cursor + 1]
        cursor += 2
        jacobian = [
            values[
                cursor + row * CONTROL_DIMENSION:
                cursor + (row + 1) * CONTROL_DIMENSION
            ]
            for row in range(RESPONSE_DIMENSION)
        ]
        cursor += RESPONSE_DIMENSION * CONTROL_DIMENSION
        gradient = values[cursor:cursor + CONTROL_DIMENSION]
        cursor += CONTROL_DIMENSION
        curve_derivative = values[cursor:cursor + CONTROL_DIMENSION]
        return {
            "gram": gram,
            "jacobian_gradient": jacobian_gradient,
            "gradient_square": gradient_square,
            "response_tangent": response_tangent,
            "loss_derivative": loss_derivative,
            "speed_square": speed_square,
            "jacobian": jacobian,
            "gradient": gradient,
            "curve_derivative": curve_derivative,
        }

    def preconditioned_invariants(
        chart,
        local,
        preconditioner,
        solution0,
        alignment_scale,
        normal_multiplier,
    ):
        raw = unpack_raw_invariants(analytic_invariants(chart, local))
        gram = raw["gram"]
        right = raw["jacobian_gradient"]
        defect = [
            [
                acb(int(row == column))
                - sum(
                    (
                        preconditioner[row][inner]
                        * gram[inner][column]
                        for inner in range(RESPONSE_DIMENSION)
                    ),
                    acb(0),
                )
                for column in range(RESPONSE_DIMENSION)
            ]
            for row in range(RESPONSE_DIMENSION)
        ]
        residual = [
            right[row]
            - sum(
                (
                    gram[row][column] * solution0[column]
                    for column in range(RESPONSE_DIMENSION)
                ),
                acb(0),
            )
            for row in range(RESPONSE_DIMENSION)
        ]
        preconditioned_residual = [
            sum(
                (
                    preconditioner[row][column] * residual[column]
                    for column in range(RESPONSE_DIMENSION)
                ),
                acb(0),
            )
            for row in range(RESPONSE_DIMENSION)
        ]
        tangent_projected0 = raw["loss_derivative"] - sum(
            (
                raw["response_tangent"][column] * solution0[column]
                for column in range(RESPONSE_DIMENSION)
            ),
            acb(0),
        )
        projected_square0 = raw["gradient_square"] - sum(
            (
                right[column] * solution0[column]
                for column in range(RESPONSE_DIMENSION)
            ),
            acb(0),
        )
        # Frozen KKT witness.  For real parameters,
        #   P w = P g + lambda P gamma_dot,
        # because P J^T=0.  The residual is formed before Cauchy extraction.
        witness_residual = [
            raw["gradient"][column]
            + alignment_scale * raw["curve_derivative"][column]
            - sum(
                (
                    raw["jacobian"][row][column] * normal_multiplier[row]
                    for row in range(RESPONSE_DIMENSION)
                ),
                acb(0),
            )
            for column in range(CONTROL_DIMENSION)
        ]
        witness_residual_square = sum(
            (item * item for item in witness_residual), acb(0)
        )
        gram_trace = sum(
            (gram[row][row] for row in range(RESPONSE_DIMENSION)),
            acb(0),
        )
        return (
            [item for row in defect for item in row]
            + preconditioned_residual
            + [projected_square0, tangent_projected0]
            + raw["response_tangent"]
            + right
            + [
                raw["loss_derivative"],
                raw["speed_square"],
                witness_residual_square,
                gram_trace,
            ]
        )

    def enclose_invariants(chart, center, half_width):
        """Enclose contracted scalar/matrix invariants on one full box."""
        half_width_ball = ap(half_width)
        sample_radius = (
            half_width_ball * ap(CAUCHY_SAMPLE_RADIUS_MULTIPLIER)
        )
        bound_radius = (
            half_width_ball * ap(CAUCHY_BOUND_RADIUS_MULTIPLIER)
        )
        if not half_width_ball < sample_radius < bound_radius:
            raise ValueError("Cauchy radii must exceed the real box half-width")

        center_raw = unpack_raw_invariants(
            analytic_invariants(chart, acb(ap(center)))
        )
        gram_midpoint = np.asarray(
            [
                [
                    midpoint_radius(center_raw["gram"][row][column].real)[0]
                    for column in range(RESPONSE_DIMENSION)
                ]
                for row in range(RESPONSE_DIMENSION)
            ],
            dtype=float,
        )
        right_midpoint = np.asarray(
            [
                midpoint_radius(item.real)[0]
                for item in center_raw["jacobian_gradient"]
            ],
            dtype=float,
        )
        singular_values = np.linalg.svd(gram_midpoint, compute_uv=False)
        inverse_float = np.linalg.inv(gram_midpoint)
        preconditioner = [
            [
                ap(float(inverse_float[row, column]))
                for column in range(RESPONSE_DIMENSION)
            ]
            for row in range(RESPONSE_DIMENSION)
        ]
        solution0_float = inverse_float @ right_midpoint
        solution0 = [ap(float(item)) for item in solution0_float]
        jacobian_midpoint = np.asarray(
            [
                [
                    midpoint_radius(
                        center_raw["jacobian"][row][column].real
                    )[0]
                    for column in range(CONTROL_DIMENSION)
                ]
                for row in range(RESPONSE_DIMENSION)
            ],
            dtype=float,
        )
        gradient_midpoint = np.asarray(
            [
                midpoint_radius(item.real)[0]
                for item in center_raw["gradient"]
            ],
            dtype=float,
        )
        tangent_midpoint = np.asarray(
            [
                midpoint_radius(item.real)[0]
                for item in center_raw["curve_derivative"]
            ],
            dtype=float,
        )
        witness_matrix = np.column_stack(
            (tangent_midpoint, -jacobian_midpoint.T)
        )
        witness_float, _, witness_rank, witness_singular_values = (
            np.linalg.lstsq(witness_matrix, -gradient_midpoint, rcond=None)
        )
        if witness_rank != RESPONSE_DIMENSION + 1:
            raise ArithmeticError("centre KKT witness matrix lacks rank nine")
        alignment_scale_float = float(witness_float[0])
        normal_multiplier_float = np.asarray(witness_float[1:], dtype=float)
        alignment_scale = ap(alignment_scale_float)
        normal_multiplier = [
            ap(float(item)) for item in normal_multiplier_float
        ]
        witness_center_residual = (
            gradient_midpoint
            + alignment_scale_float * tangent_midpoint
            - jacobian_midpoint.T @ normal_multiplier_float
        )
        preconditioner_inf_norm = float(
            np.max(np.sum(np.abs(inverse_float), axis=1))
        )

        # A rectangular complex enclosure containing the Cauchy disk proves
        # that every projective and loss denominator used below excludes zero
        # throughout the disk, not merely at the sampled boundary points.
        complex_disk = acb(
            ball(center, bound_radius), ball(0, bound_radius)
        )
        disk_phases, _ = phase_and_derivative_at(
            chart, complex_disk, analytic_output=True
        )
        response_jacobian_and_gradient(
            disk_phases, analytic_output=True
        )
        # Stage A intentionally contains no square root.  This call verifies
        # only the analytic Hamiltonian/projective denominators on the large
        # Cauchy domain.
        preconditioned_invariants(
            chart,
            complex_disk,
            preconditioner,
            solution0,
            alignment_scale,
            normal_multiplier,
        )

        pi_ball = arb.pi()
        roots = []
        samples = []
        for sample_index in range(CAUCHY_POINTS):
            angle = 2 * pi_ball * sample_index / CAUCHY_POINTS
            root = acb(angle.cos(), angle.sin())
            roots.append(root)
            local = acb(ap(center)) + sample_radius * root
            samples.append(
                preconditioned_invariants(
                    chart,
                    local,
                    preconditioner,
                    solution0,
                    alignment_scale,
                    normal_multiplier,
                )
            )

        output_count = (
            RESPONSE_DIMENSION * RESPONSE_DIMENSION
            + RESPONSE_DIMENSION
            + 2
            + RESPONSE_DIMENSION
            + RESPONSE_DIMENSION
            + 4
        )
        boundary_bounds = [arb(0) for _ in range(output_count)]
        angular_half_width = pi_ball / CAUCHY_ARCS
        for arc_index in range(CAUCHY_ARCS):
            angle = ball(
                pi_ball * (2 * arc_index + 1) / CAUCHY_ARCS,
                angular_half_width,
            )
            root = acb(angle.cos(), angle.sin())
            local = acb(ap(center)) + bound_radius * root
            values = preconditioned_invariants(
                chart,
                local,
                preconditioner,
                solution0,
                alignment_scale,
                normal_multiplier,
            )
            for index, value in enumerate(values):
                candidate = upper_point(value)
                if candidate > boundary_bounds[index]:
                    boundary_bounds[index] = candidate

        radius_ratio = sample_radius / bound_radius
        alias_factor = (
            radius_ratio**CAUCHY_POINTS
            / (1 - radius_ratio**CAUCHY_POINTS)
        )
        local_variable = acb(ball(0, half_width_ball))
        enclosed = []
        maximum_tail = arb(0)
        for output_index in range(output_count):
            coefficients = []
            for order in range(TAYLOR_ORDER + 1):
                total = sum(
                    (
                        samples[sample_index][output_index]
                        * roots[sample_index].conjugate() ** order
                        for sample_index in range(CAUCHY_POINTS)
                    ),
                    acb(0),
                )
                coefficient = total / (
                    CAUCHY_POINTS * sample_radius**order
                )
                coefficient = add_disk(
                    coefficient,
                    boundary_bounds[output_index]
                    / bound_radius**order
                    * alias_factor,
                )
                coefficients.append(coefficient)
            value = coefficients[-1]
            for coefficient in coefficients[-2::-1]:
                value = value * local_variable + coefficient
            tail = (
                boundary_bounds[output_index]
                / bound_radius ** (TAYLOR_ORDER + 1)
                * half_width_ball ** (TAYLOR_ORDER + 1)
                / (1 - half_width_ball / bound_radius)
            )
            if tail > maximum_tail:
                maximum_tail = tail
            enclosed.append(add_disk(value, tail).real)

        defect_end = RESPONSE_DIMENSION * RESPONSE_DIMENSION
        defect = [
            enclosed[row * RESPONSE_DIMENSION:(row + 1) * RESPONSE_DIMENSION]
            for row in range(RESPONSE_DIMENSION)
        ]
        cursor = defect_end
        preconditioned_residual = enclosed[cursor:cursor + RESPONSE_DIMENSION]
        cursor += RESPONSE_DIMENSION
        projected_square0 = enclosed[cursor]
        cursor += 1
        tangent_projected0 = enclosed[cursor]
        cursor += 1
        response_tangent = enclosed[cursor:cursor + RESPONSE_DIMENSION]
        cursor += RESPONSE_DIMENSION
        jacobian_gradient = enclosed[cursor:cursor + RESPONSE_DIMENSION]
        cursor += RESPONSE_DIMENSION
        loss_derivative = enclosed[cursor]
        speed_square = enclosed[cursor + 1]
        witness_residual_square = enclosed[cursor + 2]
        gram_trace = enclosed[cursor + 3]
        return {
            "defect": defect,
            "preconditioned_residual": preconditioned_residual,
            "projected_square0": projected_square0,
            "tangent_projected0": tangent_projected0,
            "jacobian_gradient": jacobian_gradient,
            "response_tangent": response_tangent,
            "loss_derivative": loss_derivative,
            "speed_square": speed_square,
            "witness_residual_square": witness_residual_square,
            "gram_trace": gram_trace,
            "maximum_tail": maximum_tail,
            "center_gram_minimum_singular_value": float(
                singular_values[-1]
            ),
            "center_solution0": [float(item) for item in solution0_float],
            "alignment_scale": alignment_scale_float,
            "normal_multiplier": [
                float(item) for item in normal_multiplier_float
            ],
            "witness_center_residual_norm": float(
                np.linalg.norm(witness_center_residual)
            ),
            "witness_matrix_minimum_singular_value": float(
                witness_singular_values[-1]
            ),
            "preconditioner_inf_norm": preconditioner_inf_norm,
        }

    def matrix_vector(matrix, vector):
        return [
            sum(
                (matrix[row][column] * vector[column]
                 for column in range(len(vector))),
                arb(0),
            )
            for row in range(len(matrix))
        ]

    def matrix_product(left, right):
        rows = len(left)
        inner = len(right)
        columns = len(right[0])
        return [
            [
                sum(
                    (left[row][k] * right[k][column]
                     for k in range(inner)),
                    arb(0),
                )
                for column in range(columns)
            ]
            for row in range(rows)
        ]

    def transpose(matrix):
        return [list(column) for column in zip(*matrix)]

    def vector_norm_upper(vector):
        square = sum(
            (upper_point(item) ** 2 for item in vector), arb(0)
        )
        return square.sqrt()

    def audit_box(chart, center, radius_value):
        invariants = enclose_invariants(chart, center, radius_value)
        defect = invariants["defect"]
        preconditioned_residual = invariants["preconditioned_residual"]
        projected_square0 = invariants["projected_square0"]
        tangent_projected0 = invariants["tangent_projected0"]
        witness_residual_square = invariants["witness_residual_square"]
        gram_trace = invariants["gram_trace"]
        jacobian_gradient = invariants["jacobian_gradient"]
        response_tangent = invariants["response_tangent"]
        dL6 = invariants["loss_derivative"]
        speed_square = invariants["speed_square"]
        maximum_taylor_tail = invariants["maximum_tail"]
        alignment_scale = ap(invariants["alignment_scale"])
        response_tangency_upper = vector_norm_upper(response_tangent)

        defect_rows = [
            sum((upper_point(item) for item in row), arb(0))
            for row in defect
        ]
        defect_bound = max(defect_rows)
        rank_pass = defect_bound < ap(GATES["maximum_right_inverse_defect"])

        if rank_pass:
            numerator = max(
                (upper_point(item) for item in preconditioned_residual),
                default=arb(0),
            )
            full_correction_radius = numerator / (1 - defect_bound)
            right_l1 = sum(
                (upper_point(item) for item in jacobian_gradient), arb(0)
            )
            tangent_l1 = sum(
                (upper_point(item) for item in response_tangent), arb(0)
            )
            projected_square_uncertainty = (
                right_l1 * full_correction_radius
            )
            stage_a_tangent_uncertainty = (
                tangent_l1 * full_correction_radius
            )
            projected_square = projected_square0 + ball(
                0, projected_square_uncertainty
            )
            # Preserve the successful v0.7.0/v0.7.2 Stage-A argument.
            tangent_projected_gradient = tangent_projected0 + ball(
                0, stage_a_tangent_uncertainty
            )
            speed_positive = speed_square > arb(0)
            orientation_pass = tangent_projected_gradient < arb(0)
            if speed_positive and orientation_pass:
                minus_pairing_lower = -arb(
                    str(tangent_projected_gradient.upper())
                )
                speed_upper_point = arb(str(speed_square.upper()))
                projected_norm_lower_ball = (
                    minus_pairing_lower / speed_upper_point.sqrt()
                )
                projected_norm_lower = float(projected_norm_lower_ball)
                pgrad_pass = (
                    projected_norm_lower_ball
                    > ap(GATES["minimum_projected_gradient_norm"])
                )
            else:
                projected_norm_lower_ball = arb(0)
                projected_norm_lower = 0.0
                pgrad_pass = False

            # Stage B: ||P(g + lambda*d - J^T*mu)|| <= ||witness||.
            # The final term converts P*d alignment to d alignment.  From
            # E=I-RG, ||G^-1||_inf <= ||R||_inf/(1-||E||_inf), while
            # ||J^T||_2 <= sqrt(trace(G)).
            gram_trace_upper = max(arb(0), upper_point(gram_trace))
            gram_inverse_two_norm_upper = (
                ap(RESPONSE_DIMENSION).sqrt()
                * ap(invariants["preconditioner_inf_norm"])
                / (1 - defect_bound)
            )
            tangent_normal_norm_upper = (
                gram_trace_upper.sqrt()
                * gram_inverse_two_norm_upper
                * response_tangency_upper
            )
            witness_square_upper = max(
                arb(0), arb(str(witness_residual_square.upper()))
            )
            witness_residual_norm_upper = witness_square_upper.sqrt()
            parallel_residual_norm_upper = (
                witness_residual_norm_upper
                + upper_point(alignment_scale) * tangent_normal_norm_upper
            )
            alignment_scale_pass = (
                alignment_scale > ap(GATES["minimum_alignment_scale"])
            )
            if pgrad_pass and alignment_scale_pass:
                parallel_relative_residual = (
                    parallel_residual_norm_upper
                    / projected_norm_lower_ball
                )
                alignment_pass = (
                    parallel_relative_residual
                    < ap(GATES["maximum_parallel_relative_residual"])
                )
            else:
                parallel_relative_residual = None
                alignment_pass = False
        else:
            full_correction_radius = None
            projected_square_uncertainty = None
            stage_a_tangent_uncertainty = None
            projected_square = arb(0)
            tangent_projected_gradient = None
            projected_norm_lower = 0.0
            pgrad_pass = False
            speed_positive = False
            orientation_pass = False
            gram_inverse_two_norm_upper = None
            tangent_normal_norm_upper = None
            witness_residual_norm_upper = None
            parallel_residual_norm_upper = None
            parallel_relative_residual = None
            alignment_scale_pass = False
            alignment_pass = False
        response_tangency_pass = (
            response_tangency_upper
            < ap(GATES["maximum_response_tangency_norm"])
        )

        descent_pass = dL6 < ap(GATES["maximum_dL6_dell"])

        stage_a_computed_values = [
            upper_float(defect_bound),
            projected_norm_lower,
            upper_float(response_tangency_upper),
            float(dL6.lower()),
            float(dL6.upper()),
            float(speed_square.lower()),
            float(speed_square.upper()),
            float(tangent_projected0.lower()),
            float(tangent_projected0.upper()),
        ]
        stage_a_finite = all(
            math.isfinite(value) for value in stage_a_computed_values
        )
        stage_b_computed_values = [
            float(witness_residual_square.lower()),
            float(witness_residual_square.upper()),
            float(gram_trace.lower()),
            float(gram_trace.upper()),
            float(alignment_scale),
        ]
        if parallel_relative_residual is not None:
            stage_b_computed_values.append(
                upper_float(parallel_relative_residual)
            )
        stage_b_finite = all(
            math.isfinite(value) for value in stage_b_computed_values
        )
        resolved = bool(rank_pass and pgrad_pass)
        stage_a_gates = {
            "all_stage_a_enclosures_finite": bool(stage_a_finite),
            "all_required_invariants_resolved": resolved,
            "formal_response_rank": bool(rank_pass),
            "negative_projected_pairing": bool(orientation_pass),
            "positive_curve_speed": bool(speed_positive),
            "projected_gradient_nonstationary": bool(pgrad_pass),
            "response_tangency": bool(response_tangency_pass),
            "strict_uniform_L6_descent": bool(descent_pass),
        }
        stage_b_gates = {
            "all_stage_b_witness_enclosures_finite": bool(stage_b_finite),
            "positive_alignment_scale": bool(alignment_scale_pass),
            "kkt_witness_parallel_residual": bool(alignment_pass),
        }
        gates = {**stage_a_gates, **stage_b_gates}
        stage_a_pass = all(stage_a_gates.values())
        stage_b_pass = stage_a_pass and all(stage_b_gates.values())
        return {
            "box_half_width": radius_value,
            "pass": bool(stage_b_pass),
            "stage_a_pass": bool(stage_a_pass),
            "stage_b_pass": bool(stage_b_pass),
            "gates": gates,
            "right_inverse_defect_upper": upper_float(defect_bound),
            "gram_midpoint_minimum_eigenvalue": float(
                invariants["center_gram_minimum_singular_value"]
            ),
            "solve_correction_radius_upper": (
                upper_float(full_correction_radius)
                if full_correction_radius is not None
                else None
            ),
            "projected_gradient_norm_lower": projected_norm_lower,
            "projected_square_base_lower": float(
                projected_square0.lower()
            ),
            "projected_square_base_upper": float(
                projected_square0.upper()
            ),
            "projected_square_full_solve_uncertainty_upper": (
                upper_float(projected_square_uncertainty)
                if projected_square_uncertainty is not None
                else None
            ),
            "projected_gradient_square_lower": float(
                projected_square.lower()
            ),
            "projected_gradient_square_upper": float(
                projected_square.upper()
            ),
            "response_tangency_norm_upper": upper_float(
                response_tangency_upper
            ),
            "dL6_dell_lower": float(dL6.lower()),
            "dL6_dell_upper": float(dL6.upper()),
            "witness_residual_square_lower": float(
                witness_residual_square.lower()
            ),
            "witness_residual_square_upper": float(
                witness_residual_square.upper()
            ),
            "witness_residual_norm_upper": (
                upper_float(witness_residual_norm_upper)
                if witness_residual_norm_upper is not None else None
            ),
            "tangent_normal_norm_upper": (
                upper_float(tangent_normal_norm_upper)
                if tangent_normal_norm_upper is not None else None
            ),
            "parallel_residual_norm_upper": (
                upper_float(parallel_residual_norm_upper)
                if parallel_residual_norm_upper is not None else None
            ),
            "parallel_relative_residual_upper": (
                upper_float(parallel_relative_residual)
                if parallel_relative_residual is not None else None
            ),
            "alignment_cosine_lower": (
                max(
                    0.0,
                    math.sqrt(max(
                        0.0,
                        1.0 - upper_float(
                            parallel_relative_residual
                        ) ** 2,
                    )),
                )
                if parallel_relative_residual is not None else None
            ),
            "tangent_projected_gradient_lower": (
                float(tangent_projected_gradient.lower())
                if tangent_projected_gradient is not None
                else None
            ),
            "tangent_projected_gradient_upper": (
                float(tangent_projected_gradient.upper())
                if tangent_projected_gradient is not None
                else None
            ),
            "frozen_tangent_projected_base_lower": float(
                tangent_projected0.lower()
            ),
            "frozen_tangent_projected_base_upper": float(
                tangent_projected0.upper()
            ),
            "stage_a_tangent_full_solve_uncertainty_upper": (
                upper_float(stage_a_tangent_uncertainty)
                if stage_a_tangent_uncertainty is not None
                else None
            ),
            "response_gram_trace_lower": float(gram_trace.lower()),
            "response_gram_trace_upper": float(gram_trace.upper()),
            "alignment_scale": float(alignment_scale),
            "normal_multiplier": invariants["normal_multiplier"],
            "witness_center_residual_norm": invariants[
                "witness_center_residual_norm"
            ],
            "witness_matrix_minimum_singular_value": invariants[
                "witness_matrix_minimum_singular_value"
            ],
            "gram_inverse_two_norm_upper": (
                upper_float(gram_inverse_two_norm_upper)
                if gram_inverse_two_norm_upper is not None else None
            ),
            "center_solution0": invariants["center_solution0"],
            "curve_speed_square_lower": float(speed_square.lower()),
            "curve_speed_square_upper": float(speed_square.upper()),
            "maximum_cauchy_taylor_tail_upper": upper_float(
                maximum_taylor_tail
            ),
        }

    atlas, atlas_source = load_atlas(args.atlas, args.inputs_zip)
    integrity = validate_atlas(atlas)
    if not all(integrity.values()):
        raise RuntimeError(f"frozen atlas integrity failed: {integrity}")

    chart = atlas["charts"][args.chart]
    macro_left = -1.0 + 2.0 * args.subdivision / SUBDIVISIONS
    macro_right = -1.0 + 2.0 * (args.subdivision + 1) / SUBDIVISIONS
    local_center = 0.5 * (macro_left + macro_right)
    child_half_width = BOX_HALF_WIDTH / CHILD_BOXES
    child_centers = [
        macro_left + (2 * index + 1) * child_half_width
        for index in range(CHILD_BOXES)
    ]
    child_intervals = [
        [
            macro_left + 2 * index * child_half_width,
            macro_left + 2 * (index + 1) * child_half_width,
        ]
        for index in range(CHILD_BOXES)
    ]

    protocol = {
        "title": TITLE,
        "version": VERSION,
        "formal_interval_arithmetic": True,
        "arb_precision_bits": PRECISION_BITS,
        "purpose": (
            "certify response rank, tangent descent, projected-gradient "
            "nonstationarity with the preserved frozen-solve proof, and "
            "certify frozen KKT-witness alignment on one complete 1/64 "
            "scalar box via sixteen exact subboxes"
        ),
        "model": "14-segment driven qubit with common quasi-static detuning",
        "metric": "Euclidean metric in the fourteen phase coordinates",
        "vector_field": (
            "unit-normalized negative Euclidean projection of grad(L6) "
            "onto ker(DR3)"
        ),
        "source_corrected_atlas_sha256": EXPECTED_ATLAS_SHA256,
        "chart": args.chart,
        "subdivision": args.subdivision,
        "macro_interval": [macro_left, macro_right],
        "box_center": local_center,
        "box_half_width": BOX_HALF_WIDTH,
        "child_boxes": CHILD_BOXES,
        "child_box_half_width": child_half_width,
        "child_parameter_intervals": child_intervals,
        "cauchy_points": CAUCHY_POINTS,
        "cauchy_arcs": CAUCHY_ARCS,
        "cauchy_sample_radius_multiplier": CAUCHY_SAMPLE_RADIUS_MULTIPLIER,
        "cauchy_bound_radius_multiplier": CAUCHY_BOUND_RADIUS_MULTIPLIER,
        "taylor_order": TAYLOR_ORDER,
        "dependency_method": (
            "Stage A forms the oriented pairing with the frozen midpoint "
            "solve and propagates the complete exact solve correction; "
            "Stage B freezes a centre least-squares witness (lambda,mu), "
            "forms g+lambda*gamma_dot-J^T*mu before Cauchy extraction, and "
            "adds a formal correction for the response-normal component of "
            "gamma_dot"
        ),
        "gates": GATES,
        "validated_ODE_claimed": False,
        "global_flow_claimed": False,
        "finite_error_outcomes_used": False,
        "uses_cloud_or_qpu": False,
        "uses_pasqal_credentials": False,
    }
    protocol_hash = sha256_bytes(canonical_json(protocol))

    banner(f"{TITLE} v{VERSION}")
    print("No PASQAL account, token, API key, project ID, cloud, or QPU is used.")
    print(json.dumps(protocol, indent=2))
    print(f"protocol_sha256 = {protocol_hash}")
    print(f"atlas_source = {atlas_source}")

    banner(
        "STAGE A FROZEN-SOLVE DESCENT / "
        "STAGE B FROZEN KKT-WITNESS ALIGNMENT"
    )
    started = time.time()
    records = []
    for child_index, child_center in enumerate(child_centers):
        try:
            record = audit_box(chart, child_center, child_half_width)
        except Exception as exc:
            record = {
                "box_half_width": child_half_width,
                "pass": False,
                "error": f"{type(exc).__name__}: {exc}",
                "gates": {"all_computed_enclosures_finite": False},
            }
        record["child_index"] = child_index
        record["parameter_interval"] = child_intervals[child_index]
        records.append(record)
        if "error" in record:
            print(
                f"[child {child_index + 1:02d}/{CHILD_BOXES:02d}] "
                f"pass=False ERROR {record['error']}"
            )
        else:
            residual_text = (
                f"{record['parallel_relative_residual_upper']:.3e}"
                if record["parallel_relative_residual_upper"] is not None
                else "unresolved"
            )
            print(
                f"[child {child_index + 1:02d}/{CHILD_BOXES:02d}] "
                f"A={record['stage_a_pass']} B={record['stage_b_pass']} "
                f"defect={record['right_inverse_defect_upper']:.3e} "
                f"|Pgrad|_lo={record['projected_gradient_norm_lower']:.6f} "
                f"tan={record['response_tangency_norm_upper']:.3e} "
                f"parallel_rel={residual_text} "
                f"dL6_hi={record['dL6_dell_upper']:.6f}"
            )

    stage_a_certified = len(records) == CHILD_BOXES and all(
        record.get("stage_a_pass", False) for record in records
    )
    stage_b_certified = stage_a_certified and all(
        record.get("pass", False) for record in records
    )
    rank_cover_certified = len(records) == CHILD_BOXES and all(
        record.get("gates", {}).get("formal_response_rank", False)
        for record in records
    )
    tangency_cover_certified = len(records) == CHILD_BOXES and all(
        record.get("gates", {}).get("response_tangency", False)
        for record in records
    )
    descent_cover_certified = len(records) == CHILD_BOXES and all(
        record.get("gates", {}).get("strict_uniform_L6_descent", False)
        for record in records
    )
    orientation_cover_certified = len(records) == CHILD_BOXES and all(
        record.get("gates", {}).get("negative_projected_pairing", False)
        for record in records
    )
    nonstationary_cover_certified = len(records) == CHILD_BOXES and all(
        record.get("gates", {}).get(
            "projected_gradient_nonstationary", False
        )
        for record in records
    )
    if stage_b_certified:
        status = (
            "FORMAL_ARB_KKT_WITNESS_ALIGNMENT_"
            "PARENT_BOX_CERTIFIED"
        )
    elif stage_a_certified:
        status = (
            "FORMAL_ARB_ORIENTED_DESCENT_CERTIFIED_"
            "ALIGNMENT_INCONCLUSIVE"
        )
    else:
        status = (
            "FORMAL_ARB_KKT_WITNESS_ALIGNMENT_"
            "PARENT_BOX_INCONCLUSIVE"
        )
    report = {
        "scientific_status": status,
        "all_gates_pass": bool(stage_b_certified),
        "formal_interval_arithmetic": True,
        "arb_precision_bits": PRECISION_BITS,
        "validated_ODE_claimed": False,
        "stage_a_rank_descent_cover_certified": bool(stage_a_certified),
        "formal_response_rank_cover_certified": bool(rank_cover_certified),
        "formal_response_tangency_cover_certified": bool(
            tangency_cover_certified
        ),
        "formal_negative_projected_pairing_cover_certified": bool(
            orientation_cover_certified
        ),
        "formal_projected_gradient_nonstationary_cover_certified": bool(
            nonstationary_cover_certified
        ),
        "kkt_witness_alignment_cover_certified": bool(
            stage_b_certified
        ),
        "uniform_single_box_L6_descent_certified": bool(
            descent_cover_certified
        ),
        "formal_single_box_projected_gradient_alignment_certified": bool(
            stage_b_certified
        ),
        "global_flow_claimed": False,
        "protocol_sha256": protocol_hash,
        "corrected_atlas_sha256": EXPECTED_ATLAS_SHA256,
        "input_integrity": integrity,
        "chart": args.chart,
        "subdivision": args.subdivision,
        "box_center": local_center,
        "box_half_width": BOX_HALF_WIDTH,
        "cover_is_exact_and_contiguous": True,
        "child_boxes_declared": CHILD_BOXES,
        "child_boxes_tested": len(records),
        "child_boxes_passing": sum(
            record.get("pass", False) for record in records
        ),
        "child_boxes_passing_stage_a": sum(
            record.get("stage_a_pass", False) for record in records
        ),
        "child_boxes_passing_stage_b": sum(
            record.get("stage_b_pass", False) for record in records
        ),
        "maximum_right_inverse_defect_upper": max(
            (
                record.get("right_inverse_defect_upper", float("inf"))
                for record in records
            ),
            default=float("inf"),
        ),
        "minimum_projected_gradient_norm_lower": min(
            (
                record.get("projected_gradient_norm_lower", 0.0)
                for record in records
            ),
            default=0.0,
        ),
        "minimum_alignment_scale": min(
            (
                record.get("alignment_scale", 0.0)
                for record in records
            ),
            default=0.0,
        ),
        "maximum_response_tangency_norm_upper": max(
            (
                record.get("response_tangency_norm_upper", float("inf"))
                for record in records
            ),
            default=float("inf"),
        ),
        "maximum_parallel_relative_residual_upper": max(
            (
                record.get("parallel_relative_residual_upper")
                if record.get("parallel_relative_residual_upper") is not None
                else float("inf")
                for record in records
            ),
            default=float("inf"),
        ),
        "maximum_dL6_dell_upper": max(
            (record.get("dL6_dell_upper", float("inf")) for record in records),
            default=float("inf"),
        ),
        "minimum_alignment_cosine_lower": min(
            (
                record.get("alignment_cosine_lower", 0.0)
                if record.get("alignment_cosine_lower") is not None
                else 0.0
                for record in records
            ),
            default=0.0,
        ),
        "elapsed_seconds": time.time() - started,
        "next_required_step": (
            "If the KKT-witness gate passes on all sixteen children, "
            "run the ten-chart screen before the full cohort. If only Stage A "
            "passes, preserve its theorem and refine only the witness "
            "subdivision or allow a low-degree lambda/mu Taylor witness."
        ),
        "scope": (
            "formal outward-rounded bounds for rank, oriented projected-gradient "
            "nonstationarity, response tangency, strict L6 descent and the "
            "frozen KKT-witness parallel residual on one serialized 1/64 box; "
            "not validated ODE "
            "existence, a "
            "complete ten-chart flow, global fibre, holonomy, cloud, or QPU"
        ),
    }

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    (output / "protocol.json").write_text(
        json.dumps(protocol, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    certificate = {
        "protocol": protocol,
        "input_integrity": integrity,
        "child_box_records": records,
        "report": report,
        "versions": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "python_flint": "0.8.0",
        },
    }
    certificate_bytes = (
        json.dumps(certificate, indent=2, sort_keys=True).encode("utf-8")
        + b"\n"
    )
    (output / "certificate.json").write_bytes(certificate_bytes)
    report["certificate_sha256"] = sha256_bytes(certificate_bytes)
    (output / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    banner("FINAL RESULT")
    print(json.dumps(report, indent=2))
    print("\nInterpretation")
    if stage_b_certified:
        print(
            "  KKT-WITNESS ALIGNMENT PASS: one complete 1/64 scalar "
            "box has formal "
            "Arb rank, oriented projected-gradient nonstationarity, uniform "
            "dL6/dell < 0, and directional alignment residual bounds."
        )
        print(
            "  This is a formal local descent certificate on the serialized "
            "atlas, not yet a validated ODE existence theorem."
        )
    elif stage_a_certified:
        print(
            "  STAGE-A PASS: rank, nonstationarity, fibre tangency and the "
            "uniform strict dL6/dell < 0 bound are certified on the parent "
            "box; only the KKT-witness alignment gate remains open."
        )
        print(
            "  Preserve the Stage-A theorem and refine only the witness "
            "subdivision or use a low-degree lambda/mu witness. This is "
            "not a validated ODE existence theorem."
        )
    else:
        print(
            "  INCONCLUSIVE: Stage A did not close on every child. Do not "
            "claim the formal parent-box rank/descent certificate."
        )


if __name__ == "__main__":
    main()
