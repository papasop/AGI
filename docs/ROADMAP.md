# Post-publication Research Roadmap

This roadmap is a documentation-only guide for work after the published local
paper theorem. It does not change the theorem, algorithms, certificates,
inputs, reference JSON, tags, releases, or Zenodo records.

The frozen paper boundary is the v0.7.4 complete-parent-box geometry/descent
certificate together with the v0.9.3 validated local intrinsic ODE microstep.
`GLOBAL_FLOW_CLAIMED` remains `false`. Every stage below must distinguish
between certified result, floating-point development evidence, design stage,
open theorem work, and speculative horizon. This roadmap is not a completion
schedule.

The organizing principle is deliberately separated across three levels:

- Level A, frozen result: P;
- Level B, mathematical/dynamical extensions: G, C, M;
- Level C, certification/foundational bridges: D, K.

The six-track dependency structure is:

- P -> G;
- P -> C;
- P -> M;
- (G, C) -> D;
- (C, M) -> K.

Realizability is only an upstream motivation: equal declared response does not
imply equal implementation, and a nonconstant response-fibre curve is a
model-level example of implementation freedom. This repository does not
establish a universal realizability principle, an extension or replacement of
the real numbers, a general nonfaithfulness theorem for real-valued
observables, a K=1 bridge, or physical spacetime emergence.

The role separation is deliberately narrow:

- geometry describes legal directions;
- the control law restores response and selects motion;
- the DAG records finite certified execution;
- the K=1 bridge must be established by independent definitions and
  predeclared tests.

These roles cannot be unified by terminology alone.

## P - Frozen Published Core

| Stage | Objective | Status |
| --- | --- | --- |
| P0 | v0.7.4 complete-parent-box geometry/descent certificate | Frozen/certified |
| P1 | v0.9.3 local intrinsic ODE microstep | Frozen/certified |
| P2 | Keep `GLOBAL_FLOW_CLAIMED = false` | Frozen boundary |
| P3 | Prevent later tracks from retroactively changing the theorem | Governance rule |

The paper-local-ODE theorem is the fixed reference point. Later v0.10.x
continuation work, controlled-flow experiments, two-metric formulations,
certificate-DAG semantics, K=1 bridge tests, protected residuals, matter-like
modes, and constants do not enlarge or reinterpret this theorem.

## G - Geometric Continuation

| Stage | Objective | Status |
| --- | --- | --- |
| G0 | Local intrinsic response-fibre ODE | Frozen/certified |
| G1 | Finite same-chart continuation | Stored v0.10.6 certificate |
| G2 | Fifth-frame certification | Open |
| G3 | Validated multi-chart transitions | Open |
| G4 | Complete response-component coverage | Open |
| G5 | Fibre connectivity and arbitrary-endpoint reachability | Open |
| G6 | Long-time existence or global response-fibre flow | Open |

The v0.10.15 fifth-frame backend is a fail-closed harness, not a fifth-frame
theorem. A future geometric-continuation theorem must certify the missing
rank, nonstationarity, inclusion, and transition gates directly.

## C - Normally Attracting Control

The candidate controlled field is schematic:

$$
\dot{\theta}
=
-P_\theta\nabla L(\theta)
-\beta J_R(\theta)^\dagger
\bigl(R(\theta)-r_\ast\bigr).
$$

| Stage | Objective | Status |
| --- | --- | --- |
| C0 | Tangential intrinsic descent | Frozen local theorem |
| C1 | Normal response-recovery feedback | Floating-point development evidence |
| C2 | Gain, radius, solver and saturation robustness | Floating-point development evidence |
| C3 | Refined numerical attraction-tube boundary | In progress/not repository-certified |
| C4 | Nonzero Arb-certified local controlled tube | Next formal milestone |
| C5 | Controlled multi-chart continuation | Open |
| C6 | Long-time normal attraction | Open |

Versions v1.1 through v1.3.1 are floating-point development evidence unless
their scripts, protocols, and reports are separately reviewed and archived as
repository evidence. They are not Arb-certified controlled-flow theorems and
must not be written as PASS for the frozen paper.

C4 is the recommended closure milestone for the current control track. It must
strictly certify at least:

- some `rho_certified > 0`;
- uniform full-row-rank margin;
- target-fibre invariance;
- strict inward condition on the tube boundary;
- response Lyapunov contraction;
- preservation of objective descent;
- local existence and uniqueness;
- saturation inactive or rigorously enclosed.

