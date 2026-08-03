# Milestones

This file keeps the detailed version history out of the README while preserving
the audit trail.

| Version | Scope | Status |
| --- | --- | --- |
| v0.7.4 | Rank, response tangency, projected-gradient nonstationarity, and strict descent on one complete subdivided parent box | Certified |
| v0.9.3 | Existence, uniqueness, exact response preservation, and strict \(L_6\) descent for one intrinsic ODE microstep | Certified reference theorem |
| v0.9.8 | Unique normal correction at the first recenter target | Certified |
| v0.9.9 | Recentered tangent/normal frame | Certified |
| v0.9.10 | Second complex fibre graph, overlap inclusion, pullback metric, and local Picard microstep | Certified |
| v0.9.11-v0.9.12 | 557-step scalar continuation and exact local-domain exhaustion boundary | Certified scalar reachable tube |
| v0.9.13 | Route correction: chart 9 is terminal, so continuation requires same-chart recentering | Certified correction |
| v0.9.15-v0.9.17 | Lohner core, hardened executable-adapter contract, and conservative formal adapter | Certified infrastructure |
| v0.9.18-v0.9.19 | Auditable diagnosis later superseded by the norm correction in v0.9.20 | Superseded |
| v0.9.20 | Corrected duplicated dimension factor and restored the 557-step scalar certificate | Certified correction |
| v0.9.21 | Six-component symmetric endpoint enclosure | Certified |
| v0.9.22 | Repository-native signed field and nonzero endpoint box | Certified |
| v0.9.23 | Complete endpoint-box inclusion and inherited unique parametric normal root | Certified |
| v0.9.24-v0.9.26 | Third-centre proof target, Arb frame, complex graph, and Picard microstep | Certified |
| v0.9.27-v0.9.28 | 263-step third-chart continuation and signed terminal endpoint box | Certified |
| v0.9.29-v0.9.30 | Fourth parametric normal root, frame, complex graph, and Picard microstep | Certified |
| v0.9.31-v0.9.32 | Ten-step fourth-chart continuation and signed terminal endpoint box | Certified finite local continuation |
| v0.9.46 | Repository-native point/box field backend refactor scaffold | Implementation-open, fail-closed |
| v0.10.1-v0.10.5 | Repository-native Arb field and same-expression 6x6 Jacobian `DX` | Certified |
| v0.10.6 | Corrected full fourth-chart domain binding and ten-step Arb Lohner support-flowpipe certificate | Latest repository reference certificate |
| v0.10.13.1 | Reindexed input-parent Taylor/affine-Lohner chain and terminal correlated set | Source-certified chain; reference-result packaging pending |
| v0.10.14.1 | Frozen terminal correlated-set object and nonlinear fourth-to-fifth transition contract | Contract emitted; no fifth-frame theorem without backend certificate |
| v0.10.15 | Fifth-frame proof-producing backend harness | Implementation-open, fail-closed |

The v0.7.4 and v0.9.3 results have different scopes: v0.7.4 covers broader
geometry but is not an ODE theorem; v0.9.3 is an ODE theorem but only for one
microscopic local step.

The v0.9.18-v0.9.19 statements about a 172-step limit and 5.985x tightening
target are retained only as correction history. They must not be cited as
current capability bounds.
