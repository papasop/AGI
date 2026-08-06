# Manuscript Provenance

This file separates three objects that must not be conflated:

- the archived manuscript/preprint version;
- the theorem-bearing software certificate boundary;
- later continuation research code in the same repository.

## Submission Candidate

- Manuscript version: submission candidate `(4)(6)` local-theorem manuscript.
- Theorem software boundary: v0.7.4 complete-parent-box descent certificate +
  v0.9.3 validated intrinsic response-fibre ODE microstep.
- Later research code excluded from this manuscript boundary: v0.10.x finite
  continuation, v0.10.13.1 source chain, v0.10.14.1/v0.10.15 fifth-frame work,
  analytic conditional-continuation manuscript, neural-network analogies, and
  global-flow claims.

## Local Candidate Files

The following local submission-candidate archive was inspected before archival:

- PDF filename: `geometric_flow_v0.9.3_paper.pdf`
- PDF SHA-256:
  `7ee7ce97fda5eaca79a18ba9cba48e4e72bf312e41dbc718094b9492cb235685`
- PDF pages: 14
- Source ZIP filename: `geometric-flow-latex (2).zip`
- Source ZIP SHA-256:
  `958d1bf3cab237c57ddba9031758559c353cd9f8d2c0380c9276c3ebb79fe5f4`
- Identical local copy: `geometric-flow-latex (3).zip`
- Identical local copy SHA-256:
  `958d1bf3cab237c57ddba9031758559c353cd9f8d2c0380c9276c3ebb79fe5f4`

Local text/source checks observed:

- theorem statement uses existence and uniqueness of the ODE solution;
- Introduction includes the Lanford--Tucker validated-numerics comparison;
- Conclusion is the short local-theorem conclusion;
- endpoint inclusion, adjacent microstep chaining, ten-chart continuation, and
  global response-fibre flow remain open.

## Previous Zenodo Record Inspected

- Zenodo record: https://zenodo.org/records/21728432
- Version DOI inspected: `10.5281/zenodo.21728432`
- Concept DOI: `10.5281/zenodo.15879392`
- Zenodo PDF filename: `geometric_flow_v0.9.3_paper.pdf`
- Zenodo PDF SHA-256:
  `3ed12cab486c42dc55aca020bcd100962a556cd536b24e5ce5b6404b5460b29a`
- Zenodo PDF MD5:
  `9f9b6679d6a6e4a7d6e31f5e3ec62e02`
- Zenodo PDF pages: 14

Status: this previous Zenodo PDF SHA-256 differs from the local `(4)(6)`
submission-candidate PDF SHA-256 above.

## Archived Zenodo Version

- Zenodo `(4)(6)` record: https://zenodo.org/records/21830043
- Zenodo `(4)(6)` version DOI: `10.5281/zenodo.21830043`
- Concept DOI: `10.5281/zenodo.15879392`
- Zenodo `(4)(6)` PDF filename: `geometric_flow_v0.9.3_paper.pdf`
- Zenodo `(4)(6)` PDF SHA-256:
  `e74467003ba39666b309fa6babbb467bd77206cbf556348f0fb50f04605c628c`
- Zenodo `(4)(6)` PDF MD5:
  `bf73435c15ebf145a6686a0b69d4b167`
- Zenodo `(4)(6)` PDF pages: 14

The archived Zenodo PDF was generated at a later time than the local candidate
PDF and is not byte-identical to the local candidate hash above. Text extraction
checks confirm that it contains the local-theorem wording required for
submission:

- there exists a unique solution;
- existence and uniqueness;
- the Lanford--Tucker validated-numerics comparison;
- endpoint inclusion and adjacent microstep chaining remain open;
- complete-atlas and global continuation remain open.

## Remaining Archival Fields To Complete

- Zenodo `(4)(6)` source ZIP SHA-256: `PENDING`
- GitHub paper tag: `paper-local-ode-v1.1`
- Git commit: the commit pointed to by `paper-local-ode-v1.1`
- SHA-256 manifest: `SHA256SUMS.txt` in the tagged commit

The previous immutable tag `paper-local-ode-v1.0` is retained. The v1.1 tag is
for manuscript wording and provenance documentation only; theorem-bearing
numerical certificates are unchanged.

## CI Evidence To Complete

Record successful GitHub Actions URLs for the submission-candidate commit:

- `structural-checks`: `PENDING`
- `reproduce-validated-ode`: `PENDING`
- `reproduce-joint-geometric-flow`: `PENDING`

The third workflow is the most important external CI reproduction gate because
it recomputes both theorem-bearing components:

- v0.7.4 parent-box geometry;
- v0.9.3 intrinsic ODE microstep;
- joint local-paper release gate.
