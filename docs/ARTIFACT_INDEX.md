# Artifact Index

This index maps stable user-facing entry points to the frozen repository
artifacts they audit or execute.  The original versioned proof files remain in
place so existing hashes, release notes, and reproduction trails are preserved.

## Stable Entrypoints

| Stable entry point | Underlying frozen artifact | Proof status | Notes |
| --- | --- | --- | --- |
| `scripts/reproduce_local_ode.py` | `src/response_fibre_intrinsic_picard_microstep_v0_9_3.py` | Certified reference theorem | Recomputes the local intrinsic ODE microstep through the existing v0.9.3 wrapper. |
| `scripts/reproduce_finite_continuation.py` | `scripts/reproduce_finite_chain.py` | Certified finite same-chart continuation plus source-chain audit | Prints the full chain by default; use `--run` only when predecessor artifacts are available. |
| `scripts/reproduce_field_jacobian.py` | `src/geometric_flow_same_expression_field_dx_v0_10_5_oneclick.py` | Certified same-expression `X,DX` | Does not claim a QR/Lohner flowpipe or fifth-frame transition. |
| `scripts/reproduce_lohner_flowpipe.py` | `src/geometric_flow_fourth_chart_qr_lohner_v0_10_6_oneclick.py` | Latest repository reference certificate | Certifies the ten-step fourth-chart support flowpipe. |
| `scripts/audit_fifth_frame.py` | `src/geometric_flow_fifth_frame_backend_v0_10_15_oneclick.py` | Implementation-open fail-closed harness | Audits scaffold status; pass `--run-backend` to execute the harness explicitly. |

Each stable entry point verifies the relevant entries in `SHA256SUMS.txt`
before invoking the long versioned artifact.  A mismatch fails closed.

## Versioned Artifacts

| Milestone | Primary artifact | Stored reference result | Claim boundary |
| --- | --- | --- | --- |
| v0.9.3 | `src/response_fibre_intrinsic_picard_microstep_v0_9_3.py` | `results/v0_9_3_reference/` | Local existence, uniqueness, response preservation, and strict descent for one intrinsic microstep. |
| v0.9.24-v0.9.32 | `response_fibre_third_frame_v0_9_24_oneclick.py` through `response_fibre_fourth_chart_signed_endpoint_v0_9_32_oneclick.py` | Release notes and SHA manifest | Certified finite local continuation through the fourth-chart signed endpoint milestone; no fifth chart. |
| v0.10.5 | `src/geometric_flow_same_expression_field_dx_v0_10_5_oneclick.py` | `results/v0_10_5/` | Repository-native same-expression field and Jacobian certificate only. |
| v0.10.6 | `src/geometric_flow_fourth_chart_qr_lohner_v0_10_6_oneclick.py` | `results/v0_10_6/` | Latest independent repository reference certificate: ten-step fourth-chart support flowpipe. |
| v0.10.13.1 | `src/geometric_flow_reindexed_taylor_chain_v0_10_13_oneclick.py` | Packaging pending | Source-certified reindexed Taylor/affine-Lohner terminal correlated set; not yet an independent reference result. |
| v0.10.14.1 | `src/geometric_flow_fifth_frame_inclusion_v0_10_14_oneclick.py` | No new reference result certificate | Integration and inclusion-gate wiring; no fifth-frame theorem. |
| v0.10.15 | `src/geometric_flow_fifth_frame_backend_v0_10_15_oneclick.py` | No certificate unless native callbacks pass | Fail-closed fifth-frame backend harness; implementation remains open. |

## Future Package Boundary

The future importable package can live under `geometric_flow/` with modules such
as `field.py`, `normal_graph.py`, `jacobian.py`, `lohner.py`, and
`certificates.py`.  That package should wrap repository-native primitives only
after their formal callbacks and certificates exist.  Until then, stable script
entry points provide readability without renaming proof archives.
