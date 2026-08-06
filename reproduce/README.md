# Reproduction Entrypoints

These scripts separate the archived local-manuscript boundary from later
continuation research-line checks:

| Scope | Script | Purpose |
| --- | --- | --- |
| Archived manuscript | `python reproduce/published_paper.py` | Verify v0.7.4 parent-box descent, v0.9.3 intrinsic ODE, hashes, and the archived-manuscript boundary. |
| Archived manuscript rerun | `python reproduce/published_paper.py --run` | Recompute the v0.7.4 + v0.9.3 theorem pair locally. |
| Level I component | `python reproduce/local_theorem.py` | Recompute the frozen v0.9.3 local ODE theorem only. |
| Research line | `python reproduce/finite_continuation.py` | Verify and reproduce the stored finite continuation reference flowpipe. |
| Research line | `python reproduce/open_next_frame_audit.py` | Audit the implementation-open fifth-frame target without upgrading claims. |

`finite_continuation.py` and `open_next_frame_audit.py` are not part of the
archived Zenodo manuscript theorem boundary.

The older `scripts/` wrappers remain as compatibility entry points. New work
should extend these three visible reproduction paths before adding any new
user-facing versioned script.
