# Prospective Principle R Protocol Scaffold

This directory contains a prospective model-level test scaffold for
realizability criteria R1--R7. It is intentionally isolated from the published
v1.2.13 theorem boundary.

Status:

```text
PROTOCOL_FROZEN_NO_R6_SEARCH_PERFORMED
```

The frozen protocol still contains no R6 search and no R6 result. This
directory now also contains subordinate Geometric-Flow R5 certificates,
culminating in `R5_FULL_SHRINKING_FAMILY_CERTIFIED`, for the frozen model
domain. These certificates do not change the frozen protocol, published
theorem boundary, source, tag, Release, manuscript, or Zenodo asset.

The isolated R7 positive-control certificate is post-protocol prospective
evidence only. The current certificate is
`certificates/r7_positive_control_v1_1.json`; the PR #53 v1.0 certificate is
superseded because it used an incomplete centered enclosure of the declared
path.

## Files

```text
README.md
CLAIM_BOUNDARY.md
frozen_protocol_v1_0.json
verify_frozen_protocol.py
requirements.txt
R7_CERTIFICATE_BOUNDARY.md
certify_r7_positive_control.py
verify_r7_certificate.py
R5_FEASIBILITY_AUDIT.md
R5_FULL_TUBE_PROTOCOL_BOUNDARY.md
R5_STATIC_ARB_GATES_BOUNDARY.md
R5_FIRST_LEAF_PREFLIGHT_BOUNDARY.md
R5_FIRST_LEAF_CENTER_DIAGNOSTIC.md
R5_FIRST_LEAF_AFFINE_DIAGNOSTIC.md
R5_SECOND_ORDER_REMAINDER_DIAGNOSTIC.md
R5_FIRST_LEAF_HESSIAN_KRAWCZYK_BOUNDARY.md
GF_PR_STAGE_NAMING_BOUNDARY.md
R5_ALL_LEAVES_HESSIAN_KRAWCZYK_BOUNDARY.md
PRINCIPLE_R_COMPLIANCE_MATRIX.md
R5_ADJACENT_LEAF_GLUING_BOUNDARY.md
R5_SEAM_RESIDUAL_NORMALIZATION_DIAGNOSTIC.md
R5_GLOBAL_IMPLICIT_BRANCH_C1_BOUNDARY.md
R5_POSITIVE_MEASURE_NONCONSTANCY_BOUNDARY.md
R5_FULL_SHRINKING_FAMILY_BOUNDARY.md
r5_full_tube_protocol_v1_0.json
prepare_r5_full_tube_auxiliary.py
verify_r5_full_tube_auxiliary.py
data/r5_full_tube_auxiliary_v1_0.json
verify_r5_full_tube_protocol.py
certify_r5_static_arb_gates.py
verify_r5_static_arb_gates.py
certificates/r5_static_arb_gates_v1_0.json
certify_r5_first_leaf_preflight.py
verify_r5_first_leaf_preflight.py
certificates/r5_first_leaf_preflight_v1_0.json
diagnose_r5_first_leaf_center.py
verify_r5_first_leaf_center_diagnostic.py
diagnostics/r5_first_leaf_center_diagnostic_v1_0.json
diagnose_r5_first_leaf_affine.py
verify_r5_first_leaf_affine_diagnostic.py
diagnostics/r5_first_leaf_affine_diagnostic_v1_0.json
diagnose_r5_second_order_remainder.py
verify_r5_second_order_remainder_diagnostic.py
diagnostics/r5_second_order_remainder_diagnostic_v1_0.json
certify_r5_first_leaf_hessian_krawczyk.py
verify_r5_first_leaf_hessian_krawczyk.py
certificates/r5_first_leaf_hessian_krawczyk_v1_0.json
certify_r5_all_leaves_hessian_krawczyk.py
verify_r5_all_leaves_hessian_krawczyk.py
certificates/r5_all_leaves_hessian_krawczyk_v1_0.json
certify_r5_adjacent_leaf_gluing.py
verify_r5_adjacent_leaf_gluing.py
diagnose_r5_seam_residual_normalization.py
verify_r5_seam_residual_normalization.py
diagnostics/r5_adjacent_leaf_gluing_v1_0.json  # superseded B3 diagnostic
diagnostics/r5_adjacent_leaf_gluing_v1_1.json
diagnostics/r5_seam_residual_normalization_diagnostic_v1_0.json
certificates/r5_adjacent_leaf_gluing_v1_1.json
certify_r5_global_implicit_branch_c1.py
verify_r5_global_implicit_branch_c1.py
certificates/r5_global_implicit_branch_c1_v1_0.json
certify_r5_positive_measure_nonconstancy.py
verify_r5_positive_measure_nonconstancy.py
certificates/r5_positive_measure_nonconstancy_v1_0.json
certify_r5_full_shrinking_family.py
verify_r5_full_shrinking_family.py
certificates/r5_full_shrinking_family_v1_0.json
certificates/r7_positive_control_v1_0.json  # superseded
certificates/r7_positive_control_v1_1.json  # current R7 positive control
```

