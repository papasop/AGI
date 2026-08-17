# R5 Shrinking-Family Feasibility Audit

Status:

```text
R5_INCONCLUSIVE_MISSING_FULL_LOOP_GRAPH_CERTIFICATE
```

This is a read-only feasibility audit for the frozen prospective Principle R
R5 shrinking-family protocol. It does not certify R5, run R6, search for R6
candidates, tune the frozen direction or epsilon sequence, perform normal
K=1 residual recovery, or modify the published Geometric-Flow theorem
boundary.

Baseline repository commit:

```text
8aacc8b2acb2dbfb6a26d81b3bbc354dfe8474c7
```

Frozen protocol:

```text
research/realizability_r1_r7/frozen_protocol_v1_0.json
PROTOCOL_FROZEN_NO_R6_SEARCH_PERFORMED
```

Short public status:

```text
R5_INCONCLUSIVE
```

The more specific internal reason is
`R5_INCONCLUSIVE_MISSING_FULL_LOOP_GRAPH_CERTIFICATE`.

## Frozen R5 Object

The audit considered only the R5 object declared in the frozen protocol:

```text
theta(a)=theta_0+T a+N psi(a)
v=(1,0,0,0,0,0)
a_epsilon(s)=epsilon*sin(2*pi*s)*v,  s in [0,1]
epsilon in {1e-14,3e-14,1e-13,3e-13,1e-12}
F_Pi(theta,v)=sqrt((D R_3(theta)v)^T W_Pi (D R_3(theta)v))
W_Pi=I_8
```

No alternate direction, epsilon, metric, response, or chart was considered.

## Feasibility Questions

1. Existing components are not sufficient, by themselves, to issue an
   independent R5 certificate for every complete loop. The frozen R5 declaration
   in `research/realizability_r1_r7/frozen_protocol_v1_0.json` names only
   `theta(a)=theta_0+T a+N psi(a)`, the direction `v`, the sinusoidal family,
   and the epsilon sequence. It does not serialize concrete `T`, `N`,
   `theta_0`, `B`/whitener, graph radii, or a machine-verifiable `psi`
   enclosure. The v0.9.2 centered Krawczyk code
   `src/response_fibre_centered_mean_value_krawczyk_v0_9_2.py` contains local
   graph machinery, but it explicitly records
   `"full_six_dimensional_picard_closed": False` and
   `"exact_response_preservation_claimed": False` in its output construction.
   The v0.9.3 intrinsic Picard code
   `src/response_fibre_intrinsic_picard_microstep_v0_9_3.py` certifies a local
   ODE microstep, not the frozen R5 loop family.

2. The available v0.9.3 stored report
   `results/v0_9_3_reference/report.json` covers one local intrinsic
   microstep. It records fields such as `"certified_time_step": 1e-14`,
   `"outer_complex_tangent_radius": 2e-11`, and gates
   `"complex_parametric_fibre_graph": true` and
   `"implicit_graph_derivative_enclosed": true`. It does not record an
   R5-specific subdivision, sine range enclosure, or full-loop tube proof for
   `s -> epsilon*sin(2*pi*s)*v` for each frozen epsilon. Comparing the largest
   epsilon with the recorded tangent radius is only a scale observation; it is
   not a complete-loop residence or graph-contraction certificate.

3. The exact response preservation argument would need to be formalized as:
   the graph equation `B(R_3(theta_0+T*a+N*psi(a))-c)=0` holds on the complete
   R5 tube, and `B` is strictly invertible on the same certified domain; hence
   `R_3(theta(a))=R_3(theta_0)` throughout the loop. The v0.9.3 report records
   `"graph_equation": "B(R3(theta0+T*a+N*psi(a))-c)=0"` and
   `"response_preservation": "DR3*W=0"` under `"proof_identities"`, and also
   records `"exact_response_preservation_certified": true` for the microstep.
   Those fields cannot be relabeled as R5 evidence without a machine
   certificate binding the same identities to the complete sinusoidal loop
   family and to the frozen R5 direction/epsilon sequence.

4. Strict nonconstancy cannot be certified by endpoint comparison, since every
   frozen loop has `a_epsilon(0)=a_epsilon(1)=0`. The R4 section of
   `frozen_protocol_v1_0.json` declares a
   `"positive-measure-speed-or-displacement"` nonconstant gate, and the R5
   section declares the sinusoidal loop, but no R5 certificate field currently
   proves a positive-measure subinterval with a rigorously enclosed nonzero
   sine value, speed, or intrinsic displacement.

5. The relevant v0.9.2/v0.9.3 components use NumPy/binary64 SVD and inverse
   computations to choose frames and preconditioners: for example
   `np.linalg.svd` and `np.linalg.inv` appear in
   `src/response_fibre_centered_mean_value_krawczyk_v0_9_2.py` in the
   `v090_frame` path and normal inverse construction, and similarly in
   `src/response_fibre_intrinsic_picard_microstep_v0_9_3.py` in the v0.9.2
   embedded path and v0.9.3 frame/preconditioner path. Such binary64 choices
   may be acceptable for candidate discovery or for choosing a preconditioner,
   but they cannot enter a theorem-bearing R5 decision unless independently
   frozen and then validated by outward Arb enclosures, Neumann defects, and
   domain gates. The current R5 protocol does not freeze those derived choices,
   and no R5 verifier currently audits them.

## Blocking Gaps

- The frozen protocol does not include concrete serialized T, N, theta_0,
  B/whitener, graph radii, or psi enclosure data for R5; it only names the
  intrinsic graph form in `frozen_protocol_v1_0.json`.
- There is no R5-specific full-loop tube certificate for
  `a_epsilon(s)=epsilon*sin(2*pi*s)*v` over `s in [0,1]`; the existing
  v0.9.3 report is a local microstep report.
- There is no R5-specific existence and uniqueness certificate for psi(a) on
  each complete loop tube; v0.9.2 explicitly leaves the full six-dimensional
  Picard gate open.
- There is no R5-specific proof that the graph equation plus an invertible
  response coordinate map implies exact R_3 preservation on the whole loop;
  v0.9.3 records this only for its local ODE construction.
- There is no R5-specific strict nonconstancy proof on a positive-measure
  subinterval, despite the R4 gate requiring positive-measure speed or
  displacement.
- There is no R5 verifier that rejects tolerance residuals, sampled residuals,
  incomplete-loop coverage, R6 fields, or normal K=1 residual-recovery data.

## Required Next Work Before Certification

A future R5 certification attempt should first create a new frozen auxiliary
R5 data file, separate from `frozen_protocol_v1_0.json`, that binds the
concrete intrinsic-chart frame and graph proof inputs. Only after that data is
frozen should a certificate generator prove, with Arb or exact algebra, the
complete-loop graph existence, uniqueness, chart residence, non-wrap,
positive-measure nonconstancy, exact response preservation, same-meter zero
cost, and epsilon-shrinking gates.

Until those gates exist and pass, the correct status is:

```text
R5_INCONCLUSIVE_MISSING_FULL_LOOP_GRAPH_CERTIFICATE
```

This audit makes no R6, Principle R universal, physical-time, energy, action,
Lorentzian, general-relativistic, hardware, normal K=1 residual-recovery, or
global-flow claim.

It also does not claim that an R5 search failed or that the frozen R5 family is
mathematically impossible. The finding is narrower: the current repository
lacks the frozen auxiliary data and full-loop graph certificate needed for a
fail-closed R5 theorem-bearing verifier.
