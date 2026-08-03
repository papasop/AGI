# Proof Map

This file is the reader-facing map of the repository's proof layers.  The
dependency graph lives in `docs/PROOF_GRAPH.md`; this page keeps the shorter
claim map used by the README and artifact index.

| Layer | Current artifact | Status | Claim boundary |
| --- | --- | --- | --- |
| I: local intrinsic ODE | v0.9.3 | theorem-bearing reference result | Existence, uniqueness, declared response preservation, and strict descent for one local microstep. |
| II: frozen-instance finite continuation | v0.10.6 reference certificate; v0.10.13.1 source chain | finite local continuation only | v0.10.6 is the latest stored reference certificate; v0.10.13.1 remains reference-result packaging pending. |
| III: conditional continuation | paper-level conditional theorem | conditional only | Does not replace the missing fifth-frame certificate for the frozen numerical instance. |
| Open backend work | v0.10.14.1/v0.10.15 | implementation-open fail-closed scaffold | No fifth frame, complete-child traversal, arbitrary endpoint connectivity, or global flow is certified. |

The stable user commands are:

```bash
python scripts/reproduce_local_ode.py
python scripts/verify_reference_results.py
python scripts/reproduce_lohner_flowpipe.py
python scripts/audit_fifth_frame.py
```

Historical proof scripts are indexed in `docs/ARTIFACT_INDEX.md` and stored
under `archive/frozen_milestones/`.  The short wrappers under `scripts/` are
the stable user-facing commands.
