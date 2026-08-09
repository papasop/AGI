#!/usr/bin/env python3
"""C4-B v1.2: centred affine-Taylor Arb enclosure.

This version retains the eight normal-coordinate dependencies to first order.
All discarded products and nonlinear Taylor terms are enclosed in outward-
rounded Arb/Acb remainder balls.  Adaptive subdivision is used only after the
dependency-aware enclosure has been attempted.

Put this file beside c4_arb_recovery_core_certificate_v1_0.py.
The certified domain is the inscribed normal-coordinate cube
|z_k| <= phase_radius/sqrt(8), not the full Euclidean ball.
"""
from __future__ import annotations

import argparse
import hashlib
import heapq
import json
import math
import platform
import sys
from pathlib import Path

import numpy as np

try:
    import c4_arb_recovery_core_certificate_v1_0 as base
except ModuleNotFoundError as exc:
    raise RuntimeError(
        "Place c4_arb_recovery_core_certificate_v1_0.py beside this file."
    ) from exc


TITLE = "C4-B ARB AFFINE-TAYLOR NORMAL-COORDINATE CERTIFICATE"
VERSION = "1.2"
NV = base.RESPONSE_DIM
DEFAULT_RADIUS = 0.020
DEFAULT_MAX_LEAVES = 4096
DEFAULT_MAX_DEPTH = 24
DEFAULT_REPORT = "c4_arb_affine_taylor_subdivision_v1_2.json"
STATUS_CERTIFIED = "C4_B_AFFINE_TAYLOR_NORMAL_CUBE_CERTIFIED"
STATUS_INCONCLUSIVE = "C4_B_AFFINE_TAYLOR_INCONCLUSIVE"


def up_abs(x):
    return base.upper(abs(x))


def nonnegative_ball_upper(value):
    """Exact nonnegative point ball made from a finite Python upper bound."""
    if not math.isfinite(value) or value < 0:
        raise FloatingPointError("non-finite affine remainder")
    return base.exact_float(value)


class Affine:
    """Complex affine form c + sum a_i eps_i + remainder, |eps_i|<=1."""
    __slots__ = ("c", "a", "r")

    def __init__(self, value=0, coeff=None, remainder=None):
        if isinstance(value, Affine):
            self.c = base.acb(value.c)
            self.a = [base.acb(v) for v in value.a]
            self.r = base.arb(value.r)
            return
        self.c = base.acb(value)
        self.a = ([base.acb(0) for _ in range(NV)] if coeff is None
                  else [base.acb(v) for v in coeff])
        self.r = base.arb(0) if remainder is None else base.arb(remainder)

    def linear_radius_upper(self):
        return sum(up_abs(v) for v in self.a)

    def remainder_upper(self):
        return base.upper(self.r)

    def deviation_upper(self):
        return self.linear_radius_upper() + self.remainder_upper()

    def enclosure(self):
        rad = nonnegative_ball_upper(self.deviation_upper())
        return self.c + base.acb(base.arb(0, rad), base.arb(0, rad))

    def __add__(self, other):
        b = Affine(other)
        return Affine(self.c+b.c,
                      [self.a[i]+b.a[i] for i in range(NV)], self.r+b.r)
    __radd__ = __add__

    def __neg__(self):
        return Affine(-self.c, [-v for v in self.a], self.r)

    def __sub__(self, other): return self + (-Affine(other))
    def __rsub__(self, other): return Affine(other) - self

    def __mul__(self, other):
        b = Affine(other)
        sx, sy = self.linear_radius_upper(), b.linear_radius_upper()
        rx, ry = self.remainder_upper(), b.remainder_upper()
        remainder = (up_abs(self.c)*ry + up_abs(b.c)*rx
                     + (sx+rx)*(sy+ry))
        return Affine(self.c*b.c,
                      [self.c*b.a[i] + b.c*self.a[i] for i in range(NV)],
                      nonnegative_ball_upper(remainder))
    __rmul__ = __mul__

    def inv(self):
        cabs_lo = base.lower(abs(self.c))
        h = self.deviation_upper()
        if not math.isfinite(cabs_lo) or cabs_lo <= h:
            raise ZeroDivisionError("affine inverse domain contains zero")
        rx = self.remainder_upper()
        remainder = (rx/(cabs_lo*cabs_lo)
                     + h*h/(cabs_lo*cabs_lo*(cabs_lo-h)))
        return Affine(1/self.c,
                      [-v/(self.c*self.c) for v in self.a],
                      nonnegative_ball_upper(remainder))

    def __truediv__(self, other): return self * Affine(other).inv()
    def __rtruediv__(self, other): return Affine(other) / self

    def exp(self):
        h = self.deviation_upper()
        rx = self.remainder_upper()
        ec = self.c.exp()
        # |exp(c)| <= exp(upper(Re(c))).
        ec_up = math.exp(base.upper(self.c.real))
        remainder = ec_up*(rx + math.exp(h)*h*h/2)
        return Affine(ec, [ec*v for v in self.a],
                      nonnegative_ball_upper(remainder))

    def sqrt(self):
        # In this program sqrt is used only for the detuning jet, which is
        # phase-independent. Reject accidental nonlinear affine use.
        if self.deviation_upper() != 0:
            raise NotImplementedError("affine sqrt with variables not required")
        return Affine(self.c.sqrt())


