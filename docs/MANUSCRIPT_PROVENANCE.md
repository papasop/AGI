# Manuscript Provenance

This document binds the submission manuscript to its source archive,
repository state, theorem-bearing software boundary, and public archive.

## Manuscript

- Title: *Computation as Geometric Flow: An Arb-Certified Local Intrinsic ODE
  on a Quantum-Control Response Fibre*
- Status: submission candidate; verify public archive status before changing
  this description
- PDF: `docs/manuscript/geometric_flow_submission_candidate_v1.1.pdf`
- PDF SHA-256:
  `86edef125808640fc7c59b2ceec39d3fd36954b4b395b20f5949de13d0364b96`
- source archive: `docs/manuscript/geometric_flow_submission_candidate_v1.1_source.zip`
- source SHA-256:
  `70526251604b9ed67997610ea370365f38f1d591b5c7a53c51fdf6bdc503e328`

## Parameter-label erratum source

- Revision: `v1.1.1_parameter_erratum`
- Scope: corrects the v0.7.4 complete-parent-box derivative label from
  serialized Chebyshev-coordinate `dL6/ds` to affine atlas-arclength
  `dL6/dell`, closes the associated manuscript-internal definition and
  provenance wording obligations, and changes no theorem-bearing value or
  proof computation.
- intermediate source archive (does not reproduce the final PDF below):
  `docs/manuscript/geometric_flow_submission_candidate_v1.1.1_parameter_erratum_source.zip`
- intermediate source SHA-256:
  `5de3c7599cdff6bc3734483af1a0986dc4755df04177077e6e5a81e2781e1fb9`
- matching final source archive:
  `docs/manuscript/geometric_flow_submission_candidate_v1.1.1_parameter_erratum_final_source.zip`
- matching final source SHA-256:
  `265042b0689b12e4d16f1ae5d498eae4b7ea4cd9adf9f5bd36bc294d55d4f01b`
- compiled PDF:
  `docs/manuscript/geometric_flow_submission_candidate_v1.1.1_parameter_erratum.pdf`
- compiled PDF SHA-256:
  `18d11f4fdeef27bf053ab1924b04ec626a51526de9a0e934a84666532d96258a`

The old v1.1 manuscript candidate files above are preserved for auditability.
The v1.1.1 final PDF was checked for the corrected affine atlas-arclength
notation in Theorem 2 and Corollary 2 and for closure of the subsequent
manuscript-internal review findings. The matching final source archive listed
above has been exported and hashed for the immutable archival release candidate.

## Public archive and repository binding

- Zenodo concept DOI: `10.5281/zenodo.21728432`
- Zenodo version DOI: `VERIFY_ON_GITHUB_OR_ZENODO`
- GitHub release URL: `VERIFY_ON_GITHUB`
- immutable paper-boundary tag: `paper-local-ode-v1.4` proposed; `VERIFY_ON_GITHUB`
- repository commit: `VERIFY_ON_GITHUB`

Do not fill these fields by inference. The version DOI must identify the exact
archived files above. If the current Zenodo version contains an earlier PDF,
create a new Zenodo version and preserve the earlier record.

Observed during this update: the public Zenodo record
`https://zenodo.org/records/21728432` advertises
`geometric_flow_v0.9.3_paper.pdf`, not the v1.1 candidate files listed above.
Therefore the v1.1 manuscript candidate requires a new Zenodo version before
the version DOI and public release fields can be completed.

Observed GitHub tags during this update: `paper-local-ode-v1.0`,
`paper-local-ode-v1.1`, `paper-local-ode-v1.2`, and
`paper-local-ode-v1.3` already exist. Do not move them. Re-verify that
`paper-local-ode-v1.4` remains unused immediately before creating a new
immutable paper-boundary tag.

## Theorem-bearing boundary

- v0.7.4: complete-parent-box rank, near-tangency, nonstationarity, and strict
  descent certificate on 16 theorem-bearing child boxes.
- v0.7.4 diagnostic exclusion: the frozen KKT-alignment threshold is not met;
  the serialized atlas is not certified as an ODE trajectory.
- v0.9.3: existence and uniqueness of a local solution to the intrinsic
  response-fibre ODE, exact declared-response preservation, and strict `L6`
  descent on `0 <= t <= 1e-14`.
- v0.10.x: later continuation research, excluded from this manuscript theorem.

## Reproduction record

- structural-checks workflow URL: `VERIFY_AFTER_SUCCESS`
- validated-ODE workflow URL: `VERIFY_AFTER_SUCCESS`
- joint v0.7.4 + v0.9.3 workflow URL: `VERIFY_AFTER_SUCCESS`
- exact workflow commit: `VERIFY_AFTER_SUCCESS`

The URLs above must refer to successful runs on the exact immutable submission
commit. An empty or unavailable status is not evidence of success.

## Licensing

- software licence: MIT
- manuscript licence: `VERIFY_AGAINST_ZENODO_FOR_V1_1`

Do not assume that the software licence also governs the manuscript.