## Verification

Run:

```bash
python research/realizability_r1_r7/verify_frozen_protocol.py
python research/realizability_r1_r7/verify_r7_certificate.py --mutation-tests
python research/realizability_r1_r7/prepare_r5_full_tube_auxiliary.py --verify-frozen
python research/realizability_r1_r7/verify_r5_full_tube_auxiliary.py --mutation-tests
python research/realizability_r1_r7/verify_r5_full_tube_protocol.py --mutation-tests
python research/realizability_r1_r7/verify_r5_static_arb_gates.py --mutation-tests
python research/realizability_r1_r7/verify_r5_first_leaf_preflight.py --mutation-tests
python research/realizability_r1_r7/verify_r5_first_leaf_center_diagnostic.py --mutation-tests
python research/realizability_r1_r7/verify_r5_first_leaf_affine_diagnostic.py --mutation-tests
python research/realizability_r1_r7/verify_r5_second_order_remainder_diagnostic.py --mutation-tests
python research/realizability_r1_r7/verify_r5_first_leaf_hessian_krawczyk.py --mutation-tests
python research/realizability_r1_r7/verify_r5_all_leaves_hessian_krawczyk.py --mutation-tests
python research/realizability_r1_r7/verify_r5_seam_residual_normalization.py --mutation-tests
python research/realizability_r1_r7/verify_r5_adjacent_leaf_gluing.py --mutation-tests
python research/realizability_r1_r7/verify_r5_global_implicit_branch_c1.py --mutation-tests
python research/realizability_r1_r7/verify_r5_positive_measure_nonconstancy.py --mutation-tests
python research/realizability_r1_r7/verify_r5_full_shrinking_family.py --mutation-tests
```

The verifier checks schema, required fields, declared file hashes, R1--R5/R7
declarations, absence of R6 result fields, and the exact frozen status string.
It does not run Arb, Krawczyk, Picard, Lohner, or any R6 search.

The R7 verifier checks the stored v1.1 certificate, including full
`eta_delta(s)=theta_0+s*delta*n` path endpoint containment for every frozen
delta. It does not run R5 or R6.

`R5_FEASIBILITY_AUDIT.md` records the first-stage, read-only R5 feasibility
audit. Its historical final status is
`R5_INCONCLUSIVE_MISSING_FULL_LOOP_GRAPH_CERTIFICATE`: at that time the
repository did not yet contain an R5-specific complete-loop implicit-graph
certificate or the auxiliary frozen intrinsic-chart data needed to verify one
fail-closed. The report is retained as provenance, not as the current R5
frontier. It has been operationally superseded by the later R5-A/B0--B6 chain,
which culminates in `R5_FULL_SHRINKING_FAMILY_CERTIFIED`. It is not an R5
certificate, does not report a failed R5 search, and does not run R6.

`r5_full_tube_protocol_v1_0.json` is the prospectively frozen subordinate
R5-A protocol for the full-tube graph certificate on the one-dimensional
segment `a=t*v, |t|<=1e-12`. Its immutable protocol status is
`R5_FULL_TUBE_PROTOCOL_FROZEN_NO_CERTIFICATE_RUN`; this records the state at
protocol freeze and is retained as provenance. The subsequent R5-A/B0--B6
chain certifies the committed candidate objects without altering that frozen
protocol.
`data/r5_full_tube_auxiliary_v1_0.json` is the committed candidate auxiliary
artifact for `theta_0`, `T`, `N`, graph-equation response-coordinate map `B`,
target `c`, and numerical candidate preconditioner `P`. Its byte content is
frozen and hash-bound. Its binary64 SVD construction is platform-sensitive and
is not a cross-platform reproducibility or theorem-bearing gate. Local
regeneration is a diagnostic only. The protocol itself does not run R5 or R6
and does not relabel v0.9.2/v0.9.3 as R5 or R6 evidence.