class AJet:
    """Univariate detuning jet with Affine phase-dependent coefficients."""
    def __init__(self, value=0):
        self.c = [Affine(0) for _ in range(base.JET_ORDER+1)]
        if isinstance(value, AJet):
            self.c = [Affine(v) for v in value.c]
        elif isinstance(value, (list, tuple)):
            for i, v in enumerate(value[:base.JET_ORDER+1]): self.c[i] = Affine(v)
        else:
            self.c[0] = Affine(value)

    def __add__(self, other):
        b=AJet(other); z=AJet(); z.c=[self.c[i]+b.c[i] for i in range(len(self.c))]; return z
    __radd__=__add__
    def __neg__(self):
        z=AJet(); z.c=[-v for v in self.c]; return z
    def __sub__(self,other): return self+(-AJet(other))
    def __rsub__(self,other): return AJet(other)-self
    def __mul__(self,other):
        b=AJet(other); z=AJet()
        for n in range(base.JET_ORDER+1):
            z.c[n]=sum((self.c[k]*b.c[n-k] for k in range(n+1)),Affine(0))
        return z
    __rmul__=__mul__
    def inv(self):
        z=AJet(); z.c[0]=self.c[0].inv()
        for n in range(1,base.JET_ORDER+1):
            z.c[n]=-z.c[0]*sum((self.c[k]*z.c[n-k]
                                for k in range(1,n+1)),Affine(0))
        return z
    def __truediv__(self,other): return self*AJet(other).inv()
    def __rtruediv__(self,other): return AJet(other)/self
    def sqrt(self):
        z=AJet(); z.c[0]=self.c[0].sqrt()
        for n in range(1,base.JET_ORDER+1):
            z.c[n]=(self.c[n]-sum((z.c[k]*z.c[n-k]
                                   for k in range(1,n)),Affine(0)))/(2*z.c[0])
        return z
    def exp(self):
        z=AJet(); z.c[0]=self.c[0].exp()
        for n in range(1,base.JET_ORDER+1):
            z.c[n]=sum((k*self.c[k]*z.c[n-k]
                        for k in range(1,n+1)),Affine(0))/n
        return z
    def sin(self):
        return ((base.acb(0,1)*self).exp()-(base.acb(0,-1)*self).exp())/base.acb(0,2)
    def cos(self):
        return ((base.acb(0,1)*self).exp()+(base.acb(0,-1)*self).exp())/2


def matvec(m,v):
    return [m[0][0]*v[0]+m[0][1]*v[1],m[1][0]*v[0]+m[1][1]*v[1]]


def phase_forms(N0, centre, half):
    forms=[]
    for i in range(base.NPHASE):
        c=base.exact_float(base.REFERENCE_PHASES[i])
        for k in range(NV): c += base.exact_float(N0[i,k])*base.exact_float(centre[k])
        a=[base.exact_float(N0[i,k])*base.exact_float(half[k]) for k in range(NV)]
        forms.append(Affine(c,a))
    return forms


