#!/usr/bin/env python3
"""C4-A: Arb certificate for the normal recovery core.

This standalone/Colab-friendly script reconstructs the documented 14-phase
response map and encloses it on a continuous parameter box with 256-bit Arb
ball arithmetic.  For the frozen binary64 right inverse Y of the centre
Jacobian it attempts to certify

    q = ||I - J(theta) Y||_inf < 1

uniformly on the box.  Consequently the recovery-only closed loop

    theta_dot = -beta Y (R(theta) - R_star)

satisfies, while the trajectory remains in the certified box,

    D^+ ||R(theta)-R_star||_inf <= -beta (1-q) ||R(theta)-R_star||_inf.

This is a rigorous recovery-core certificate, not the complete controlled
flow theorem: it does not certify the tangential objective term, saturation,
parameter-box invariance, global existence, K=1, Pulser, or QPU behaviour.

Colab dependency cell (run once, then restart the runtime if requested):
    %pip install -q "python-flint==0.8.0" "numpy==2.0.2"
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
    from flint import acb, arb, ctx
except ModuleNotFoundError as exc:
    raise RuntimeError(
        "python-flint is required. In Colab run: "
        "%pip install -q 'python-flint==0.8.0' 'numpy==2.0.2'"
    ) from exc


TITLE = "C4-A ARB RECOVERY-CORE CERTIFICATE"
VERSION = "1.0"
PRECISION_BITS = 256
OMEGA = 1.0
TAU = 0.62
NPHASE = 14
JET_ORDER = 6
RESPONSE_DIM = 8
BETA = 100.0
DEFAULT_RADIUS = 0.020
DEFAULT_REPORT = "c4_arb_recovery_core_certificate_v1_0.json"

REFERENCE_PHASES = np.array([
    3.006797722681818, 2.7106859720155914, 1.1306621045783265,
    -2.6568476957176808, 1.4365241820035193, -2.0773016506803064,
    0.16320548211467623, 3.089644890790571, -0.8755338801622679,
    -2.6500043472817922, 0.9588777193059705, -3.1075630669100938,
    0.7072945305932086, -0.48362649203822405,
], dtype=float)


def exact_float(x: float) -> arb:
    """Return the exact binary64 value as an Arb number."""
    n, d = float(x).as_integer_ratio()
    return arb(n) / arb(d)


def real_ball(mid: float, radius: float = 0.0) -> arb:
    return exact_float(mid) + arb(0, exact_float(radius))


def upper(x: arb) -> float:
    return float(x.upper())


def lower(x: arb) -> float:
    return float(x.lower())


def ball_record(x: arb) -> dict:
    lo, hi = lower(x), upper(x)
    return {"ball": str(x),
            "lower": lo if math.isfinite(lo) else None,
            "upper": hi if math.isfinite(hi) else None}


class FJet:
    """Floating complex jet used only to freeze the centre preconditioner."""
    def __init__(self, value=0):
        self.c = np.zeros(JET_ORDER + 1, dtype=complex)
        if isinstance(value, FJet):
            self.c[:] = value.c
        elif np.ndim(value) == 1:
            a = np.asarray(value, dtype=complex)
            self.c[:min(len(a), JET_ORDER + 1)] = a[:JET_ORDER + 1]
        else:
            self.c[0] = value

    def __add__(self, other):
        z = FJet(self); z.c += FJet(other).c; return z
    __radd__ = __add__
    def __neg__(self):
        z = FJet(self); z.c *= -1; return z
    def __sub__(self, other): return self + (-FJet(other))
    def __rsub__(self, other): return FJet(other) - self
    def __mul__(self, other):
        a, b, z = self.c, FJet(other).c, FJet()
        for n in range(JET_ORDER + 1):
            z.c[n] = sum(a[k] * b[n-k] for k in range(n + 1))
        return z
    __rmul__ = __mul__
    def inv(self):
        z = FJet(); z.c[0] = 1 / self.c[0]
        for n in range(1, JET_ORDER + 1):
            z.c[n] = -z.c[0] * sum(
                self.c[k] * z.c[n-k] for k in range(1, n + 1))
        return z
    def __truediv__(self, other): return self * FJet(other).inv()
    def __rtruediv__(self, other): return FJet(other) / self
    def sqrt(self):
        z = FJet(); z.c[0] = np.sqrt(self.c[0])
        for n in range(1, JET_ORDER + 1):
            z.c[n] = (self.c[n] - sum(
                z.c[k] * z.c[n-k] for k in range(1, n))) / (2 * z.c[0])
        return z
    def exp(self):
        z = FJet(); z.c[0] = np.exp(self.c[0])
        for n in range(1, JET_ORDER + 1):
            z.c[n] = sum(k * self.c[k] * z.c[n-k]
                         for k in range(1, n + 1)) / n
        return z
    def sin(self): return ((1j*self).exp() - (-1j*self).exp()) / (2j)
    def cos(self): return ((1j*self).exp() + (-1j*self).exp()) / 2


class BJet:
    """Complex Taylor jet whose coefficients are outward-rounded Acb balls."""
    def __init__(self, value=0):
        self.c = [acb(0) for _ in range(JET_ORDER + 1)]
        if isinstance(value, BJet):
            self.c = [acb(v) for v in value.c]
        elif isinstance(value, (list, tuple)):
            for i, v in enumerate(value[:JET_ORDER + 1]): self.c[i] = acb(v)
        else:
            self.c[0] = acb(value)

    def __add__(self, other):
        b = BJet(other); z = BJet()
        z.c = [self.c[i] + b.c[i] for i in range(JET_ORDER + 1)]; return z
    __radd__ = __add__
    def __neg__(self):
        z = BJet(); z.c = [-v for v in self.c]; return z
    def __sub__(self, other): return self + (-BJet(other))
    def __rsub__(self, other): return BJet(other) - self
    def __mul__(self, other):
        b, z = BJet(other), BJet()
        for n in range(JET_ORDER + 1):
            z.c[n] = sum((self.c[k] * b.c[n-k] for k in range(n + 1)), acb(0))
        return z
    __rmul__ = __mul__
    def inv(self):
        z = BJet(); z.c[0] = 1 / self.c[0]
        for n in range(1, JET_ORDER + 1):
            z.c[n] = -z.c[0] * sum(
                (self.c[k] * z.c[n-k] for k in range(1, n + 1)), acb(0))
        return z
    def __truediv__(self, other): return self * BJet(other).inv()
    def __rtruediv__(self, other): return BJet(other) / self
    def sqrt(self):
        z = BJet(); z.c[0] = self.c[0].sqrt()
        for n in range(1, JET_ORDER + 1):
            z.c[n] = (self.c[n] - sum(
                (z.c[k] * z.c[n-k] for k in range(1, n)), acb(0))) / (2*z.c[0])
        return z
    def exp(self):
        z = BJet(); z.c[0] = self.c[0].exp()
        for n in range(1, JET_ORDER + 1):
            z.c[n] = sum((k*self.c[k]*z.c[n-k]
                          for k in range(1, n + 1)), acb(0)) / n
        return z
    def sin(self): return ((acb(0, 1)*self).exp() - (acb(0, -1)*self).exp()) / acb(0, 2)
    def cos(self): return ((acb(0, 1)*self).exp() + (acb(0, -1)*self).exp()) / 2


def matvec2(matrix, vector):
    return [matrix[0][0]*vector[0] + matrix[0][1]*vector[1],
            matrix[1][0]*vector[0] + matrix[1][1]*vector[1]]


def nominal_state_float(phases):
    a = TAU * OMEGA / 2
    co, si = math.cos(a), math.sin(a) / OMEGA
    state = np.array([1+0j, 0+0j])
    for phi in phases:
        em, ep = np.exp(-1j*phi), np.exp(1j*phi)
        state = np.array([[co, -1j*si*OMEGA*em],
                          [-1j*si*OMEGA*ep, co]]) @ state
    return state / np.linalg.norm(state)


TARGET = nominal_state_float(REFERENCE_PHASES)
ORTHOGONAL = np.array([-TARGET[1].conjugate(), TARGET[0].conjugate()])


def projective_float(phases, mirror=False):
    delta = FJet([0, 1]); radius = (1 + delta*delta).sqrt()
    cosine = (radius*(TAU/2)).cos(); sine = (radius*(TAU/2)).sin()/radius
    state = [FJet(1), FJet(0)]
    deriv = [[FJet(0), FJet(0)] for _ in range(NPHASE)]
    for i, phi in enumerate(phases):
        em, ep = np.exp(-1j*phi), np.exp(1j*phi)
        if not mirror:
            m = [[cosine-1j*sine*delta, -1j*sine*em],
                 [-1j*sine*ep, cosine+1j*sine*delta]]
            dm = [[FJet(0), -sine*em], [sine*ep, FJet(0)]]
        else:
            m = [[cosine+1j*sine*delta, 1j*sine*ep],
                 [1j*sine*em, cosine-1j*sine*delta]]
            dm = [[FJet(0), -sine*ep], [sine*em, FJet(0)]]
        old, state = state, matvec2(m, state)
        new = []
        for j in range(NPHASE):
            value = matvec2(m, deriv[j])
            if j == i:
                local = matvec2(dm, old)
                value = [value[0]+local[0], value[1]+local[1]]
            new.append(value)
        deriv = new
    nw = ORTHOGONAL.conjugate() if not mirror else ORTHOGONAL
    dw = TARGET.conjugate() if not mirror else TARGET
    num = FJet(nw[0])*state[0] + FJet(nw[1])*state[1]
    den = FJet(dw[0])*state[0] + FJet(dw[1])*state[1]
    z, dz = num/den, []
    for d in deriv:
        dn = FJet(nw[0])*d[0] + FJet(nw[1])*d[1]
        dd = FJet(dw[0])*d[0] + FJet(dw[1])*d[1]
        dz.append((dn*den-num*dd)/(den*den))
    return z, dz


def centre_jacobian():
    _, dz = projective_float(REFERENCE_PHASES, False)
    _, dzb = projective_float(REFERENCE_PHASES, True)
    J = np.empty((RESPONSE_DIM, NPHASE))
    for k in range(4):
        for j in range(NPHASE):
            re = (dz[j].c[k] + dzb[j].c[k]) / 2
            im = (dz[j].c[k] - dzb[j].c[k]) / (2j)
            J[k, j], J[4+k, j] = re.real, im.real
    return J


def cb(z: complex) -> acb:
    return acb(exact_float(z.real), exact_float(z.imag))


def projective_ball(phases, mirror=False):
    delta = BJet([acb(0), acb(1)]); radius = (1 + delta*delta).sqrt()
    cosine = (radius*exact_float(TAU/2)).cos()
    sine = (radius*exact_float(TAU/2)).sin()/radius
    state = [BJet(1), BJet(0)]
    deriv = [[BJet(0), BJet(0)] for _ in range(NPHASE)]
    for i, phi in enumerate(phases):
        em, ep = acb(0, -phi).exp(), acb(0, phi).exp()
        if not mirror:
            m = [[cosine-acb(0,1)*sine*delta, -acb(0,1)*sine*em],
                 [-acb(0,1)*sine*ep, cosine+acb(0,1)*sine*delta]]
            dm = [[BJet(0), -sine*em], [sine*ep, BJet(0)]]
        else:
            m = [[cosine+acb(0,1)*sine*delta, acb(0,1)*sine*ep],
                 [acb(0,1)*sine*em, cosine-acb(0,1)*sine*delta]]
            dm = [[BJet(0), -sine*ep], [sine*em, BJet(0)]]
        old, state = state, matvec2(m, state)
        new = []
        for j in range(NPHASE):
            value = matvec2(m, deriv[j])
            if j == i:
                local = matvec2(dm, old)
                value = [value[0]+local[0], value[1]+local[1]]
            new.append(value)
        deriv = new
    nw = ORTHOGONAL.conjugate() if not mirror else ORTHOGONAL
    dw = TARGET.conjugate() if not mirror else TARGET
    num = BJet(cb(nw[0]))*state[0] + BJet(cb(nw[1]))*state[1]
    den = BJet(cb(dw[0]))*state[0] + BJet(cb(dw[1]))*state[1]
    z, dz = num/den, []
    for d in deriv:
        dn = BJet(cb(nw[0]))*d[0] + BJet(cb(nw[1]))*d[1]
        dd = BJet(cb(dw[0]))*d[0] + BJet(cb(dw[1]))*d[1]
        dz.append((dn*den-num*dd)/(den*den))
    return z, dz, den.c[0]


def interval_jacobian(radius):
    phases = [real_ball(x, radius) for x in REFERENCE_PHASES]
    _, dz, den = projective_ball(phases, False)
    _, dzb, denb = projective_ball(phases, True)
    J = [[arb(0) for _ in range(NPHASE)] for _ in range(RESPONSE_DIM)]
    for k in range(4):
        for j in range(NPHASE):
            re = (dz[j].c[k] + dzb[j].c[k]) / 2
            im = (dz[j].c[k] - dzb[j].c[k]) / acb(0, 2)
            J[k][j], J[4+k][j] = re.real, im.real
    return J, den, denb


def matmul(A, B):
    rows, inner, cols = len(A), len(B), len(B[0])
    return [[sum((A[i][k]*B[k][j] for k in range(inner)), arb(0))
             for j in range(cols)] for i in range(rows)]


def inf_norm(A):
    row_sums = [sum((abs(x) for x in row), arb(0)) for row in A]
    return max(row_sums, key=upper), row_sums


def main(argv=None):
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--radius", type=float, default=DEFAULT_RADIUS)
    parser.add_argument("--report", default=DEFAULT_REPORT)
    args, unknown = parser.parse_known_args(argv)
    if unknown:
        print("[notice] ignored notebook/kernel arguments:", unknown)
    if not (0 < args.radius <= 0.1):
        raise ValueError("--radius must lie in (0, 0.1]")

    ctx.prec = PRECISION_BITS
    J0 = centre_jacobian()
    # Frozen binary64 Moore-Penrose right inverse. Every entry is subsequently
    # reconstructed exactly as a rational binary64 number in Arb.
    Y0 = J0.T @ np.linalg.inv(J0 @ J0.T)
    Y = [[exact_float(Y0[i, j]) for j in range(RESPONSE_DIM)]
         for i in range(NPHASE)]

    protocol = {
        "version": VERSION,
        "precision_bits": PRECISION_BITS,
        "radius": args.radius,
        "domain": "axis-aligned 14-phase box theta_ref + [-radius,radius]^14",
        "beta": BETA,
        "controller": "theta_dot=-beta*Y0*(R(theta)-R_star)",
        "preconditioner": "frozen binary64 right inverse; exact rational reconstruction in Arb",
        "criterion": "q=||I-J(box)Y0||_inf<1",
        "model": "documented 14-segment driven-qubit projective response, orders 0..3",
    }
    phash = hashlib.sha256(json.dumps(
        protocol, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    print("=" * 88)
    print(f"{TITLE} v{VERSION}")
    print("=" * 88)
    print("scope: rigorous recovery core on a continuous phase box; not complete C4/QPU evidence")
    print("protocol sha256:", phash)
    print("radius:", args.radius, "precision:", PRECISION_BITS, "bits")

    try:
        Jbox, den, denb = interval_jacobian(args.radius)
        JY = matmul(Jbox, Y)
        defect = [[(arb(1) if i == j else arb(0)) - JY[i][j]
                   for j in range(RESPONSE_DIM)] for i in range(RESPONSE_DIM)]
        q, rows = inf_norm(defect)
        q_up = upper(q)
        contraction = arb(BETA) * (arb(1) - q)
        # abs(z).lower()>0 is the relevant nonvanishing test.  Merely asking
        # whether an Acb disc contains the exact point 0 can be weaker when its
        # rectangular absolute-value enclosure touches zero.
        denominator_ok = lower(abs(den)) > 0.0 and lower(abs(denb)) > 0.0
        regularity_ok = math.isfinite(q_up) and q_up < 1.0
        contraction_lo = lower(contraction)
        contraction_ok = math.isfinite(contraction_lo) and contraction_lo > 0.0
        gates = {
            "projective_denominators_exclude_zero": bool(denominator_ok),
            "uniform_right_inverse_defect_below_one": bool(regularity_ok),
            "positive_lyapunov_contraction_rate": bool(contraction_ok),
        }
        certified = all(gates.values())
        status = "C4_A_RECOVERY_CORE_CERTIFIED" if certified else "C4_A_INCONCLUSIVE"
        result = {
            "title": TITLE, "version": VERSION,
            "protocol": protocol, "protocol_sha256": phash,
            "frozen_preconditioner_hex": [[float(v).hex() for v in row] for row in Y0],
            "bounds": {
                "forward_projective_denominator_abs": ball_record(abs(den)),
                "mirror_projective_denominator_abs": ball_record(abs(denb)),
                "right_inverse_defect_inf_norm": ball_record(q),
                "defect_row_sums": [ball_record(x) for x in rows],
                "lyapunov_contraction_rate_lower_bound": ball_record(contraction),
            },
            "gates": gates, "all_gates_pass": certified,
            "scientific_status": status,
            "claim_boundary": (
                "Rigorous 256-bit Arb certificate for the recovery-only normal controller "
                "while trajectories remain in the declared phase box. It does not certify "
                "the tangential descent term, saturation, phase-box invariance, global flow, "
                "K=1, Pulser, cloud, hardware, or QPU behaviour."
            ),
            "environment": {"python": platform.python_version(),
                            "numpy": np.__version__, "python_flint": "0.8.0-compatible"},
        }
    except Exception as exc:
        # Arithmetic failure/indeterminate intervals are inconclusive, never a
        # negative theorem and never a certificate.
        result = {
            "title": TITLE, "version": VERSION,
            "protocol": protocol, "protocol_sha256": phash,
            "gates": {}, "all_gates_pass": False,
            "scientific_status": "C4_A_INCONCLUSIVE",
            "error_type": type(exc).__name__, "error": str(exc),
            "claim_boundary": "No certificate was emitted.",
        }

    Path(args.report).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result.get(k) for k in
          ("bounds", "gates", "all_gates_pass", "scientific_status", "error_type", "error")
          if k in result}, indent=2))
    print("report:", args.report)
    return 0 if result["all_gates_pass"] else 2


if __name__ == "__main__":
    code = main()
    if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:
        raise SystemExit(code)
