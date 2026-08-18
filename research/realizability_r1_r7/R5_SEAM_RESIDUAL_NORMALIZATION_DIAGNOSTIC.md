# R5-B3a Seam Residual Normalization Diagnostic

Status: `R5_SEAM_RESIDUAL_NORMALIZATION_DIAGNOSIS_COMPLETE`

Classification: `KRAWCZYK_BOOKKEEPING_DEFECT`

This diagnostic explains why the R5-B3 common-endpoint diagnostic reported a
common forcing bound near `2.72e-18` while the R5-B2 leafwise affine-Hessian
forcing bounds are near `1e-27`.

The two values are not a response normalization mismatch.  Both paths apply
the same response-coordinate map `B` and the same preconditioner `P`.

The discrepancy comes from the B3 center/radius bookkeeping.  The B3 helper
`r5_box_to_center_radius` constructs the Krawczyk center as
`arb(str(mid), str(radius))`, so the stored center `b0` still carries the full
intersection-box radius.  The B3 diagnostic then evaluates `F(b0)` on that
interval-valued center and also adds the separate `Z*r` Krawczyk radius term.
A Krawczyk center should be point-like; the box width should enter through the
separate interval `X-b0`.

Recomputing the same seam equations at the point midpoint gives strict Arb
residuals near `1e-27`, consistent with the B2 leafwise scale:

- seam 0 B2 adjacent `Y_total` upper: about `2.89e-27`
- seam 0 point-midpoint common residual: about `1.72e-27`
- seam 0 B3 interval-center residual: about `2.72e-18`
- seam 14 B2 adjacent `Y_total` upper: about `1.54e-26`
- seam 14 point-midpoint common residual: about `2.05e-27`
- seam 14 B3 interval-center residual: about `2.72e-18`

The diagnostic also checks the coordinate equivalence
`theta0+T*s*v+N*(b_C+S*(s-a_C)) =
theta_C+(T*v+N*S)*(s-a_C)` to roundoff-scale Arb enclosure.  Thus the observed
gap is not explained by a transposition, response-cost normalization, or a
different physical variable.

This is diagnostic only.  It does not certify B3, repair the existing B3
diagnostic, start B4, modify the frozen protocol, run R6, or perform normal
K=1 residual recovery.
