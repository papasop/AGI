# Artifact Index

This index maps stable user-facing entry points to the frozen repository
artifacts they audit or execute.  The original versioned proof files remain in
place so existing hashes, release notes, and reproduction trails are preserved.

## Stable Entrypoints

| Paper layer | Preferred entry point | Compatibility wrapper |
| --- | --- | --- |
| I. Local theorem | `reproduce/local_theorem.py` | `scripts/reproduce_local_ode.py` |
| II. Frozen finite continuation | `reproduce/finite_continuation.py` | `scripts/reproduce_lohner_flowpipe.py` |
| III. Open next-frame audit | `reproduce/open_next_frame_audit.py` | `scripts/audit_fifth_frame.py` |

| Stable entry point | Underlying frozen artifact | Proof status | Notes |
| --- | --- | --- | --- |
| `scripts/reproduce_local_ode.py` | `src/response_fibre_intrinsic_picard_microstep_v0_9_3.py` | Certified reference theorem | Recomputes the local intrinsic ODE microstep through the existing v0.9.3 wrapper. |
| `scripts/reproduce_finite_continuation.py` | `scripts/reproduce_finite_chain.py` | Certified finite same-chart continuation plus source-chain audit | Prints the full chain by default; use `--run` only when predecessor artifacts are available. |
| `scripts/reproduce_field_jacobian.py` | `archive/milestones/06_taylor_lohner/geometric_flow_same_expression_field_dx_v0_10_5_oneclick.py` | Certified same-expression `X,DX` | Does not claim a QR/Lohner flowpipe or fifth-frame transition. |
| `scripts/reproduce_lohner_flowpipe.py` | `archive/milestones/06_taylor_lohner/geometric_flow_fourth_chart_qr_lohner_v0_10_6_oneclick.py` | Latest repository reference certificate | Certifies the ten-step fourth-chart support flowpipe. |
| `scripts/audit_fifth_frame.py` | `archive/milestones/06_taylor_lohner/geometric_flow_fifth_frame_backend_v0_10_15_oneclick.py` | Implementation-open fail-closed harness | Audits scaffold status; pass `--run-backend` to execute the harness explicitly. |

Each stable entry point verifies the relevant entries in `SHA256SUMS.txt`
before invoking the long versioned artifact.  A mismatch fails closed.

## Versioned Artifacts

| Manuscript archive | Primary artifact | Stored reference result | Claim boundary |
| --- | --- | --- | --- |
| v1.2.12 | `docs/manuscript/geometric_flow_v1_2_12_freeze_candidate.pdf`; `docs/manuscript/geometric_flow_v1_2_12_source.zip` | Recommended public version: DOI `10.5281/zenodo.21895917`; GitHub Release `paper-local-ode-v1.6` | Textual revision only; incorporates v1.2.9 errata; no theorem-bearing certificate, numerical gate, Arb rerun, or global-flow claim. |
| v1.2.9 | `docs/manuscript/geometric_flow_v1_2_9_freeze_candidate.pdf`; `docs/MANUSCRIPT_ERRATA_v1.2.9.md` | Historical public Zenodo/GitHub release boundary | Immutable historical version DOI and erratum; theorem-bearing boundary remains v0.7.4 + v0.9.3. |

