# R5-B1d Second-Order Remainder Provenance Audit

Status:

```text
B1C_REMAINDER_DEPENDENCY_ARTIFACT
```

This is a diagnostic-only audit of the R5-B1c first-leaf affine remainder. It
does not modify the frozen R1--R7 protocol, generate an R5 certificate, inspect
other leaves, run R6, or perform normal K=1 residual recovery.

## Provenance Finding

The B1c `pure_alpha_second_order_remainder` is constructed in
`diagnose_r5_first_leaf_affine.py` by evaluating the whole-leaf natural interval
`F_aff_alpha = F(theta_C + (T*v + N*S) alpha)` and then subtracting the already
intervalized center and first-order terms:

```text
R2_alpha = F_aff_alpha - F0 - J_alpha_affine * alpha
```

This is an interval subtraction after dependency has already been lost. It is
not a correlated Taylor remainder and does not compute an explicit Hessian.

## Independent Analytic Check

The diagnostic script constructs a second formal variable for the affine leaf
coordinate and propagates it through the same v0.7.4 projective-jet response
formula. It bounds

```text
H_alpha = sup || P B D^2 R3(theta_C + (T*v + N*S) alpha)[w,w] ||_inf
```

over the first leaf, with `w=T*v+N*S`, and reports the Lagrange bound

```text
Y2_true <= (1/2) H_alpha alpha_radius^2.
```

The result is diagnostic, not theorem-bearing. If a future R5 protocol revision
uses this form, it must freeze the directional-Hessian construction and verify
the full leaf/tube gates independently.
