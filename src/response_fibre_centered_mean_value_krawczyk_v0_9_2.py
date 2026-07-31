#!/usr/bin/env python3
"""Centered mean-value Arb fibre-chart/Krawczyk preflight v0.9.2.

This revision removes the independent interval subtraction
R(theta0 + T*a) - R(theta0) that dominated v0.9.1.  The parameter residual is
enclosed by the exact mean-value identity

    B(R(theta0 + T*a) - R(theta0))
      = integral_0^1 B J(theta0 + s*T*a) T*a ds,

so its constant term is exactly zero.  Response tangency and the normally
stabilized response identity are certified algebraically after formal
invertibility of the whitened Gram matrix has been established.  This remains
an architecture preflight: it does not claim the six-dimensional Picard ODE.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
import textwrap
import time
import urllib.request
import zipfile
from pathlib import Path
from typing import Any


TITLE = "RESPONSE-FIBRE ARB CENTERED MEAN-VALUE KRAWCZYK PREFLIGHT"
VERSION = "0.9.2"
IMPLEMENTATION_REVISION = "zero-constant-mean-value-residual-algebraic-identities"

EXPECTED_ATLAS_SHA256 = (
    "c02acc1c76e0b670793340150d1a875fdc373e0ac7c46d3360a7824b66a3a5ef"
)
EXPECTED_V074_SOURCE_SHA256 = (
    "1f71c4918d1cd1d6c45dc0da4a7358e176baac9116c8f71f4a949a6d657520f8"
)
EXPECTED_INPUTS_ZIP_SHA256 = (
    "2efd863f5ff26da1067594f068bfe265678e6ebac480574ff0574ccc55f98666"
)
RAW_BASE = "https://raw.githubusercontent.com/papasop/Geometric-Flow/main"
SOURCE_NAME = "response_fibre_arb_kkt_witness_alignment_v0_7_4.py"
INPUTS_NAME = "response_fibre_v0_6_2_backend_inputs.zip"


def script_directory() -> Path:
    raw = globals().get("__file__")
    return Path(raw).resolve().parent if raw else Path.cwd().resolve()


def find_existing(explicit: str | None, names: list[str]) -> Path | None:
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit))
    for root in (Path.cwd(), script_directory(), Path("/content")):
        for name in names:
            candidates.extend(
                [root / name, root / "src" / name, root / "inputs" / name]
            )
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    return None


def acquire_exact_file(
    explicit: str | None,
    names: list[str],
    destination: Path,
    url: str,
    expected_sha256: str,
    allow_download: bool,
) -> Path:
    path = find_existing(explicit, names)
    if path is None:
        if not allow_download:
            raise FileNotFoundError(
                f"Missing {names[0]}; upload it or remove --no-download."
            )
        destination.parent.mkdir(parents=True, exist_ok=True)
        print(f"[recovery] downloading {names[0]} from the public repository")
        urllib.request.urlretrieve(url, destination)
        path = destination.resolve()
    digest = sha256_file(path)
    if digest != expected_sha256:
        raise RuntimeError(
            f"Frozen file hash mismatch for {path}: "
            f"{digest} != {expected_sha256}"
        )
    return path


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def atlas_hash_from_zip(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        names = [
            name
            for name in archive.namelist()
            if name == "corrected_atlas.json"
            or name.endswith("/corrected_atlas.json")
        ]
        if len(names) != 1:
            raise RuntimeError(
                "inputs ZIP must contain exactly one corrected_atlas.json"
            )
        atlas = json.loads(archive.read(names[0]))
    return hashlib.sha256(canonical_json(atlas)).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def injection() -> str:
    code = r'''
import os

v083_child = int(os.environ["V083_CHILD_INDEX"])
v083_tube_radius = ap(os.environ["V083_TUBE_RADIUS"])
v083_phase_radius = ap(os.environ["V083_PHASE_RADIUS"])
v083_u_arcs = int(os.environ["V083_U_ARCS"])
v083_phase_arcs = int(os.environ["V083_PHASE_ARCS"])
v083_neumann_terms = int(os.environ["V083_NEUMANN_TERMS"])
v083_output = Path(os.environ["V083_OUTPUT"])
v083_output.mkdir(parents=True, exist_ok=True)


def v083_matvec(matrix, vector):
    return [
        sum((matrix[r][c] * vector[c] for c in range(len(vector))), acb(0))
        for r in range(len(matrix))
    ]


def v083_matmul(left, right):
    return [
        [
            sum(
                (left[r][k] * right[k][c] for k in range(len(right))),
                acb(0),
            )
            for c in range(len(right[0]))
        ]
        for r in range(len(left))
    ]


def v083_inf_matrix(matrix):
    return max(
        (sum((upper_point(x) for x in row), arb(0)) for row in matrix),
        default=arb(0),
    )


def v083_two(vector):
    return sum((upper_point(x) ** 2 for x in vector), arb(0)).sqrt()


def v083_preconditioner(local_center):
    raw = unpack_raw_invariants(analytic_invariants(chart, acb(ap(local_center))))
    gram = np.asarray(
        [
            [midpoint_radius(raw["gram"][r][c].real)[0]
             for c in range(RESPONSE_DIMENSION)]
            for r in range(RESPONSE_DIMENSION)
        ],
        dtype=float,
    )
    inverse = np.linalg.inv(gram)
    return [
        [acb(ap(float(inverse[r, c]))) for c in range(RESPONSE_DIMENSION)]
        for r in range(RESPONSE_DIMENSION)
    ]


def v083_raw(phases, preconditioner, need_field):
    jacobian, gradient = response_jacobian_and_gradient(phases, True)
    gram = [
        [
            sum(
                (jacobian[r][k] * jacobian[c][k]
                 for k in range(CONTROL_DIMENSION)),
                acb(0),
            )
            for c in range(RESPONSE_DIMENSION)
        ]
        for r in range(RESPONSE_DIMENSION)
    ]
    rg = v083_matmul(preconditioner, gram)
    defect = [
        [acb(int(r == c)) - rg[r][c] for c in range(RESPONSE_DIMENSION)]
        for r in range(RESPONSE_DIMENSION)
    ]
    result = {"defect": defect, "jacobian": jacobian, "gradient": gradient}
    if not need_field:
        return result
    defect_upper = v083_inf_matrix(defect)
    if not defect_upper < arb(1):
        raise ArithmeticError(
            f"boundary Neumann inverse unresolved: {upper_float(defect_upper):.6e}"
        )
    right = [
        sum((jacobian[r][k] * gradient[k] for k in range(CONTROL_DIMENSION)), acb(0))
        for r in range(RESPONSE_DIMENSION)
    ]
    z = v083_matvec(preconditioner, right)
    term = list(z)
    solution = [acb(0) for _ in range(RESPONSE_DIMENSION)]
    for _ in range(v083_neumann_terms):
        solution = [solution[i] + term[i] for i in range(RESPONSE_DIMENSION)]
        term = v083_matvec(defect, term)
    z_upper = max((upper_point(x) for x in z), default=arb(0))
    tail = defect_upper ** v083_neumann_terms / (1 - defect_upper) * z_upper
    solution = [add_disk(x, tail) for x in solution]
    projected = [
        gradient[k]
        - sum((jacobian[r][k] * solution[r] for r in range(RESPONSE_DIMENSION)), acb(0))
        for k in range(CONTROL_DIMENSION)
    ]
    square = sum((x * x for x in projected), acb(0))
    if not square.real > arb(0):
        raise ArithmeticError("projected square leaves the open right half-plane")
    norm = square.sqrt()
    if norm.contains(0):
        raise ArithmeticError("projected norm contains zero")
    result.update(
        {
            "defect_upper": defect_upper,
            "projected": projected,
            "field": [-x / norm for x in projected],
            "pgrad_lower": arb(str(square.real.lower())).sqrt(),
            "tail": tail,
        }
    )
    return result


def v083_run():
    if not 0 <= v083_child < CHILD_BOXES:
        raise ValueError("child index outside 0..15")
    center = child_centers[v083_child]
    half_width = child_half_width
    u_interval = child_intervals[v083_child]
    outer_u_radius = ap(3) * ap(half_width)
    preconditioner = v083_preconditioner(center)

    # The frozen scalar Taylor proof supplies the correlated centreline base.
    center_record = audit_box(chart, center, half_width)
    if not center_record.get("stage_a_pass", False):
        raise ArithmeticError("frozen dependency-preserving centreline Stage A failed")
    center_defect = ap(center_record["right_inverse_defect_upper"])
    center_pgrad = ap(center_record["projected_gradient_norm_lower"])

    pi_ball = arb.pi()
    u_half_angle = pi_ball / v083_u_arcs
    z_half_angle = pi_ball / v083_phase_arcs
    e_column_majorants = []
    projected_column_majorants = []
    field_derivative_columns = []
    maximum_boundary_defect = arb(0)
    maximum_neumann_tail = arb(0)

    # First verify only analytic Hamiltonian/projective denominators on a
    # rectangular superset.  No inverse or square root is invoked here.
    u_rectangle = acb(ball(center, outer_u_radius), ball(0, outer_u_radius))
    base_rectangle, _ = phase_and_derivative_at(chart, u_rectangle, True)
    for direction in range(CONTROL_DIMENSION):
        domain = [x + acb(ball(0, v083_tube_radius)) for x in base_rectangle]
        domain[direction] = domain[direction] + acb(
            ball(0, v083_phase_radius), ball(0, v083_phase_radius)
        )
        response_jacobian_and_gradient(domain, True)

    for direction in range(CONTROL_DIMENSION):
        e_max = [[arb(0) for _ in range(RESPONSE_DIMENSION)]
                 for _ in range(RESPONSE_DIMENSION)]
        p_max = [arb(0) for _ in range(CONTROL_DIMENSION)]
        f_max = [arb(0) for _ in range(CONTROL_DIMENSION)]
        for ua in range(v083_u_arcs):
            u_angle = ball(
                pi_ball * (2 * ua + 1) / v083_u_arcs,
                u_half_angle,
            )
            u_root = acb(u_angle.cos(), u_angle.sin())
            local = acb(ap(center)) + outer_u_radius * u_root
            base_phases, _ = phase_and_derivative_at(chart, local, True)
            for za in range(v083_phase_arcs):
                z_angle = ball(
                    pi_ball * (2 * za + 1) / v083_phase_arcs,
                    z_half_angle,
                )
                z_root = acb(z_angle.cos(), z_angle.sin())
                phases = [x + acb(ball(0, v083_tube_radius)) for x in base_phases]
                phases[direction] = phases[direction] + v083_phase_radius * z_root
                audit = v083_raw(phases, preconditioner, True)
                maximum_boundary_defect = max(
                    maximum_boundary_defect, audit["defect_upper"]
                )
                maximum_neumann_tail = max(maximum_neumann_tail, audit["tail"])
                for r in range(RESPONSE_DIMENSION):
                    for c in range(RESPONSE_DIMENSION):
                        e_max[r][c] = max(e_max[r][c], upper_point(audit["defect"][r][c]))
                for k in range(CONTROL_DIMENSION):
                    p_max[k] = max(p_max[k], upper_point(audit["projected"][k]))
                    f_max[k] = max(f_max[k], upper_point(audit["field"][k]))

        e_derivative = [[e_max[r][c] / v083_phase_radius
                         for c in range(RESPONSE_DIMENSION)]
                        for r in range(RESPONSE_DIMENSION)]
        e_column_majorants.append(v083_inf_matrix(e_derivative))
        projected_column_majorants.append(
            sum(((x / v083_phase_radius) ** 2 for x in p_max), arb(0)).sqrt()
        )
        field_derivative_columns.append(
            sum(((x / v083_phase_radius) ** 2 for x in f_max), arb(0)).sqrt()
        )
        print(
            f"[direction {direction + 1:02d}/{CONTROL_DIMENSION:02d}] "
            f"Eprime_inf={upper_float(e_column_majorants[-1]):.3e} "
            f"Pprime_2={upper_float(projected_column_majorants[-1]):.3e} "
            f"DXcol_2={upper_float(field_derivative_columns[-1]):.3e}"
        )

    defect_inflation = v083_tube_radius * sum(e_column_majorants, arb(0))
    tube_defect = center_defect + defect_inflation
    projected_variation = v083_tube_radius * sum(projected_column_majorants, arb(0))
    tube_pgrad = center_pgrad - projected_variation
    lipschitz = sum((x * x for x in field_derivative_columns), arb(0)).sqrt()

    chart_left, chart_right = map(float, chart["arclength_interval"])
    chart_length = chart_right - chart_left
    ell_interval = [
        chart_left + 0.5 * (u + 1.0) * chart_length for u in u_interval
    ]
    h = ap(ell_interval[1] - ell_interval[0])
    contraction = h * lipschitz

    # Convert the already formal v0.7.4 KKT alignment enclosure into a
    # conservative normalized-field residual.  This is expected to be the
    # remaining loose gate, and is never silently replaced by a sampled value.
    parallel = center_record.get("parallel_residual_norm_upper")
    speed_lo = max(0.0, center_record["curve_speed_square_lower"]) ** 0.5
    speed_hi = max(0.0, center_record["curve_speed_square_upper"]) ** 0.5
    if parallel is None:
        residual_upper = None
    else:
        scale_floor = min(
            float(center_pgrad),
            float(center_record["alignment_scale"]) * speed_lo,
        )
        residual_upper = ap(max(abs(speed_lo - 1), abs(speed_hi - 1))) + (
            ap(2) * ap(parallel) / ap(scale_floor)
        )

    if residual_upper is not None and contraction < arb(1):
        required_radius = h * residual_upper / (1 - contraction)
        utilization = required_radius / v083_tube_radius
    else:
        required_radius = None
        utilization = None

    gates = {
        "dependency_preserving_centerline_stage_a": True,
        "projective_domains_analytic": True,
        "tube_response_rank": bool(tube_defect < ap(0.8)),
        "tube_projected_gradient_nonstationary": bool(tube_pgrad > ap(0.6)),
        "exact_response_invariance_identity": True,
        "complete_fourteen_direction_DX_majorant": True,
        "picard_contraction": bool(contraction < ap(0.5)),
        "formal_centerline_residual_resolved": residual_upper is not None,
        "picard_self_mapping": bool(
            utilization is not None and utilization < ap(0.95)
        ),
        "uniform_strict_L6_descent": bool(tube_pgrad > ap(0.55)),
    }
    all_pass = all(gates.values())
    result = {
        "scientific_status": (
            "VALIDATED_LOCAL_PROJECTED_GRADIENT_ODE_SINGLE_CHILD_CERTIFIED"
            if all_pass
            else "DEPENDENCY_PRESERVING_ARB_TUBE_SINGLE_CHILD_INCONCLUSIVE"
        ),
        "all_gates_pass": bool(all_pass),
        "formal_interval_arithmetic": True,
        "arb_precision_bits": PRECISION_BITS,
        "validated_ODE_claimed": bool(all_pass),
        "ODE_existence_certified": bool(all_pass),
        "ODE_uniqueness_in_declared_tube_certified": bool(all_pass),
        "exact_response_preservation_certified": bool(all_pass),
        "uniform_L6_descent_certified_for_validated_solution": bool(all_pass),
        "global_flow_claimed": False,
        "child_index": v083_child,
        "u_interval": u_interval,
        "ell_interval": ell_interval,
        "ode_step_width": float(h),
        "tube_radius": float(v083_tube_radius),
        "phase_cauchy_radius": float(v083_phase_radius),
        "u_outer_cauchy_radius": float(outer_u_radius),
        "centerline_rank_defect_upper": float(center_defect),
        "transverse_rank_defect_inflation_upper": upper_float(defect_inflation),
        "tube_rank_defect_upper": upper_float(tube_defect),
        "centerline_projected_gradient_norm_lower": float(center_pgrad),
        "transverse_projected_gradient_variation_upper": upper_float(projected_variation),
        "tube_projected_gradient_norm_lower": float(tube_pgrad),
        "maximum_boundary_neumann_defect_upper": upper_float(maximum_boundary_defect),
        "maximum_boundary_neumann_tail_upper": upper_float(maximum_neumann_tail),
        "field_lipschitz_upper": upper_float(lipschitz),
        "picard_contraction_factor": upper_float(contraction),
        "formal_centerline_ode_residual_upper": (
            upper_float(residual_upper) if residual_upper is not None else None
        ),
        "picard_required_radius": (
            upper_float(required_radius) if required_radius is not None else None
        ),
        "tube_utilization": (
            upper_float(utilization) if utilization is not None else None
        ),
        "uniform_dL6_dell_upper": -float(tube_pgrad),
        "gates": gates,
        "scope": (
            "one dependency-preserving scalar child with a fourteen-direction "
            "transverse majorant; not the other children or global fibre"
        ),
    }
    (v083_output / "dependency_preserving_tube_certificate.json").write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return result


banner("STAGE C - DEPENDENCY-PRESERVING U / TRANSVERSE MAJORANT")
try:
    v083_result = v083_run()
except Exception as exc:
    v083_result = {
        "scientific_status": "DEPENDENCY_PRESERVING_ARB_TUBE_SINGLE_CHILD_INCONCLUSIVE",
        "all_gates_pass": False,
        "formal_interval_arithmetic": True,
        "validated_ODE_claimed": False,
        "error": f"{type(exc).__name__}: {exc}",
        "scope": "fail-closed dependency-preserving tube attempt",
    }
    (v083_output / "dependency_preserving_tube_certificate.json").write_text(
        json.dumps(v083_result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )

banner("FINAL RESULT v0.8.3")
print(json.dumps(v083_result, indent=2))
print("\nInterpretation")
if v083_result.get("all_gates_pass"):
    print("  PASS: one dependency-preserving local projected-gradient ODE child is validated.")
else:
    print("  INCONCLUSIVE: preserve every passing tube gate and refine only the first open bound.")
    print("  Do not claim a validated ODE unless all gates pass.")
raise SystemExit(0)
'''
    return textwrap.indent(textwrap.dedent(code).strip("\n") + "\n", "    ")


def injection_v090() -> str:
    code = r'''
import os

v090_child = int(os.environ["V090_CHILD_INDEX"])
v090_tube_radius = ap(os.environ["V090_TUBE_RADIUS"])
v090_sample_radius = ap(os.environ["V090_SAMPLE_RADIUS"])
v090_bound_radius = ap(os.environ["V090_BOUND_RADIUS"])
v090_points = int(os.environ["V090_CAUCHY_POINTS"])
v090_arcs = int(os.environ["V090_CAUCHY_ARCS"])
v090_order = int(os.environ["V090_TAYLOR_ORDER"])
v090_neumann_terms = int(os.environ["V090_NEUMANN_TERMS"])
v090_output = Path(os.environ["V090_OUTPUT"])
v090_output.mkdir(parents=True, exist_ok=True)


def v090_matvec(matrix, vector):
    return [
        sum((matrix[r][c] * vector[c] for c in range(len(vector))), acb(0))
        for r in range(len(matrix))
    ]


def v090_matmul(left, right):
    return [
        [
            sum((left[r][k] * right[k][c] for k in range(len(right))), acb(0))
            for c in range(len(right[0]))
        ]
        for r in range(len(left))
    ]


def v090_inf_matrix(matrix):
    return max(
        (sum((upper_point(x) for x in row), arb(0)) for row in matrix),
        default=arb(0),
    )


def v090_whitener(local_center):
    raw = unpack_raw_invariants(analytic_invariants(chart, acb(ap(local_center))))
    jacobian = np.asarray(
        [
            [midpoint_radius(raw["jacobian"][r][c].real)[0]
             for c in range(CONTROL_DIMENSION)]
            for r in range(RESPONSE_DIMENSION)
        ],
        dtype=float,
    )
    left, singular_values, _ = np.linalg.svd(jacobian, full_matrices=False)
    if singular_values[-1] <= 0.0:
        raise ArithmeticError("midpoint response Jacobian is rank deficient")
    whitening = np.diag(1.0 / singular_values) @ left.T
    matrix = [
        [acb(ap(float(whitening[r, c]))) for c in range(RESPONSE_DIMENSION)]
        for r in range(RESPONSE_DIMENSION)
    ]
    inverse_float = np.linalg.inv(whitening)
    inverse_matrix = [
        [acb(ap(float(inverse_float[r, c])))
         for c in range(RESPONSE_DIMENSION)]
        for r in range(RESPONSE_DIMENSION)
    ]
    inverse_product = v090_matmul(inverse_matrix, matrix)
    invertibility_defect = v090_inf_matrix(
        [
            [
                acb(int(r == c)) - inverse_product[r][c]
                for c in range(RESPONSE_DIMENSION)
            ]
            for r in range(RESPONSE_DIMENSION)
        ]
    )
    if not invertibility_defect < arb(1):
        raise ArithmeticError(
            "frozen SVD whitening matrix invertibility unresolved"
        )
    return matrix, singular_values, invertibility_defect


def v090_field(phases, whitener):
    jacobian, gradient = response_jacobian_and_gradient(phases, True)
    whitened_jacobian = v090_matmul(whitener, jacobian)
    whitened_gram = [
        [
            sum(
                (whitened_jacobian[r][k] * whitened_jacobian[c][k]
                 for k in range(CONTROL_DIMENSION)),
                acb(0),
            )
            for c in range(RESPONSE_DIMENSION)
        ]
        for r in range(RESPONSE_DIMENSION)
    ]
    defect = [
        [
            acb(int(r == c)) - whitened_gram[r][c]
            for c in range(RESPONSE_DIMENSION)
        ]
        for r in range(RESPONSE_DIMENSION)
    ]
    defect_upper = v090_inf_matrix(defect)
    if not defect_upper < arb(1):
        raise ArithmeticError(
            f"coordinate-disk Neumann inverse unresolved: "
            f"{upper_float(defect_upper):.6e}"
        )
    right = [
        sum((whitened_jacobian[r][k] * gradient[k]
             for k in range(CONTROL_DIMENSION)), acb(0))
        for r in range(RESPONSE_DIMENSION)
    ]
    # The midpoint preconditioner is the identity in whitened response
    # coordinates.  The Neumann series therefore solves
    # (Jw Jw^T) y = Jw g directly.
    z = list(right)
    term = list(z)
    solution = [acb(0) for _ in range(RESPONSE_DIMENSION)]
    for _ in range(v090_neumann_terms):
        solution = [solution[i] + term[i] for i in range(RESPONSE_DIMENSION)]
        term = v090_matvec(defect, term)
    z_upper = max((upper_point(x) for x in z), default=arb(0))
    tail = defect_upper ** v090_neumann_terms / (1 - defect_upper) * z_upper
    solution = [add_disk(x, tail) for x in solution]
    projected = [
        gradient[k]
        - sum((whitened_jacobian[r][k] * solution[r]
               for r in range(RESPONSE_DIMENSION)), acb(0))
        for k in range(CONTROL_DIMENSION)
    ]
    square = sum((x * x for x in projected), acb(0))
    if not square.real > arb(0):
        raise ArithmeticError(
            "projected-gradient square leaves the open right half-plane"
        )
    norm = square.sqrt()
    if norm.contains(0):
        raise ArithmeticError("projected-gradient norm contains zero")
    return {
        "field": [-x / norm for x in projected],
        "defect_upper": defect_upper,
        "neumann_tail": tail,
    }


def v090_direction(base_phases, whitener, direction):
    pi_ball = arb.pi()
    roots = []
    samples = []
    maximum_defect = arb(0)
    maximum_neumann_tail = arb(0)
    for index in range(v090_points):
        angle = 2 * pi_ball * index / v090_points
        root = acb(angle.cos(), angle.sin())
        roots.append(root)
        phases = list(base_phases)
        phases[direction] = phases[direction] + v090_sample_radius * root
        audit = v090_field(phases, whitener)
        samples.append(audit["field"])
        maximum_defect = max(maximum_defect, audit["defect_upper"])
        maximum_neumann_tail = max(
            maximum_neumann_tail, audit["neumann_tail"]
        )

    boundary_bounds = [arb(0) for _ in range(CONTROL_DIMENSION)]
    angular_half_width = pi_ball / v090_arcs
    for arc in range(v090_arcs):
        angle = ball(
            pi_ball * (2 * arc + 1) / v090_arcs,
            angular_half_width,
        )
        root = acb(angle.cos(), angle.sin())
        phases = list(base_phases)
        phases[direction] = phases[direction] + v090_bound_radius * root
        audit = v090_field(phases, whitener)
        maximum_defect = max(maximum_defect, audit["defect_upper"])
        maximum_neumann_tail = max(
            maximum_neumann_tail, audit["neumann_tail"]
        )
        for component in range(CONTROL_DIMENSION):
            boundary_bounds[component] = max(
                boundary_bounds[component],
                upper_point(audit["field"][component]),
            )

    ratio = v090_sample_radius / v090_bound_radius
    alias_factor = ratio ** v090_points / (1 - ratio ** v090_points)
    coefficients = []
    for component in range(CONTROL_DIMENSION):
        component_coefficients = []
        for order in range(v090_order + 1):
            total = sum(
                (
                    samples[index][component]
                    * roots[index].conjugate() ** order
                    for index in range(v090_points)
                ),
                acb(0),
            )
            coefficient = total / (v090_points * v090_sample_radius ** order)
            coefficient = add_disk(
                coefficient,
                boundary_bounds[component]
                / v090_bound_radius ** order
                * alias_factor,
            )
            component_coefficients.append(coefficient)
        coefficients.append(component_coefficients)

    q = v090_tube_radius / v090_bound_radius
    derivative_components = []
    maximum_derivative_tail = arb(0)
    for component in range(CONTROL_DIMENSION):
        polynomial = sum(
            (
                ap(order)
                * upper_point(coefficients[component][order])
                * v090_tube_radius ** (order - 1)
                for order in range(1, v090_order + 1)
            ),
            arb(0),
        )
        tail = (
            boundary_bounds[component]
            / v090_bound_radius
            * (
                ap(v090_order + 1) * q ** v090_order
                - ap(v090_order) * q ** (v090_order + 1)
            )
            / (1 - q) ** 2
        )
        derivative_components.append(polynomial + tail)
        maximum_derivative_tail = max(maximum_derivative_tail, tail)

    column_norm = sum(
        (value ** 2 for value in derivative_components), arb(0)
    ).sqrt()
    constant_norm = sum(
        (upper_point(coefficients[k][0]) ** 2
         for k in range(CONTROL_DIMENSION)),
        arb(0),
    ).sqrt()
    return {
        "direction": direction,
        "maximum_boundary_neumann_defect_upper": upper_float(maximum_defect),
        "maximum_neumann_tail_upper": upper_float(maximum_neumann_tail),
        "centered_constant_coefficient_norm_upper": upper_float(constant_norm),
        "directional_DX_column_norm_upper": upper_float(column_norm),
        "maximum_derivative_tail_upper": upper_float(maximum_derivative_tail),
        "coefficient_order": v090_order,
        "pass": bool(maximum_defect < arb(1)),
    }


def v090_run():
    if not 0 <= v090_child < CHILD_BOXES:
        raise ValueError("child index outside 0..15")
    if not (
        arb(0) < v090_tube_radius < v090_sample_radius < v090_bound_radius
    ):
        raise ValueError(
            "require 0 < tube radius < sample radius < bound radius"
        )
    if not 1 <= v090_order < v090_points:
        raise ValueError("Taylor order must lie in 1..cauchy_points-1")

    center = child_centers[v090_child]
    half_width = child_half_width
    u_interval = child_intervals[v090_child]
    center_record = audit_box(chart, center, half_width)
    if not center_record.get("stage_a_pass", False):
        raise ArithmeticError("frozen child Stage A failed")
    whitener, midpoint_singular_values, whitener_invertibility_defect = (
        v090_whitener(center)
    )
    base_phases, _ = phase_and_derivative_at(chart, acb(ap(center)), True)
    center_field = v090_field(base_phases, whitener)

    direction_records = []
    for direction in range(CONTROL_DIMENSION):
        record = v090_direction(base_phases, whitener, direction)
        direction_records.append(record)
        print(
            f"[direction {direction + 1:02d}/{CONTROL_DIMENSION:02d}] "
            f"defect={record['maximum_boundary_neumann_defect_upper']:.3e} "
            f"DXcol={record['directional_DX_column_norm_upper']:.3e} "
            f"tail={record['maximum_derivative_tail_upper']:.3e}"
        )

    columns = [
        ap(record["directional_DX_column_norm_upper"])
        for record in direction_records
    ]
    frobenius_majorant = sum((x * x for x in columns), arb(0)).sqrt()
    maximum_boundary_defect = max(
        ap(record["maximum_boundary_neumann_defect_upper"])
        for record in direction_records
    )
    maximum_tail = max(
        ap(record["maximum_derivative_tail_upper"])
        for record in direction_records
    )
    all_directions_pass = all(record["pass"] for record in direction_records)
    diagnostic_pass = bool(all_directions_pass and center_record["stage_a_pass"])

    chart_left, chart_right = map(float, chart["arclength_interval"])
    chart_length = chart_right - chart_left
    ell_interval = [
        chart_left + 0.5 * (u + 1.0) * chart_length for u in u_interval
    ]
    result = {
        "scientific_status": (
            "SVD_WHITENED_CENTERED_TAYLOR_DX_PREFLIGHT_SUPPORTED"
            if diagnostic_pass
            else "SVD_WHITENED_CENTERED_TAYLOR_DX_PREFLIGHT_INCONCLUSIVE"
        ),
        "all_gates_pass": diagnostic_pass,
        "formal_interval_arithmetic": True,
        "arb_precision_bits": PRECISION_BITS,
        "validated_ODE_claimed": False,
        "ODE_existence_certified": False,
        "full_fourteen_dimensional_tube_certified": False,
        "child_index": v090_child,
        "u_interval": u_interval,
        "ell_interval": ell_interval,
        "tube_radius": float(v090_tube_radius),
        "phase_cauchy_sample_radius": float(v090_sample_radius),
        "phase_cauchy_bound_radius": float(v090_bound_radius),
        "centerline_stage_a_certified": True,
        "centerline_projected_gradient_norm_lower": center_record[
            "projected_gradient_norm_lower"
        ],
        "centerline_dL6_dell_upper": center_record["dL6_dell_upper"],
        "midpoint_response_singular_values": [
            float(value) for value in midpoint_singular_values
        ],
        "midpoint_response_condition_number": float(
            midpoint_singular_values[0] / midpoint_singular_values[-1]
        ),
        "whitener_invertibility_neumann_defect_upper": upper_float(
            whitener_invertibility_defect
        ),
        "response_preconditioning": (
            "frozen B=diag(1/sigma) U^T from the midpoint SVD; "
            "Jw=BJ and E=I-Jw Jw^T"
        ),
        "center_field_neumann_defect_upper": upper_float(
            center_field["defect_upper"]
        ),
        "maximum_coordinate_disk_neumann_defect_upper": upper_float(
            maximum_boundary_defect
        ),
        "directional_DX_frobenius_majorant_upper": upper_float(
            frobenius_majorant
        ),
        "maximum_centered_derivative_tail_upper": upper_float(maximum_tail),
        "direction_records": direction_records,
        "gates": {
            "frozen_child_stage_a": True,
            "frozen_svd_whitener_formally_invertible": True,
            "fourteen_coordinate_disks_analytic": all_directions_pass,
            "centered_positive_order_coefficients_extracted": True,
            "constant_term_excluded_from_DX": True,
            "full_mixed_transverse_remainder_enclosed": False,
            "u_dependent_polydisc_enclosed": False,
        },
        "next_required_step": (
            "Lift these centered one-coordinate majorants to the full "
            "u-dependent fourteen-variable polydisc, including mixed "
            "Taylor monomials; only then use the bound in Picard/Krawczyk."
        ),
        "scope": (
            "formal Arb centered-Cauchy directional DX diagnostic at one "
            "child midpoint; not a multivariate tube or validated ODE"
        ),
    }
    (v090_output / "svd_whitened_centered_taylor_dx_certificate.json").write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return result


banner("STAGE C - CENTERED CAUCHY/TAYLOR DIRECTIONAL DX")
try:
    v090_result = v090_run()
except Exception as exc:
    v090_result = {
        "scientific_status": "SVD_WHITENED_CENTERED_TAYLOR_DX_PREFLIGHT_INCONCLUSIVE",
        "all_gates_pass": False,
        "formal_interval_arithmetic": True,
        "validated_ODE_claimed": False,
        "error": f"{type(exc).__name__}: {exc}",
        "scope": "fail-closed centered directional DX attempt",
    }
    (v090_output / "svd_whitened_centered_taylor_dx_certificate.json").write_text(
        json.dumps(v090_result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )

banner("FINAL RESULT v0.9.1")
print(json.dumps(v090_result, indent=2))
print("\nInterpretation")
if v090_result.get("all_gates_pass"):
    print("  PASS: all fourteen centered coordinate-DX disks close.")
    print("  This is a derivative-design certificate, not a validated ODE.")
else:
    print("  INCONCLUSIVE: refine only the first reported coordinate-disk bound.")
    print("  Do not claim a validated ODE.")
raise SystemExit(0)
'''
    return textwrap.indent(textwrap.dedent(code).strip("\n") + "\n", "    ")


def injection_v090_arch() -> str:
    code = r'''
import os

v090_child = int(os.environ["V090_CHILD_INDEX"])
v090_tangent_radius = ap(os.environ["V090_TANGENT_RADIUS"])
v090_normal_radius = ap(os.environ["V090_NORMAL_RADIUS"])
v090_kappa = ap(os.environ["V090_KAPPA"])
v090_neumann_terms = int(os.environ["V090_NEUMANN_TERMS"])
v090_output = Path(os.environ["V090_OUTPUT"])
v090_output.mkdir(parents=True, exist_ok=True)


def v090_matvec(matrix, vector):
    return [
        sum((matrix[r][c] * vector[c] for c in range(len(vector))), acb(0))
        for r in range(len(matrix))
    ]


def v090_matmul(left, right):
    return [
        [
            sum((left[r][k] * right[k][c] for k in range(len(right))), acb(0))
            for c in range(len(right[0]))
        ]
        for r in range(len(left))
    ]


def v090_transpose(matrix):
    return [list(column) for column in zip(*matrix)]


def v090_inf_matrix(matrix):
    return max(
        (sum((upper_point(x) for x in row), arb(0)) for row in matrix),
        default=arb(0),
    )


def v090_two(vector):
    return sum((upper_point(x) ** 2 for x in vector), arb(0)).sqrt()


def v090_response(phases):
    z, _ = projective_jet_and_derivatives(phases, mirror=False)
    zbar, _ = projective_jet_and_derivatives(phases, mirror=True)
    values = []
    for order in range(RESPONSE_ORDER + 1):
        values.append((z.c[order] + zbar.c[order]) / 2)
    for order in range(RESPONSE_ORDER + 1):
        values.append((z.c[order] - zbar.c[order]) / (2 * I))
    return values


def v090_frame(local_center):
    raw = unpack_raw_invariants(analytic_invariants(chart, acb(ap(local_center))))
    jacobian_float = np.asarray(
        [
            [midpoint_radius(raw["jacobian"][r][c].real)[0]
             for c in range(CONTROL_DIMENSION)]
            for r in range(RESPONSE_DIMENSION)
        ],
        dtype=float,
    )
    left, singular_values, right_t = np.linalg.svd(
        jacobian_float, full_matrices=True
    )
    if singular_values[-1] <= 0.0:
        raise ArithmeticError("midpoint response Jacobian is rank deficient")
    normal_float = right_t[:RESPONSE_DIMENSION, :].T
    tangent_float = right_t[RESPONSE_DIMENSION:, :].T
    whitening_float = np.diag(1.0 / singular_values) @ left.T
    whitener = [
        [acb(ap(float(whitening_float[r, c])))
         for c in range(RESPONSE_DIMENSION)]
        for r in range(RESPONSE_DIMENSION)
    ]
    normal = [
        [acb(ap(float(normal_float[r, c])))
         for c in range(RESPONSE_DIMENSION)]
        for r in range(CONTROL_DIMENSION)
    ]
    tangent = [
        [acb(ap(float(tangent_float[r, c])))
         for c in range(CONTROL_DIMENSION - RESPONSE_DIMENSION)]
        for r in range(CONTROL_DIMENSION)
    ]

    inverse_float = np.linalg.inv(whitening_float)
    inverse = [
        [acb(ap(float(inverse_float[r, c])))
         for c in range(RESPONSE_DIMENSION)]
        for r in range(RESPONSE_DIMENSION)
    ]
    product = v090_matmul(inverse, whitener)
    invertibility_defect = v090_inf_matrix(
        [[acb(int(r == c)) - product[r][c]
          for c in range(RESPONSE_DIMENSION)]
         for r in range(RESPONSE_DIMENSION)]
    )
    if not invertibility_defect < arb(1):
        raise ArithmeticError("SVD whitener invertibility unresolved")
    return {
        "raw": raw,
        "singular_values": singular_values,
        "whitener": whitener,
        "normal": normal,
        "tangent": tangent,
        "whitener_invertibility_defect": invertibility_defect,
    }


def v090_phase_box(base, tangent, normal, tangent_radius, normal_radius):
    phases = []
    for row in range(CONTROL_DIMENSION):
        radius = tangent_radius * sum(
            (upper_point(tangent[row][c])
             for c in range(CONTROL_DIMENSION - RESPONSE_DIMENSION)),
            arb(0),
        )
        radius += normal_radius * sum(
            (upper_point(normal[row][c])
             for c in range(RESPONSE_DIMENSION)),
            arb(0),
        )
        phases.append(base[row] + acb(ball(0, radius)))
    return phases


def v090_neumann_solve(whitened_jacobian, right):
    gram = [
        [sum((whitened_jacobian[r][k] * whitened_jacobian[c][k]
              for k in range(CONTROL_DIMENSION)), acb(0))
         for c in range(RESPONSE_DIMENSION)]
        for r in range(RESPONSE_DIMENSION)
    ]
    defect = [
        [acb(int(r == c)) - gram[r][c]
         for c in range(RESPONSE_DIMENSION)]
        for r in range(RESPONSE_DIMENSION)
    ]
    defect_upper = v090_inf_matrix(defect)
    if not defect_upper < arb(1):
        raise ArithmeticError(
            f"whitened response inverse unresolved: "
            f"{upper_float(defect_upper):.6e}"
        )
    term = list(right)
    solution = [acb(0) for _ in range(RESPONSE_DIMENSION)]
    for _ in range(v090_neumann_terms):
        solution = [solution[i] + term[i] for i in range(RESPONSE_DIMENSION)]
        term = v090_matvec(defect, term)
    right_upper = max((upper_point(x) for x in right), default=arb(0))
    tail = defect_upper ** v090_neumann_terms / (1 - defect_upper) * right_upper
    return [add_disk(x, tail) for x in solution], defect_upper, tail


def v090_run():
    if not 0 <= v090_child < CHILD_BOXES:
        raise ValueError("child index outside 0..15")
    if not (v090_tangent_radius > arb(0) and v090_normal_radius > arb(0)):
        raise ValueError("chart radii must be positive")
    if not v090_kappa > arb(0):
        raise ValueError("kappa must be positive")

    center = child_centers[v090_child]
    half_width = child_half_width
    u_interval = child_intervals[v090_child]
    center_record = audit_box(chart, center, half_width)
    if not center_record.get("stage_a_pass", False):
        raise ArithmeticError("frozen child Stage A failed")

    base_phases, _ = phase_and_derivative_at(chart, acb(ap(center)), True)
    frame = v090_frame(center)
    whitener = frame["whitener"]
    normal = frame["normal"]
    tangent = frame["tangent"]
    jacobian0 = frame["raw"]["jacobian"]
    whitened_jacobian0 = v090_matmul(whitener, jacobian0)

    tangent_residual = v090_matmul(whitened_jacobian0, tangent)
    normal_derivative0 = v090_matmul(whitened_jacobian0, normal)
    tangent_residual_upper = v090_inf_matrix(tangent_residual)
    normal_identity_defect = v090_inf_matrix(
        [[acb(int(r == c)) - normal_derivative0[r][c]
          for c in range(RESPONSE_DIMENSION)]
         for r in range(RESPONSE_DIMENSION)]
    )
    center_gram = [
        [sum((whitened_jacobian0[r][k] * whitened_jacobian0[c][k]
              for k in range(CONTROL_DIMENSION)), acb(0))
         for c in range(RESPONSE_DIMENSION)]
        for r in range(RESPONSE_DIMENSION)
    ]
    center_rank_defect = v090_inf_matrix(
        [[acb(int(r == c)) - center_gram[r][c]
          for c in range(RESPONSE_DIMENSION)]
         for r in range(RESPONSE_DIMENSION)]
    )

    tangent_only_phases = v090_phase_box(
        base_phases, tangent, normal, v090_tangent_radius, arb(0)
    )
    full_phases = v090_phase_box(
        base_phases, tangent, normal,
        v090_tangent_radius, v090_normal_radius
    )
    # Correlation-preserving parameter residual.  For every real
    # a in [-r_a,r_a]^6, the complete segment theta0+s*T*a lies inside
    # tangent_only_phases.  Hence the fundamental theorem of calculus gives
    #
    #   B(R(theta0+T*a)-R(theta0))
    #     = int_0^1 B J(theta0+s*T*a) T*a ds.
    #
    # Enclosing BJ T on the segment box and multiplying by a therefore
    # retains the exact zero constant term.  No subtraction of two
    # independently rounded response enclosures occurs.
    jacobian_tangent_box, _ = response_jacobian_and_gradient(
        tangent_only_phases, True
    )
    whitened_jacobian_tangent_box = v090_matmul(
        whitener, jacobian_tangent_box
    )
    mean_value_tangent_derivative = v090_matmul(
        whitened_jacobian_tangent_box, tangent
    )
    parameter_residual_radii = [
        v090_tangent_radius
        * sum(
            (upper_point(mean_value_tangent_derivative[row][column])
             for column in range(CONTROL_DIMENSION - RESPONSE_DIMENSION)),
            arb(0),
        )
        for row in range(RESPONSE_DIMENSION)
    ]
    parameter_residual = [
        acb(ball(0, radius)) for radius in parameter_residual_radii
    ]
    parameter_residual_upper = max(
        parameter_residual_radii, default=arb(0)
    )

    jacobian_box, _gradient_box = response_jacobian_and_gradient(
        full_phases, True
    )
    whitened_jacobian_box = v090_matmul(whitener, jacobian_box)
    normal_derivative_box = v090_matmul(whitened_jacobian_box, normal)

    normal_mid_float = np.asarray(
        [[midpoint_radius(normal_derivative0[r][c].real)[0]
          for c in range(RESPONSE_DIMENSION)]
         for r in range(RESPONSE_DIMENSION)],
        dtype=float,
    )
    normal_inverse_float = np.linalg.inv(normal_mid_float)
    normal_inverse = [
        [acb(ap(float(normal_inverse_float[r, c])))
         for c in range(RESPONSE_DIMENSION)]
        for r in range(RESPONSE_DIMENSION)
    ]
    krawczyk_defect = [
        [acb(int(r == c)) - value
         for c, value in enumerate(row)]
        for r, row in enumerate(v090_matmul(normal_inverse, normal_derivative_box))
    ]
    krawczyk_center = [
        -value for value in v090_matvec(normal_inverse, parameter_residual)
    ]
    krawczyk_component_radii = []
    for r in range(RESPONSE_DIMENSION):
        radius = upper_point(krawczyk_center[r])
        radius += v090_normal_radius * sum(
            (upper_point(krawczyk_defect[r][c])
             for c in range(RESPONSE_DIMENSION)),
            arb(0),
        )
        krawczyk_component_radii.append(radius)
    krawczyk_utilization = max(krawczyk_component_radii) / v090_normal_radius
    krawczyk_defect_upper = v090_inf_matrix(krawczyk_defect)

    tube_gram = [
        [sum((whitened_jacobian_box[r][k]
              * whitened_jacobian_box[c][k]
              for k in range(CONTROL_DIMENSION)), acb(0))
         for c in range(RESPONSE_DIMENSION)]
        for r in range(RESPONSE_DIMENSION)
    ]
    tube_rank_defect = v090_inf_matrix(
        [[acb(int(r == c)) - tube_gram[r][c]
          for c in range(RESPONSE_DIMENSION)]
         for r in range(RESPONSE_DIMENSION)]
    )

    # Do not numerically subtract dependency-related interval expressions to
    # test an algebraic identity.  If ||I-G||<1, G=Jw*Jw^T is invertible.
    # Therefore, exactly (over the reals),
    #
    # Jw [I-Jw^T G^-1 Jw] = 0,
    # Jw [Jw^T G^-1 r] = r.
    #
    # Consequently Jw X_kappa=-kappa*r.  The proof gate below is conditional
    # only on the formal tube-rank enclosure and invertibility of B; it has no
    # cancellation-prone floating or interval residual.
    projected_tangency = arb(0)
    stabilized_identity_residual_upper = arb(0)

    rank_pass = bool(center_rank_defect < ap(0.8))
    tangent_frame_pass = bool(tangent_residual_upper < ap(1e-6))
    normal_frame_pass = bool(normal_identity_defect < ap(0.8))
    krawczyk_pass = bool(
        krawczyk_defect_upper < ap(0.8)
        and krawczyk_utilization < ap(0.95)
    )
    tube_rank_pass = bool(tube_rank_defect < ap(0.8))
    identity_pass = bool(
        tube_rank_pass
        and frame["whitener_invertibility_defect"] < arb(1)
    )
    gates = {
        "frozen_child_stage_a": True,
        "response_rank_at_chart_center": rank_pass,
        "six_dimensional_tangent_frame": tangent_frame_pass,
        "eight_dimensional_normal_frame": normal_frame_pass,
        "response_penalty_kernel_identity": rank_pass,
        "parameterized_normal_krawczyk_graph": krawczyk_pass,
        "tube_response_rank": tube_rank_pass,
        "projected_field_response_tangency": identity_pass,
        "normally_stabilized_response_identity": identity_pass,
        "full_six_dimensional_picard_closed": False,
    }
    architecture_pass = all(
        value for key, value in gates.items()
        if key != "full_six_dimensional_picard_closed"
    )

    chart_left, chart_right = map(float, chart["arclength_interval"])
    chart_length = chart_right - chart_left
    ell_interval = [
        chart_left + 0.5 * (u + 1.0) * chart_length for u in u_interval
    ]
    result = {
        "scientific_status": (
            "ARB_FIBRE_CHART_STABILIZED_ODE_ARCHITECTURE_SUPPORTED"
            if architecture_pass
            else "ARB_FIBRE_CHART_STABILIZED_ODE_ARCHITECTURE_INCONCLUSIVE"
        ),
        "all_gates_pass": False,
        "architecture_gates_pass": bool(architecture_pass),
        "formal_interval_arithmetic": True,
        "arb_precision_bits": PRECISION_BITS,
        "validated_ODE_claimed": False,
        "ODE_existence_certified": False,
        "exact_response_preservation_claimed": False,
        "child_index": v090_child,
        "u_interval": u_interval,
        "ell_interval": ell_interval,
        "tangent_dimension": CONTROL_DIMENSION - RESPONSE_DIMENSION,
        "normal_dimension": RESPONSE_DIMENSION,
        "tangent_radius": float(v090_tangent_radius),
        "normal_radius": float(v090_normal_radius),
        "normal_stabilization_kappa": float(v090_kappa),
        "midpoint_response_singular_values": [
            float(value) for value in frame["singular_values"]
        ],
        "midpoint_response_condition_number": float(
            frame["singular_values"][0] / frame["singular_values"][-1]
        ),
        "whitener_invertibility_neumann_defect_upper": upper_float(
            frame["whitener_invertibility_defect"]
        ),
        "center_whitened_rank_defect_upper": upper_float(center_rank_defect),
        "tangent_frame_response_residual_upper": upper_float(
            tangent_residual_upper
        ),
        "normal_frame_identity_defect_upper": upper_float(
            normal_identity_defect
        ),
        "krawczyk_normal_derivative_defect_upper": upper_float(
            krawczyk_defect_upper
        ),
        "centered_parameter_residual_upper": upper_float(
            parameter_residual_upper
        ),
        "mean_value_tangent_derivative_inf_upper": upper_float(
            v090_inf_matrix(mean_value_tangent_derivative)
        ),
        "krawczyk_normal_box_utilization": upper_float(krawczyk_utilization),
        "tube_whitened_rank_defect_upper": upper_float(tube_rank_defect),
        "projected_field_response_tangency_upper": upper_float(
            projected_tangency
        ),
        "stabilized_identity_residual_upper": upper_float(
            stabilized_identity_residual_upper
        ),
        "projected_solve_tail_upper": None,
        "normal_solve_tail_upper": None,
        "response_identity_proof_kind": (
            "exact algebra after Arb-certified invertibility; no independent "
            "interval subtraction"
        ),
        "exact_algebraic_identities": {
            "response_penalty_hessian": "H_R=DR3^T DR3 on R3=c",
            "penalty_kernel": "ker(H_R)=ker(DR3)=T_theta M_c",
            "stabilized_extension": (
                "X_kappa=Y-kappa*Jw^T*(Jw*Jw^T)^(-1)*B*(R3-c), "
                "for any Y in ker(DR3)"
            ),
            "response_dynamics": "d/dt[B(R3-c)]=-kappa*B(R3-c)",
        },
        "gates": gates,
        "next_required_step": (
            "If the centered mean-value Krawczyk gate passes, pull the "
            "declared metric and L6 back to the six-dimensional graph and "
            "close a square-root-free Taylor/Picard inclusion there."
        ),
        "scope": (
            "single-child formal tangent/normal frame, parameterized normal "
            "Krawczyk graph and normally stabilized response identity; not a "
            "six-dimensional Picard theorem or global flow"
        ),
    }
    (v090_output / "centered_mean_value_krawczyk_certificate.json").write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return result


banner("STAGE C - FIBRE FRAME / NORMAL KRAWCZYK / STABILIZED RESPONSE")
try:
    v090_result = v090_run()
except Exception as exc:
    v090_result = {
        "scientific_status": "ARB_FIBRE_CHART_STABILIZED_ODE_ARCHITECTURE_INCONCLUSIVE",
        "all_gates_pass": False,
        "architecture_gates_pass": False,
        "formal_interval_arithmetic": True,
        "validated_ODE_claimed": False,
        "error": f"{type(exc).__name__}: {exc}",
        "scope": "fail-closed fibre-chart/stabilized-ODE architecture preflight",
    }
    (v090_output / "centered_mean_value_krawczyk_certificate.json").write_text(
        json.dumps(v090_result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )

banner("FINAL RESULT v0.9.2")
print(json.dumps(v090_result, indent=2))
print("\nInterpretation")
if v090_result.get("architecture_gates_pass"):
    print("  ARCHITECTURE PASS: the local fibre graph and stable normal extension close.")
    print("  The six-dimensional Picard inclusion remains the next theorem step.")
else:
    print("  INCONCLUSIVE: refine only the first open frame/Krawczyk bound.")
print("  Do not claim a validated ODE from this preflight.")
raise SystemExit(0)
'''
    return textwrap.indent(textwrap.dedent(code).strip("\n") + "\n", "    ")


def patch_frozen_source(source: bytes) -> str:
    text = source.decode("utf-8")
    needle = '''    banner(
        "STAGE A FROZEN-SOLVE DESCENT / "
        "STAGE B FROZEN KKT-WITNESS ALIGNMENT"
    )
'''
    if text.count(needle) != 1:
        raise RuntimeError("frozen Stage-A insertion point not unique")
    return text.replace(needle, injection_v090_arch() + needle)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs-zip")
    parser.add_argument("--v074-source")
    parser.add_argument("--child-index", type=int, default=15)
    parser.add_argument("--tangent-radius", default="3e-8")
    parser.add_argument("--normal-radius", default="3e-8")
    parser.add_argument("--kappa", default="1.0")
    parser.add_argument("--neumann-terms", type=int, default=16)
    parser.add_argument("--no-download", action="store_true")
    parser.add_argument(
        "--output",
        default="response_fibre_fibre_chart_stabilized_ode_v0_9_0_results",
    )
    args, ignored = parser.parse_known_args()
    if ignored:
        print(f"[notice] ignored notebook arguments: {ignored}")
    if not 0 <= args.child_index < 16:
        raise ValueError("--child-index must be between 0 and 15")

    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    recovery = Path("/content") if Path("/content").is_dir() else output / "inputs"
    inputs_zip = acquire_exact_file(
        args.inputs_zip,
        [INPUTS_NAME, "response_fibre_v0_6_2_backend_inputs (1).zip"],
        recovery / INPUTS_NAME,
        f"{RAW_BASE}/inputs/{INPUTS_NAME}",
        EXPECTED_INPUTS_ZIP_SHA256,
        not args.no_download,
    )
    source_path = acquire_exact_file(
        args.v074_source,
        [SOURCE_NAME],
        recovery / SOURCE_NAME,
        f"{RAW_BASE}/src/{SOURCE_NAME}",
        EXPECTED_V074_SOURCE_SHA256,
        not args.no_download,
    )
    if atlas_hash_from_zip(inputs_zip) != EXPECTED_ATLAS_SHA256:
        raise RuntimeError("corrected atlas hash mismatch")

    protocol = {
        "title": TITLE,
        "version": VERSION,
        "implementation_revision": IMPLEMENTATION_REVISION,
        "formal_interval_arithmetic": True,
        "arb_precision_bits": 192,
        "purpose": (
            "replace the ambient fourteen-dimensional Euclidean tube by a "
            "six-tangent/eight-normal fibre chart and audit a stable normal "
            "response extension before the intrinsic Picard proof"
        ),
        "coordinate_model": (
            "theta=theta0+T*a+N*b with dim(a)=6 and dim(b)=8; "
            "solve B(R3(theta)-c)=0 for b=psi(a)"
        ),
        "response_preconditioning": (
            "frozen midpoint SVD whitening B=diag(1/sigma)U^T; "
            "projector invariant under the invertible response-row transform"
        ),
        "child_index": args.child_index,
        "tangent_radius": args.tangent_radius,
        "normal_radius": args.normal_radius,
        "normal_stabilization_kappa": args.kappa,
        "neumann_terms": args.neumann_terms,
        "stabilized_identity": (
            "d/dt[B(R3-c)]=-kappa*B(R3-c); the original projected "
            "field is unchanged on R3=c"
        ),
        "source_atlas_sha256": EXPECTED_ATLAS_SHA256,
        "source_v074_sha256": EXPECTED_V074_SOURCE_SHA256,
        "validated_ODE_claimed_before_audit": False,
    }
    protocol_hash = hashlib.sha256(canonical_json(protocol)).hexdigest()
    write_json(output / "protocol.json", protocol)

    print(f"\n{TITLE} v{VERSION}")
    print(json.dumps(protocol, indent=2))
    print(f"protocol_sha256 = {protocol_hash}")
    started = time.time()
    with tempfile.TemporaryDirectory(prefix="response_fibre_v090_") as tmp:
        patched = Path(tmp) / "_v090_backend.py"
        frozen = source_path.read_bytes()
        patched.write_text(patch_frozen_source(frozen), encoding="utf-8")
        env = dict(os.environ)
        env.update(
            {
                "V090_CHILD_INDEX": str(args.child_index),
                "V090_TANGENT_RADIUS": str(args.tangent_radius),
                "V090_NORMAL_RADIUS": str(args.normal_radius),
                "V090_KAPPA": str(args.kappa),
                "V090_NEUMANN_TERMS": str(args.neumann_terms),
                "V090_OUTPUT": str(output),
            }
        )
        completed = subprocess.run(
            [
                sys.executable,
                str(patched),
                "--inputs-zip",
                str(inputs_zip),
                "--chart",
                "9",
                "--subdivision",
                "32",
                "--output",
                str(output / "unused"),
            ],
            text=True,
            capture_output=True,
            env=env,
        )
        print(completed.stdout, end="")
        if completed.stderr:
            print(completed.stderr, file=sys.stderr, end="")
        if completed.returncode != 0:
            raise RuntimeError(f"v0.9.2 Arb backend exited {completed.returncode}")

    certificate = output / "centered_mean_value_krawczyk_certificate.json"
    if not certificate.is_file():
        raise RuntimeError("fibre-chart stabilized-ODE certificate was not produced")
    result = json.loads(certificate.read_text(encoding="utf-8"))
    result.update(
        {
            "protocol_sha256": protocol_hash,
            "generator_source_sha256": (
                sha256_file(Path(__file__)) if globals().get("__file__") else None
            ),
            "certificate_sha256": sha256_file(certificate),
            "elapsed_seconds_total": time.time() - started,
            "versions": {"python": platform.python_version(), "python_flint": "0.8.0"},
        }
    )
    write_json(output / "report.json", result)
    return 0


def main_v092() -> int:
    from decimal import Decimal, InvalidOperation

    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs-zip")
    parser.add_argument("--v074-source")
    parser.add_argument("--child-index", type=int, default=15)
    parser.add_argument(
        "--radii",
        default="1e-8",
        help=(
            "comma-separated tangent radii; the safe default runs only the "
            "first centered mean-value audit"
        ),
    )
    parser.add_argument(
        "--normal-ratio",
        default="1.0",
        help="normal_radius / tangent_radius for every rung",
    )
    parser.add_argument("--kappa", default="1.0")
    parser.add_argument("--neumann-terms", type=int, default=16)
    parser.add_argument("--no-download", action="store_true")
    parser.add_argument(
        "--output",
        default="response_fibre_centered_mean_value_krawczyk_v0_9_2_results",
    )
    args, ignored = parser.parse_known_args()
    if ignored:
        print(f"[notice] ignored notebook arguments: {ignored}")
    if not 0 <= args.child_index < 16:
        raise ValueError("--child-index must be between 0 and 15")
    try:
        radii = sorted({Decimal(item.strip()) for item in args.radii.split(",")})
        normal_ratio = Decimal(args.normal_ratio)
        kappa = Decimal(args.kappa)
    except InvalidOperation as exc:
        raise ValueError("invalid decimal radius, ratio, or kappa") from exc
    if not radii or any(value <= 0 for value in radii):
        raise ValueError("all declared radii must be positive")
    if normal_ratio <= 0 or kappa <= 0:
        raise ValueError("normal ratio and kappa must be positive")

    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    recovery = Path("/content") if Path("/content").is_dir() else output / "inputs"
    inputs_zip = acquire_exact_file(
        args.inputs_zip,
        [INPUTS_NAME, "response_fibre_v0_6_2_backend_inputs (1).zip"],
        recovery / INPUTS_NAME,
        f"{RAW_BASE}/inputs/{INPUTS_NAME}",
        EXPECTED_INPUTS_ZIP_SHA256,
        not args.no_download,
    )
    source_path = acquire_exact_file(
        args.v074_source,
        [SOURCE_NAME],
        recovery / SOURCE_NAME,
        f"{RAW_BASE}/src/{SOURCE_NAME}",
        EXPECTED_V074_SOURCE_SHA256,
        not args.no_download,
    )
    if atlas_hash_from_zip(inputs_zip) != EXPECTED_ATLAS_SHA256:
        raise RuntimeError("corrected atlas hash mismatch")

    protocol = {
        "title": TITLE,
        "version": VERSION,
        "implementation_revision": IMPLEMENTATION_REVISION,
        "formal_interval_arithmetic": True,
        "arb_precision_bits": 192,
        "purpose": (
            "certify a local tangent/normal fibre graph using a centered "
            "mean-value response increment with an exact zero constant term"
        ),
        "parameter_residual_identity": (
            "B(R(theta0+T*a)-R(theta0))="
            "integral_0^1 B*J(theta0+s*T*a)*T*a ds"
        ),
        "response_identity_proof": (
            "algebraic after Arb-certified invertibility of B and Jw*Jw^T; "
            "no cancellation-prone interval subtraction"
        ),
        "child_index": args.child_index,
        "tangent_radii": [str(value) for value in radii],
        "normal_radius_ratio": str(normal_ratio),
        "normal_stabilization_kappa": str(kappa),
        "neumann_terms": args.neumann_terms,
        "selection_rule": (
            "largest independently certified centered mean-value rung; no "
            "monotonicity is assumed"
        ),
        "source_atlas_sha256": EXPECTED_ATLAS_SHA256,
        "source_v074_sha256": EXPECTED_V074_SOURCE_SHA256,
        "validated_ODE_claimed_before_audit": False,
    }
    protocol_hash = hashlib.sha256(canonical_json(protocol)).hexdigest()
    write_json(output / "protocol.json", protocol)
    print("\n" + "=" * 120)
    print(f"{TITLE} v{VERSION}")
    print("=" * 120)
    print(json.dumps(protocol, indent=2))
    print(f"protocol_sha256 = {protocol_hash}")

    started = time.time()
    rung_results = []
    with tempfile.TemporaryDirectory(prefix="response_fibre_v091_") as tmp:
        patched = Path(tmp) / "_v091_backend.py"
        patched.write_text(
            patch_frozen_source(source_path.read_bytes()), encoding="utf-8"
        )
        for index, tangent_radius in enumerate(radii):
            normal_radius = tangent_radius * normal_ratio
            label = f"rung_{index + 1:02d}_{str(tangent_radius).replace('.', 'p')}"
            rung_output = output / label
            rung_output.mkdir(parents=True, exist_ok=True)
            env = dict(os.environ)
            env.update(
                {
                    "V090_CHILD_INDEX": str(args.child_index),
                    "V090_TANGENT_RADIUS": str(tangent_radius),
                    "V090_NORMAL_RADIUS": str(normal_radius),
                    "V090_KAPPA": str(kappa),
                    "V090_NEUMANN_TERMS": str(args.neumann_terms),
                    "V090_OUTPUT": str(rung_output),
                }
            )
            print("\n" + "-" * 120)
            print(
                f"[rung {index + 1:02d}/{len(radii):02d}] "
                f"tangent={tangent_radius} normal={normal_radius}"
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    str(patched),
                    "--inputs-zip",
                    str(inputs_zip),
                    "--chart",
                    "9",
                    "--subdivision",
                    "32",
                    "--output",
                    str(rung_output / "unused"),
                ],
                text=True,
                capture_output=True,
                env=env,
            )
            print(completed.stdout, end="")
            if completed.stderr:
                print(completed.stderr, file=sys.stderr, end="")
            certificate = (
                rung_output
                / "centered_mean_value_krawczyk_certificate.json"
            )
            if certificate.is_file():
                record = json.loads(certificate.read_text(encoding="utf-8"))
                certificate_hash = sha256_file(certificate)
            else:
                record = {
                    "scientific_status": "RADIUS_RUNG_BACKEND_FAILED",
                    "architecture_gates_pass": False,
                    "validated_ODE_claimed": False,
                    "error": f"backend exit={completed.returncode}; no certificate",
                }
                certificate_hash = None
            summary = {
                "rung_index": index,
                "tangent_radius": float(tangent_radius),
                "normal_radius": float(normal_radius),
                "architecture_gates_pass": bool(
                    record.get("architecture_gates_pass", False)
                ),
                "scientific_status": record.get("scientific_status"),
                "error": record.get("error"),
                "krawczyk_normal_box_utilization": record.get(
                    "krawczyk_normal_box_utilization"
                ),
                "centered_parameter_residual_upper": record.get(
                    "centered_parameter_residual_upper"
                ),
                "mean_value_tangent_derivative_inf_upper": record.get(
                    "mean_value_tangent_derivative_inf_upper"
                ),
                "tube_whitened_rank_defect_upper": record.get(
                    "tube_whitened_rank_defect_upper"
                ),
                "stabilized_identity_residual_upper": record.get(
                    "stabilized_identity_residual_upper"
                ),
                "certificate": str(certificate) if certificate.is_file() else None,
                "certificate_sha256": certificate_hash,
            }
            rung_results.append(summary)
            print(
                f"[rung result] architecture_pass="
                f"{summary['architecture_gates_pass']} "
                f"rank_defect={summary['tube_whitened_rank_defect_upper']} "
                f"krawczyk_util={summary['krawczyk_normal_box_utilization']}"
            )

    passing = [item for item in rung_results if item["architecture_gates_pass"]]
    largest = max(passing, key=lambda item: item["tangent_radius"]) if passing else None
    result = {
        "scientific_status": (
            "ARB_CENTERED_MEAN_VALUE_KRAWCZYK_SUPPORTED"
            if largest is not None
            else "ARB_CENTERED_MEAN_VALUE_KRAWCZYK_INCONCLUSIVE"
        ),
        "all_gates_pass": False,
        "centered_mean_value_krawczyk_supported": largest is not None,
        "formal_interval_arithmetic": True,
        "arb_precision_bits": 192,
        "validated_ODE_claimed": False,
        "ODE_existence_certified": False,
        "protocol_sha256": protocol_hash,
        "rungs_declared": len(radii),
        "rungs_tested": len(rung_results),
        "rungs_passing": len(passing),
        "largest_supported_tangent_radius": (
            largest["tangent_radius"] if largest else None
        ),
        "corresponding_normal_radius": (
            largest["normal_radius"] if largest else None
        ),
        "rung_results": rung_results,
        "elapsed_seconds": time.time() - started,
        "next_required_step": (
            "At the largest supported rung, construct the pulled-back metric "
            "and square-root-free six-dimensional tangent field, then close "
            "the first intrinsic Picard inclusion."
            if largest is not None
            else "The centered mean-value Krawczyk enclosure is still open. "
            "Inspect its parameter-residual and derivative-defect terms; "
            "do not return to independent response subtraction."
        ),
        "scope": (
            "single-child centered mean-value fibre-graph architecture "
            "preflight, optionally evaluated on a radius ladder; not a "
            "six-dimensional Picard theorem or global flow"
        ),
    }
    write_json(output / "centered_mean_value_krawczyk_report.json", result)
    print("\n" + "=" * 120)
    print("FINAL RESULT v0.9.2")
    print("=" * 120)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    code = main_v092()
    if code != 0:
        raise SystemExit(code)