| Milestone | Primary artifact | Stored reference result | Claim boundary |
| --- | --- | --- | --- |
| v0.9.3 | `src/response_fibre_intrinsic_picard_microstep_v0_9_3.py` | `results/v0_9_3_reference/` | Local existence, uniqueness, response preservation, and strict descent for one intrinsic microstep. |
| v0.9.24-v0.9.32 | `archive/milestones/04_third_chart/response_fibre_third_frame_v0_9_24_oneclick.py` through `archive/milestones/05_fourth_chart/response_fibre_fourth_chart_signed_endpoint_v0_9_32_oneclick.py` | Release notes and SHA manifest | Certified finite local continuation through the fourth-chart signed endpoint milestone; no fifth chart. |
| v0.10.5 | `archive/milestones/06_taylor_lohner/geometric_flow_same_expression_field_dx_v0_10_5_oneclick.py` | `results/v0_10_5/` | Repository-native same-expression field and Jacobian certificate only. |
| v0.10.6 | `archive/milestones/06_taylor_lohner/geometric_flow_fourth_chart_qr_lohner_v0_10_6_oneclick.py` | `results/v0_10_6/` | Latest independent repository reference certificate: ten-step fourth-chart support flowpipe. |
| v0.10.13.1 | `archive/milestones/06_taylor_lohner/geometric_flow_reindexed_taylor_chain_v0_10_13_oneclick.py` | Packaging pending | Source-certified reindexed Taylor/affine-Lohner terminal correlated set; not yet an independent reference result. |
| v0.10.14.1 | `archive/milestones/06_taylor_lohner/geometric_flow_fifth_frame_inclusion_v0_10_14_oneclick.py` | No new reference result certificate | Integration and inclusion-gate wiring; no fifth-frame theorem. |
| v0.10.15 | `archive/milestones/06_taylor_lohner/geometric_flow_fifth_frame_backend_v0_10_15_oneclick.py` | No certificate unless native callbacks pass | Fail-closed fifth-frame backend harness; implementation remains open. |

## Proof Map Summary

| Level | Version | Role | Status | Supersedes |
| --- | --- | --- | --- | --- |
| I | v0.9.3 | Local intrinsic ODE | theorem-bearing reference result | - |
| II | v0.10.6 | Fourth-chart Lohner support flowpipe | latest repository reference certificate | v0.9.32 continuation inputs |
| II | v0.10.13.1 | Finite correlated continuation | source-certified; reference packaging pending | v0.10.6 chain input |
| III | conditional theorem | Conditional continuation | paper-level conditional statement | - |
| Open | v0.10.14.1/v0.10.15 | Fifth-frame transition contract and backend harness | implementation-open fail-closed scaffold | - |

## Historical Status

| Version | Classification | Reason |
| --- | --- | --- |
| v0.9.18 | superseded | induced-norm factor corrected by v0.9.20; do not use as a current conclusion entry point |
| v0.9.34 | retracted | ellipsoid did not contain the complete endpoint box |
| v0.9.40 | superseded | invalid equal per-entry allocation |
| v0.10.9 | failed closed | corrected by mean-value v0.10.9.1 |

## Archived Frozen Milestone Classes

The historical `response_fibre_*_oneclick.py` and v0.10 one-click backend files
have been moved out of the repository root and maintenance `src/` surface into
`archive/milestones/`.  Their original filenames are preserved, and the
stable user interface remains the short wrappers under `scripts/`.
Superseded, retracted, and corrected milestones are cross-referenced in
`docs/archive/SUPERSEDED_RESULTS.md`.

