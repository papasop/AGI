# Five-Stage Controlled Response-Fibre Geometry Programme

> This document defines the active post-publication research programme. It does not alter the frozen v0.7.4 + v0.9.3 published theorem, its source code, its interval certificates, or its claim boundary. The programme is sequential: a later stage may be investigated numerically, but it cannot be promoted to a theorem-level claim before the required earlier gates are satisfied.

| Stage | Object | Current status | Promotion gate |
| ----- | ------ | -------------- | -------------- |
| 1 | Intrinsic response-fibre flow | Frozen local theorem | Already certified within published boundary |
| 2 | Normally attracting controlled flow | Floating-point development evidence | Nonzero Arb-certified controlled tube |
| 3 | Process-cost/process-time functional | Open definition | Coordinate-invariant operational law |
| 4 | Critical zero mode | Open bridge test | Predeclared Arb-certified critical co-location |
| 5 | Unified controlled geometry | Not established | Joint certificate plus independent observable |

## Stage 1 - Certified Intrinsic Response-Fibre Flow

### Scientific Question

Can a nonconstant trajectory preserve the declared response while strictly
reducing an independent implementation objective?

### Mathematical Field

$$
\dot{\theta}_T
=
-P_\theta\nabla L(\theta),
\qquad
P_\theta
=
I-J_R(\theta)^\dagger J_R(\theta).
$$

### Required Identities

$$
J_R(\theta)\dot{\theta}_T=0,
$$

and

$$
\frac{dL}{dt}
=
-|P_\theta\nabla L(\theta)|^2<0
$$

where the projected gradient is nonzero.

### Current Status

Frozen and certified locally by the published v0.7.4 + v0.9.3 theorem
boundary.

### What Stage 1 Proves

- declared-response preservation;
- strict descent of an independent objective;
- local existence and uniqueness of the certified intrinsic ODE solution;
- nonconstant motion inside a local response-fibre chart.

### What Stage 1 Does Not Prove

- global fibre connectivity;
- arbitrary endpoint connection;
- long-time existence;
- attraction back to the fibre after perturbation;
- K=1 criticality;
- process-time divergence;
- physical spacetime or hardware behaviour.

Stage 1 is the fixed foundation and must not be rewritten by later stages.

## Stage 2 - Certified Feedback Recovery and Controlled Attraction

### Scientific Question

Can a perturbed implementation be driven back toward the target response fibre
while preserving tangential objective descent?

### Candidate Controlled Field

$$
\dot{\theta}
=
-P_\theta\nabla L(\theta)
-\beta J_R(\theta)^\dagger
\bigl(R(\theta)-r_\ast\bigr).
$$

The first term is tangential descent. The second term is normal
response-recovery feedback.

### Numerical Development Evidence

The v1.1-v1.3.1 experiments are floating-point development tests unless and
until their scripts, protocols, and reports are reviewed and archived. They are
not part of the frozen paper theorem and are not Arb certificates.

### Formal Closure Milestone

Stage 2 closes only with a nonzero Arb-certified local controlled attraction
tube satisfying all of the following:

- `rho_certified > 0`;
- uniform full-row-rank margin;
- target-fibre invariance;
- strict inward-pointing condition on the tube boundary;
- response Lyapunov contraction;
- preservation of objective descent;
- local existence and uniqueness;
- control saturation proven inactive or rigorously enclosed.

This is the C4-equivalent closure gate. That phrase is explanatory only and
does not restore the former C-track roadmap.

### Stop Rule

If the numerical tube boundary is not stable under solver tolerance, direction
sampling, or saturation counterfactuals, stop and repair the numerical model
before attempting an Arb certificate.

### Promotion Rule

Do not describe normally attracting control as K=1. Feedback recovery and K=1
criticality are logically independent until Stage 4 and Stage 5 succeed.

## Stage 3 - Coordinate-Invariant Process-Cost and Process-Time Definition

### Scientific Question

Can the cost of implementing a physical change be defined independently of an
arbitrary trajectory parametrization?

Introduce a candidate process functional such as

$$
T_{\mathrm{proc}}[\gamma]
=
\int_\gamma N(\theta,d\theta),
$$

or an equivalent coordinate-invariant construction.

Do not freeze one formula as a theorem before testing invariance.

### Required Gates

Stage 3 must establish:

1. coordinate invariance;
2. invariance under admissible reparametrization;
3. positivity or explicitly stated degeneracy;
4. additivity or a rigorously defined composition law;
5. finiteness away from declared critical points;
6. a clear relationship to measurable time, energy, exposure, control effort, or another operational resource;
7. independence from arbitrary controller gain whenever a fundamental interpretation is claimed.

### Required Distinction

Maintain the distinction between:

- external evolution parameter (t);
- path cost;
- control effort;
- process-relative time;
- unit-change cost.

Do not call them physically identical without a theorem and an operational
measurement protocol.

### Stop Rule

If the proposed process time changes under a coordinate transformation or
admissible reparametrization without a corresponding physical change, reject or
revise the definition.

### Current Status

Open. No process-time theorem is currently part of the repository.

## Stage 4 - Independently Defined Critical Zero-Mode Test

### Scientific Question

Does the same frozen response-fibre model possess a genuine critical event with
spectral closure, rank reduction, null-image formation, and candidate
process-cost divergence?

Define independently, before scanning data:

$$
G(\theta),\qquad
A(d,\theta),\qquad
d_c,\qquad
N_Q(v;d).
$$

The definitions must not be chosen after observing the desired critical value.

### Predeclared Critical Gates

At one common frozen critical point, test:

$$
\det A(d_c)=0,
$$

$$
\operatorname{rank}A(d_c)=1,
$$

$$
\ker A(d_c)\neq{0},
$$

$$
\operatorname{Im}A(d_c)
\subseteq
\mathcal N(G),
$$

and, if Stage 3 provides a valid process-cost definition,

$$
N_Q(v_c;d)\rightarrow\infty
\quad\text{as}\quad d\rightarrow d_c.
$$

### Required Controls

- continuous predeclared parameter scan;
- off-critical negative controls;
- Euclidean-signature or noncritical comparison where meaningful;
- coordinate-change tests;
- perturbation stability;
- independent numerical reconstruction;
- Arb certification before theorem-level promotion.

### Stop Rules

- Full-row-rank response recovery is not evidence of rank-one criticality.
- Saturation-induced failure is not evidence of a K=1 transition.
- A fitted singularity is not a process-time divergence theorem.
- A null vector obtained only after tuning definitions to the answer is not an independent bridge.
- Do not infer matter, light, gravity, spacetime, or constants from a rank-drop event alone.

### Current Status

Open. The repository has no certified K=1 bridge.

## Stage 5 - Unified Co-Location Theorem or Falsification

### Scientific Question

Do physical realization, feedback recovery, critical zero modes, and
process-time behaviour belong to one controlled geometric event in the same
model?

Stage 5 may be claimed only if Stages 1-4 provide compatible frozen
definitions and certificates.

### Required Co-Location Statement

The same frozen model, parameter point, state neighbourhood, and declared
observables must simultaneously support:

1. a nonconstant physically admissible implementation;
2. certified response-fibre geometry;
3. certified feedback recovery near the target fibre;
4. a nontrivial critical zero mode;
5. certified spectral closure and rank reduction;
6. certified null-image formation;
7. a valid process-cost or process-time law;
8. certified critical asymptotics of that process quantity;
9. an independent operational observable distinguishing the critical prediction.

Symbolically, the desired result is not merely four separate observations, but
one co-located event:

$$
\boxed{
\text{realization}
+
\text{recovery}
+
\text{critical zero mode}
+
\text{process-time law}
=
\text{one controlled geometric structure}
}
$$

### Independence Requirement

The definitions of geometry, controller, critical operator, metric, and process
time must be frozen before the final reveal. Reusing the same implementation is
allowed only when shared dependencies are explicitly disclosed and
independently cross-checked.

### Possible Outcomes

The programme must permit three honest outcomes:

- **Supported:** all predeclared gates co-locate and are certified.
- **Partially supported:** some structures exist but do not co-locate.
- **Falsified in the tested model:** the critical bridge or process-time prediction fails.

Failure at Stage 5 must not invalidate the frozen Stage 1 theorem or a
completed Stage 2 controlled-tube theorem.

### Prohibited Claims Without Additional Evidence

Even successful Stage 5 completion would not by itself prove:

- a replacement for real analysis;
- Gödel-type incompleteness;
- general relativity as a subset;
- matter emergence;
- a fundamental constant;
- universal quantum collapse;
- PASQAL or other QPU hardware behaviour;
- a universal physical theory.

Those require separate definitions, theorems, and experiments.
