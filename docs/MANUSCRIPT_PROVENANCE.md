# Manuscript Provenance

This document binds the submission manuscript to its source archive,
repository state, theorem-bearing software boundary, and public archive status.
It separates three objects that must not be conflated:

- the manuscript/preprint file version;
- the theorem-bearing software certificate boundary;
- later continuation research code in the same repository.

## Repository Submission Candidate

- Manuscript version: submission candidate v1.1 local-theorem manuscript.
- Title: *Computation as Geometric Flow: An Arb-Certified Local Intrinsic ODE
  on a Quantum-Control Response Fibre*
- PDF: `manuscripts/submission/v1.1/geometric_flow_submission_candidate_v1.1.pdf`
- PDF SHA-256:
  `86edef125808640fc7c59b2ceec39d3fd36954b4b395b20f5949de13d0364b96`
- Source archive:
  `manuscripts/submission/v1.1/geometric_flow_submission_candidate_v1.1_source.zip`
- Source archive SHA-256:
  `70526251604b9ed67997610ea370365f38f1d591b5c7a53c51fdf6bdc503e328`
- PDF pages: 14

Local PDF/source checks observed:

- theorem statement uses existence and uniqueness of the ODE solution;
- Introduction includes the Lanford--Tucker validated-numerics comparison;
- Conclusion is the short local-theorem conclusion;
- endpoint inclusion, adjacent microstep chaining, ten-chart continuation, and
  global response-fibre flow remain open.

## Public Archive Status

- Zenodo concept DOI: `10.5281/zenodo.15879392`
- Latest inspected Zenodo record: https://zenodo.org/records/21830043
- Latest inspected Zenodo version DOI: `10.5281/zenodo.21830043`
- Latest inspected Zenodo PDF SHA-256:
  `e74467003ba39666b309fa6babbb467bd77206cbf556348f0fb50f04605c628c`
- Latest inspected Zenodo PDF MD5:
  `bf73435c15ebf145a6686a0b69d4b167`

Status: the latest inspected Zenodo PDF is not byte-identical to the repository
submission candidate above. It passed text-level checks for the local-theorem
wording, but it does not bind the exact repository PDF/source archive bytes.

Required archival action: create a new Zenodo version for the repository
submission candidate if byte-identical public archival is required. Preserve
the existing Zenodo version chain; do not overwrite an earlier version.

## Fields To Complete Before Final Submission

- Zenodo version DOI for the exact repository PDF/source archive: `PENDING`
- GitHub release URL containing the exact PDF/source archive: `PENDING`
- immutable paper-boundary tag: `paper-local-ode-v1.3`
- repository commit: commit pointed to by `paper-local-ode-v1.3`
- exact workflow commit: `PENDING`

The previous immutable tags `paper-local-ode-v1.0`, `paper-local-ode-v1.1`, and
`paper-local-ode-v1.2` are retained and must not be moved. The v1.3 tag is for
the repository submission-candidate PDF/source archive and provenance update
only; theorem-bearing numerical certificates are unchanged.

## Theorem-Bearing Boundary

- v0.7.4: complete-parent-box rank, near-tangency, nonstationarity, and strict
  descent certificate on 16 theorem-bearing child boxes.
- v0.7.4 diagnostic exclusion: the frozen KKT-alignment threshold is not met;
  the serialized atlas is not certified as an ODE trajectory.
- v0.9.3: existence and uniqueness of a local solution to the intrinsic
  response-fibre ODE, exact declared-response preservation, and strict `L6`
  descent on `0 <= t <= 1e-14`.
- v0.10.x: later continuation research, excluded from this manuscript theorem.

## Reproduction Record

- structural-checks workflow URL: `PENDING`
- reproduce-validated-ode workflow URL: `PENDING`
- reproduce-joint-geometric-flow workflow URL: `PENDING`

The URLs above must refer to successful runs on the exact immutable submission
commit. An empty or unavailable status is not evidence of success.

## Licensing

- software licence: MIT
- manuscript licence: CC BY 4.0, matching the Zenodo record metadata unless a
  later public archive version states otherwise

Do not assume that the software licence also governs the manuscript.
