# Integration guide

1. Create a branch from the current `main` branch.
2. Copy the three scripts in this package into `src/`.
3. Preserve the existing v0.10.6 files and correction history.
4. Add a README milestone section for v0.10.13.1 and v0.10.14.1.
5. State explicitly that v0.10.15 is an implementation-open native adapter
   harness, not a fifth-frame theorem.
6. Run `python -m py_compile src/*.py` and the repository structural checks.
7. Do not add reference certificates unless they were produced by the same
   frozen source hashes and independently verified.

Recommended pull-request title:

```text
Add v0.10.13.1 terminal correlated-set milestone and fifth-frame contract
```

Recommended claim boundary:

> The reindexed ten-step local-root, second-order Taylor, and correlated
> affine/Lohner chain is certified. The terminal correlated set is frozen for
> a fifth-frame transition audit. No fifth frame, fifth Picard chart,
> complete-child continuation, or global flow is claimed.
