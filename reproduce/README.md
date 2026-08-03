# Reproduction Entrypoints

These three scripts mirror the paper-level claim structure:

| Layer | Script | Purpose |
| --- | --- | --- |
| I | `python reproduce/local_theorem.py` | Recompute the frozen v0.9.3 local ODE theorem. |
| II | `python reproduce/finite_continuation.py` | Verify and reproduce the stored finite continuation reference flowpipe. |
| III | `python reproduce/open_next_frame_audit.py` | Audit the implementation-open fifth-frame target without upgrading claims. |

The older `scripts/` wrappers remain as compatibility entry points. New work
should extend these three visible reproduction paths before adding any new
user-facing versioned script.