def projective_affine(phases, mirror=False):
    delta=AJet([base.acb(0),base.acb(1)])
    radius=(1+delta*delta).sqrt()
    cosine=(radius*base.exact_float(base.TAU/2)).cos()
    sine=(radius*base.exact_float(base.TAU/2)).sin()/radius
    state=[AJet(1),AJet(0)]
    deriv=[[AJet(0),AJet(0)] for _ in range(base.NPHASE)]
    for i,phi in enumerate(phases):
        em=(base.acb(0,-1)*phi).exp(); ep=(base.acb(0,1)*phi).exp()
        if not mirror:
            m=[[cosine-base.acb(0,1)*sine*delta,-base.acb(0,1)*sine*em],
               [-base.acb(0,1)*sine*ep,cosine+base.acb(0,1)*sine*delta]]
            dm=[[AJet(0),-sine*em],[sine*ep,AJet(0)]]
        else:
            m=[[cosine+base.acb(0,1)*sine*delta,base.acb(0,1)*sine*ep],
               [base.acb(0,1)*sine*em,cosine-base.acb(0,1)*sine*delta]]
            dm=[[AJet(0),-sine*ep],[sine*em,AJet(0)]]
        old,state=state,matvec(m,state)
        new=[]
        for j in range(base.NPHASE):
            val=matvec(m,deriv[j])
            if j==i:
                loc=matvec(dm,old); val=[val[0]+loc[0],val[1]+loc[1]]
            new.append(val)
        deriv=new
    nw=base.ORTHOGONAL.conjugate() if not mirror else base.ORTHOGONAL
    dw=base.TARGET.conjugate() if not mirror else base.TARGET
    num=AJet(base.cb(nw[0]))*state[0]+AJet(base.cb(nw[1]))*state[1]
    den=AJet(base.cb(dw[0]))*state[0]+AJet(base.cb(dw[1]))*state[1]
    z=num/den; dz=[]
    for d in deriv:
        dn=AJet(base.cb(nw[0]))*d[0]+AJet(base.cb(nw[1]))*d[1]
        dd=AJet(base.cb(dw[0]))*d[0]+AJet(base.cb(dw[1]))*d[1]
        dz.append((dn*den-num*dd)/(den*den))
    return z,dz,den.c[0]


def certify(N0,Y,centre,half):
    try:
        forms=phase_forms(N0,centre,half)
        _,dz,den=projective_affine(forms,False)
        _,dzb,denb=projective_affine(forms,True)
        den_lo=base.lower(abs(den.enclosure())); denb_lo=base.lower(abs(denb.enclosure()))
        if den_lo<=0 or denb_lo<=0:
            return False,"projective_denominator",None,den_lo,denb_lo
        J=[[base.arb(0) for _ in range(base.NPHASE)] for _ in range(NV)]
        for k in range(4):
            for j in range(base.NPHASE):
                re=(dz[j].c[k]+dzb[j].c[k])/2
                im=(dz[j].c[k]-dzb[j].c[k])/base.acb(0,2)
                J[k][j]=re.enclosure().real; J[4+k][j]=im.enclosure().real
        JY=base.matmul(J,Y)
        D=[[(base.arb(1) if i==j else base.arb(0))-JY[i][j]
            for j in range(NV)] for i in range(NV)]
        q,_=base.inf_norm(D); qu=base.upper(q)
        ok=math.isfinite(qu) and qu<1
        return ok,"certified" if ok else "right_inverse_defect",qu,den_lo,denb_lo
    except Exception as exc:
        return False,f"{type(exc).__name__}: {exc}",None,None,None


