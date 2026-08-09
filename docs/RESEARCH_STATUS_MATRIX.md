# Research Status Matrix

This matrix is the repository-level evidence ledger for current and future
tracks. It is documentation only and does not add new scientific results.

## Evidence Classes

```text
FROZEN_CERTIFIED
ARB_CERTIFIED_LOCAL
NUMERICAL_PREFLIGHT
EMULATOR_EVIDENCE
DESIGN_ONLY
OPEN_THEOREM
SPECULATIVE
NOT_YET_ARCHIVED
```

`NOT_YET_ARCHIVED` is used for local or external work that has not yet passed
repository intake with executable scripts, protocols, reports, manifests, and
claim-boundary review.

## Current Matrix

| Track | Item | Status | Boundary |
| --- | --- | --- | --- |
| P | v0.7.4 + v0.9.3 published theorem | FROZEN_CERTIFIED | Published local ODE boundary only |
| G | v0.10.6 finite continuation | ARB_CERTIFIED_LOCAL | Frozen finite same-chart/finite-chain evidence, not global flow |
| G | global flow | OPEN_THEOREM | No complete fibre or arbitrary-endpoint theorem |
| C | C4-D1 finite product-tube residence | ARB_CERTIFIED_LOCAL | Fixed local product tube; no positive invariance or global continuation |
| C | C4-E2a nine-chart overlap chain | ARB_CERTIFIED_LOCAL | Overlap-chain certificate; not validated-flowpipe continuation |
| C | C4-E2b validated flowpipe transport | OPEN_THEOREM | Next control-geometry milestone |
| W | finite-shot/memory/delay controller | NOT_YET_ARCHIVED | Local/external outputs are not current repository evidence |
| T | process-time definition | DESIGN_ONLY | Candidate definitions only |
| M | pseudo-Riemannian layer | OPEN_THEOREM | No physical spacetime claim |
| D | certificate DAG | DESIGN_ONLY | Derived execution semantics only |
| K | response-fibre K=1 bridge | OPEN_THEOREM | Independent bridge not established |

## Promotion Rules

- `DESIGN_ONLY` requires a predeclared protocol before numerical evidence.
- `NUMERICAL_PREFLIGHT` requires frozen scripts, reports, manifests, controls,
  and review before it can be repository evidence.
- `EMULATOR_EVIDENCE` is not hardware/QPU evidence.
- `ARB_CERTIFIED_LOCAL` requires interval-certified gates and scoped local
  claims.
- Any promotion requires a dedicated pull request and updated claim boundary.

The not-yet-archived Pulser v1.0-v1.3 outputs must not be cited as repository
evidence until they are imported through a later W-layer evidence PR.
