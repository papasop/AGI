## Summary

This PR reorganizes repository navigation so readers can identify the strongest
current claims within the first page of the README.

## What Changed

- Replaced the long README development log with a single status table, theorem
  summary, finite-continuation summary, claim boundary, and stable reproduction
  entry points.
- Moved the full milestone table to `docs/MILESTONES.md`.
- Added `docs/ARTIFACT_INDEX.md` for stable entry points and frozen artifact
  mapping.
- Added `docs/PROOF_MAP.md` and preview-only archive migration reports for the
  proposed `archive/frozen_milestones/` layout.
- Added `docs/PROOF_GRAPH.md` for the three proof layers and dependency graph.
- Added `docs/REPRODUCIBILITY.md` for the full one-click script order.
- Updated `docs/PAPER_WORDING.md` and `docs/CLAIM_SCOPE.md` to distinguish
  unconditional local theorem, frozen-instance finite continuation, and
  conditional/next-frame work.
- Archived the one-time v0.10.14.1 integration note under
  `docs/archive/INTEGRATION_v0.10.14.1.md`.
- Added stable wrapper scripts under `scripts/` for local ODE, finite
  continuation, field/Jacobian, Lohner flowpipe, and fifth-frame scaffold
  auditing.
- Added `tools/plan_archive_migration.py`; it emits old-path to new-path
  migration reports and intentionally refuses `--apply`.
- Updated `tools/verify_release.py` and regenerated hash manifests.

## Claim Boundary

No mathematical claim is upgraded. v0.10.6 remains the latest stored repository
reference certificate. v0.10.13.1 is described as a source-certified chain with
reference-result packaging pending. v0.10.15 remains implementation-open and
does not certify a fifth frame.

## Checks

- `python3 tools/verify_release.py`
- `python3 scripts/verify_reference_results.py`
- `/sbin/sha256sum -c SHA256SUMS_v0.9.32.txt`
- `PYTHONPYCACHEPREFIX=/private/tmp/geoflow-docs-nav-pycache python3 -m compileall -q src tools tests scripts`
- `python3 -m pytest tests`
- `python3 scripts/reproduce_lohner_flowpipe.py --check-only`
- `python3 scripts/reproduce_finite_continuation.py`
- `python3 scripts/audit_fifth_frame.py`
- `python3 tools/plan_archive_migration.py`
- `git diff --check`
