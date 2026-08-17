# R5-A Full-Tube Graph Protocol Boundary

Status:

```text
R5_FULL_TUBE_PROTOCOL_FROZEN_NO_CERTIFICATE_RUN
```

This document scopes the subordinate R5-A protocol for the prospective
Principle R R5 shrinking-family problem. It is a protocol freeze only. It does
not certify R5, run R5, run R6, search for candidates, perform normal K=1
residual recovery, or modify the published Geometric-Flow theorem boundary.

The protocol is bound to deterministic candidate auxiliary data in
`data/r5_full_tube_auxiliary_v1_0.json`. That file freezes `theta_0`, `T`,
`N`, the graph-equation response-coordinate map `B`, target `c`, and numerical
candidate preconditioner `P`. The data are produced by replaying the existing
v0.9.3 midpoint SVD construction and are explicitly pending independent Arb
validation. They are not theorem-bearing evidence.

The frozen R5 loops all lie in the single intrinsic line segment
`a=t*v, |t|<=1e-12`. The subordinate protocol therefore freezes the future
certificate target as one full-tube implicit graph problem:

```text
theta(t)=theta_0+T*(t*v)+N*psi(t*v),  t in [-1e-12,1e-12].
```

If that maximum tube is later certified, graph existence and chart residence
for the five frozen sinusoidal loops may be inferred as subset statements. This
protocol does not certify those subset statements yet.

## Required Future Logic

The future theorem-bearing R5-A certificate must use the following implication
chain. Tolerance residuals, sampled residuals, or interval residuals containing
zero are not sufficient.

1. A strict interval Newton/Krawczyk proof gives a unique graph branch
   `psi(t*v)` on every sub-tube and overlap consistency between adjacent
   sub-tubes.
2. Therefore `H(t,psi(t))=0` holds mathematically exactly on the covered tube.
3. The fixed response-coordinate map `B` is proved strictly invertible by an
   independent Arb/Neumann certificate.
4. The exact implicit identity and strict invertibility of `B` imply the full
   response identity `R_3(theta(t))-R_3(theta_0)=0`.
5. The R3 protocol-relative cost meter is therefore zero along the certified
   graph curve.

## Floating-Point Boundary

Binary64 SVD, inverse computations, or optimization may be used only for
candidate discovery. Before theorem-bearing use, fixed `T`, `N`, `B`, and
preconditioner data must be serialized and checked by independent Arb
post-hoc gates: frame rank, dimensions, transversality, strict invertibility
of `B`, preconditioner defect, Krawczyk self-map, Krawczyk contraction, and
sub-tube overlap consistency.

The names are deliberately separated:

- `W_Pi` is the R3 protocol-relative response-cost weight.
- `B` is the response-coordinate map in `B(R3(theta)-c)=0`.
- `P` is the numerical candidate inverse/preconditioner for `B*DR3(theta0)*N`.

## Nonconstancy Gate

Closed-loop endpoint comparison is forbidden because
`a_epsilon(0)=a_epsilon(1)=0`. The future certificate must use the preselected
positive-measure interval `I=[0,1/12]`. It must prove a strict positive lower
bound for `cos(2*pi*s)` on `I`, nonzero intrinsic coordinate speed, and an
environment-space speed lower bound from a certified embedding singular value
or coordinate projection.

## Exclusions

This protocol is not an R5 certificate, not an R6 result, not a Principle R
validation, not physical-time/energy/action evidence, not Lorentzian or
general-relativistic evidence, not hardware validation, and not a global-flow
claim. Existing v0.9.2 and v0.9.3 artifacts remain design references only and
must not be relabeled as R5 or R6 certificates.