| Class | Frozen artifacts | Current status | Archive target |
| --- | --- | --- | --- |
| 01 local foundation | `archive/milestones/01_local_foundation/response_fibre_validated_continuation_v0_9_4_1_oneclick.py`, `archive/milestones/01_local_foundation/response_fibre_two_step_continuation_v0_9_5_oneclick.py`, `archive/milestones/01_local_foundation/response_fibre_recenter_preflight_v0_9_6_oneclick.py`, `archive/milestones/01_local_foundation/response_fibre_normal_root_v0_9_7_oneclick.py`, `archive/milestones/01_local_foundation/response_fibre_arb_normal_root_v0_9_8_oneclick.py` | Audit history, initial continuation, and normal-root setup | `archive/milestones/01_local_foundation/` |
| 02 second chart | `archive/milestones/02_second_chart/response_fibre_recentered_frame_v0_9_9_oneclick.py`, `archive/milestones/02_second_chart/response_fibre_second_chart_v0_9_10_oneclick.py`, `archive/milestones/02_second_chart/response_fibre_finite_continuation_v0_9_11_oneclick.py`, `archive/milestones/02_second_chart/response_fibre_transition_preflight_v0_9_12_oneclick.py`, `archive/milestones/02_second_chart/response_fibre_route_correction_v0_9_13_oneclick.py` | Second local chart continuation and route correction | `archive/milestones/02_second_chart/` |
| 03 endpoint enclosure | `archive/milestones/03_endpoint_enclosure/response_fibre_endpoint_identifiability_v0_9_14_oneclick.py`, `archive/milestones/03_endpoint_enclosure/response_fibre_validated_lohner_v0_9_15_oneclick.py`, `archive/milestones/03_endpoint_enclosure/response_fibre_adapter_hardening_v0_9_16_oneclick.py`, `archive/milestones/03_endpoint_enclosure/response_fibre_executable_adapter_v0_9_17_oneclick.py`, `archive/milestones/03_endpoint_enclosure/response_fibre_local_dx_target_v0_9_19_oneclick.py`, `archive/milestones/03_endpoint_enclosure/response_fibre_cauchy_norm_correction_v0_9_20_oneclick.py`, `archive/milestones/03_endpoint_enclosure/response_fibre_six_component_endpoint_v0_9_21_oneclick.py`, `archive/milestones/03_endpoint_enclosure/response_fibre_signed_field_export_v0_9_22_oneclick.py` | Lohner, adapter, norm-correction, and endpoint-box evidence | `archive/milestones/03_endpoint_enclosure/` |
| Superseded v0.9.18 | `archive/milestones/superseded/v0_9_18/response_fibre_lohner_stress_v0_9_18_oneclick.py` | Superseded by v0.9.20 norm correction; retained for audit only | `archive/milestones/superseded/v0_9_18/` |
| 04 third chart | `archive/milestones/04_third_chart/response_fibre_third_recenter_inclusion_v0_9_23_oneclick.py` through `archive/milestones/04_third_chart/response_fibre_third_chart_signed_endpoint_v0_9_28_oneclick.py` | Valid finite continuation chain | `archive/milestones/04_third_chart/` |
| 05 fourth chart | `archive/milestones/05_fourth_chart/response_fibre_fourth_frame_v0_9_29_oneclick.py` through `archive/milestones/05_fourth_chart/response_fibre_fourth_chart_signed_endpoint_v0_9_32_oneclick.py` | Valid finite continuation chain feeding later v0.10 work | `archive/milestones/05_fourth_chart/` |
| 06 Taylor/Lohner | `archive/milestones/06_taylor_lohner/geometric_flow_active_backend_export_v0_10_1_oneclick.py` through `archive/milestones/06_taylor_lohner/geometric_flow_fifth_frame_backend_v0_10_15_oneclick.py` | Current effective backend chain through v0.10.13.1 plus implementation-open fifth-frame harness | `archive/milestones/06_taylor_lohner/` |

The migration changes repository paths and raw GitHub URLs, so wrappers,
manifests, verifier paths, reproduction commands, and embedded dependency
downloads were updated together in the same archive-migration PR.

## Target Archive Layout

```text
archive/
  milestones/
    01_local_foundation/
    02_second_chart/
    03_endpoint_enclosure/
    04_third_chart/
    05_fourth_chart/
    06_taylor_lohner/
    superseded/
```

Run `python tools/plan_archive_migration.py` to regenerate
`docs/ARCHIVE_MIGRATION_PLAN.json` and `docs/ARCHIVE_MIGRATION_PLAN.md`. The
tool records legacy path, archive path, SHA-256, classification, and remaining
legacy text references. It is read-only and refuses `--apply`.

## Future Package Boundary

The future importable package can live under `geometric_flow/` with modules such
as `field.py`, `normal_graph.py`, `jacobian.py`, `lohner.py`, and
`certificates.py`.  That package should wrap repository-native primitives only
after their formal callbacks and certificates exist.  Stable script entry
points provide readability while archived proof files keep their historical
filenames. Avoid adding new user-facing versioned scripts when a milestone can
be routed through `src/`, `reproduce/`, and `archive/milestones/`.
