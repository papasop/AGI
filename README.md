# Computation as Geometric Flow

[![Structural checks](https://github.com/papasop/Geometric-Flow/actions/workflows/structural-checks.yml/badge.svg)](https://github.com/papasop/Geometric-Flow/actions/workflows/structural-checks.yml)
[![Validated ODE reproduction](https://github.com/papasop/Geometric-Flow/actions/workflows/reproduce-validated-ode.yml/badge.svg)](https://github.com/papasop/Geometric-Flow/actions/workflows/reproduce-validated-ode.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Can a computation move through different control implementations while
preserving its declared response and strictly improving another objective?

This repository studies that question on a frozen fourteen-phase
quantum-control model: fourteen phase parameters for a driven-qubit detuning
scan. Its reference result is a computer-assisted local theorem verified with
192-bit Arb interval arithmetic.

## What Is Proved

**Proved, Level I.** For the frozen v0.9.3 instance, the repository certifies a
unique six-dimensional intrinsic ODE microstep that:

- preserves the declared response map \(\mathcal R_3\);
- strictly decreases the independent objective \(L_6\);
- remains inside a formally validated local response-fibre chart.

**Milestone, Level II.** Later repository artifacts extend this construction
through finite same-chart continuation, with v0.10.6 as the latest stored
reference certificate.

**Conditional theorem, Level III.** The paper-level continuation statement is
conditional on supplying the missing next-frame certificates. The repository
does not yet prove a fifth frame or a global flow.

## Three-Layer Status

| Layer | Current Repository Status | Claim |
| --- | --- | --- |
| I. Local theorem | v0.9.3 intrinsic ODE microstep | Certified reference theorem |
| II. Frozen finite continuation | v0.10.6 fourth-chart Lohner support flowpipe | Latest stored repository reference certificate |
| III. Next-frame / global work | v0.10.13.1 source chain and v0.10.15 fail-closed harness | Implementation-open; not a fifth-frame or global-flow theorem |

For Layer II, v0.10.6 is the packaged reference certificate stored under
`results/`; v0.10.13.1 records a stronger reindexed source chain whose
reference-result packaging is still pending. The v0.10.15 fifth-frame backend
harness is fail-closed scaffold work.

## Quick Start

```bash
git clone https://github.com/papasop/Geometric-Flow.git
cd Geometric-Flow
python -m pip install -r requirements.txt
python reproduce/local_theorem.py --check-only
```

## Choose A Reproduction Path

Python 3.12 and `python-flint==0.8.0` are recommended.

| Goal | Command |
| --- | --- |
| Recompute the local ODE theorem | `python reproduce/local_theorem.py` |
| Reproduce the fourth-chart Lohner flowpipe | `python reproduce/finite_continuation.py` |
| Audit the open fifth-frame target | `python reproduce/open_next_frame_audit.py` |
| Verify stored certificates and hashes | `python scripts/verify_reference_results.py` |

The stable scripts verify the relevant frozen SHA-256 entries before calling
their archived long-form proof drivers in `archive/milestones/`.

Compatibility commands remain available under `scripts/`, including
`scripts/reproduce_finite_continuation.py` and
`scripts/reproduce_field_jacobian.py`, but new readers should start with the
three `reproduce/` entry points above.

## Repository Shape

The visible repository structure is intentionally small:

- `src/`: core geometric code and maintained formal backends;
- `reproduce/`: the three paper-level reproduction entry points;
- `archive/milestones/`: historical v0.9.x/v0.10.x milestone scripts with
  original filenames preserved.

New proof work should first attach to `src/` and the three `reproduce/`
entry points. Avoid adding another user-facing versioned script unless it is
also archived and indexed.

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
stability. This README changes reading order only, not proof content.

## Documentation

- [docs/CLAIM_SCOPE.md](docs/CLAIM_SCOPE.md): precise allowed and forbidden claims
- [docs/MATHEMATICS.md](docs/MATHEMATICS.md): mathematical construction
- [docs/REFERENCE_RESULTS.md](docs/REFERENCE_RESULTS.md): stored numerical certificates and metrics
- [docs/PROOF_NAVIGATION.md](docs/PROOF_NAVIGATION.md): guide to proof maps, artifact indexes, and reproduction docs
- [docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md): full script order and audit notes
- [docs/PAPER_WORDING.md](docs/PAPER_WORDING.md): paper wording and citation boundary
- [docs/releases/](docs/releases/): release notes
- [docs/archive/](docs/archive/): historical migration and supersession notes

## 中文概览

<details>
<summary>中文概览</summary>

本仓库研究：当多组量子控制参数产生相同的声明响应时，是否可以沿响应纤维
连续移动，同时严格降低另一个目标函数。

当前已严格证明局部 ODE 微步和冻结实例上的有限同图延拓；尚未证明第五局部图、
完整子域遍历或全局几何流。

</details>

## Citation And Licence

Suggested citation for the local theorem: cite the repository artifact and the
exact v0.9.3 release or commit, as recorded in [CITATION.cff](CITATION.cff).
Treat v0.10.14.1/v0.10.15 material as development milestones, not as
fifth-frame or global-flow theorems. The project is released under the
[MIT license](LICENSE).
