#!/usr/bin/env python3
"""C4-D1: rigorous finite residence time in a 6D x 8D product tube.

The fixed orthonormal chart is

    theta = theta_ref + T0 xi + N0 z,
    |xi_i| <= h_T,  |z_j| <= h_N.

All phase, response, Jacobian, and objective-gradient evaluations are carried
out with 256-bit outward-rounded Arb/Acb balls.  The Neumann condition

    q = ||I - J(theta) Y0||_inf < 1

proves full row rank throughout the product tube.  Instead of interval-
inverting J J^T, the script bounds the dynamic Moore--Penrose inverse using
the existence of Y0(JY0)^(-1) and the minimum-2-norm property of J^+.

The resulting uniform speed bound M yields the rigorous residence time

    T_cert = min_i distance(initial subbox, outer face)_i / M.

This proves finite residence only.  It does not prove positive invariance,
saturation, moving-chart continuation, K=1, Pulser, or QPU behaviour.
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
    import c4_arb_recovery_core_certificate_v1_0 as base
    import c4_arb_affine_taylor_subdivision_v1_2 as engine
    import c4_arb_quadratic_taylor_defect_v1_4 as quadratic_engine
except ModuleNotFoundError as exc:
    raise RuntimeError(
        "Use c4_d1_arb_product_tube_residence_bundle.zip with python-flint 0.8.0"
    ) from exc


TITLE = "C4-D1 ARB PRODUCT-TUBE FINITE-RESIDENCE CERTIFICATE"
VERSION = "1.0"
DEFAULT_REPORT = "c4_d1_arb_product_tube_residence_v1_0.json"


def record(ball):
    return {
        "ball": str(ball),
        "lower": float(base.lower(ball)),
        "upper": float(base.upper(ball)),
    }


def frozen_chart():
    j0 = base.centre_jacobian()
    _, singular, vh = np.linalg.svd(j0, full_matrices=True)
    n0 = vh[: base.RESPONSE_DIM].T
    t0 = vh[base.RESPONSE_DIM :].T
    y0 = j0.T @ np.linalg.inv(j0 @ j0.T)
    return t0, n0, y0, singular


def arb_matrix(values):
    return [[base.exact_float(float(x)) for x in row] for row in values]


def phase_radii(t0, n0, tangent_half, normal_half):
    # Exact binary64 reconstruction is used for every frozen chart entry and
    # declared half-width; additions/multiplications are outward-rounded Arb.
    radii = []
    for phase in range(base.NPHASE):
        radius = base.arb(0)
        for value in t0[phase]:
            radius += abs(base.exact_float(float(value))) * base.exact_float(tangent_half)
        for value in n0[phase]:
            radius += abs(base.exact_float(float(value))) * base.exact_float(normal_half)
        radii.append(radius)
    return radii


def interval_objects(t0, n0, y0, tangent_half, normal_half):
    # Reconfigure the reusable quadratic engine from its original 8 normal
    # variables to all 14 product-chart variables.  This retains the shared
    # xi/z dependence that a phasewise interval box would destroy.
    variable_count = base.NPHASE
    engine.NV = variable_count
    quadratic_engine.NV = variable_count
    engine.Affine = quadratic_engine.Quadratic
    frame = np.column_stack((t0, n0))
    centre = np.zeros(variable_count)
    half = np.r_[np.full(t0.shape[1], tangent_half),
                 np.full(n0.shape[1], normal_half)]
    forms = engine.phase_forms(frame, centre, half)
    z, dz, den_q = engine.projective_affine(forms, False)
    zb, dzb, denb_q = engine.projective_affine(forms, True)
    den, denb = den_q.enclosure(), denb_q.enclosure()
    radii = phase_radii(t0, n0, tangent_half, normal_half)

    jacobian = [[base.arb(0) for _ in range(base.NPHASE)]
                for _ in range(base.RESPONSE_DIM)]
    for order in range(4):
        for phase in range(base.NPHASE):
            re = (dz[phase].c[order] + dzb[phase].c[order]) / 2
            im = (dz[phase].c[order] - dzb[phase].c[order]) / base.acb(0, 2)
            jacobian[order][phase] = re.enclosure().real
            jacobian[4 + order][phase] = im.enclosure().real

    y_arb = arb_matrix(y0)
    jy = base.matmul(jacobian, y_arb)
    defect = [[
        (base.arb(1) if i == j else base.arb(0)) - jy[i][j]
        for j in range(base.RESPONSE_DIM)
    ] for i in range(base.RESPONSE_DIM)]
    q_ball, q_rows = base.inf_norm(defect)

    # Response error e = R(theta)-R(theta_ref), orders 0..3, real then imag.
    z0, _ = base.projective_float(base.REFERENCE_PHASES, False)
    response_error = []
    for order in range(4):
        response_error.append(
            z.c[order].enclosure().real - base.exact_float(z0.c[order].real)
        )
    for order in range(4):
        response_error.append(
            z.c[order].enclosure().imag - base.exact_float(z0.c[order].imag)
        )

    # The documented objective is coefficient 6 of q/(1+q), q=z*zb.
    # Its phase gradient is coefficient 6 of
    # (dz_j*zb + z*dzb_j)/(1+z*zb)^2.
    product = z * zb
    denominator = 1 + product
    gradients = []
    for phase in range(base.NPHASE):
        derivative_product = dz[phase] * zb + z * dzb[phase]
        value = derivative_product / (denominator * denominator)
        gradients.append(value.c[6].enclosure().real)

    return {
        "phase_radii": radii,
        "den": den,
        "denb": denb,
        "q": q_ball,
        "q_rows": q_rows,
        "response_error": response_error,
        "gradients": gradients,
    }


def upper_abs(ball):
    return float(base.upper(abs(ball)))


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--normal-radius", type=float, default=1.0e-5)
    parser.add_argument("--tangent-half-width", type=float, default=1.0e-6)
    parser.add_argument("--initial-fraction", type=float, default=0.25)
    parser.add_argument("--beta", type=float, default=base.BETA)
    parser.add_argument("--report", default=DEFAULT_REPORT)
    args, unknown = parser.parse_known_args(argv)
    if unknown:
        print("[notice] ignored notebook/kernel arguments:", unknown)
    if not (0 < args.normal_radius <= 3.25e-4):
        raise ValueError("normal-radius must lie in (0, 3.25e-4]")
    if not (args.tangent_half_width > 0 and args.beta > 0):
        raise ValueError("tangent-half-width and beta must be positive")
    if not (0 <= args.initial_fraction < 1):
        raise ValueError("initial-fraction must lie in [0,1)")

    base.ctx.prec = base.PRECISION_BITS
    normal_half = args.normal_radius / math.sqrt(base.RESPONSE_DIM)
    t0, n0, y0, singular = frozen_chart()
    protocol = {
        "version": VERSION,
        "precision_bits": base.PRECISION_BITS,
        "chart": "theta_ref+T0*xi+N0*z",
        "outer_tangent_half_width": args.tangent_half_width,
        "outer_normal_coordinate_half_width": normal_half,
        "normal_radius_parameter": args.normal_radius,
        "initial_subbox_fraction": args.initial_fraction,
        "beta": args.beta,
        "flow": "theta_dot=-P_MP gradL-beta J^+(R-R_star)",
        "criterion": "q=||I-JY0||_inf<1 and outward-rounded finite speed bound",
    }
    phash = hashlib.sha256(json.dumps(
        protocol, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    print("=" * 100)
    print(f"{TITLE} v{VERSION}")
    print("=" * 100)
    print("scope: rigorous finite residence in a fixed product tube; not invariance/K=1/QPU")
    print("protocol sha256:", phash)
    print("outer tangent half-width:", args.tangent_half_width)
    print("outer normal coordinate half-width:", normal_half)

    try:
        data = interval_objects(
            t0, n0, y0, args.tangent_half_width, normal_half
        )
        q_upper = upper_abs(data["q"])
        denominator_lower = float(base.lower(abs(data["den"])))
        denominator_mirror_lower = float(base.lower(abs(data["denb"])))
        regular = math.isfinite(q_upper) and q_upper < 1

        e_inf = max(upper_abs(x) for x in data["response_error"])
        gradient_inf = max(upper_abs(x) for x in data["gradients"])

        # Frobenius norm is a rigorous upper bound for ||Y0||_2.
        y0_frobenius_sq = sum(
            (base.exact_float(float(value)) ** 2 for value in y0.ravel()),
            base.arb(0),
        )
        y0_frobenius = y0_frobenius_sq.sqrt()
        y0_frobenius_upper = float(base.upper(y0_frobenius))

        # A=JY0. Neumann: ||A^-1||_inf <= 1/(1-q), hence
        # ||A^-1||_2 <= sqrt(8)/(1-q). Since J^+ minimizes the 2-norm
        # solution for every right-hand side, ||J^+||_2 is bounded by the
        # constructed right inverse Y0 A^-1.
        if regular:
            inverse_2_upper = math.sqrt(base.RESPONSE_DIM) / (1 - q_upper)
            pseudoinverse_2_upper = y0_frobenius_upper * inverse_2_upper
            tangent_speed_upper = math.sqrt(base.NPHASE) * gradient_inf
            recovery_speed_upper = (
                args.beta * pseudoinverse_2_upper
                * math.sqrt(base.RESPONSE_DIM) * e_inf
            )
            theta_speed_2_upper = tangent_speed_upper + recovery_speed_upper
        else:
            inverse_2_upper = pseudoinverse_2_upper = math.inf
            tangent_speed_upper = recovery_speed_upper = math.inf
            theta_speed_2_upper = math.inf

        tangent_margin = (1 - args.initial_fraction) * args.tangent_half_width
        normal_margin = (1 - args.initial_fraction) * normal_half
        residence = (
            min(tangent_margin, normal_margin) / theta_speed_2_upper
            if math.isfinite(theta_speed_2_upper) and theta_speed_2_upper > 0
            else None
        )

        gates = {
            "projective_denominators_exclude_zero": bool(
                denominator_lower > 0 and denominator_mirror_lower > 0
            ),
            "uniform_neumann_defect_below_one": bool(regular),
            "response_and_gradient_bounds_finite": bool(
                math.isfinite(e_inf) and math.isfinite(gradient_inf)
            ),
            "uniform_vector_field_speed_bound_finite": bool(
                math.isfinite(theta_speed_2_upper)
            ),
            "strictly_positive_certified_residence_time": bool(
                residence is not None and residence > 0
            ),
        }
        passed = all(gates.values())
        status = (
            "C4_D1_FINITE_RESIDENCE_CERTIFIED" if passed
            else "C4_D1_INCONCLUSIVE"
        )
        result = {
            "title": TITLE,
            "version": VERSION,
            "protocol": protocol,
            "protocol_sha256": phash,
            "bounds": {
                "maximum_phase_coordinate_radius": max(
                    float(base.upper(x)) for x in data["phase_radii"]
                ),
                "forward_projective_denominator_abs_lower": denominator_lower,
                "mirror_projective_denominator_abs_lower": denominator_mirror_lower,
                "neumann_defect_inf_norm": record(data["q"]),
                "response_error_inf_norm_upper": e_inf,
                "objective_gradient_inf_norm_upper": gradient_inf,
                "frozen_right_inverse_frobenius_upper": y0_frobenius_upper,
                "JY0_inverse_2_norm_upper": inverse_2_upper,
                "moore_penrose_inverse_2_norm_upper": pseudoinverse_2_upper,
                "tangent_field_2_norm_upper": tangent_speed_upper,
                "recovery_field_2_norm_upper": recovery_speed_upper,
                "full_vector_field_2_norm_upper": theta_speed_2_upper,
                "tangent_boundary_margin": tangent_margin,
                "normal_boundary_margin": normal_margin,
                "certified_residence_time_lower_bound": residence,
                "minimum_centre_singular_value": float(singular[-1]),
            },
            "gates": gates,
            "all_gates_pass": passed,
            "scientific_status": status,
            "claim_boundary": (
                "Rigorous 256-bit outward-rounded finite-residence certificate "
                "for initial data in the declared inner product subbox and the "
                "unsaturated dynamic Moore-Penrose controlled flow. It does not "
                "prove positive invariance or continuation beyond T_cert."
            ),
            "required_next_step": (
                "C4-E moving-chart recentering/overlap certification is required "
                "for continuation beyond the single certified residence window."
                if passed else
                "Reduce the product tube or introduce correlated Taylor/affine "
                "enclosures; an inconclusive interval is not a counterexample."
            ),
            "environment": {
                "python": platform.python_version(),
                "numpy": np.__version__,
                "python_flint": "0.8.0-compatible",
            },
        }
    except Exception as exc:
        result = {
            "title": TITLE,
            "version": VERSION,
            "protocol": protocol,
            "protocol_sha256": phash,
            "gates": {},
            "all_gates_pass": False,
            "scientific_status": "C4_D1_INCONCLUSIVE",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "claim_boundary": "Arithmetic failure emitted no certificate.",
        }

    Path(args.report).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("\nSUMMARY")
    print(json.dumps({k: result.get(k) for k in (
        "bounds", "gates", "all_gates_pass", "scientific_status",
        "required_next_step", "error_type", "error") if k in result}, indent=2))
    print("report:", args.report)
    return 0 if result["all_gates_pass"] else 2


if __name__ == "__main__":
    code = main()
    if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:
        raise SystemExit(code)
