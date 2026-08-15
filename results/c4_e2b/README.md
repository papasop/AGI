# C4-E2b generated results

This directory intentionally contains no manufactured certificate. Running the
resume entrypoint writes checkpoints and reports here so that they can be saved
before a Colab runtime is discarded.

An absent JSON file means that stage has not been completed in the current
checkout. `INCONCLUSIVE` must not be relabelled as `FAIL` or `PASS`.

## v0.3.4.1 local run

This checkout preserves the completed v0.3.2/v0.3.3/v0.3.4.1 recovery run:

- `c4_e2b_transition_12_arb_ladder_v0_3_2.json` records the 32-slab
  transition 1->2 ladder as `C4_E2B_TRANSITION_12_LADDER_INCONCLUSIVE`.
  The frozen 0->1 prerequisite passes, the endpoint centre remains inside the
  overlap, and the complete endpoint box is not certified inside the overlap.
- `c4_e2b_local_bridge_candidate_v0_3_3.json` and
  `c4_e2b_local_recenter_affine_handoff_v0_3_3.json` record a local affine
  bridge candidate whose preflight gates pass. This is not a fresh Arb
  transition certificate.
- `c4_e2b_handoff_controller_covariance_v0_3_4_1.json` records the
  controller-covariance diagnostic status
  `INTERVAL_DEPENDENCY_DOMINATES_DESCENT_TEST`.

The diagnostic interpretation is cause separation: midpoint descent remains
visible, while interval dependency/wrapping dominates the complete-box descent
test. The recorded next step is to preserve affine correlations or subdivide
only the handoff box. This directory does not claim validated-flowpipe
continuation, complete transition 1->2 certification, hardware validation, or
global flow.

## v0.3.5 affine-correlated zero-time handoff residual

This checkout preserves the original v0.3.5 report unchanged for provenance:

- `c4_e2b_affine_correlated_handoff_v0_3_5.json` records
  `C4_E2B_AFFINE_CORRELATED_HANDOFF_CERTIFIED`.
- The complete frozen level-32 endpoint enclosure is accepted in one leaf,
  without subdivision, when the source-chart affine generators are retained.
- The accepted leaf has strict objective descent with
  `maximum_accepted_dL_upper = -2.2171423824770025`.
- The corrected-controller inverse Neumann defect remains below one with
  `maximum_accepted_inverse_neumann_defect = 0.015748151846082692`.
- The target-domain containment use remains below one with
  `maximum_accepted_target_domain_use = 0.00237998237338449`.

External audit identified a binary64 outward-rounding residual in the original
controller-inverse Neumann norm/tail calculation and in quadratic-enclosure
radius helpers. The zero-time handoff decision is numerically robust under the
recorded margins, but the original controller-inverse and quadratic enclosure
radii contain round-to-nearest binary64 norm and tail calculations. The
original artifact is retained for provenance and is pending rigorous
outward-rounded recertification.

The v0.3.5.1 repair chain is therefore `pending_recertification` until a fresh
Colab run produces new hash-bound JSON. This directory must not infer the new
certificate from the old report or from console logs.

Neither v0.3.5 nor v0.3.5.1 certifies a positive-time target-chart Picard slab,
transition 2->3, an eight-chart continuation, a fifth frame, a complete
response fibre, hardware validation, or global flow. The v0.3.6 name remains
reserved for the first rigorously enclosed positive-time Picard slab.