Stop/go gates:

- After C4 is completed, pause the control line and turn to either the K=1
  bridge or a two-metric theorem.
- If C3 numerical boundaries are unstable under solver tolerances, stop and
  repair the numerical setup before claiming progress.

See [CONTROL_EXTENSION_SCOPE.md](CONTROL_EXTENSION_SCOPE.md).

## M - Two-metric Geometry

The intended separation is:

- `g_+`: a positive Riemannian metric for path length, optimization cost, and
  control cost on response fibres;
- `g_-`: a candidate pseudo-Riemannian metric for critical or null response
  directions.

| Stage | Objective | Status |
| --- | --- | --- |
| M0 | Unified Riemannian cost metric | Open formulation |
| M1 | Process-cost/path-length functional | Open |
| M2 | Candidate pseudo-Riemannian metric | Conceptual/open |
| M3 | Signature and null-direction theorem | Open |
| M4 | Compatibility of `g_+` and `g_-` | Open |
| M5 | Coordinate-invariant certified examples | Open |

The pseudo-Riemannian structure is candidate/open. No equivalence with
physical spacetime or general relativity is claimed.

See [TWO_METRIC_SCOPE.md](TWO_METRIC_SCOPE.md).

## D - Certificate Execution DAG

| Stage | Objective | Status |
| --- | --- | --- |
| D0 | Certified regions as nodes | Design |
| D1 | Validated transitions as edges | Partial local ingredients only |
| D2 | Strict monotone certificate quantity | Open |
| D3 | Finite certificate DAG | Open |
| D4 | Continuous-trajectory/discrete-path correspondence | Open |
| D5 | Soundness and relative completeness theorem | Open |

Continuous response fibres may contain loops. `DAG` refers only to a derived
certificate or execution graph. Orientation alone does not prove acyclicity; a
strictly monotone certified quantity is required.

Stop/go gate: if C3 numerical boundaries are unstable under solver tolerances,
do not use them as DAG edges. Stop and repair the solver or certificate
boundary first.

See [CERTIFICATE_DAG_SCOPE.md](CERTIFICATE_DAG_SCOPE.md).

## K - K=1 Bridge

| Stage | Objective | Status |
| --- | --- | --- |
| K0 | Abstract rank-one/null-flow critical mechanism | Separate theoretical candidate |
| K1 | Define `G`, `A(d)`, `d_c`, and `N_Q` in the response-fibre model | Open |
| K2 | Predeclared continuous critical scan | Open |
| K3 | Co-location of spectral closure, rank drop, and null image | Open |
| K4 | Arb-certified bridge | Open |
| K5 | Independent physical observable | Open |
| K6 | Protected residual or matter-like mode | Speculative |
| K7 | Dimensionless constant candidate | Speculative |

The K=1 bridge has not been established. Normally attracting control tests do
not establish K=1: their Jacobian remains full row rank, and observed
attraction-tube failures may come from finite control saturation rather than a
K=1 critical rank drop.

Stop/go gates:

- If the K1 bridge has no spectral-gap closure, do not interpret it as a K1
  implementation.
- Without a protected, uncontrollable, coordinate-invariant residual mode, do
  not use the phrase "matter emergence".
- If constants require tuning to match target values, do not call the result a
  fundamental constant derivation.

See [K1_BRIDGE_SCOPE.md](K1_BRIDGE_SCOPE.md).

## Dependency Order

```text
Level A: frozen result

P: frozen published core
|
|-- Level B: mathematical/dynamical extensions
|   |-- G: geometric continuation
|   |-- C: normally attracting control
|   `-- M: two-metric geometry
|
`-- Level C: certification/foundational bridges
    |-- D: certificate execution graph
    |       depends on (G, C)
    |
    `-- K: K=1 bridge
            depends on (C, M)
            |
            `-- protected residuals / constants
                (speculative horizon)
```

The Riemannian and pseudo-Riemannian structures describe continuous geometry;
the control law selects dynamics; the certificate DAG records finite certified
execution. Geometric continuation and certificate execution can develop in
parallel as long as D records only certified finite transitions. C4 remains
the recommended closure milestone for the current control track before turning
to K=1 bridge work or a two-metric theorem. K=1 bridge work is a separate
bridge problem, not an automatic consequence of the first three tracks.
