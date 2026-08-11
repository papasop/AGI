# Manuscript Provenance

This document binds the submission manuscript to its source archive,
repository state, theorem-bearing software boundary, and public archive.

## Historical manuscript candidates

- Title: *Computation as Geometric Flow: An Arb-Certified Local Intrinsic ODE
  on a Quantum-Control Response Fibre*
- Status: historical v1.1 candidate retained for audit history. The current
  frozen manuscript is v1.2.9; see "v1.2.9 manuscript" below.
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
  `0c1eb8b3a881e6b0e0fdf466ed84bbaa603b7c9f5257e7745a27da0adc3473cb`
- compiled PDF:
  `docs/manuscript/geometric_flow_submission_candidate_v1.1.1_parameter_erratum.pdf`
- compiled PDF SHA-256:
  `18d11f4fdeef27bf053ab1924b04ec626a51526de9a0e934a84666532d96258a`

The old v1.1 manuscript candidate files above are preserved for auditability.
The current frozen manuscript is v1.2.9; see "v1.2.9 manuscript" below.
The v1.1 records are retained for audit history.
The v1.1.1 final PDF was checked for the corrected affine atlas-arclength
notation in Theorem 2 and Corollary 2 and for closure of the subsequent
manuscript-internal review findings. The matching final source archive listed
above has been exported and hashed for the immutable archival release candidate.

## v1.2.9 manuscript

- Manuscript version: `v1.2.9`
- Scope: manuscript freeze candidate with no Arb rerun and no change to the
  v0.7.4 or v0.9.3 theorem-bearing software boundary.
- PDF:
  `docs/manuscript/geometric_flow_v1_2_9_freeze_candidate.pdf`
- PDF SHA-256:
  `1755b3ac6ea6f2efb5115a4b54591083cfbe57a1738b9dac1ca34e211d5760b7`
- source archive:
  `docs/manuscript/geometric_flow_v1_2_9_source.zip`
- source SHA-256:
  `6c6d842c8ca6a31631cee3f83e42f52d8accabe34950d8c8683ce457b35b713a`
- pages: 19, A4
- last displayed equation: (37)
- references: [1]-[18]
- theorem software boundary: unchanged v0.7.4 parent-box certificate and
  unchanged v0.9.3 intrinsic ODE certificate.
- Arb rerun: not performed for this manuscript freeze; the existing frozen
  theorem certificates remain the governing numerical evidence.
- `GLOBAL_FLOW_CLAIMED`: false
- repository release tag: `paper-local-ode-v1.5`
- manuscript/tag mapping: `v1.2.9` manuscript ->
  `paper-local-ode-v1.5` repository release.
- manuscript integration merge commit:
  `49f04aa61d796fa4da40f9b94a155a435f113f8d`
- source PR: `https://github.com/papasop/Geometric-Flow/pull/32`
- GitHub release URL:
  `https://github.com/papasop/Geometric-Flow/releases/tag/paper-local-ode-v1.5`

Release identifiers for this revision:

- Zenodo version DOI: `10.5281/zenodo.21882158`
- final release commit:
  `8742913c3ba992db98b90bc79cd691a31199d1e7`
- exact tag: `paper-local-ode-v1.5`
- annotated tag object:
  `038ac83231af925725da8f9a2c9b10067053bcf6`
- peeled commit:
  `8742913c3ba992db98b90bc79cd691a31199d1e7`
- workflow URLs:
  - structural-checks:
    `https://github.com/papasop/Geometric-Flow/actions/runs/31452933116`
  - reproduce-validated-ode:
    `https://github.com/papasop/Geometric-Flow/actions/runs/31452933117`
  - reproduce-joint-geometric-flow:
    `https://github.com/papasop/Geometric-Flow/actions/runs/31452933149`
- exact workflow commit for all three successful tag-triggered runs:
  `8742913c3ba992db98b90bc79cd691a31199d1e7`

The final `paper-local-ode-v1.5` tag must point to the `main` commit produced
after the release-metadata PR is merged. It must not point to PR #32's merge
commit; `49f04aa61d796fa4da40f9b94a155a435f113f8d` records manuscript
integration only.

`paper-local-ode-v1.4` predates the v1.2.9 manuscript integration and is
preserved unchanged. It must not be moved, deleted, or reused for v1.2.9. The
historical `paper-local-ode-v1.4` annotated tag object is
`b28425354835365b5a33d13a9e7abb006aaaf80e` and its peeled commit is
`09c17df957159ae4c867ea8ab6090a108a3e5784`.

The v1.2.9 source archive contains its own `README_BUILD.md` and
`SOURCE_MANIFEST.md`. The handoff review reports that its source-file manifest
passes, a clean three-pass `pdflatex` build produces a 19-page A4 PDF, and the
rebuilt/frozen `pdftotext -layout` comparison is identical. The rebuilt PDF
byte hash may differ because pdfTeX regenerates time and ID metadata; the
frozen PDF above remains the archival manuscript.

## Public archive and repository binding

- Historical Zenodo version DOI: `10.5281/zenodo.21728432`
- Zenodo version DOI: `10.5281/zenodo.21882158`
- Zenodo DOI URL: `https://doi.org/10.5281/zenodo.21882158`
- GitHub release URL:
  `https://github.com/papasop/Geometric-Flow/releases/tag/paper-local-ode-v1.5`
- immutable paper-boundary tag: `paper-local-ode-v1.5`
- annotated tag object:
  `038ac83231af925725da8f9a2c9b10067053bcf6`
- peeled commit:
  `8742913c3ba992db98b90bc79cd691a31199d1e7`
- repository commit:
  `8742913c3ba992db98b90bc79cd691a31199d1e7`

The Zenodo version DOI `10.5281/zenodo.21882158` identifies the frozen v1.2.9
manuscript. The historical Zenodo version DOI `10.5281/zenodo.21728432` and
the public record `https://zenodo.org/records/21728432` identify an earlier
public manuscript version and boundary. The actual all-versions Concept DOI is
not recorded here because it has not been independently verified from the
authoritative Zenodo metadata.

Observed GitHub tags during this update: `paper-local-ode-v1.0`,
`paper-local-ode-v1.1`, `paper-local-ode-v1.2`, `paper-local-ode-v1.3`, and
`paper-local-ode-v1.4` already exist. Do not move them. The annotated
`paper-local-ode-v1.5` tag was created and verified at the object and
peeled-commit identifiers recorded above; it must not be moved or reused.

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

- structural-checks workflow URL:
  `https://github.com/papasop/Geometric-Flow/actions/runs/31452933116`
- validated-ODE workflow URL:
  `https://github.com/papasop/Geometric-Flow/actions/runs/31452933117`
- joint v0.7.4 + v0.9.3 workflow URL:
  `https://github.com/papasop/Geometric-Flow/actions/runs/31452933149`
- exact workflow commit:
  `8742913c3ba992db98b90bc79cd691a31199d1e7`

The URLs above must refer to successful runs on the exact immutable submission
commit. An empty or unavailable status is not evidence of success.

## Licensing

- software licence: MIT
- manuscript licence: Creative Commons Attribution 4.0 International
  (CC BY 4.0)

CC BY 4.0 governs the v1.2.9 manuscript and manuscript source archive. MIT
continues to govern the repository software. The two licences cover different
artifact classes.