`certificates/r5_static_arb_gates_v1_0.json` records the R5-B0 static Arb
gate result for the frozen candidate objects only. Its status is
`R5_STATIC_ARB_GATES_CERTIFIED`. It certifies static rank, transversality,
`B` invertibility, and preconditioner-defect gates, but it is not an R5
full-tube certificate and does not certify graph existence, exact response
preservation, zero total cost, nonconstancy, R6, or normal K=1 recovery.

`certificates/r5_first_leaf_preflight_v1_0.json` records the R5-B1a
first-leaf Krawczyk preflight for leaf index 0 of the frozen 16-leaf
decomposition. Its status is
`R5_FIRST_LEAF_PREFLIGHT_INCONCLUSIVE`: chart residence, no-wrap, `B`
invertibility, normal-Jacobian invertibility, and contraction are strictly
verified, but the Krawczyk self-map is not strictly contained in the fixed
candidate normal box. This is not an R5 failure, not a full-tube result, and
not R6.

`diagnostics/r5_first_leaf_center_diagnostic_v1_0.json` records the R5-B1b
center/forcing diagnostic for the same first leaf. Its status is
`R5_FIRST_LEAF_CENTER_DIAGNOSIS_COMPLETE` with classification
`MULTIPLE_CAUSES`: the interval forcing term dominates the reported self-map
bound, while the pointwise Newton correction also exceeds the frozen normal-box
radius. It is diagnostic-only and does not recenter, resize, certify, or freeze
a new candidate.

`diagnostics/r5_first_leaf_affine_diagnostic_v1_0.json` records the R5-B1c
leaf-centered affine-correlated feasibility diagnostic for the same first leaf.
Its status is `AFFINE_CORRELATED_REMAINDER_TOO_WIDE`: the candidate center
reduces the point residual, and the diagnostic preserves a single `alpha` in
`theta_C+(T*v+N*S)alpha+N eta`, but the current strict remainder enclosure is
still too wide for every predeclared candidate `eta` radius. This is not an R5
certificate, does not change the frozen `1e-23` normal box, and does not run
R6 or normal K=1 recovery.

`diagnostics/r5_second_order_remainder_diagnostic_v1_0.json` records the
R5-B1d provenance audit of the B1c pure-alpha second-order remainder. Its
status is `B1C_REMAINDER_DEPENDENCY_ARTIFACT`: B1c formed its remainder by
subtracting center and first-order intervals after natural interval evaluation,
whereas an independent analytic directional-Hessian bound gives a true
Lagrange remainder near `2.20e-28`. This is diagnostic-only and does not revise
the B1c result, certify the first leaf, change the frozen protocol, inspect
other leaves, run R6, or perform normal K=1 recovery.

`certificates/r5_first_leaf_hessian_krawczyk_v1_0.json` records the R5-B1e
first-leaf affine-Hessian Krawczyk result for leaf index 0 only. Its status is
`R5_FIRST_LEAF_HESSIAN_KRAWCZYK_CERTIFIED`: using the B1c affine center/slope
and the B1d explicit directional-Hessian Lagrange remainder, the predeclared
eta radii `1e-26`, `1e-24`, `1e-23`, `1e-22`, and `1e-20` have strict
self-map margins. This certifies only first-leaf graph root
existence/uniqueness; it is not a full R5 tube certificate, not R6, and not
normal K=1 recovery.

`certificates/r5_all_leaves_hessian_krawczyk_v1_0.json` records the R5-B2
all-leaves affine-Hessian Krawczyk preflight over the 16 frozen initial tube
leaves. Its status is `R5_ALL_LEAVES_HESSIAN_KRAWCZYK_CERTIFIED`: every leaf
has a strict local normal-root existence/uniqueness gate at the formal eta
radius `1e-23` under the same predeclared formula, radius set, and 192-bit Arb
precision. This remains local leaf evidence only. It does not certify adjacent
leaf gluing, full-path continuity, exact response preservation, zero total
cost, positive-measure nonconstancy, PR-R6, full R5, a global ODE flow, or
normal K=1 recovery.

