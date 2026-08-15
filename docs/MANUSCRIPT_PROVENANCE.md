# Manuscript Provenance

This document binds the submission manuscript to its source archive,
repository state, theorem-bearing software boundary, and public archive.

## Historical manuscript candidates

- Title: *Computation as Geometric Flow: An Arb-Certified Local Intrinsic ODE
  on a Quantum-Control Response Fibre*
- Status: historical v1.1 candidate retained for audit history. The current
  recommended reading manuscript is v1.2.13; see "v1.2.13 manuscript" below.
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
The recommended reading manuscript is v1.2.13; see "v1.2.13 manuscript" below.
The v1.2.9 manuscript remains the previous public archive and historical DOI
boundary.
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
- textual clarifications and errata:
  `docs/MANUSCRIPT_ERRATA_v1.2.9.md`
- clarification SHA-256:
  `1469688fbdf85b2b5af5a8c184e298d0b1186d49030dd0d44b51ee3e1ee91ca2`
- clarification boundary: repository-level textual clarification only;
  the frozen PDF and source archive remain unchanged.
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

## v1.2.12 manuscript

- Manuscript version: `v1.2.12`
- Scope: textual revision only. Manuscript v1.2.12 incorporates the recorded
  v1.2.9 errata and subsequent textual clarifications into a self-contained
  recommended reading version. It does not change the mathematical
  conclusions, theorem-bearing constants, frozen certificates, or the v0.7.4 +
  v0.9.3 theorem boundary. No Arb rerun was performed or required. The frozen
  v1.2.9 assets and their erratum remain immutable historical records.
- PDF:
  `docs/manuscript/geometric_flow_v1_2_12_freeze_candidate.pdf`
- PDF SHA-256:
  `8f431f83aba4714b9895c3e94e10b24152dc6154e2d65792687ef4b6ced87768`
- source archive:
  `docs/manuscript/geometric_flow_v1_2_12_source.zip`
- source SHA-256:
  `2a2e6f0135ee2b53f0d022eb506c87aff4885e94a592c4f4ec8e7bdceb4f5d5b`
- source manifest inside archive:
  `geometric-flow-latex/SOURCE_MANIFEST.md`
- source manifest SHA-256:
  `fac13564730834b3f00323f8924415097228454889534299fee5616de42611ce`
- pages: 20, A4
- last displayed equation: (37)
- references: [1]-[18]
- baseline v1.2.9 source archive SHA-256:
  `6c6d842c8ca6a31631cee3f83e42f52d8accabe34950d8c8683ce457b35b713a`
- v1.2.9 erratum SHA-256:
  `1469688fbdf85b2b5af5a8c184e298d0b1186d49030dd0d44b51ee3e1ee91ca2`
- theorem software boundary: unchanged v0.7.4 parent-box certificate and
  unchanged v0.9.3 intrinsic ODE certificate.
- Arb rerun: not performed for this manuscript revision; the existing frozen
  theorem certificates remain the governing numerical evidence.
- `GLOBAL_FLOW_CLAIMED`: false
- repository release tag: `paper-local-ode-v1.6`
- manuscript/tag mapping: `v1.2.12` manuscript ->
  `paper-local-ode-v1.6` repository release.
- final release commit:
  `9f00cef039a8b97598e06e87614f9b506a81cddc`
- repository commit:
  `9f00cef039a8b97598e06e87614f9b506a81cddc`
- annotated tag object:
  `e4da94c96f271d5eed63a1d18821476686de9aa3`
- peeled commit:
  `9f00cef039a8b97598e06e87614f9b506a81cddc`
- GitHub release URL:
  `https://github.com/papasop/Geometric-Flow/releases/tag/paper-local-ode-v1.6`
- Zenodo version DOI: `10.5281/zenodo.21895917`
- Zenodo DOI URL: `https://doi.org/10.5281/zenodo.21895917`
- all-versions Concept DOI: `10.5281/zenodo.15879392`
- source PR: `https://github.com/papasop/Geometric-Flow/pull/42`
- workflow URLs:
  - structural-checks:
    `https://github.com/papasop/Geometric-Flow/actions/runs/31549636860`
  - reproduce-validated-ode:
    `https://github.com/papasop/Geometric-Flow/actions/runs/31549636994`
  - reproduce-joint-geometric-flow:
    `https://github.com/papasop/Geometric-Flow/actions/runs/31549636914`
- exact workflow commit for all three successful tag-triggered runs:
  `9f00cef039a8b97598e06e87614f9b506a81cddc`

The v1.2.12 source archive contains its own `README_BUILD.md` and
`SOURCE_MANIFEST.md`. The archive manifest reports a clean three-pass
`pdflatex` build, 20 A4 pages, last displayed equation (37), references
[1]-[18], zero undefined references or citations, zero rerun requests after
three passes, and zero overfull or underfull boxes. The source manifest lists
16 source-file hashes and excludes `SOURCE_MANIFEST.md` itself to avoid a
self-hash loop.

