# R5-B0 Static Arb Gate Boundary

Status:

```text
R5_STATIC_ARB_GATES_CERTIFIED
```

This document scopes the R5-B0 static Arb verification for the prospective
Principle R R5 program. It verifies only fixed, already-frozen candidate
objects from `data/r5_full_tube_auxiliary_v1_0.json` against
`r5_full_tube_protocol_v1_0.json`.

R5-B0 is not an R5 full-tube certificate. It does not certify graph existence,
graph uniqueness, overlap consistency, chart residence on the tube, exact
response preservation, zero total response cost, nonconstancy of the loop
family, or the R5 shrinking-family claim. It does not run R6 and does not
perform normal K=1 residual recovery.

## Certified Static Gates

The static gate record may certify only:

- path, shape, SHA-256, finite-decimal, protocol, and source identity;
- full rank of the frozen `T` frame via an Arb Gram determinant;
- full rank of the frozen `N` frame via an Arb Gram determinant;
- full rank/transversality of `[T N]` via an Arb determinant;
- strict invertibility of frozen `B` via an Arb determinant and inverse defect;
- strict preconditioner defect `||I-P*(B*DR3(theta_0)*N)||_inf < 1`.

All pass/fail decisions are made from Arb enclosures at 192-bit precision.
Binary64 is recorded only as the historical candidate-construction method for
`T`, `N`, `B`, and `P`; it is not a theorem decision path.

## Name Separation

- `W_Pi` is the R3 protocol-relative response-cost weight.
- `B` is the response-coordinate map in the graph equation.
- `P` is the candidate preconditioner for `B*DR3(theta_0)*N`.

These objects must not be conflated.

## Exclusions

The static gate record must not contain an R5 full-tube certificate, an R6
search or result, a normal K=1 recovery result, or an exact-response/zero-cost
claim. A residual interval containing zero is not accepted as exact response
preservation.
