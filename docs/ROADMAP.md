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

The organizing principle is deliberately separated across four levels:

- Level A, frozen result: P;
- Level B, mathematical/dynamical extensions: G, C, M;
- Level C, control and execution extensions: W, D;
- Level D, foundational candidates: T, K.

The dependency structure is:

- P -> G;
- P -> C;
- P -> M;
- C -> W;
- (C, W, M) -> T;
- (G, C) -> D;
- (C, M) -> K.

Dependency arrows are not proof arrows. W success does not automatically
prove T, T success does not automatically prove K=1, and C4 is not a Wiener
theory. Process time is not physical time unless future work proves
coordinate invariance, a reparameterization law, and independent experimental
support.

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
| C1 | Normal response-recovery feedback | Numerical preflight history |
| C2 | Gain, radius, solver and saturation robustness | Numerical preflight history |
| C3 | Refined numerical attraction-tube boundary | Superseded by C4-D1/C4-E2a local certificates |
| C4-D1 | Nonzero finite product-tube residence | Arb-certified local |
| C4-E2a | Nine-chart moving-atlas overlap chain | Arb-certified local |
| C4-E2b | Validated flowpipe transport | Open theorem |
| C5 | Controlled multi-chart continuation | Open |
| C6 | Long-time normal attraction | Open |

The current C4 certificates are post-publication controlled-geometry evidence.
They do not modify the published local ODE theorem, do not claim positive
invariance, and do not establish Wiener-type observation-memory feedback.
C4-E2a is an overlap-chain certificate, not a validated-flowpipe continuation.

C4-style closure milestones must strictly certify at least:

- some `rho_certified > 0`;
- uniform full-row-rank margin;
- target-fibre invariance;
- strict inward condition on the tube boundary;
- response Lyapunov contraction;
- preservation of objective descent;
- local existence and uniqueness;
- saturation inactive or rigorously enclosed.

Stop/go gates:

- After C4-E2b is completed, pause the control line and turn to either the
  W-layer feedback protocol, the K=1 bridge, or a two-metric theorem.
- If C3 numerical boundaries are unstable under solver tolerances, stop and
  repair the numerical setup before claiming progress.

See [CONTROL_EXTENSION_SCOPE.md](CONTROL_EXTENSION_SCOPE.md).

## W - Wiener-Type Observation, Memory And Delayed Feedback

The W layer is not a restatement of C4. It adds noisy observation, state
estimation, finite memory, delay, drift, saturation, and controller updates
based on historical observations.

| Stage | Objective | Status |
| --- | --- | --- |
| W0 | Memoryless feedback baseline | External/local indications only; not archived |
| W1 | Finite-shot observation model | External/local indications only; not archived |
| W2 | Delay/drift/saturation decomposition | External/local indications only; not archived |
| W3 | Explicit estimator and memory state | Open |
| W4 | Held-out stability map | Open |
| W5 | Emulator cross-model validation | Open |
| W6 | Hardware protocol | Open |
| W7 | Independent QPU evidence | Open |

Do not cite unmerged Pulser v1.0-v1.3 outputs as repository evidence. A future
W-layer evidence PR must archive scripts, protocols, reports, manifests,
seeds, software versions, negative controls, claim boundaries, and failure
status.

W-layer evidence must not be described as QPU or hardware evidence unless an
independent hardware protocol and result are actually archived.

See [WIENER_FEEDBACK_SCOPE.md](WIENER_FEEDBACK_SCOPE.md).

## T - Candidate Process-Time Geometry

The current control and emulator protocols use external integration time
`t_ext`. The T layer is reserved for a candidate accumulated recovery/process
coordinate such as `tau_rec`; it is not established.

| Stage | Objective | Status |
| --- | --- | --- |
| T0 | Define candidate process increment | DESIGN_ONLY |
| T1 | Positivity and monotonicity | OPEN_THEOREM |
| T2 | Coordinate invariance | OPEN_THEOREM |
| T3 | Reparameterization law | OPEN_THEOREM |
| T4 | Coupling to estimator-memory dynamics | OPEN_THEOREM |
| T5 | Independent protocol equivalence test | OPEN_THEOREM |
| T6 | Arb-certified example | OPEN_THEOREM |
| T7 | Hardware falsification test | OPEN_THEOREM |

Stop rules:

- Without `kappa_rec > 0`, do not call the coordinate a time.
- Without coordinate invariance, do not call it a geometric scalar.
- Without a reparameterization law, do not call it an intrinsic clock.
- Without independent protocol equivalence tests, do not call it physical
  time.
- Do not define process time directly as `K_rec`.
- Do not claim changes to relativity, thermodynamics, or quantum mechanics.

See [PROCESS_TIME_SCOPE.md](PROCESS_TIME_SCOPE.md).

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
Level A - frozen theorem
P

Level B - geometric extensions
P -> G
P -> C
P -> M

Level C - control and execution extensions
C -> W
(G, C) -> D

Level D - foundational candidates
(C, W, M) -> T
(C, M) -> K
```

The Riemannian and pseudo-Riemannian structures describe continuous geometry;
the control law selects dynamics; the certificate DAG records finite certified
execution. Geometric continuation and certificate execution can develop in
parallel as long as D records only certified finite transitions.

C4 does not equal Wiener theory. W success would not automatically prove T,
and T success would not automatically prove K=1. K=1 bridge work is a
separate bridge problem, not an automatic consequence of geometric
continuation, controlled attraction, or process-time definitions.