`diagnostics/r5_adjacent_leaf_gluing_v1_0.json` records the R5-B3
adjacent-leaf common-root and C0 gluing diagnostic for the 15 internal seams.
Its status is `R5_ADJACENT_LEAF_C0_GLUING_NOT_CERTIFIED`: all seam
intersection boxes are nonempty with strict interior and the left/right
physical equations match, but the common endpoint Krawczyk self-map fails at
the frozen formal radius. This does not refute existence of a glued branch; it
only means the original B3 common-root gate did not certify it. The record is
kept as a superseded negative diagnostic because B3a later identified its
center/radius bookkeeping defect. It does not certify C0 or C1 gluing,
full-path response identity, zero total cost, positive-measure nonconstancy,
PR-R5, PR-R6, full GF-R5, global ODE flow, R6 search, or normal K=1 recovery.

`diagnostics/r5_seam_residual_normalization_diagnostic_v1_0.json` records the
R5-B3a seam residual normalization and coordinate-equivalence audit. Its status
is `R5_SEAM_RESIDUAL_NORMALIZATION_DIAGNOSIS_COMPLETE` with classification
`KRAWCZYK_BOOKKEEPING_DEFECT`: the previously reported B3 common forcing scale
near `2.72e-18` comes from evaluating the common residual at an interval-valued
box center and then separately applying the Krawczyk `Z*r` term. Recomputing at
the point midpoint gives seam residuals near `1e-27`, consistent with B2. This
is diagnostic-only and does not certify B3, start B4, modify the frozen
protocol, run R6, or perform normal K=1 recovery.

`certificates/r5_adjacent_leaf_gluing_v1_1.json` records the corrected R5-B3b
point-center Krawczyk common-root certification. Its status is
`R5_ADJACENT_LEAF_C0_GLUING_CERTIFIED`: all 15 internal seams certify a common
endpoint root for the same physical equation, attach to the left and right B2
unique-root tubes, and therefore give a single C0 branch across the 16 local
leaves. This remains a gluing certificate only. It does not certify C1 gluing,
full-path response identity, absolute continuity, zero total cost,
positive-measure nonconstancy, PR-R5, PR-R6, full GF-R5, global ODE flow, R6
search, or normal K=1 recovery.

`certificates/r5_global_implicit_branch_c1_v1_0.json` records the R5-B4
global implicit branch regularity certificate. Its status is
`R5_GLOBAL_IMPLICIT_BRANCH_C1_CERTIFIED`: using the B2 leaf root tubes and the
B3b common endpoint roots, all 16 leaves certify invertible `D_bF`, Arb
implicit-derivative enclosures, chart residence, and no-wrap margins, and all
15 seams attach their left and right derivatives to the same common physical
implicit derivative. The frozen protocol has no independent B4 ODE field, so
ODE consistency remains explicitly unclaimed. This is still not positive-
measure nonconstancy, full-path zero cost, PR-R5, PR-R6, full GF-R5, a global
ODE flow, R6 search, or normal K=1 recovery.

`certificates/r5_positive_measure_nonconstancy_v1_0.json` records the R5-B5
positive-measure nonconstancy certificate. Its status is
`R5_POSITIVE_MEASURE_NONCONSTANCY_CERTIFIED`: using the frozen interval
`I=[0,1/12]`, the frozen epsilon sequence, the frozen direction `v=e_1`, and
the B4 C1 derivative bound, all five declared loops have a strictly positive
environment-coordinate speed lower bound on a positive-measure set. This stage
does not check full-path zero response cost, generate a full R5 certificate,
certify PR-R5 or PR-R6, run R6, or perform normal K=1 recovery.

`certificates/r5_full_shrinking_family_v1_0.json` records the R5-B6 full
shrinking-family certificate for the frozen Geometric-Flow R5 model. Its status
is `R5_FULL_SHRINKING_FAMILY_CERTIFIED`: B4 supplies the single C1 implicit
branch and exact response-identity logic, B5 supplies positive-measure
nonconstancy, and all five frozen epsilon loops stay inside the certified full
tube. The protocol-relative response cost is certified to be exactly zero by
the invertible `B` implication, not by residual tolerance or sampling. This is
the full GF-R5 shrinking-family certificate only; it does not supply PR-R6,
run R6, perform normal K=1 recovery, certify a global ODE flow, or alter the
published theorem boundary.

## Scope

The published Geometric-Flow theorem remains the v1.2.13 local quantum-control
result. Existing v0.7.4 and v0.9.3 artifacts may inform this protocol design,
but they are not imported as new prospective R6 evidence.
