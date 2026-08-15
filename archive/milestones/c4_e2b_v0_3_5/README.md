# C4-E2b affine-correlated handoff v0.3.5

This directory archives the repository copy of the v0.3.5 driver:

`C4_E2B_AFFINE_CORRELATED_HANDOFF_SUBDIVISION_v0_3_5.py`

It consumes the frozen C4-E2b v0.3.2 level-32 endpoint checkpoint, the v0.3.3
local affine bridge candidate, and the v0.3.4.1 controller-covariance
diagnostic. The generated certificate is stored under
`results/c4_e2b/c4_e2b_affine_correlated_handoff_v0_3_5.json`.

## Result status

The deposited certificate reports:

- `scientific_status = C4_E2B_AFFINE_CORRELATED_HANDOFF_CERTIFIED`
- `all_gates_pass = true`
- `evaluations = 1`
- `accepted_leaves = 1`
- `blocked_leaves = 0`
- `maximum_leaf_depth = 0`
- `maximum_accepted_dL_upper = -2.2171423824770025`
- `maximum_accepted_inverse_neumann_defect = 0.015748151846082692`
- `maximum_accepted_target_domain_use = 0.00237998237338449`

## Claim boundary

This is a zero-time chart 1->2 handoff certificate for the complete frozen
level-32 endpoint enclosure, retaining source-chart affine correlations while
evaluating the target-centred corrected controller.

It does not certify a positive-time target-chart Picard slab, transition 2->3,
an eight-chart continuation, a fifth frame, a complete response fibre, global
flow, K=1, Pulser, hardware, or QPU behaviour.

The next research driver is v0.3.6: one rigorously enclosed positive-time
Picard slab starting from the certified chart-2 initial enclosure.
