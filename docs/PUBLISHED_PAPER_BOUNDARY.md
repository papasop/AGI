# Published Paper Boundary

This file records the theorem boundary for the published Zenodo paper and
separates it from later repository development milestones.

## Recommended Manuscript

- Title: *Computation as Geometric Flow: An Arb-Certified Local Intrinsic ODE on
  a Quantum-Control Response Fibre*
- Manuscript version: `v1.2.13`
- PDF:
  `docs/manuscript/geometric_flow_v1_2_13_disclosure_revision.pdf`
- PDF SHA-256:
  `ac32035f2d0ead1db713e8724ad8838241a86dd61514712348955117207f92fa`
- source archive:
  `docs/manuscript/geometric_flow_v1_2_13_source.zip`
- source SHA-256:
  `0be1613be102d878f9b5362fa1d61792d4e3a6496dc5cb3a97f139b6ac64db06`
- source manifest SHA-256:
  `29d08de1a9f14f20aa668a0b257d4827f6a3f684208bb2c804cc9105b28feb07`
- repository release tag: `paper-local-ode-v1.7`
- GitHub Release:
  https://github.com/papasop/Geometric-Flow/releases/tag/paper-local-ode-v1.7
- Zenodo version DOI: https://doi.org/10.5281/zenodo.21947745
- all-versions Concept DOI: https://doi.org/10.5281/zenodo.15879392

Manuscript v1.2.13 is a disclosure and notation revision derived from v1.2.12.
It incorporates the recorded v1.2.9 errata and subsequent textual
clarifications into the recommended reading version. It does not change the
mathematical conclusions, theorem-bearing constants, frozen certificates, or
the v0.7.4 + v0.9.3 theorem boundary. No Arb rerun was performed or required.
The frozen v1.2.12 and v1.2.9 assets remain immutable historical records.

This manuscript boundary is `v1.2.13`. The theorem-bearing software boundary
remains the
frozen v0.7.4 parent-box certificate plus the frozen v0.9.3 local intrinsic
ODE certificate. No Arb rerun was performed for the manuscript freeze.
`GLOBAL_FLOW_CLAIMED=false`.

## Historical Public Release

- Manuscript version: `v1.2.12`
- PDF:
  `docs/manuscript/geometric_flow_v1_2_12_freeze_candidate.pdf`
- PDF SHA-256:
  `8f431f83aba4714b9895c3e94e10b24152dc6154e2d65792687ef4b6ced87768`
- source archive:
  `docs/manuscript/geometric_flow_v1_2_12_source.zip`
- source SHA-256:
  `2a2e6f0135ee2b53f0d022eb506c87aff4885e94a592c4f4ec8e7bdceb4f5d5b`
- GitHub Release:
  https://github.com/papasop/Geometric-Flow/releases/tag/paper-local-ode-v1.6
- Zenodo version DOI: https://doi.org/10.5281/zenodo.21895917

The v1.2.12 release is preserved as a historical public version. It is not
overwritten by the v1.2.13 disclosure/notation revision.

## Earlier Historical Public Release

- Manuscript version: `v1.2.9`
- Zenodo record: https://zenodo.org/records/21882158
- Historical version DOI: https://doi.org/10.5281/zenodo.21882158
- GitHub Release:
  https://github.com/papasop/Geometric-Flow/releases/tag/paper-local-ode-v1.5

The v1.2.9 public release is preserved as a historical version DOI and release
boundary. It is not overwritten by the v1.2.12 Gate A archive branch.

## Included

- v0.7.4 complete-parent-box descent certificate.
- v0.9.3 validated intrinsic response-fibre ODE microstep.
- `python reproduce/published_paper.py` as the local verification entry point
  for the stored published-paper boundary.
- The frozen v0.9.3 software theorem boundary recorded in `CITATION.cff`,
  `results/v0_9_3_reference/`, and the hash manifest.

## Erratum

The frozen v1.2.9 manuscript remains unchanged. Its official textual
clarifications, including the certified initial condition, Picard tube,
target-state convention, certificate-field mapping, and provenance, are
recorded in
[`MANUSCRIPT_ERRATA_v1.2.9.md`](MANUSCRIPT_ERRATA_v1.2.9.md).

These clarifications do not alter the frozen PDF, source archive,
theorem-bearing software boundary, numerical certificate, or claim scope,
and they require no Arb rerun.

The complete-parent-box loss derivative constant `-0.6530784697700559` is a
bound on `dL6/dell`, where `ell` is the affine atlas arclength coordinate
recorded by the serialized chart. It is not a bound on `dL6/ds` in the local
Chebyshev coordinate. The monotone affine relation between `s` and `ell`
preserves the strict ordering statement; no frozen certificate value, proof
gate, hash-bound input, or Arb algorithm is changed.

When certificates or scripts display longer decimal values, those displays are
nearest-rounded binary64 renderings of the stored certificate data. The
manuscript uses outward-safe decimal quotations for public theorem wording.
This display convention does not change any theorem-bearing source, input,
certificate, protocol, report, numerical constant, or validation threshold.

## Excluded

- v0.10.6 finite continuation and fourth-chart Lohner support flowpipe.
- v0.10.13.1 reindexed Taylor/affine-Lohner source chain.
- v0.10.14.1/v0.10.15 fifth-frame and fail-closed backend work.
- The analytic conditional-continuation manuscript.
- Fifth-frame certification, complete-child traversal, ten-chart continuation,
  arbitrary endpoint connection, response-fibre connectedness, or any
  unconditional global flow.

Later v0.10.x work remains excluded from the v1.2.13 local-theorem
boundary.

## Tag Boundary

- Immutable paper-boundary tag: `paper-local-ode-v1.7`
- Annotated tag object:
  `f9e28082345d86ef47a8786865d5f90d4d9b6257`
- Peeled commit:
  `f470b702b4dc87ef0df8ef28c19112174932c134`

The current tag binds the v1.2.13 Zenodo version DOI, the GitHub Release above,
the local-paper title, the v0.7.4 + v0.9.3 theorem-bearing software boundary,
the SHA-256 manifest, and the explicit exclusion of v0.10.x continuation work
from the published-paper theorem claim. It must not be moved or reused. The
historical `paper-local-ode-v1.6` and `paper-local-ode-v1.5` tags remain
immutable and continue to bind the v1.2.12 and v1.2.9 public releases.

Historical note: `paper-local-ode-v1.0`, the historical version DOI
`10.5281/zenodo.21728432`, and `https://zenodo.org/records/21728432` belong to
an earlier public manuscript boundary and are not the current v1.2.12
or v1.2.13 manuscript/release boundary. Zenodo's authoritative record metadata identifies
`10.5281/zenodo.15879392` as the all-versions Concept DOI.
