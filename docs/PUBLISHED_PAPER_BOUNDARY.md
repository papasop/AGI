# Published Paper Boundary

This file records the theorem boundary for the published Zenodo paper and
separates it from later repository development milestones.

## Published Paper

- Title: *Computation as Geometric Flow: An Arb-Certified Local Intrinsic ODE on
  a Quantum-Control Response Fibre*
- Zenodo record: https://zenodo.org/records/21728432
- DOI: https://doi.org/10.5281/zenodo.21728432

## Included

- v0.7.4 complete-parent-box descent certificate.
- v0.9.3 validated intrinsic response-fibre ODE microstep.
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

The immutable paper-boundary tag is `paper-local-ode-v1.0`. It is intended to
bind the Zenodo DOI, the local-paper title above, the v0.7.4 and v0.9.3
certificate boundary, the SHA-256 manifest, and the explicit exclusion of
v0.10.x continuation work from the published-paper theorem claim.
