# Prospective Principle R Protocol Scaffold

This directory contains a prospective model-level test scaffold for
realizability criteria R1--R7. It is intentionally isolated from the published
v1.2.13 theorem boundary.

Status:

```text
PROTOCOL_FROZEN_NO_R6_SEARCH_PERFORMED
```

This scaffold freezes a future protocol only. It does not execute an R6
search, does not produce a certificate, and does not change any frozen source,
certificate, tag, Release, manuscript, or Zenodo asset.

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
```

The verifier checks schema, required fields, declared file hashes, R1--R5/R7
declarations, absence of R6 result fields, and the exact frozen status string.
It does not run Arb, Krawczyk, Picard, Lohner, or any R6 search.

The R7 verifier checks the stored v1.1 certificate, including full
`eta_delta(s)=theta_0+s*delta*n` path endpoint containment for every frozen
delta. It does not run R5 or R6.

`R5_FEASIBILITY_AUDIT.md` records a first-stage, read-only R5 feasibility
audit. Its final status is
`R5_INCONCLUSIVE_MISSING_FULL_LOOP_GRAPH_CERTIFICATE` because the repository
does not yet contain an R5-specific complete-loop implicit-graph certificate or
the auxiliary frozen intrinsic-chart data needed to verify one fail-closed. It
is not an R5 certificate, does not report a failed R5 search, and does not run
R6.

`r5_full_tube_protocol_v1_0.json` freezes a subordinate R5-A protocol for a
future full-tube graph certificate on the one-dimensional segment
`a=t*v, |t|<=1e-12`. Its status is
`R5_FULL_TUBE_PROTOCOL_FROZEN_NO_CERTIFICATE_RUN`.
`data/r5_full_tube_auxiliary_v1_0.json` is the committed candidate auxiliary
artifact for `theta_0`, `T`, `N`, graph-equation response-coordinate map `B`,
target `c`, and numerical candidate preconditioner `P`. Its byte content is
frozen and hash-bound. Its binary64 SVD construction is platform-sensitive and
is not a cross-platform reproducibility or theorem-bearing gate. Local
regeneration is a diagnostic only; future R5-B work must certify the committed
candidate objects by independent Arb validation of frame rank, transversality,
`B` invertibility, preconditioner defect, and full-tube graph gates before any
R5 certificate can exist. The protocol does not run R5 or R6 and does not
relabel v0.9.2/v0.9.3 as R5 or R6 evidence.

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

## Scope

The published Geometric-Flow theorem remains the v1.2.13 local quantum-control
result. Existing v0.7.4 and v0.9.3 artifacts may inform this protocol design,
but they are not imported as new prospective R6 evidence.
