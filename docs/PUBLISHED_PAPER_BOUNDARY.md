# Published Paper Boundary

This file records the theorem boundary for the archived Zenodo manuscript and
separates it from later repository development milestones.

## Archived Manuscript

- Title: *Computation as Geometric Flow: An Arb-Certified Local Intrinsic ODE on
  a Quantum-Control Response Fibre*
- Zenodo record: https://zenodo.org/records/21830043
- DOI: https://doi.org/10.5281/zenodo.21830043

For manuscript/PDF/source-archive hashes and the `(4)(6)` submission-candidate
archival status, see `docs/MANUSCRIPT_PROVENANCE.md`.

## Included

- v0.7.4 complete-parent-box descent certificate.
- v0.9.3 validated intrinsic response-fibre ODE microstep.
- `python reproduce/published_paper.py` as the local verification entry point
  for the stored archived-manuscript boundary.
- The frozen v0.9.3 software theorem boundary recorded in `CITATION.cff`,
  `results/v0_9_3_reference/`, and the hash manifest.

## Excluded

- v0.10.6 finite continuation and fourth-chart Lohner support flowpipe.
- v0.10.13.1 reindexed Taylor/affine-Lohner source chain.
- v0.10.14.1/v0.10.15 fifth-frame and fail-closed backend work.
- The analytic conditional-continuation manuscript.
- Fifth-frame certification, complete-child traversal, ten-chart continuation,
  arbitrary endpoint connection, response-fibre connectedness, or any
  unconditional global flow.

## Tag Boundary

The first immutable paper-boundary tag is `paper-local-ode-v1.0`. It binds the
Zenodo DOI, the local-paper title above, the v0.7.4 and v0.9.3 certificate
boundary, the SHA-256 manifest, and the explicit exclusion of v0.10.x
continuation work from the archived-manuscript theorem claim.

The follow-up tag `paper-local-ode-v1.1` is reserved for manuscript wording and
provenance documentation only. It does not change theorem-bearing numerical
certificates.
