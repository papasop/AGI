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

## v0.3.5 affine-correlated zero-time handoff

This checkout also preserves the completed v0.3.5 certificate:

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

This certifies a zero-time chart 1->2 handoff for the complete frozen level-32
endpoint enclosure, with target-domain containment, corrected-controller
regularity, exact response identity, and strict objective descent on the
complete enclosure.

It does not certify a positive-time target-chart Picard slab, transition 2->3,
an eight-chart continuation, a fifth frame, a complete response fibre, hardware
validation, or global flow. The next research step is v0.3.6: one rigorously
enclosed positive-time Picard slab starting from the certified chart-2 initial
enclosure.
