# Computation as Geometric Flow

[![Structural checks](https://github.com/papasop/Geometric-Flow/actions/workflows/structural-checks.yml/badge.svg)](https://github.com/papasop/Geometric-Flow/actions/workflows/structural-checks.yml)
[![Validated ODE reproduction](https://github.com/papasop/Geometric-Flow/actions/workflows/reproduce-validated-ode.yml/badge.svg)](https://github.com/papasop/Geometric-Flow/actions/workflows/reproduce-validated-ode.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

This repository contains the frozen sources, interval certificates, and
reproduction entrypoints for the published local response-fibre theorem.

The central result separates response invariance from dynamical stationarity:
a direction invisible to the declared finite response may still carry strict
descent of an independent objective. In the certified model, this residual
freedom supports a six-dimensional intrinsic normalized projected-gradient
dynamics.

The model is a frozen fourteen-phase quantum-control model: fourteen phase
parameters for a driven-qubit detuning scan. Its reference result is a
computer-assisted local theorem verified with 192-bit Arb interval arithmetic.

The published Zenodo paper, *Computation as Geometric Flow: An Arb-Certified
Local Intrinsic ODE on a Quantum-Control Response Fibre*, establishes the
Level-I local theorem: a complete-parent-box descent certificate and a
validated intrinsic response-fibre ODE microstep. Later finite-continuation
artifacts and the analytic conditional-continuation manuscript are continuing
work in the same repository and are outside the theorem boundary of the
published Zenodo version. See the
[Zenodo record](https://zenodo.org/records/21728432) and
[docs/PUBLISHED_PAPER_BOUNDARY.md](docs/PUBLISHED_PAPER_BOUNDARY.md).

## What Is Proved

**Proved, Level I.** For the frozen v0.9.3 instance, the repository certifies
existence and uniqueness of a local solution to a six-dimensional intrinsic
ODE initial-value problem over one validated microstep. The solution:

- preserves the declared response map \(\mathcal R_3\);
- strictly decreases the independent objective \(L_6\);
- remains inside a formally validated local response-fibre chart.

"Frozen" means the model parameters, atlas coefficients, code, and reference
artifacts are hash-bound; changing any of them defines a different
computational statement.

**Milestone, Level II.** Later repository artifacts extend this construction
through finite same-chart continuation, with v0.10.6 as the latest stored
reference certificate.

For v0.7.4, all 16 theorem-bearing rank, near-tangency, nonstationarity, and
descent boxes pass. A separate KKT-alignment diagnostic misses its predeclared
threshold. Consequently, the serialized parent-box atlas is not claimed to be
an ODE trajectory.

**Conditional theorem, Level III.** A separate analytic
conditional-continuation manuscript proves a continuation criterion from
compactness, uniform rank, and uniform nonstationarity hypotheses. Those
hypotheses are not yet certified on the complete response fibre, and this work
is outside the theorem boundary of the published Zenodo paper. The repository
does not yet prove a fifth frame or a global flow.

## Theory Boundary In One Paragraph

The computation acts on a frozen analytic pulse model: fourteen phase
coordinates \(\theta\in\mathbb R^{14}\), exact segment propagators, and a
projective jet response \(\mathcal R_3=(a_0,\dots,a_3)\) produced by exact
finite jet recurrences, not polynomial truncation. "Exact preservation" means
this declared finite response map only: not higher-order coefficients, the
full physical output, or hardware behaviour. Improvement means strict decrease
of the independent objective \(L_6\) along the response fibre. Everything
outside the three layers below, including the fifth frame, complete-child
traversal, ten-chart continuation, fibre connectedness, arbitrary endpoint
connection, and any unconditional global flow, is not claimed anywhere in this
repository.

## Three-Layer Status

| Layer | Current Repository Status | Claim | Boundary |
| --- | --- | --- | --- |
| I. Local theorem | v0.9.3 intrinsic ODE microstep | Certified reference theorem | One Picard microstep, \(0\le t\le 10^{-14}\), near child 15 |
| II. Frozen finite continuation | v0.10.6 fourth-chart Lohner support flowpipe | Latest stored repository reference certificate | Declared finite chain of recentered charts only; instance-specific |
| III. Next-frame / global work | v0.10.13.1 source chain and v0.10.15 fail-closed harness | Implementation-open; not a fifth-frame or global-flow theorem | Holds only where compactness, uniform rank, and uniform nonstationarity are assumed; not certified on the complete fibre |

For Layer II, v0.10.6 is the packaged reference certificate stored under
`results/`; v0.10.13.1 records a stronger reindexed source chain whose
reference-result packaging is still pending. The v0.10.15 fifth-frame backend
harness is fail-closed scaffold work.

## Quick Start

```bash
git clone https://github.com/papasop/Geometric-Flow.git
cd Geometric-Flow
python -m pip install -r requirements.txt
python scripts/verify_reference_results.py
python reproduce/published_paper.py
```

The verification command checks frozen SHA-256 entries and stored reference
certificates before you rerun any proof driver. By default,
`python reproduce/published_paper.py` checks frozen stored artifacts; only
`python reproduce/published_paper.py --run` recomputes the v0.7.4 + v0.9.3
theorem pair from frozen source.

## Choose A Reproduction Path

Python 3.12 and `python-flint==0.8.0` are recommended.

| Goal | Command |
| --- | --- |
| Verify the published Zenodo paper boundary | `python reproduce/published_paper.py` |
| Recompute the published v0.7.4 + v0.9.3 theorem pair | `python reproduce/published_paper.py --run` |
| Verify stored certificates and hashes | `python scripts/verify_reference_results.py` |
| Recompute the v0.9.3 local ODE theorem only | `python reproduce/local_theorem.py` |
| Reproduce the fourth-chart Lohner flowpipe | `python reproduce/finite_continuation.py` |
| Audit the open fifth-frame target | `python reproduce/open_next_frame_audit.py` |

The stable scripts verify the relevant frozen SHA-256 entries before calling
their archived long-form proof drivers in `archive/milestones/`.

`finite_continuation.py` and `open_next_frame_audit.py` are continuing global
flow research-line entry points; they are not part of the published Zenodo
paper theorem boundary.

Compatibility commands remain available under `scripts/`, including
`scripts/reproduce_finite_continuation.py` and
`scripts/reproduce_field_jacobian.py`, but new readers should start with the
three `reproduce/` entry points above.

## Repository Shape

The visible repository structure is intentionally small:

- `src/`: core geometric code and maintained formal backends;
- `reproduce/`: published-paper and research-line reproduction entry points;
- `archive/milestones/`: historical v0.9.x/v0.10.x milestone scripts with
  original filenames preserved.

New proof work should first attach to `src/` and the visible `reproduce/`
entry points. Avoid adding another user-facing versioned script unless it is
also archived and indexed.

## Active Five-Stage Research Programme

The frozen paper theorem remains unchanged. Post-publication work now follows
one sequential validation chain: certified intrinsic response-fibre motion;
certified normal recovery; a coordinate-invariant process-cost definition; an
independently defined critical zero-mode test; and only then a possible
co-location theorem. Later stages are not interpretations of earlier numerical
results and may fail without invalidating the published local theorem.

| Stage | Object | Current status | Promotion gate |
| ----- | ------ | -------------- | -------------- |
| 1 | Intrinsic response-fibre flow | Frozen local theorem | Already certified within published boundary |
| 2 | Normally attracting controlled flow | Floating-point development evidence | Nonzero Arb-certified controlled tube |
| 3 | Process-cost/process-time functional | Open definition | Coordinate-invariant operational law |
| 4 | Critical zero mode | Open bridge test | Predeclared Arb-certified critical co-location |
| 5 | Unified controlled geometry | Not established | Joint certificate plus independent observable |

The full active programme is documented in
[docs/FIVE_STAGE_CONTROL_GEOMETRY_PROGRAM.md](docs/FIVE_STAGE_CONTROL_GEOMETRY_PROGRAM.md).
Global continuation may remain an open mathematical problem, but it is not an
active numbered stage. The programme does not prove K=1, pseudo-Riemannian
geometry, process-relative time, global flow, physical spacetime, matter
emergence, fundamental constants, or hardware behaviour.

## Roadmap

Compatibility note for existing release checks: the immediate continuation research direction,
**Toward a global response-fibre flow**, remains outside the active numbered
stages and is not a theorem of the published paper.

The immediate
  open step is the fifth-frame backend; v0.10.15 is fail-closed scaffold work,
not a fifth-frame theorem. The separate neural-network analogy remains in
[docs/NEURAL_NETWORK_RESPONSE_FIBRES.md](docs/NEURAL_NETWORK_RESPONSE_FIBRES.md).

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
- [docs/PUBLISHED_PAPER_BOUNDARY.md](docs/PUBLISHED_PAPER_BOUNDARY.md): Zenodo theorem boundary
- [docs/PAPER_WORDING.md](docs/PAPER_WORDING.md): paper wording and citation boundary
- [docs/MANUSCRIPT_PROVENANCE.md](docs/MANUSCRIPT_PROVENANCE.md): submission manuscript hashes, archive status, and release fields
- [docs/REVIEWER_REPRODUCTION.md](docs/REVIEWER_REPRODUCTION.md): minimal reviewer reproduction route for the frozen theorem boundary
- [docs/FIVE_STAGE_CONTROL_GEOMETRY_PROGRAM.md](docs/FIVE_STAGE_CONTROL_GEOMETRY_PROGRAM.md): active post-publication five-stage validation programme
- [docs/releases/](docs/releases/): release notes
- [docs/archive/](docs/archive/): historical migration and supersession notes

## 中文概览

<details>
<summary>展开摘要</summary>

本仓库研究：当多组量子控制参数产生相同的声明响应时，是否可以沿响应纤维
连续移动，同时严格降低另一个目标函数。

当前已严格证明局部 ODE 微步和冻结实例上的有限同图延拓；尚未证明第五局部图、
完整子域遍历或全局几何流。

发表后的研究不再按多个并行理论标签组织，而采用五阶段验证链：局部响应纤维流、
受控吸引、过程成本定义、临界零模检验和最终共定位检验。当前只有第一阶段属于
冻结的严格论文结果；第二阶段仍在从浮点数值证据走向 Arb 认证；第三至第五阶段
均为开放问题。神经网络
响应纤维只是独立类比方向，不属于本文发表定理。

</details>

## Citation And Licence

Suggested citation for the local theorem and published paper boundary is
recorded in [CITATION.cff](CITATION.cff). The Zenodo paper DOI is
[10.5281/zenodo.21728432](https://doi.org/10.5281/zenodo.21728432).
Treat v0.10.14.1/v0.10.15 material as development milestones, not as
fifth-frame or global-flow theorems. The project is released under the
[MIT license](LICENSE).