## v1.2.13 manuscript

- Manuscript version: `v1.2.13`
- Scope: disclosure and notation revision only, derived from v1.2.12. The
  revision resolves manuscript-exposition gaps concerning frame construction,
  Krawczyk normal-box uniqueness, the segment-propagator factor convention,
  reflected analytic extension, fixed zero-threshold child gates,
  cross-environment reproducibility, and subdivision indexing. It does not
  change theorem statements, mathematical conclusions, theorem-bearing
  constants, interval endpoints, frozen certificates, validation gates, or the
  v0.7.4 + v0.9.3 theorem boundary.
- PDF:
  `docs/manuscript/geometric_flow_v1_2_13_disclosure_revision.pdf`
- PDF SHA-256:
  `ac32035f2d0ead1db713e8724ad8838241a86dd61514712348955117207f92fa`
- source archive:
  `docs/manuscript/geometric_flow_v1_2_13_source.zip`
- source SHA-256:
  `0be1613be102d878f9b5362fa1d61792d4e3a6496dc5cb3a97f139b6ac64db06`
- source manifest inside archive:
  `geometric-flow-latex/SOURCE_MANIFEST.md`
- source manifest SHA-256:
  `29d08de1a9f14f20aa668a0b257d4827f6a3f684208bb2c804cc9105b28feb07`
- pages: 21, A4
- last displayed equation: (37)
- references: [1]-[18]
- GitHub asset sizes:
  - `geometric_flow_v1_2_13_disclosure_revision.pdf`: 397423 bytes
  - `geometric_flow_v1_2_13_source.zip`: 39434 bytes
- GitHub asset SHA-256:
  - `geometric_flow_v1_2_13_disclosure_revision.pdf`:
    `ac32035f2d0ead1db713e8724ad8838241a86dd61514712348955117207f92fa`
  - `geometric_flow_v1_2_13_source.zip`:
    `0be1613be102d878f9b5362fa1d61792d4e3a6496dc5cb3a97f139b6ac64db06`
- Zenodo asset sizes:
  - `geometric_flow_v1_2_13_disclosure_revision.pdf`: 397423 bytes
  - `geometric_flow_v1_2_13_source.zip`: 39434 bytes
- Zenodo MD5:
  - `geometric_flow_v1_2_13_disclosure_revision.pdf`:
    `63620c0e46b3568fd8fbc4cb11cbd5ae`
  - `geometric_flow_v1_2_13_source.zip`:
    `a37b76f21d90f36820944bb7c9adfe6a`
- Independent public-download SHA-256:
  - GitHub PDF:
    `ac32035f2d0ead1db713e8724ad8838241a86dd61514712348955117207f92fa`
  - GitHub source ZIP:
    `0be1613be102d878f9b5362fa1d61792d4e3a6496dc5cb3a97f139b6ac64db06`
  - Zenodo PDF:
    `ac32035f2d0ead1db713e8724ad8838241a86dd61514712348955117207f92fa`
  - Zenodo source ZIP:
    `0be1613be102d878f9b5362fa1d61792d4e3a6496dc5cb3a97f139b6ac64db06`
- GitHub/Zenodo asset consistency:
  - PDF: byte-identical public downloads.
  - source ZIP: byte-identical public downloads.
- deterministic build metadata:
  `SOURCE_DATE_EPOCH=1786789922`, `FORCE_SOURCE_DATE=1`
- declared build engine:
  `pdfTeX 3.141592653-2.6-1.40.25 (TeX Live 2023/Debian)`
- declared build command: three passes of
  `pdflatex -interaction=nonstopmode -halt-on-error main.tex`
- theorem software boundary: unchanged v0.7.4 parent-box certificate and
  unchanged v0.9.3 intrinsic ODE certificate.
- Arb rerun: not performed for this manuscript revision; the existing frozen
  theorem certificates remain the governing numerical evidence.
- C4-E2b dependency: none.
- `GLOBAL_FLOW_CLAIMED`: false
- repository release tag: `paper-local-ode-v1.7`
- manuscript/tag mapping: `v1.2.13` manuscript ->
  `paper-local-ode-v1.7` repository release.
- final release commit:
  `f470b702b4dc87ef0df8ef28c19112174932c134`
- repository commit:
  `f470b702b4dc87ef0df8ef28c19112174932c134`
- annotated tag object:
  `f9e28082345d86ef47a8786865d5f90d4d9b6257`
- peeled commit:
  `f470b702b4dc87ef0df8ef28c19112174932c134`
- GitHub release URL:
  `https://github.com/papasop/Geometric-Flow/releases/tag/paper-local-ode-v1.7`
