## Summary

This PR adds the v0.10.14.1 incremental source delta after the certified
v0.10.6 support-flowpipe milestone.

## What Changed

- Added `src/geometric_flow_reindexed_taylor_chain_v0_10_13_oneclick.py`.
- Added `src/geometric_flow_fifth_frame_inclusion_v0_10_14_oneclick.py`.
- Added `src/geometric_flow_fifth_frame_backend_v0_10_15_oneclick.py`.
- Added `docs/INTEGRATION.md` and `RELEASE_NOTES_v0.10.14.1.md`.
- Updated README, changelog, claim-scope docs, release verification, and hash
  manifests.

## Scientific Scope

The packaged source boundary is the reindexed ten-step local-root,
second-order Taylor, and correlated affine/Lohner chain plus a frozen terminal
correlated set for a fourth-to-fifth transition audit.

The v0.10.15 script is a fail-closed proof-producing backend harness. Its
native Arb callbacks remain implementation-open until a real adapter replaces
the generated template and all formal gates pass.

## Claim Boundary

No fifth frame, fifth Picard chart, complete-child continuation,
atlas-wide continuation, or global-flow theorem is claimed. This delta does
not add repository reference result certificates beyond the existing v0.10.6
reference set.

## Checks

- `/sbin/sha256sum /Users/bai/Downloads/Geometric-Flow_v0.10.14.1_update.zip`
- `unzip -t /Users/bai/Downloads/Geometric-Flow_v0.10.14.1_update.zip`
- `python3 tools/verify_release.py`
- `/sbin/sha256sum -c SHA256SUMS.txt`
- `/sbin/sha256sum -c SHA256SUMS_v0.9.32.txt`
- `PYTHONPYCACHEPREFIX=/private/tmp/geoflow-v010141-pycache python3 -m compileall -q src tools tests`
- `python3 -m pytest tests`
