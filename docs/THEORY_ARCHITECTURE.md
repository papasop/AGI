# Theory Architecture

This document separates the frozen published theorem from post-publication
research layers. It is documentation only. It does not add a scientific
result, modify certificates, alter Zenodo metadata, or enlarge the published
local ODE theorem.

## Umbrella Map

```text
Process-Control Geometry - future umbrella theory
|
+-- P - Frozen published geometric-flow core
|   +-- P0: v0.7.4 parent-box descent certificate
|   `-- P1: v0.9.3 validated local intrinsic ODE microstep
|
+-- G - Geometric continuation
|   `-- finite/multi-chart/global continuation research
|
+-- C - Geometric feedback recovery
|   `-- normally attracting response-fibre controlled ODE
|
+-- W - Wiener-type observation, memory and delayed feedback
|   `-- finite-shot estimation, delay, drift, saturation and memory
|
+-- T - Candidate process-time geometry
|   `-- state-dependent clock or accumulated process cost
|
+-- M - Two-metric geometry
+-- D - Certificate execution DAG
`-- K - Independent K=1 bridge
```

## Dependency Relations

```text
P -> G
P -> C
C -> W
(C, W, M) -> T
(G, C) -> D
(C, M) -> K
```

Dependency arrows are not proof arrows. They say where concepts and evidence
would have to come from before a later layer can be responsibly interpreted.

The current level ordering is:

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

Do not place T before P or C. The current controllers still use external
integration time.

## Non-Implications

- W success does not automatically prove T.
- T success does not automatically prove K=1.
- C4 is geometric feedback recovery, not a Wiener theory.
- Process time is not physical time unless future work proves coordinate
  invariance, a reparameterization law, and independent experimental support.
- The future umbrella theory can contain P only as a frozen subtheory; it
  cannot reinterpret or enlarge the published P conclusions.

## Governance Rules

1. `paper/**` accepts errata only, not post-publication theory expansion.
2. New theory work belongs under `research/**`.
3. Every evidence-class promotion requires a separate pull request.
4. `NUMERICAL_PREFLIGHT` cannot be promoted directly to `ARB_CERTIFIED_LOCAL`.
5. Emulator evidence must not be labelled as hardware or QPU evidence.
6. Process time and K=1 must be established separately; similar terminology
   does not merge them.
7. Future papers should use a new manuscript version or a new paper, not
   overwrite the DOI boundary of the published geometric-flow ODE paper.
8. Negative results must be preserved, including feedback failure under
   combined stress or cases with `K_rec < 0`.

## Boundary

This architecture records a possible future composition:

```text
published local ODE core
+ geometric continuation
+ controlled recovery
+ observation-memory-delay feedback
+ candidate process coordinate
+ two-metric / DAG / K=1 bridges
```

Only P is frozen as the published theorem. Every other layer remains bounded
by its own evidence class in the research status matrix.
