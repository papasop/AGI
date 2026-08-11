# Published Paper Boundary

This file records the theorem boundary for the published Zenodo paper and
separates it from later repository development milestones.

## Published Paper

- Title: *Computation as Geometric Flow: An Arb-Certified Local Intrinsic ODE on
  a Quantum-Control Response Fibre*
- Manuscript version: `v1.2.9`
- Zenodo record: https://zenodo.org/records/21882158
- Version DOI: https://doi.org/10.5281/zenodo.21882158
- GitHub Release:
  https://github.com/papasop/Geometric-Flow/releases/tag/paper-local-ode-v1.5

This manuscript/release boundary is `v1.2.9` /
`paper-local-ode-v1.5`. The theorem-bearing software boundary remains the
frozen v0.7.4 parent-box certificate plus the frozen v0.9.3 local intrinsic
ODE certificate. No Arb rerun was performed for the manuscript freeze.
`GLOBAL_FLOW_CLAIMED=false`.

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

Later v0.10.x work remains excluded from the published v1.2.9 theorem
boundary.

## Tag Boundary

- Immutable paper-boundary tag: `paper-local-ode-v1.5`
- Annotated tag object:
  `038ac83231af925725da8f9a2c9b10067053bcf6`
- Peeled commit:
  `8742913c3ba992db98b90bc79cd691a31199d1e7`

The tag binds the v1.2.9 Zenodo version DOI, the GitHub Release above, the
local-paper title, the v0.7.4 + v0.9.3 theorem-bearing software boundary, the
SHA-256 manifest, and the explicit exclusion of v0.10.x continuation work from
the published-paper theorem claim. It must not be moved or reused.

Historical note: `paper-local-ode-v1.0`, the historical version DOI
`10.5281/zenodo.21728432`, and `https://zenodo.org/records/21728432` belong to
an earlier public manuscript boundary and are not the current v1.2.9
manuscript/release boundary. The actual all-versions Concept DOI is not
recorded here because it has not been independently verified from the
authoritative Zenodo metadata.
