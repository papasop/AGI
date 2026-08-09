#!/usr/bin/env python3
"""C4-B v1.3: defect-centred affine Arb certificate.

The v1.2 implementation enclosed every entry of J(theta) before multiplying
by the ill-conditioned frozen right inverse Y0.  That destroys cancellations
between Jacobian columns.  This version keeps the complete affine forms through
the matrix product J(theta)Y0 and encloses only

    D(theta) = I - J(theta)Y0.

Thus both the centre cancellation and all first-order normal-coordinate
correlations are retained.  Nonlinear discarded terms remain outward-rounded
Arb/Acb remainder balls inherited from v1.2.

Required sibling files:
  c4_arb_recovery_core_certificate_v1_0.py
  c4_arb_affine_taylor_subdivision_v1_2.py
"""
from __future__ import annotations

import math
import sys

try:
    import c4_arb_recovery_core_certificate_v1_0 as base
    import c4_arb_affine_taylor_subdivision_v1_2 as engine
except ModuleNotFoundError as exc:
    raise RuntimeError(
        "Use c4_b_v1_3_colab_bundle.zip so the v1.0 and v1.2 engine files "
        "are present beside this script."
    ) from exc


TITLE = "C4-B ARB DEFECT-CENTRED AFFINE CERTIFICATE"
VERSION = "1.3"
DEFAULT_REPORT = "c4_arb_defect_centered_affine_v1_3.json"


def defect_centered_certify(N0, Y, centre, half):
    """Enclose I-JY only after affine matrix multiplication."""
    try:
        forms = engine.phase_forms(N0, centre, half)
        _, dz, den = engine.projective_affine(forms, False)
        _, dzb, denb = engine.projective_affine(forms, True)

        den_lo = base.lower(abs(den.enclosure()))
        denb_lo = base.lower(abs(denb.enclosure()))
        if not (math.isfinite(den_lo) and math.isfinite(denb_lo)
                and den_lo > 0 and denb_lo > 0):
            return False, "projective_denominator", None, den_lo, denb_lo

        # Keep all eight affine noise symbols in every J entry.
        J = [[engine.Affine(0) for _ in range(base.NPHASE)]
             for _ in range(base.RESPONSE_DIM)]
        for order in range(4):
            for column in range(base.NPHASE):
                J[order][column] = (
                    dz[column].c[order] + dzb[column].c[order]) / 2
                J[4 + order][column] = (
                    dz[column].c[order] - dzb[column].c[order]) / base.acb(0, 2)

        # Critical v1.3 change: affine sum first, interval projection last.
        D = [[engine.Affine(1 if i == j else 0)
              for j in range(base.RESPONSE_DIM)]
             for i in range(base.RESPONSE_DIM)]
        for i in range(base.RESPONSE_DIM):
            for j in range(base.RESPONSE_DIM):
                product = sum(
                    (J[i][k] * Y[k][j] for k in range(base.NPHASE)),
                    engine.Affine(0),
                )
                D[i][j] = D[i][j] - product

        D_interval = [[D[i][j].enclosure().real
                       for j in range(base.RESPONSE_DIM)]
                      for i in range(base.RESPONSE_DIM)]
        q, _ = base.inf_norm(D_interval)
        q_upper = base.upper(q)
        certified = math.isfinite(q_upper) and q_upper < 1.0
        return (certified,
                "certified" if certified else "right_inverse_defect",
                q_upper if math.isfinite(q_upper) else None,
                den_lo, denb_lo)
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}", None, None, None


def main(argv=None):
    # The audited subdivision/coverage/output driver stays identical to v1.2;
    # only the enclosure primitive and frozen metadata labels change.
    engine.certify = defect_centered_certify
    engine.TITLE = TITLE
    engine.VERSION = VERSION
    engine.DEFAULT_REPORT = DEFAULT_REPORT
    engine.STATUS_CERTIFIED = "C4_B_DEFECT_CENTERED_NORMAL_CUBE_CERTIFIED"
    engine.STATUS_INCONCLUSIVE = "C4_B_DEFECT_CENTERED_INCONCLUSIVE"
    return engine.main(argv)


if __name__ == "__main__":
    code = main()
    if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:
        raise SystemExit(code)
