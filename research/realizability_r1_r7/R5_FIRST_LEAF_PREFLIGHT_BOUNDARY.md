# R5-B1a First-Leaf Preflight Boundary

Status:

```text
R5_FIRST_LEAF_PREFLIGHT_INCONCLUSIVE
```

This document scopes the R5-B1a first-leaf full-tube preflight for the
prospective Principle R R5 program. It applies only to the first frozen
initial leaf of `r5_full_tube_protocol_v1_0.json`.

The preflight asks whether the frozen R5-B0 static objects can support a
strict 192-bit Arb interval-Newton/Krawczyk existence and uniqueness check on
one parameter leaf. It is not an R5 full-tube certificate, not an R5
shrinking-family certificate, not an R6 result, and not a normal K=1 residual
recovery.

## Bound Inputs

The certificate must bind the parent R1-R7 protocol, the R5 full-tube
protocol, the frozen R5 auxiliary candidate artifact, and the R5-B0 static Arb
gate certificate by path and SHA-256. The frozen objects `theta_0`, `T`, `N`,
`B`, `c`, and `P` are reused exactly from
`data/r5_full_tube_auxiliary_v1_0.json`.

No new frame, direction, response-coordinate map, graph target, or
preconditioner may be chosen in this stage.

## Certified Leaf

Only leaf index `0` of the fixed 16-leaf bisection of
`[-1e-12,1e-12]` is in scope:

```text
[-1e-12, -8.75e-13]
```

The graph equation is

```text
F(t,b)=B*(R_3(theta_0+T*(t*v)+N*b)-c)=0,
v=(1,0,0,0,0,0).
```

The response model and derivative are evaluated by injecting the preflight
audit into the frozen v0.7.4 Arb response driver. All pass/fail gates are
decided from outward-rounded Arb enclosures at 192-bit precision.

## Accepted Meaning

If certified, this stage may claim only:

```text
R5_FIRST_LEAF_PREFLIGHT_CERTIFIED
```

meaning that the first frozen leaf admits a strict local implicit normal graph
preflight with chart/no-wrap residence, strict `B` and normal-Jacobian
invertibility, Krawczyk self-map inclusion, contraction below one, and the
logical implication from exact `F=0` plus invertible `B` to exact response
identity on this one leaf.

It does not claim full tube coverage, overlap consistency, zero total response
cost, nonconstancy of the shrinking loop family, R5 certification, Principle R
validation, physical time/energy/action, Lorentzian or general-relativistic
structure, hardware validation, or global flow.

The v1.0 preflight is fail-closed inconclusive: the frozen first-leaf run
proves strict chart/no-wrap residence, strict `B` invertibility, strict
normal-Jacobian invertibility, and contraction below one for the attempted box,
but the Krawczyk image is not strictly contained in the fixed candidate normal
box. This is not a mathematical counterexample to R5 and not an R6 result.

## Name Separation

- `W_Pi` is the R3 protocol-relative response-cost weight.
- `B` is the response-coordinate map in the graph equation.
- `P` is the frozen candidate preconditioner for
  `B*DR3(theta)*N`.

These objects must not be conflated.