- GitHub Release ID: `371035428`
- GitHub asset IDs:
  - `geometric_flow_v1_2_13_disclosure_revision.pdf`: `515640471`
  - `geometric_flow_v1_2_13_source.zip`: `515640493`
- Zenodo record URL: `https://zenodo.org/records/21947745`
- Zenodo version DOI: `10.5281/zenodo.21947745`
- Zenodo DOI URL: `https://doi.org/10.5281/zenodo.21947745`
- all-versions Concept DOI: `10.5281/zenodo.15879392`
- Zenodo resource type: Preprint
- Zenodo access: open
- Zenodo license: Creative Commons Attribution 4.0 International (CC BY 4.0)
- publication date: `2026-08-15`
- source PR: `https://github.com/papasop/Geometric-Flow/pull/49`
- release provenance:
  `docs/manuscript/V1_2_13_RELEASE_PROVENANCE.md`
- workflow URLs:
  - structural-checks:
    `https://github.com/papasop/Geometric-Flow/actions/runs/31882336563`
  - reproduce-validated-ode:
    `https://github.com/papasop/Geometric-Flow/actions/runs/31882336589`
  - reproduce-joint-geometric-flow:
    `https://github.com/papasop/Geometric-Flow/actions/runs/31882336569`
- exact workflow commit for all three successful tag-triggered runs:
  `f470b702b4dc87ef0df8ef28c19112174932c134`
- private L3 audit package: not included in the public GitHub Release or
  Zenodo record.

The supplied source archive is the source bundle for the 21-page disclosure
revision PDF. Its internal `SOURCE_MANIFEST.md` verifies 16/16 source-file
hashes. The archive excludes build products such as `main.aux`, `main.log`,
`main.out`, `main.toc`, and `main.pdf`. The deterministic build was attested
with pdfTeX 1.40.25, TeX Live 2023/Debian, `SOURCE_DATE_EPOCH=1786789922`,
`FORCE_SOURCE_DATE=1`, and three `pdflatex` passes; the rebuilt PDF was
byte-identical to the archived repository PDF.

## Public archive and repository binding

- Historical Zenodo version DOI: `10.5281/zenodo.21728432`
- Previous Zenodo version DOI: `10.5281/zenodo.21882158`
- Previous Zenodo version DOI: `10.5281/zenodo.21895917`
- Current Zenodo version DOI: `10.5281/zenodo.21947745`
- current Zenodo DOI URL: `https://doi.org/10.5281/zenodo.21947745`
- all-versions Concept DOI: `10.5281/zenodo.15879392`
- GitHub release URL:
  `https://github.com/papasop/Geometric-Flow/releases/tag/paper-local-ode-v1.7`
- immutable paper-boundary tag: `paper-local-ode-v1.7`
- annotated tag object:
  `f9e28082345d86ef47a8786865d5f90d4d9b6257`
- peeled commit:
  `f470b702b4dc87ef0df8ef28c19112174932c134`
- repository commit:
  `f470b702b4dc87ef0df8ef28c19112174932c134`

The Zenodo version DOI `10.5281/zenodo.21947745` identifies the frozen v1.2.13
recommended reading manuscript. The preceding version DOI
`10.5281/zenodo.21895917` identifies v1.2.12, `10.5281/zenodo.21882158`
identifies v1.2.9, and the historical version DOI `10.5281/zenodo.21728432`
identifies an earlier public manuscript boundary.
Zenodo's authoritative record metadata identifies `10.5281/zenodo.15879392`
as the all-versions Concept DOI.

Observed GitHub tags during this update: `paper-local-ode-v1.0`,
`paper-local-ode-v1.1`, `paper-local-ode-v1.2`, `paper-local-ode-v1.3`, and
`paper-local-ode-v1.4` already exist. Do not move them. The annotated
`paper-local-ode-v1.5` historical tag remains immutable. The annotated
`paper-local-ode-v1.6` historical tag remains immutable. The annotated
`paper-local-ode-v1.7` tag was verified at the object and peeled-commit
identifiers recorded above; it must not be moved or reused.

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
  `https://github.com/papasop/Geometric-Flow/actions/runs/31549636860`
- validated-ODE workflow URL:
  `https://github.com/papasop/Geometric-Flow/actions/runs/31549636994`
- joint v0.7.4 + v0.9.3 workflow URL:
  `https://github.com/papasop/Geometric-Flow/actions/runs/31549636914`
- exact workflow commit:
  `9f00cef039a8b97598e06e87614f9b506a81cddc`

The URLs above must refer to successful runs on the exact immutable submission
commit. An empty or unavailable status is not evidence of success.

## Licensing

- software licence: MIT
- manuscript licence: Creative Commons Attribution 4.0 International
  (CC BY 4.0)

CC BY 4.0 governs the v1.2.13, v1.2.12, and historical v1.2.9 manuscripts and
their manuscript source archives. MIT continues to govern the repository
software. The two licences cover different artifact classes.
