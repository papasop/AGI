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
3. **C4-E0 — moving-chart preflight.** A floating-point sampled trajectory
   constructs nine candidate charts and eight pointwise adjacent overlaps.
4. **C4-E1a/E2a — Arb overlap-chain certificate.** A 256-bit outward-rounded
   Arb calculation certifies a positive-volume overlap chain for all eight
   adjacent transitions of the frozen nine-chart atlas, with local
   invertibility and positive local residence in each new chart.

The stored D1 reference run obtained approximately

```text
q_upper = 0.1641355441
T_cert  = 7.41147e-9
```

The certified time is deliberately conservative. It establishes a local
finite-time theorem, not useful-duration control, positive invariance,
long-time continuation, or global flow.

The stored E2a overlap-chain report records

```text
charts                               = 9
adjacent transitions                 = 8
positive-volume overlap boxes        = 8/8
maximum Neumann-defect upper bound   = 0.018601705183309603
minimum local residence lower bound  = 6.050195285542712e-10
aggregate local residence budget     = 4.844642545380921e-09
```

The aggregate local residence budget is not a continuation time. C4-E2a does
not prove that a controlled interval flowpipe reaches every overlap box.

## Claim boundary

Allowed wording: *a post-publication Arb certificate establishes a strictly
positive finite residence time for the declared unsaturated controlled flow in
one fixed local product tube.*

Forbidden wording includes: the published paper proved controlled attraction;
the tube is positively invariant; the flow continues globally; C4 establishes
K=1; or the result is Pulser/PASQAL/QPU evidence.

The next research gate is C4-E2b validated-flowpipe continuation. It must prove
flowpipe transport between the already certified overlap boxes before any
finite moving-chart continuation time is claimed.
