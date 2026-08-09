#!/usr/bin/env python3
"""Normally attracting response-fibre flow: real 14-phase model preflight v1.1.

Numerical prospective test only. It reconstructs the documented Geometric-Flow
14-segment driven-qubit model without importing its proof engine. It is not an
Arb certificate, K=1/Law-III derivation, Pulser test, or QPU result.
"""
from __future__ import annotations

import hashlib
import json
import math
import platform
import sys
from pathlib import Path

import numpy as np

TITLE = "NORMALLY ATTRACTING RESPONSE-FIBRE FLOW -- REAL 14-PHASE PREFLIGHT"
VERSION = "1.1"
OMEGA = 1.0
TAU = 0.62
NPHASE = 14
JET_ORDER = 6
RESPONSE_ORDER = 3
RESPONSE_DIM = 8

REFERENCE_PHASES = np.array([
    3.006797722681818, 2.7106859720155914, 1.1306621045783265,
    -2.6568476957176808, 1.4365241820035193, -2.0773016506803064,
    0.16320548211467623, 3.089644890790571, -0.8755338801622679,
    -2.6500043472817922, 0.9588777193059705, -3.1075630669100938,
    0.7072945305932086, -0.48362649203822405,
], dtype=float)

SEED = 20260809
BETA = 100.0
PERTURBATION_SCALES = (1e-4, 3e-4, 1e-3)
TRIALS_PER_SCALE = 1                 # tangent + normal + mixed => 9 trials
FLOW_TIME = 0.1
STEPS = 80
SVD_RCOND = 1e-11
REPORT = "normally_attracting_response_fibre_real_model_v1_1_report.json"


class Jet:
    """Truncated complex Taylor series with ordinary-power coefficients."""
    def __init__(self, x=0):
        if isinstance(x, Jet):
            self.c = x.c.copy()
        elif np.ndim(x) == 1:
            self.c = np.zeros(JET_ORDER + 1, complex)
            a = np.asarray(x, complex)
            self.c[:min(len(a), JET_ORDER + 1)] = a[:JET_ORDER + 1]
        else:
            self.c = np.zeros(JET_ORDER + 1, complex)
            self.c[0] = x

    def __add__(self, other):
        z = Jet(self); z.c += Jet(other).c; return z
    __radd__ = __add__
    def __neg__(self):
        z = Jet(self); z.c *= -1; return z
    def __sub__(self, other): return self + (-Jet(other))
    def __rsub__(self, other): return Jet(other) - self
    def __mul__(self, other):
        a, b = self.c, Jet(other).c
        z = Jet()
        for n in range(JET_ORDER + 1):
            z.c[n] = sum(a[k] * b[n-k] for k in range(n+1))
        return z
    __rmul__ = __mul__
    def inv(self):
        if abs(self.c[0]) < 1e-14: raise FloatingPointError("singular jet")
        z = Jet(); z.c[0] = 1 / self.c[0]
        for n in range(1, JET_ORDER + 1):
            z.c[n] = -z.c[0] * sum(self.c[k]*z.c[n-k] for k in range(1,n+1))
        return z
    def __truediv__(self, other): return self * Jet(other).inv()
    def __rtruediv__(self, other): return Jet(other) / self
    def sqrt(self):
        z = Jet(); z.c[0] = np.sqrt(self.c[0])
        if abs(z.c[0]) < 1e-14: raise FloatingPointError("singular sqrt jet")
        for n in range(1, JET_ORDER + 1):
            z.c[n] = (self.c[n] - sum(z.c[k]*z.c[n-k] for k in range(1,n))) / (2*z.c[0])
        return z
    def exp(self):
        z = Jet(); z.c[0] = np.exp(self.c[0])
        for n in range(1, JET_ORDER + 1):
            z.c[n] = sum(k*self.c[k]*z.c[n-k] for k in range(1,n+1))/n
        return z
    def sin(self): return ((1j*self).exp() - (-1j*self).exp())/(2j)
    def cos(self): return ((1j*self).exp() + (-1j*self).exp())/2


def matvec(m, v):
    return [m[0][0]*v[0] + m[0][1]*v[1], m[1][0]*v[0] + m[1][1]*v[1]]


def nominal_state(phases):
    a = TAU*OMEGA/2
    co, si = math.cos(a), math.sin(a)/OMEGA
    state = np.array([1+0j, 0+0j])
    for phi in phases:
        em, ep = np.exp(-1j*phi), np.exp(1j*phi)
        u = np.array([[co, -1j*si*OMEGA*em],[-1j*si*OMEGA*ep, co]])
        state = u @ state
    return state


TARGET = nominal_state(REFERENCE_PHASES)
TARGET /= np.linalg.norm(TARGET)
ORTHOGONAL = np.array([-TARGET[1].conjugate(), TARGET[0].conjugate()])


