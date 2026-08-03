# Computation as Geometric Flow

This repository develops Arb-certified, repository-native continuation
milestones for response-preserving intrinsic descent in a frozen fourteen-phase
quantum-control model.

The reference theorem is local: the frozen v0.9.3 artifact proves existence and
uniqueness of a six-dimensional intrinsic ODE microstep, exact preservation of
the declared response map \(\mathcal R_3\), and strict decrease of \(L_6\).
Later repository artifacts certify finite same-chart continuation milestones.

## Three-Layer Status

| Layer | Current Repository Status | Claim |
| --- | --- | --- |
| I. Local theorem | v0.9.3 intrinsic ODE microstep | Certified reference theorem |
| II. Frozen finite continuation | v0.10.6 fourth-chart Lohner support flowpipe | Latest stored repository reference certificate |
| III. Next-frame / global work | v0.10.13.1 source chain and v0.10.15 fail-closed harness | Implementation-open; not a fifth-frame or global-flow theorem |

The v0.10.13.1 source chain records a reindexed Taylor/affine-Lohner terminal
set, but its reference-result packaging is pending. The v0.10.15 fifth-frame
backend harness is fail-closed scaffold work.

## Quick Start

Python 3.12 and `python-flint==0.8.0` are recommended.

```bash
python scripts/reproduce_local_ode.py
python scripts/verify_reference_results.py
python scripts/reproduce_lohner_flowpipe.py
python scripts/audit_fifth_frame.py
```

Optional finite-chain wrappers:

```bash
python scripts/reproduce_finite_continuation.py
python scripts/reproduce_field_jacobian.py
```

The stable scripts verify the relevant frozen SHA-256 entries before calling
their archived long-form proof drivers in `archive/frozen_milestones/`.

## Claim Boundary

The repository currently certifies local strict ODE behavior and finite
frozen-instance continuation milestones. It does not certify:

- a fifth tangent/normal frame or fifth local fibre graph;
- complete traversal of child 15;
- a successor atlas chart after terminal chart 9;
- complete ten-chart continuation;
- connectivity of arbitrary points in a response fibre; or
- a global geometric flow.

The archived milestone scripts keep their original long filenames for audit
stability. This repository cleanup changes navigation, not proof content.

## Documentation

- [docs/CLAIM_SCOPE.md](docs/CLAIM_SCOPE.md): precise allowed and forbidden claims
- [docs/MATHEMATICS.md](docs/MATHEMATICS.md): mathematical construction
- [docs/REFERENCE_RESULTS.md](docs/REFERENCE_RESULTS.md): stored numerical certificates and metrics
- [docs/PROOF_NAVIGATION.md](docs/PROOF_NAVIGATION.md): guide to proof maps, artifact indexes, and reproduction docs
- [docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md): full script order and audit notes
- [docs/releases/](docs/releases/): release notes
- [docs/archive/](docs/archive/): historical migration and supersession notes

## Citation And Licence

Cite the frozen v0.9.3 theorem for the local ODE result unless a later paper
version explicitly supersedes it. Treat v0.10.14.1/v0.10.15 material as
development milestones, not as fifth-frame or global-flow theorems.

See [CITATION.cff](CITATION.cff) and [LICENSE](LICENSE).
