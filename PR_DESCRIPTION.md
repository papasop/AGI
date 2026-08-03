## Summary

Archive frozen milestone scripts and update repository paths.

## Changes

- Move historical `response_fibre_*_oneclick.py` scripts from the repository
  root into categorized `archive/frozen_milestones/` folders.
- Move v0.10 one-click Taylor/Lohner backend scripts from `src/` into
  `archive/frozen_milestones/06_taylor_lohner/`.
- Preserve every frozen script filename.
- Update stable wrappers under `scripts/` to call the archived paths after
  checking SHA-256 entries.
- Update `docs/REPRODUCIBILITY.md`, `docs/ARTIFACT_INDEX.md`, verifier paths,
  update verifier paths, raw GitHub source paths, and SHA manifests.
- Convert `tools/plan_archive_migration.py` into a read-only applied-migration
  audit report generator.

## Compatibility And Scientific Scope

- No theorem is upgraded.
- No certificate is promoted or reclassified as stronger.
- v0.10.6 remains the latest stored repository reference certificate.
- v0.10.13.1 remains source-certified with reference-result packaging pending.
- v0.10.14.1/v0.10.15 remain implementation-open fifth-frame scaffold work.
- No fifth frame, complete-child traversal, arbitrary endpoint connectivity, or
  global flow is claimed.

## Checks

- `python3 tools/verify_release.py`
- `python3 scripts/verify_reference_results.py`
- `/sbin/sha256sum -c SHA256SUMS_v0.9.32.txt`
- `python3 tools/plan_archive_migration.py`
- `python3 scripts/reproduce_lohner_flowpipe.py --check-only`
- `python3 scripts/reproduce_finite_continuation.py`
- `python3 scripts/audit_fifth_frame.py`
- `PYTHONPYCACHEPREFIX=/private/tmp/geoflow-archive-migration-pycache python3 -m compileall -q archive src tools tests scripts`
- `python3 -m pytest tests`
- `git diff --check`