def projective_jet_and_derivatives(phases, mirror=False):
    delta = Jet([0,1])
    radius = (1 + delta*delta).sqrt()
    cosine = (radius*(TAU/2)).cos()
    sine = (radius*(TAU/2)).sin()/radius
    state = [Jet(1), Jet(0)]
    derivatives = [[Jet(0),Jet(0)] for _ in range(NPHASE)]
    for i, phi in enumerate(phases):
        em, ep = np.exp(-1j*phi), np.exp(1j*phi)
        if not mirror:
            matrix = [[cosine-1j*sine*delta, -1j*sine*em],[-1j*sine*ep, cosine+1j*sine*delta]]
            dm = [[Jet(0), -sine*em],[sine*ep, Jet(0)]]
        else:
            matrix = [[cosine+1j*sine*delta, 1j*sine*ep],[1j*sine*em, cosine-1j*sine*delta]]
            dm = [[Jet(0), -sine*ep],[sine*em, Jet(0)]]
        old = state
        state = matvec(matrix, old)
        new = []
        for j in range(NPHASE):
            val = matvec(matrix, derivatives[j])
            if j == i:
                loc = matvec(dm, old); val = [val[0]+loc[0], val[1]+loc[1]]
            new.append(val)
        derivatives = new
    nw = ORTHOGONAL.conjugate() if not mirror else ORTHOGONAL
    dw = TARGET.conjugate() if not mirror else TARGET
    num, den = Jet(nw[0])*state[0] + Jet(nw[1])*state[1], Jet(dw[0])*state[0] + Jet(dw[1])*state[1]
    z = num/den
    dz = []
    for d in derivatives:
        dn, dd = Jet(nw[0])*d[0]+Jet(nw[1])*d[1], Jet(dw[0])*d[0]+Jet(dw[1])*d[1]
        dz.append((dn*den-num*dd)/(den*den))
    return z, dz


def response_jacobian_gradient_loss(phases):
    z, dz = projective_jet_and_derivatives(phases, False)
    zb, dzb = projective_jet_and_derivatives(phases, True)
    response = np.r_[z.c[:4].real, z.c[:4].imag]
    J = np.empty((RESPONSE_DIM,NPHASE))
    for k in range(4):
        for j in range(NPHASE):
            re = (dz[j].c[k]+dzb[j].c[k])/2
            im = (dz[j].c[k]-dzb[j].c[k])/(2j)
            J[k,j], J[4+k,j] = re.real, im.real
    q, denom = z*zb, 1+z*zb
    loss = (q/denom).c[6].real
    grad = np.empty(NPHASE)
    for j in range(NPHASE):
        dq = dz[j]*zb + z*dzb[j]
        grad[j] = (dq/(denom*denom)).c[6].real
    return response, J, grad, float(loss)


R_STAR = response_jacobian_gradient_loss(REFERENCE_PHASES)[0]


def geometry(theta):
    r,J,g,L = response_jacobian_gradient_loss(theta)
    U,s,Vh = np.linalg.svd(J,full_matrices=False)
    keep = s > SVD_RCOND*s[0]
    Jdag = (Vh[keep].T/s[keep]) @ U[:,keep].T
    P = np.eye(NPHASE)-Jdag@J
    tangent = -P@g
    n = np.linalg.norm(tangent)
    if n > 1e-14: tangent /= n  # repository's unit-normalized field
    return r-R_STAR,J,Jdag,P,tangent,g,L,s


def field(theta, mode):
    e,J,Jdag,P,tangent,g,L,s = geometry(theta)
    if mode == "tangent": return tangent
    if mode == "feedback": return tangent-BETA*(Jdag@e)
    # Spectrally normalized ordinary transpose penalty: its fastest local
    # response mode has rate BETA, while weak modes expose conditioning.
    if mode == "penalty":
        sigma_max=np.linalg.svd(J,compute_uv=False)[0]
        return tangent-(BETA/(sigma_max*sigma_max))*(J.T@e)
    raise ValueError(mode)


def rk4(theta0, mode):
    x = theta0.copy(); h=FLOW_TIME/STEPS
    for _ in range(STEPS):
        k1=field(x,mode)
        k2=field(x+h*k1/2,mode)
        k3=field(x+h*k2/2,mode)
        k4=field(x+h*k3,mode)
        x += h*(k1+2*k2+2*k3+k4)/6
        if not np.all(np.isfinite(x)): raise FloatingPointError("non-finite trajectory")
    return x


def unit(v):
    n=np.linalg.norm(v)
    if n<1e-15: raise FloatingPointError("zero perturbation direction")
    return v/n


