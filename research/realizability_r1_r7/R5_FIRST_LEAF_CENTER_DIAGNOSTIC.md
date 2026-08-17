# R5-B1b First-Leaf Center Diagnostic

Status:

```text
R5_FIRST_LEAF_CENTER_DIAGNOSIS_COMPLETE
```

This is a diagnostic-only record for the first frozen leaf of the prospective
R5 full-tube protocol. It explains why the R5-B1a Krawczyk self-map preflight
is inconclusive. It is not an R5 certificate, not a corrected preflight, not a
new frozen protocol, not an R6 result, and not a normal K=1 residual recovery.

The diagnostic keeps the frozen `theta_0`, `T`, `N`, graph-equation map `B`,
target `c`, preconditioner `P`, direction `v`, first-leaf interval, Arb
precision, subdivision policy, and normal-box radius unchanged. The frozen
normal box is not resized or recentered.

## Krawczyk Bookkeeping

The R5-B1a preflight used

```text
K_a(X)=b_0-PF(a,b_0)+(I-PJ_N(a,X))(X-b_0)
```

with `b_0=0` and `X=[-r,r]^8`, `r=1e-23`. Since the box is centered at zero,
the self-map enclosure is checked by the sufficient infinity-norm bound

```text
Y + Z*r < r,
Y = sup ||P F(a,0)||_inf,
Z = sup ||I-PJ_N(a,X)||_inf.
```

The image center/forcing term `Y` and the interval-width term `Z*r` are stored
separately in `diagnostics/r5_first_leaf_center_diagnostic_v1_0.json`.

## Boundary

This diagnostic may classify the first-leaf preflight failure as center-offset,
tangent-defect, interval-width, implementation/bookkeeping, multiple causes,
or inconclusive. It must not certify the first leaf, the full tube, R5, R6, a
physical-time/energy/action claim, Lorentzian or general-relativistic
structure, hardware validation, or global flow.
