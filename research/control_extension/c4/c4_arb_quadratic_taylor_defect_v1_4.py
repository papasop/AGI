#!/usr/bin/env python3
"""C4-B v1.4: quadratic Taylor defect-centred Arb certificate.

This version retains every constant, 8 linear, and 8x8 ordered quadratic
normal-coordinate coefficient.  Only cubic-and-higher analytic terms and
pre-existing remainder interactions enter the outward-rounded remainder ball.
The full quadratic forms are propagated through the response engine and the
matrix product J(theta)Y0 before interval projection.

Required sibling files are supplied by c4_b_v1_4_colab_bundle.zip.
"""
from __future__ import annotations

import math
import sys

try:
    import c4_arb_recovery_core_certificate_v1_0 as base
    import c4_arb_affine_taylor_subdivision_v1_2 as engine
    import c4_arb_defect_centered_affine_v1_3 as defect_engine
except ModuleNotFoundError as exc:
    raise RuntimeError("Use c4_b_v1_4_colab_bundle.zip with all dependencies.") from exc


TITLE = "C4-B ARB QUADRATIC-TAYLOR DEFECT CERTIFICATE"
VERSION = "1.4"
DEFAULT_REPORT = "c4_arb_quadratic_taylor_defect_v1_4.json"
NV = base.RESPONSE_DIM


def up_abs(x):
    return base.upper(abs(x))


def point_upper(x):
    if not math.isfinite(x) or x < 0:
        raise FloatingPointError("invalid quadratic remainder")
    return base.exact_float(x)


def zero_matrix():
    return [[base.acb(0) for _ in range(NV)] for _ in range(NV)]


class Quadratic:
    """c + a_i eps_i + q_ij eps_i eps_j + r, |eps_i|<=1."""
    __slots__ = ("c", "a", "q", "r")

    def __init__(self, value=0, coeff=None, quadratic=None, remainder=None):
        if isinstance(value, Quadratic):
            self.c = base.acb(value.c)
            self.a = [base.acb(v) for v in value.a]
            self.q = [[base.acb(v) for v in row] for row in value.q]
            self.r = base.arb(value.r)
            return
        # Permit conversion from the v1.2 affine class if encountered.
        if hasattr(value, "c") and hasattr(value, "a") and hasattr(value, "r"):
            self.c = base.acb(value.c)
            self.a = [base.acb(v) for v in value.a]
            self.q = zero_matrix()
            self.r = base.arb(value.r)
            return
        self.c = base.acb(value)
        self.a = ([base.acb(0) for _ in range(NV)] if coeff is None
                  else [base.acb(v) for v in coeff])
        self.q = (zero_matrix() if quadratic is None else
                  [[base.acb(v) for v in row] for row in quadratic])
        self.r = base.arb(0) if remainder is None else base.arb(remainder)

    def linear_radius_upper(self):
        return sum(up_abs(v) for v in self.a)

    def quadratic_radius_upper(self):
        return sum(up_abs(v) for row in self.q for v in row)

    def remainder_upper(self):
        return base.upper(self.r)

    def deviation_upper(self):
        return (self.linear_radius_upper()+self.quadratic_radius_upper()
                + self.remainder_upper())

    def enclosure(self):
        radius=point_upper(self.deviation_upper())
        return self.c+base.acb(base.arb(0,radius),base.arb(0,radius))

    def __add__(self,other):
        b=Quadratic(other)
        return Quadratic(self.c+b.c,
          [self.a[i]+b.a[i] for i in range(NV)],
          [[self.q[i][j]+b.q[i][j] for j in range(NV)] for i in range(NV)],
          self.r+b.r)
    __radd__=__add__

    def __neg__(self):
        return Quadratic(-self.c,[-v for v in self.a],
          [[-v for v in row] for row in self.q],self.r)
    def __sub__(self,other): return self+(-Quadratic(other))
    def __rsub__(self,other): return Quadratic(other)-self

    def __mul__(self,other):
        b=Quadratic(other)
        lx,ly=self.linear_radius_upper(),b.linear_radius_upper()
        qx,qy=self.quadratic_radius_upper(),b.quadratic_radius_upper()
        rx,ry=self.remainder_upper(),b.remainder_upper()
        q=[[self.c*b.q[i][j]+b.c*self.q[i][j]+self.a[i]*b.a[j]
            for j in range(NV)] for i in range(NV)]
        # Terms not represented through degree two.
        remainder=(up_abs(self.c)*ry+up_abs(b.c)*rx
          +lx*qy+qx*ly+qx*qy
          +(lx+qx)*ry+(ly+qy)*rx+rx*ry)
        return Quadratic(self.c*b.c,
          [self.c*b.a[i]+b.c*self.a[i] for i in range(NV)],q,
          point_upper(remainder))
    __rmul__=__mul__

    def inv(self):
        c_lo=base.lower(abs(self.c)); h=self.deviation_upper()
        if not math.isfinite(c_lo) or c_lo<=h:
            raise ZeroDivisionError("quadratic inverse domain contains zero")
        l=self.linear_radius_upper(); qrad=self.quadratic_radius_upper()
        r=self.remainder_upper(); tail=qrad+r
        # 1/(c+h)=1/c-h/c^2+h^2/c^3+R3.  Retain -Q/c^2
        # and L^2/c^3; enclose all remaining contributions.
        remainder=(r/(c_lo*c_lo)
          +(2*l*tail+tail*tail)/(c_lo**3)
          +h**3/(c_lo**3*(c_lo-h)))
        q=[[-self.q[i][j]/(self.c*self.c)
             +self.a[i]*self.a[j]/(self.c*self.c*self.c)
             for j in range(NV)] for i in range(NV)]
        return Quadratic(1/self.c,
          [-v/(self.c*self.c) for v in self.a],q,point_upper(remainder))

    def __truediv__(self,other): return self*Quadratic(other).inv()
    def __rtruediv__(self,other): return Quadratic(other)/self

    def exp(self):
        l=self.linear_radius_upper(); qrad=self.quadratic_radius_upper()
        r=self.remainder_upper(); h=l+qrad+r; tail=qrad+r
        ec=self.c.exp(); ec_up=math.exp(base.upper(self.c.real))
        remainder=ec_up*(r+(2*l*tail+tail*tail)/2+math.exp(h)*h**3/6)
        q=[[ec*(self.q[i][j]+self.a[i]*self.a[j]/2)
            for j in range(NV)] for i in range(NV)]
        return Quadratic(ec,[ec*v for v in self.a],q,point_upper(remainder))

    def sqrt(self):
        if self.deviation_upper()!=0:
            raise NotImplementedError("variable quadratic sqrt is not used")
        return Quadratic(self.c.sqrt())


def main(argv=None):
    # All jet, response, matrix-defect, subdivision, coverage and report logic
    # is reused. Dynamic global lookup makes AJet instantiate Quadratic here.
    engine.Affine=Quadratic
    engine.TITLE=TITLE
    engine.VERSION=VERSION
    engine.DEFAULT_REPORT=DEFAULT_REPORT
    engine.STATUS_CERTIFIED="C4_B_QUADRATIC_TAYLOR_NORMAL_CUBE_CERTIFIED"
    engine.STATUS_INCONCLUSIVE="C4_B_QUADRATIC_TAYLOR_INCONCLUSIVE"
    engine.certify=defect_engine.defect_centered_certify
    return engine.main(argv)


if __name__=="__main__":
    code=main()
    if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:
        raise SystemExit(code)
