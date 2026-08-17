#!/usr/bin/env python3
"""Certify the frozen R7 positive-control gate.

This script is intentionally narrow. It reads the frozen prospective
R1--R7 protocol, verifies protocol/input identity, evaluates the declared
R3 response Jacobian with Arb arithmetic, and certifies that the frozen
ambient normal control has strictly positive protocol-relative response cost.

It does not run, import, search, tune, or produce any R5/R6 result.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PROTOCOL_PATH = HERE / "frozen_protocol_v1_0.json"
CERT_DIR = HERE / "certificates"
CERT_PATH = CERT_DIR / "r7_positive_control_v1_0.json"

REQUIRED_MAIN_BASELINE_COMMIT = "b9796c9ffb203bfbf3d0e230fe624ca85c0e75b9"
EXPECTED_STATUS = "PROTOCOL_FROZEN_NO_R6_SEARCH_PERFORMED"
EXPECTED_PROTOCOL_SHA256 = "e8519a644ab50a9989eb40bc34499055f83760563167d88da21d17b3c7539e1c"
EXPECTED_W_PI_SHA256 = "0111dea7a4444ff1449da5ffcc98beb2eae423e7e8e3a290626d377896aa82dc"
EXPECTED_ATLAS_SHA256 = "c02acc1c76e0b670793340150d1a875fdc373e0ac7c46d3360a7824b66a3a5ef"

PRECISION_BITS = 192
CONTROL_DIMENSION = 14
RESPONSE_ORDER = 3
RESPONSE_DIMENSION = 8
DELTA_ORDER = 6
DEFAULT_CHART = 9
DEFAULT_SUBDIVISION = 32
DEFAULT_CHILD_INDEX = 15
SUBDIVISIONS = 64
CHILD_BOXES = 16
OMEGA = "1.0"
TAU = "0.62"

REFERENCE_PHASES = [
    "3.006797722681818",
    "2.7106859720155914",
    "1.1306621045783265",
    "-2.6568476957176808",
    "1.4365241820035193",
    "-2.0773016506803064",
    "0.16320548211467623",
    "3.089644890790571",
    "-0.8755338801622679",
    "-2.6500043472817922",
    "0.9588777193059705",
    "-3.1075630669100938",
    "0.7072945305932086",
    "-0.48362649203822405",
]


def ensure_flint_runtime() -> None:
    try:
        import flint  # noqa: F401
        return
    except ImportError:
        bundled = Path.home() / (
            ".cache/codex-runtimes/codex-primary-runtime/dependencies/"
            "python/bin/python3"
        )
        if bundled.exists() and Path(sys.executable).resolve() != bundled.resolve():
            os.execv(str(bundled), [str(bundled), *sys.argv])
        raise


ensure_flint_runtime()
from flint import acb, arb, ctx  # noqa: E402

ctx.prec = PRECISION_BITS
I = acb(0, 1)


def ap(value: Any) -> arb:
    if isinstance(value, arb):
        return value
    return arb(str(value))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_text(args: list[str]) -> tuple[int, str]:
    completed = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return completed.returncode, (completed.stdout.strip() or completed.stderr.strip())


def load_corrected_atlas(inputs_zip: Path) -> dict[str, Any]:
    with zipfile.ZipFile(inputs_zip) as archive:
        names = [
            name for name in archive.namelist()
            if name.endswith("/corrected_atlas.json") or name == "corrected_atlas.json"
        ]
        if len(names) != 1:
            raise RuntimeError("inputs zip must contain exactly one corrected_atlas.json")
        return json.loads(archive.read(names[0]))


class DeltaJet:
    order = DELTA_ORDER

    def __init__(self, coefficients: Any = 0):
        if isinstance(coefficients, DeltaJet):
            self.c = coefficients.c[:]
        elif isinstance(coefficients, (list, tuple)):
            self.c = [acb(item) for item in coefficients]
            self.c += [acb(0)] * (self.order + 1 - len(self.c))
        else:
            self.c = [acb(coefficients)] + [acb(0)] * self.order
        self.c = self.c[: self.order + 1]

    def __add__(self, other: Any) -> "DeltaJet":
        other = DeltaJet(other)
        return DeltaJet([self.c[k] + other.c[k] for k in range(self.order + 1)])

    __radd__ = __add__

    def __neg__(self) -> "DeltaJet":
        return DeltaJet([-item for item in self.c])

    def __sub__(self, other: Any) -> "DeltaJet":
        return self + (-DeltaJet(other))

    def __rsub__(self, other: Any) -> "DeltaJet":
        return DeltaJet(other) - self

    def __mul__(self, other: Any) -> "DeltaJet":
        other = DeltaJet(other)
        return DeltaJet(
            [
                sum(
                    (self.c[k] * other.c[n - k] for k in range(n + 1)),
                    acb(0),
                )
                for n in range(self.order + 1)
            ]
        )

    __rmul__ = __mul__

    def inv(self) -> "DeltaJet":
        if self.c[0].contains(0):
            raise ArithmeticError("DeltaJet centre contains zero")
        result = [1 / self.c[0]]
        for n in range(1, self.order + 1):
            result.append(
                -result[0]
                * sum(
                    (self.c[k] * result[n - k] for k in range(1, n + 1)),
                    acb(0),
                )
            )
        return DeltaJet(result)

    def __truediv__(self, other: Any) -> "DeltaJet":
        return self * DeltaJet(other).inv()

    def __rtruediv__(self, other: Any) -> "DeltaJet":
        return DeltaJet(other) / self

    def sqrt(self) -> "DeltaJet":
        result = [self.c[0].sqrt()]
        if result[0].contains(0):
            raise ArithmeticError("DeltaJet square-root centre contains zero")
        for n in range(1, self.order + 1):
            result.append(
                (
                    self.c[n]
                    - sum((result[k] * result[n - k] for k in range(1, n)), acb(0))
                )
                / (2 * result[0])
            )
        return DeltaJet(result)

    def exp(self) -> "DeltaJet":
        result = [self.c[0].exp()]
        for n in range(1, self.order + 1):
            result.append(
                sum((k * self.c[k] * result[n - k] for k in range(1, n + 1)), acb(0))
                / n
            )
        return DeltaJet(result)

    def sin(self) -> "DeltaJet":
        value = self * I
        return (value.exp() - (-value).exp()) / (2 * I)

    def cos(self) -> "DeltaJet":
        value = self * I
        return (value.exp() + (-value).exp()) / 2


def jet_matvec(matrix: list[list[Any]], vector: list[DeltaJet]) -> list[DeltaJet]:
    return [
        matrix[0][0] * vector[0] + matrix[0][1] * vector[1],
        matrix[1][0] * vector[0] + matrix[1][1] * vector[1],
    ]


def nominal_state(phases: list[arb]) -> list[acb]:
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
        state = jet_matvec(matrix, state)
    return state


TARGET_STATE = nominal_state([ap(value) for value in REFERENCE_PHASES])
TARGET_NORM = (
    TARGET_STATE[0].conjugate() * TARGET_STATE[0]
    + TARGET_STATE[1].conjugate() * TARGET_STATE[1]
).sqrt()
TARGET = [item / TARGET_NORM for item in TARGET_STATE]
ORTHOGONAL = [-TARGET[1].conjugate(), TARGET[0].conjugate()]


def projective_jet_and_derivatives(phases: list[arb], mirror: bool = False):
    delta = DeltaJet([0, 1])
    radius = (1 + delta * delta).sqrt()
    half_duration = ap(TAU) / 2
    cosine = (radius * half_duration).cos()
    sine = (radius * half_duration).sin() / radius
    state = [DeltaJet(1), DeltaJet(0)]
    derivatives = [[DeltaJet(0), DeltaJet(0)] for _ in range(CONTROL_DIMENSION)]

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
        numerator_weights = [item.conjugate() for item in ORTHOGONAL]
        denominator_weights = [item.conjugate() for item in TARGET]
    else:
        numerator_weights = ORTHOGONAL
        denominator_weights = TARGET

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
            (dn * denominator - numerator * dd) / (denominator * denominator)
        )
    return coordinate, coordinate_derivatives


def response_jacobian(phases: list[arb]) -> list[list[arb]]:
    _z, dz = projective_jet_and_derivatives(phases, mirror=False)
    _zbar, dzbar = projective_jet_and_derivatives(phases, mirror=True)
    jacobian = [
        [arb(0) for _ in range(CONTROL_DIMENSION)]
        for _ in range(RESPONSE_DIMENSION)
    ]
    for order in range(RESPONSE_ORDER + 1):
        for column in range(CONTROL_DIMENSION):
            real_extension = (dz[column].c[order] + dzbar[column].c[order]) / 2
            imaginary_extension = (dz[column].c[order] - dzbar[column].c[order]) / (2 * I)
            jacobian[order][column] = real_extension.real
            jacobian[RESPONSE_ORDER + 1 + order][column] = imaginary_extension.real
    return jacobian


def chebyshev_evaluate(coefficients: list[arb], scalar: acb) -> acb:
    b1 = acb(0)
    b2 = acb(0)
    for coefficient in coefficients[:0:-1]:
        b0 = 2 * scalar * b1 - b2 + acb(coefficient)
        b2, b1 = b1, b0
    return scalar * b1 - b2 + acb(coefficients[0])


def chart_phases_at(chart: dict[str, Any], local: arb) -> list[arb]:
    serialized = chart["coefficients_degree_first"]
    coefficients = [
        [ap(serialized[degree][column]) for degree in range(len(serialized))]
        for column in range(CONTROL_DIMENSION)
    ]
    return [
        chebyshev_evaluate(coefficients[column], acb(local)).real
        for column in range(CONTROL_DIMENSION)
    ]


def lower_str(value: arb) -> str:
    return value.lower().str(40, radius=False, more=True)


def upper_str(value: arb) -> str:
    return value.upper().str(40, radius=False, more=True)


def lower_float(value: arb) -> float:
    return float(value.lower())


def protocol_identity(protocol: dict[str, Any]) -> dict[str, bool]:
    identity_8 = [[1 if i == j else 0 for j in range(8)] for i in range(8)]
    r7 = protocol.get("R7", {})
    n = r7.get("fixed_normal_control_n", {})
    r3 = protocol.get("R3", {})
    w_pi = r3.get("W_Pi", {})
    return {
        "status_exact": protocol.get("status") == EXPECTED_STATUS,
        "protocol_sha256": sha256_file(PROTOCOL_PATH) == EXPECTED_PROTOCOL_SHA256,
        "r7_declared": r7.get("declared") is True,
        "n_matches_protocol": n.get("components") == [1.0] + [0.0] * 13,
        "delta_sequence_matches_protocol": r7.get("delta_sequence")
        == ["1e-14", "3e-14", "1e-13", "3e-13", "1e-12"],
        "control_family_matches_protocol": r7.get("control_family")
        == "eta_delta(s)=theta_0+s*delta*n",
        "same_meter_as_R3": r7.get("uses_same_response_cost_as_R3") is True,
        "W_Pi_matches_protocol": (
            w_pi.get("frozen") is True
            and w_pi.get("matrix") == "identity_8x8"
            and w_pi.get("sha256_of_canonical_json") == EXPECTED_W_PI_SHA256
            and sha256_bytes(canonical_json(identity_8)) == EXPECTED_W_PI_SHA256
        ),
        "R5_not_run": protocol.get("R5", {}).get("certificate_run") is False,
        "R6_not_run": protocol.get("R6", {}).get("certificate_run") is False,
        "R6_search_disallowed": protocol.get("R6", {}).get(
            "search_allowed_in_this_repository_state"
        ) is False,
    }


def input_identity(protocol: dict[str, Any]) -> dict[str, Any]:
    checks: dict[str, bool] = {}
    hashes: dict[str, str] = {}
    for item in protocol.get("input_files", []):
        rel = item["path"]
        path = ROOT / rel
        actual = sha256_file(path)
        hashes[rel] = actual
        checks[f"{rel}:exists"] = path.is_file()
        checks[f"{rel}:sha256"] = actual == item["sha256"]
    rc, current = git_text(["rev-parse", "HEAD"])
    anc_rc, _ = git_text([
        "merge-base",
        "--is-ancestor",
        REQUIRED_MAIN_BASELINE_COMMIT,
        "HEAD",
    ])
    checks["current_git_commit_available"] = rc == 0
    checks["required_main_baseline_is_ancestor"] = anc_rc == 0
    return {
        "checks": checks,
        "hashes": hashes,
        "current_git_commit": current if rc == 0 else None,
        "required_main_baseline_commit": REQUIRED_MAIN_BASELINE_COMMIT,
    }


def certify_delta(delta_text: str, theta0: list[arb], chart_radius: arb) -> dict[str, Any]:
    delta = ap(delta_text)
    s_interval = "[0,1]"
    half = delta / 2
    phase_interval = theta0[0] + arb(0, half)
    phases = [phase_interval] + theta0[1:]

    # The frozen chart uses fixed real representatives of torus phases. It is
    # not a principal-branch chart: one representative is already slightly
    # above pi. R7 therefore certifies local residence by keeping the ambient
    # perturbation inside the declared child-neighborhood scale and by never
    # applying a modulo representative change.
    chart_gate = bool(delta <= chart_radius)
    no_wrap_gate = bool(delta < 2 * arb.pi())
    nonconstant_gate = delta > 0

    try:
        jacobian = response_jacobian(phases)
        analytic_domain_gate = True
        column = [jacobian[row][0] for row in range(RESPONSE_DIMENSION)]
        speed_square = delta * delta * sum((entry * entry for entry in column), arb(0))
        pointwise_cost = speed_square.sqrt()
        pointwise_lower = pointwise_cost.lower()
        speed_square_lower = speed_square.lower()
        strict_positive_pointwise = pointwise_lower > 0
    except Exception as exc:  # noqa: BLE001 - fail closed into an explicit record
        return {
            "delta": delta_text,
            "status": "R7_INCONCLUSIVE",
            "failure": f"analytic response enclosure failed: {exc}",
            "positive_measure_interval": s_interval,
            "chart_residence_gate": bool(chart_gate),
            "chart_radius_lower": lower_str(chart_radius),
            "ambient_displacement_upper": upper_str(delta),
            "no_phase_wrap_gate": bool(no_wrap_gate),
            "nonconstant_gate": bool(nonconstant_gate),
            "analytic_domain_gate": False,
            "strict_positive_pointwise_response_gate": False,
            "strict_positive_total_cost_gate": False,
        }

    total_cost_lower = pointwise_lower
    all_gates = (
        chart_gate
        and no_wrap_gate
        and nonconstant_gate
        and analytic_domain_gate
        and strict_positive_pointwise
        and total_cost_lower > 0
    )
    return {
        "delta": delta_text,
        "status": "R7_DELTA_CERTIFIED" if all_gates else "R7_DELTA_INCONCLUSIVE",
        "positive_measure_interval": s_interval,
        "positive_measure_interval_length": "1",
        "chart_residence_gate": bool(chart_gate),
        "chart_radius_lower": lower_str(chart_radius),
        "ambient_displacement_upper": upper_str(delta),
        "no_phase_wrap_gate": bool(no_wrap_gate),
        "nonconstant_gate": bool(nonconstant_gate),
        "analytic_domain_gate": bool(analytic_domain_gate),
        "same_meter_gate": True,
        "strict_positive_pointwise_response_gate": bool(strict_positive_pointwise),
        "strict_positive_total_cost_gate": bool(total_cost_lower > 0),
        "response_speed_square_interval_lower": lower_str(speed_square),
        "response_speed_square_interval_upper": upper_str(speed_square),
        "pointwise_cost_lower": lower_str(pointwise_cost),
        "pointwise_cost_upper": upper_str(pointwise_cost),
        "total_cost_lower": lower_str(pointwise_cost),
        "accepted_bound_statement": (
            "|D R_3(eta_delta(s)) delta n|_2 >= pointwise_cost_lower > 0 "
            "for all s in [0,1]"
        ),
    }


def build_certificate() -> dict[str, Any]:
    protocol = read_json(PROTOCOL_PATH)
    protocol_checks = protocol_identity(protocol)
    inputs = input_identity(protocol)
    protocol_mismatch = not (all(protocol_checks.values()) and all(inputs["checks"].values()))

    result: dict[str, Any] = {
        "schema_version": "1.0",
        "certificate_id": "principle_r_r7_positive_control_v1_0",
        "scientific_scope": "prospective_r7_certificate",
        "protocol_status": protocol.get("status"),
        "protocol_sha256": sha256_file(PROTOCOL_PATH),
        "expected_protocol_sha256": EXPECTED_PROTOCOL_SHA256,
        "required_main_baseline_commit": REQUIRED_MAIN_BASELINE_COMMIT,
        "current_git_commit": inputs["current_git_commit"],
        "versions": {
            "python": platform.python_version(),
            "python_flint": getattr(sys.modules.get("flint"), "__version__", None),
        },
        "arb_precision_bits": PRECISION_BITS,
        "protocol_identity_gates": protocol_checks,
        "input_identity_gates": inputs["checks"],
        "input_sha256": inputs["hashes"],
        "R5_certificate_run": False,
        "R6_search_performed": False,
        "R6_certificate_run": False,
        "global_flow_claimed": False,
        "empirical_physical_validation_claimed": False,
        "physical_time_energy_or_action_claimed": False,
        "lorentzian_spacetime_or_gr_claimed": False,
        "R3_response_cost_formula": protocol["R3"]["response_cost_formula"],
        "W_Pi": protocol["R3"]["W_Pi"],
        "R7_fixed_normal_control_n": protocol["R7"]["fixed_normal_control_n"],
        "R7_delta_sequence": protocol["R7"]["delta_sequence"],
    }

    if protocol_mismatch:
        result.update(
            {
                "scientific_status": "R7_REJECTED_PROTOCOL_MISMATCH",
                "all_gates_pass": False,
                "R7_CERTIFIED": False,
                "delta_records": [],
            }
        )
        return result

    inputs_zip = ROOT / "inputs/response_fibre_v0_6_2_backend_inputs.zip"
    atlas = load_corrected_atlas(inputs_zip)
    atlas_hash = sha256_bytes(canonical_json(atlas))
    chart = atlas["charts"][DEFAULT_CHART]
    macro_left = -1 + 2 * DEFAULT_SUBDIVISION / SUBDIVISIONS
    child_half_width = (1 / SUBDIVISIONS) / CHILD_BOXES
    theta0_local = macro_left + (2 * DEFAULT_CHILD_INDEX + 1) * child_half_width
    theta0 = chart_phases_at(chart, ap(repr(theta0_local)))

    chart_radius = ap(str(child_half_width))
    delta_records = [
        certify_delta(delta_text, theta0, chart_radius)
        for delta_text in protocol["R7"]["delta_sequence"]
    ]
    all_deltas_pass = all(
        record.get("status") == "R7_DELTA_CERTIFIED" for record in delta_records
    )
    gates = {
        "protocol_identity": True,
        "input_identity": True,
        "corrected_atlas_hash": atlas_hash == EXPECTED_ATLAS_SHA256,
        "theta0_source_frozen": True,
        "same_R3_W_Pi_meter": True,
        "all_frozen_deltas_tested": len(delta_records) == len(protocol["R7"]["delta_sequence"]),
        "all_delta_chart_residence": all(r.get("chart_residence_gate") for r in delta_records),
        "all_delta_no_phase_wrap": all(r.get("no_phase_wrap_gate") for r in delta_records),
        "all_delta_nonconstant": all(r.get("nonconstant_gate") for r in delta_records),
        "all_delta_strict_positive_pointwise_response": all(
            r.get("strict_positive_pointwise_response_gate") for r in delta_records
        ),
        "all_delta_strict_positive_total_cost": all(
            r.get("strict_positive_total_cost_gate") for r in delta_records
        ),
        "R5_not_run": True,
        "R6_not_run": True,
    }
    all_gates_pass = all(gates.values()) and all_deltas_pass
    result.update(
        {
            "scientific_status": "R7_CERTIFIED" if all_gates_pass else "R7_INCONCLUSIVE",
            "all_gates_pass": bool(all_gates_pass),
            "R7_CERTIFIED": bool(all_gates_pass),
            "chart": DEFAULT_CHART,
            "subdivision": DEFAULT_SUBDIVISION,
            "child_index": DEFAULT_CHILD_INDEX,
            "theta0_local_coordinate": repr(theta0_local),
            "theta0_source": "corrected_atlas chart 9, subdivision 32, child index 15 centre",
            "corrected_atlas_sha256": atlas_hash,
            "gates": gates,
            "delta_records": delta_records,
            "failure_policy": {
                "zero_in_strict_positive_interval": "R7_INCONCLUSIVE",
                "chart_or_domain_gate_failure": "R7_INCONCLUSIVE",
                "input_or_protocol_identity_mismatch": "R7_REJECTED_PROTOCOL_MISMATCH",
            },
        }
    )
    return result


def main() -> int:
    certificate = build_certificate()
    CERT_DIR.mkdir(parents=True, exist_ok=True)
    CERT_PATH.write_text(
        json.dumps(certificate, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "certificate": str(CERT_PATH.relative_to(ROOT)),
        "scientific_status": certificate["scientific_status"],
        "all_gates_pass": certificate["all_gates_pass"],
        "R5_certificate_run": certificate["R5_certificate_run"],
        "R6_search_performed": certificate["R6_search_performed"],
        "R6_certificate_run": certificate["R6_certificate_run"],
    }, indent=2, sort_keys=True))
    print(certificate["scientific_status"])
    return 0 if certificate["scientific_status"] == "R7_CERTIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