def main():
    protocol={"version":VERSION,"seed":SEED,"beta":BETA,"flow_time":FLOW_TIME,"steps":STEPS,
      "perturbation_scales":PERTURBATION_SCALES,"trials_per_scale_and_kind":TRIALS_PER_SCALE,
      "integrator":"fixed-step classical RK4",
      "model":"repository-documented 14-segment driven qubit with common quasi-static detuning",
      "response":"real/imaginary Taylor coefficients orders 0..3 of projective coordinate",
      "objective":"order-6 Taylor coefficient of q/(1+q)","metric":"Euclidean in 14 phases"}
    phash=hashlib.sha256(json.dumps(protocol,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    print("="*96); print(f"{TITLE} v{VERSION}"); print("="*96)
    print("scope: real documented numerical model; not Arb/K=1/Pulser/QPU evidence")
    print("protocol sha256:",phash)
    rng=np.random.default_rng(SEED)
    e0,J0,Jd0,P0,t0,g0,L0,s0=geometry(REFERENCE_PHASES)
    records=[]
    for scale in PERTURBATION_SCALES:
      for rep in range(TRIALS_PER_SCALE):
       for kind in ("tangent","normal","mixed"):
        raw=rng.normal(size=NPHASE); tv=unit(P0@raw); nv=unit(Jd0@rng.normal(size=RESPONSE_DIM))
        direction=tv if kind=="tangent" else nv if kind=="normal" else unit(tv+nv)
        start=REFERENCE_PHASES+scale*direction
        start_geo=geometry(start); start_e=np.linalg.norm(start_geo[0]); startsafe=max(start_e,1e-30)
        row={"scale":scale,"rep":rep,"kind":kind,"start_response_norm":start_e,"start_loss":start_geo[6]}
        for mode in ("tangent","feedback","penalty"):
            end=rk4(start,mode); eg=geometry(end)
            row[mode]={"response_norm":float(np.linalg.norm(eg[0])),"loss":eg[6],
             "response_reduction":float(1-np.linalg.norm(eg[0])/startsafe),"min_sigma_end":float(eg[7][-1])}
        records.append(row)
        print(f"[{len(records):02d}/09] {kind:7s} scale={scale:.0e} "
          f"e0={start_e:.3e} fb={row['feedback']['response_norm']:.3e} "
          f"tan={row['tangent']['response_norm']:.3e} pen={row['penalty']['response_norm']:.3e}")
    normal_mixed=[r for r in records if r["kind"]!="tangent"]
    fb_red=[r["feedback"]["response_reduction"] for r in normal_mixed]
    penalty_wins=[r["feedback"]["response_norm"] < r["penalty"]["response_norm"] for r in normal_mixed]
    tangent_nonrecovery=[r["tangent"]["response_norm"] > .5*r["start_response_norm"] for r in normal_mixed]
    # Closed-loop flow must still descend from its own perturbed initial point;
    # it need not beat the infeasible tangent-only endpoint in objective value.
    loss_ok=[r["feedback"]["loss"] <= r["start_loss"]+1e-6 for r in records]
    zero_t=np.linalg.norm(field(REFERENCE_PHASES,"feedback")-field(REFERENCE_PHASES,"tangent"))
    allvals=[]
    for r in records:
      allvals += [r[m][k] for m in ("tangent","feedback","penalty") for k in ("response_norm","loss","min_sigma_end")]
    gates={"all_finite":bool(np.all(np.isfinite(allvals))),"reference_on_fibre":bool(np.linalg.norm(e0)<1e-12),
      "reference_full_row_rank":bool(s0[-1]>1e-4),"zero_residual_reduces_to_original_flow":bool(zero_t<1e-10),
      "feedback_reduces_normal_mixed_response_99pct":bool(min(fb_red)>.99),
      "feedback_beats_penalty_at_least_90pct":bool(np.mean(penalty_wins)>=.90),
      "tangent_only_does_not_recover":bool(all(tangent_nonrecovery)),"feedback_does_not_spoil_loss":bool(all(loss_ok))}
    result={"title":TITLE,"version":VERSION,"protocol":protocol,"protocol_sha256":phash,"records":records,
      "summary":{"reference_response_norm":float(np.linalg.norm(e0)),"reference_loss":L0,"min_sigma_reference":float(s0[-1]),
       "minimum_feedback_reduction":float(min(fb_red)),"feedback_penalty_win_fraction":float(np.mean(penalty_wins)),
       "zero_residual_field_difference":float(zero_t)},"gates":gates,"all_gates_pass":all(gates.values()),
      "scientific_status":"REAL_MODEL_NORMALLY_ATTRACTING_FLOW_SUPPORTED" if all(gates.values()) else "REAL_MODEL_PREFLIGHT_INCONCLUSIVE",
      "claim_boundary":"floating-point prospective test in documented 14-phase model; no interval proof, K=1 derivation, Pulser, cloud, or QPU evidence",
      "environment":{"python":platform.python_version(),"numpy":np.__version__}}
    Path(REPORT).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("\nSUMMARY"); print(json.dumps({k:v for k,v in result.items() if k in ("summary","gates","all_gates_pass","scientific_status")},indent=2))
    print("report:",REPORT)
    return 0 if result["all_gates_pass"] else 2


if __name__ == "__main__":
    code=main()
    if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:
        raise SystemExit(code)
