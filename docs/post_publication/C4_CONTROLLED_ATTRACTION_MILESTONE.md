# C4 controlled-attraction milestone (post-publication)

This milestone is separate from the immutable published-paper boundary.
Nothing here changes the published source, frozen reference theorem, paper PDF,
or prior release artifacts.

## Result hierarchy

1. **C4-D0 — numerical preflight.** Three sampled tangent/normal/mixed starts
   remained in a declared 6D x 8D product chart over the selected numerical
   time window. This is parameter-selection evidence only.
2. **C4-D1 — rigorous finite residence.** A 14-variable quadratic Taylor
   enclosure with 256-bit Arb arithmetic proves
   `||I-J(theta)Y0||_inf < 1` throughout a smaller product tube, outward-bounds
   the complete unsaturated dynamic Moore--Penrose controlled field, and
   derives a strictly positive residence-time lower bound.

The stored D1 reference run obtained approximately

```text
q_upper = 0.1641355441
T_cert  = 7.41147e-9
```

The certified time is deliberately conservative. It establishes a local
finite-time theorem, not useful-duration control, positive invariance,
long-time continuation, or global flow.

## Claim boundary

Allowed wording: *a post-publication Arb certificate establishes a strictly
positive finite residence time for the declared unsaturated controlled flow in
one fixed local product tube.*

Forbidden wording includes: the published paper proved controlled attraction;
the tube is positively invariant; the flow continues globally; C4 establishes
K=1; or the result is Pulser/PASQAL/QPU evidence.

The next research gate is C4-E: a separately reviewed moving-chart overlap and
recentring certificate.