def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--phase-radius",type=float,default=DEFAULT_RADIUS)
    p.add_argument("--max-leaves",type=int,default=DEFAULT_MAX_LEAVES)
    p.add_argument("--max-depth",type=int,default=DEFAULT_MAX_DEPTH)
    p.add_argument("--report",default=DEFAULT_REPORT)
    args,unknown=p.parse_known_args(argv)
    if unknown: print("[notice] ignored notebook/kernel arguments:",unknown)
    base.ctx.prec=base.PRECISION_BITS
    J0=base.centre_jacobian(); U,s,Vh=np.linalg.svd(J0,full_matrices=False)
    N0=Vh.T; Y0=J0.T@np.linalg.inv(J0@J0.T)
    Y=[[base.exact_float(Y0[i,j]) for j in range(NV)] for i in range(base.NPHASE)]
    h0=np.full(NV,args.phase_radius/math.sqrt(NV)); c0=np.zeros(NV)
    sens=np.sum(np.abs(N0),axis=0)
    protocol={"version":VERSION,"precision_bits":base.PRECISION_BITS,
      "phase_radius":args.phase_radius,"domain":"theta_ref+N0*z; |z_k|<=rho/sqrt(8)",
      "enclosure":"centred complex affine forms with rigorous nonlinear remainder balls",
      "max_leaves":args.max_leaves,"max_depth":args.max_depth,
      "criterion":"denominators exclude zero and ||I-JY0||_inf<1 on every leaf"}
    phash=hashlib.sha256(json.dumps(protocol,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    print("="*100); print(f"{TITLE} v{VERSION}"); print("="*100)
    print("scope: rigorous inscribed 8D normal cube; recovery core only")
    print("protocol sha256:",phash)
    heap=[(-float(max(h0)),0,c0,h0,0)]; serial=1; accepted=[]; unresolved=[]; evaluated=0
    worst=-math.inf; mind=math.inf
    while heap:
        _,_,c,h,d=heapq.heappop(heap); evaluated+=1
        ok,reason,q,dl,dbl=certify(N0,Y,c,h)
        if q is not None: worst=max(worst,q)
        for x in (dl,dbl):
            if x is not None and math.isfinite(x): mind=min(mind,x)
        rec={"centre":c.tolist(),"half":h.tolist(),"depth":d,"certified":ok,
             "reason":reason,"q_upper":q,"denominator_lower":dl,
             "mirror_denominator_lower":dbl}
        if ok: accepted.append(rec)
        elif d>=args.max_depth or len(heap)+len(accepted)+len(unresolved)+2>args.max_leaves:
            unresolved.append(rec)
        else:
            axis=int(np.argmax(h*sens)); hh=h.copy(); hh[axis]*=.5
            disp=np.zeros(NV); disp[axis]=hh[axis]
            for cc in (c-disp,c+disp):
                heapq.heappush(heap,(-float(max(hh)),serial,cc,hh.copy(),d+1)); serial+=1
        if evaluated==1 or evaluated%50==0:
            print(f"[boxes {evaluated}] accepted={len(accepted)} pending={len(heap)} unresolved={len(unresolved)}")
        if len(heap)+len(accepted)+len(unresolved)>=args.max_leaves:
            while heap:
                _,_,c,h,d=heapq.heappop(heap)
                unresolved.append({"centre":c.tolist(),"half":h.tolist(),"depth":d,
                  "certified":False,"reason":"leaf_budget_exhausted","q_upper":None,
                  "denominator_lower":None,"mirror_denominator_lower":None})
            break
    complete=bool(accepted) and not unresolved
    gates={"reference_full_row_rank":bool(s[-1]>1e-3),
      "full_declared_cube_covered":complete,"every_terminal_leaf_certified":complete,
      "positive_uniform_contraction_rate":bool(complete and worst<1)}
    passed=all(gates.values()); rate=base.BETA*(1-worst) if passed else None
    result={"title":TITLE,"version":VERSION,"protocol":protocol,"protocol_sha256":phash,
      "summary":{"boxes_evaluated":evaluated,"accepted_leaves":len(accepted),
        "unresolved_leaves":len(unresolved),"minimum_centre_singular_value":float(s[-1]),
        "worst_q_upper":worst if math.isfinite(worst) else None,
        "minimum_denominator_lower":mind if math.isfinite(mind) else None,
        "uniform_contraction_rate_lower_bound":rate},
      "accepted_leaves":accepted,"unresolved_leaves":unresolved,"gates":gates,
      "all_gates_pass":passed,"scientific_status":
        STATUS_CERTIFIED if passed else STATUS_INCONCLUSIVE,
      "claim_boundary":"Recovery-only controller on the declared inscribed normal cube; not full ball, tangential descent, saturation, invariant tube, global flow, K=1 or QPU.",
      "environment":{"python":platform.python_version(),"numpy":np.__version__}}
    Path(args.report).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("\nSUMMARY"); print(json.dumps({k:result[k] for k in ("summary","gates","all_gates_pass","scientific_status")},indent=2)); print("report:",args.report)
    return 0 if passed else 2


if __name__=="__main__":
    code=main()
    if "ipykernel" not in sys.modules and "google.colab" not in sys.modules: raise SystemExit(code)
