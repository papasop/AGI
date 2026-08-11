# Computation as Geometric Flow

[![Structural checks](https://github.com/papasop/Geometric-Flow/actions/workflows/structural-checks.yml/badge.svg)](https://github.com/papasop/Geometric-Flow/actions/workflows/structural-checks.yml)
[![Validated ODE reproduction](https://github.com/papasop/Geometric-Flow/actions/workflows/reproduce-validated-ode.yml/badge.svg)](https://github.com/papasop/Geometric-Flow/actions/workflows/reproduce-validated-ode.yml)
[![License: MIT](https://img.shields.io/badge/Software%20License-MIT-blue.svg)](LICENSE)

A computer-assisted theorem showing that exact preservation of a declared
finite response can coexist with strict decrease of an independent
implementation objective along an intrinsic response-fibre ODE.

Can a computation move through implementation space while preserving a declared
finite response and strictly descending an independent objective? This
repository answers that local question with frozen sources, interval certificates, and
reproduction entrypoints. The theorem separates response invariance from dynamical stationarity: there is a direction invisible to the declared finite response, yet it gives strict
descent of an independent objective.

The model has fourteen phase
parameters for a driven-qubit detuning scan and is verified with
192-bit Arb interval arithmetic. The archived v1.2.12 manuscript is
*Computation as Geometric Flow: An Arb-Certified
Local Intrinsic ODE on a Quantum-Control Response Fibre*. It incorporates the
recorded v1.2.9 errata and subsequent textual clarifications into a
self-contained recommended reading version and establishes the
Level-I local theorem. It does not change the mathematical
conclusions, theorem-bearing constants, frozen certificates, or the v0.7.4 +
v0.9.3 theorem boundary. No Arb rerun was performed or required. Later
repository artifacts are continuing work and are outside the theorem boundary of the
published Zenodo version; see
[published paper boundary](docs/PUBLISHED_PAPER_BOUNDARY.md). The historical
version DOI
[10.5281/zenodo.21728432](https://doi.org/10.5281/zenodo.21728432)
identifies the earlier public manuscript boundary; it is not the preferred
current-manuscript citation. The v1.2.9 DOI
[10.5281/zenodo.21882158](https://doi.org/10.5281/zenodo.21882158) and
[`paper-local-ode-v1.5`](https://github.com/papasop/Geometric-Flow/releases/tag/paper-local-ode-v1.5)
remain immutable historical records. The v1.2.12 tag, GitHub Release, and
Zenodo version DOI are pending.
The historical raw record URL `https://zenodo.org/records/21728432` is not the
current paper record.

## Start Here

| Purpose | Link |
| --- | --- |
| Read the recommended v1.2.12 manuscript | [`docs/manuscript/geometric_flow_v1_2_12_freeze_candidate.pdf`](docs/manuscript/geometric_flow_v1_2_12_freeze_candidate.pdf) |
| Inspect the matching v1.2.12 source ZIP | [`docs/manuscript/geometric_flow_v1_2_12_source.zip`](docs/manuscript/geometric_flow_v1_2_12_source.zip) |
| Audit the historical v1.2.9 public release | [GitHub Release `paper-local-ode-v1.5`](https://github.com/papasop/Geometric-Flow/releases/tag/paper-local-ode-v1.5) |
| Verify the published theorem boundary | [`python reproduce/published_paper.py`](reproduce/published_paper.py) |
| Follow the proof and certificate map | [Proof navigation](docs/PROOF_NAVIGATION.md) |
| View the wider research programme | [Y.Y.N. Li - Open and Current Research](https://zenodo.org/communities/yyn-li-open-research/about) |

## What Is Proved

**Proved, Level I.** For the frozen fourteen-phase driven-qubit model, the
repository certifies existence and uniqueness of a local solution for an
initial-value problem over one validated microstep:

\[
0 \le t \le 10^{-14}.
\]

This local solution preserves the declared response map, strictly decreases the independent objective, and remains inside a formally validated local response-fibre chart.

"Frozen" means the model parameters, atlas coefficients, code, and reference
artifacts are hash-bound; changing any of them defines a different
computational statement.

For v0.7.4, all 16 theorem-bearing rank, near-tangency, nonstationarity, and
descent boxes pass. A separate KKT-alignment diagnostic misses its predeclared
threshold, so the serialized parent-box atlas is not claimed to be
an ODE trajectory.

**Milestone, Level II.** The repository stores v0.10.6 as the latest stored
reference certificate for finite same-chart continuation evidence. It does not
yet prove a fifth frame or a global flow.

**Conditional theorem, Level III.** A separate analytic
conditional-continuation manuscript concerns compactness, uniform rank, and
uniform nonstationarity hypotheses. Those hypotheses are not yet certified on the complete response fibre and are outside the theorem boundary of the published Zenodo paper. This does not yet prove a fifth frame or a global flow.

The theorem is local. No global response-fibre flow, arbitrary endpoint
connection, hardware result, or QPU claim is made.

## Theory Boundary In One Paragraph

The computation acts on a frozen analytic pulse model: fourteen phase
coordinates \(\theta\in\mathbb R^{14}\), exact segment propagators, and a
projective jet response \(\mathcal R_3=(a_0,\dots,a_3)\) produced by exact
finite jet recurrences, not polynomial truncation. "Exact preservation" means
this declared finite response map only: not higher-order coefficients, not the
full physical output, and not hardware behaviour. Improvement means strict
decrease of the independent objective \(L_6\) along the response fibre.
Everything outside the layers below, including arbitrary endpoint
connection and unconditional global flow, is not claimed here.

## Three-Layer Status

| Layer | Current Repository Status | Claim | Boundary |
| --- | --- | --- | --- |
| I. Local theorem | v0.9.3 intrinsic ODE microstep | Certified reference theorem | One Picard microstep, \(0\le t\le 10^{-14}\), near child 15 |
| II. Frozen finite continuation | v0.10.6 fourth-chart Lohner support flowpipe | Latest stored repository reference certificate | Declared finite chain of recentered charts only; instance-specific |
| III. Next-frame / global work | v0.10.13.1 source chain and v0.10.15 fail-closed harness | Implementation-open; not a fifth-frame or global-flow theorem | Holds only where compactness, uniform rank, and uniform nonstationarity are assumed; not certified on the complete fibre |

v0.10.6 is the packaged reference certificate. v0.10.13.1 records a stronger reindexed source chain, but reference-result packaging is still pending.
v0.10.15 is implementation-open fifth-frame fail-closed scaffold work.

## Quick Start

```bash
git clone https://github.com/papasop/Geometric-Flow.git
cd Geometric-Flow
python -m pip install -r requirements.txt
python scripts/verify_reference_results.py
python reproduce/published_paper.py
```

`python scripts/verify_reference_results.py` checks frozen SHA-256 entries and stored reference
certificates. `python reproduce/published_paper.py` checks frozen stored artifacts
and the published theorem boundary; only
`python reproduce/published_paper.py --run` recomputes the v0.7.4 + v0.9.3
theorem pair from frozen source. Python 3.12 and `python-flint==0.8.0` are
recommended.

## Claim Boundary

Certified:

- v0.7.4 complete-parent-box regularity, nonstationarity, and descent
  certificate;
- v0.9.3 local intrinsic ODE existence and uniqueness;
- exact preservation of the declared finite response \(\mathcal R_3\);
- strict \(L_6\) descent;
- one local Picard microstep.

Not certified:

- fifth frame;
- complete child traversal;
- complete ten-chart continuation;
- arbitrary endpoint connection;
- complete fibre connectedness;
- unconditional global flow;
- hardware or QPU behaviour.

The affine atlas-arclength derivative-label correction is documented in
[paper wording](docs/PAPER_WORDING.md) and changes no frozen certificate or
strict-descent claim.

## Choose A Reproduction Path

| Goal | Command |
| --- | --- |
| Verify the published Zenodo paper boundary | `python reproduce/published_paper.py` |
| Recompute the published v0.7.4 + v0.9.3 theorem pair | `python reproduce/published_paper.py --run` |
| Verify stored certificates and hashes | `python scripts/verify_reference_results.py` |
| Recompute the v0.9.3 local ODE theorem only | `python reproduce/local_theorem.py` |
| Reproduce the fourth-chart Lohner flowpipe | `python reproduce/finite_continuation.py` |
| Audit the open fifth-frame target | `python reproduce/open_next_frame_audit.py` |

The stable entry points verify the relevant frozen SHA-256 entries before
calling archived proof drivers. The finite-continuation and fifth-frame
commands are not part of the published Zenodo
paper theorem boundary.

Compatibility commands remain available under `scripts/`, including
`scripts/reproduce_finite_continuation.py` and
`scripts/reproduce_field_jacobian.py`; these wrappers verify the relevant
frozen SHA-256 entries before delegating to archived drivers.

## Repository Shape

- `src/`: core geometric code and maintained formal backends.
- `reproduce/`: published-paper and research-line reproduction entry points.
- `archive/milestones/`: historical v0.9.x/v0.10.x milestone scripts with
  original filenames preserved.
- `docs/`: claim boundaries, proof navigation, release provenance, and
  post-publication research maps.
- `results/`: stored reference certificates and reports.

Avoid adding another user-facing versioned script. Prefer the stable
`reproduce/` entry points and archive raw historical drivers under
`archive/milestones/`.

## Roadmap

The v1.2.12 manuscript revision and the published v1.2.9 theorem boundary
remain frozen in scope. Later finite-continuation,
controlled-attraction, feedback, process-time, two-metric, certificate-DAG,
and K=1 investigations do not enlarge the local theorem.

The immediate continuation research direction is **Toward a global response-fibre flow**. The immediate
  open step is the fifth-frame backend; v0.10.15 is fail-closed scaffold work.
The stored v0.10.6 reference records finite same-chart continuation evidence.
The fifth-frame backend remains open, and later v0.10.x material is outside
the v1.2.12 theorem boundary. K=1, physical time, and global flow are not
established. Neural response-fibre material is an independent analogue; see
[neural network response fibres](docs/NEURAL_NETWORK_RESPONSE_FIBRES.md). It
is not a theorem of the published paper.

See:

- [Post-publication roadmap](docs/ROADMAP.md)
- [Theory architecture](docs/THEORY_ARCHITECTURE.md)
- [Research status matrix](docs/RESEARCH_STATUS_MATRIX.md)

## Documentation

Paper and claim boundary:

- [Claim scope](docs/CLAIM_SCOPE.md)
- [Published paper boundary](docs/PUBLISHED_PAPER_BOUNDARY.md)
- [Paper wording](docs/PAPER_WORDING.md)
- [Manuscript v1.2.9 clarifications and errata](docs/MANUSCRIPT_ERRATA_v1.2.9.md)
- [Manuscript provenance](docs/MANUSCRIPT_PROVENANCE.md)
- [Reviewer reproduction](docs/REVIEWER_REPRODUCTION.md)

Proof and reproduction:

- [Proof navigation](docs/PROOF_NAVIGATION.md)
- [Mathematics](docs/MATHEMATICS.md)
- [Reference results](docs/REFERENCE_RESULTS.md)
- [Reproducibility](docs/REPRODUCIBILITY.md)
- [Proof map](docs/PROOF_MAP.md)

Post-publication research:

- [Roadmap](docs/ROADMAP.md)
- [Theory architecture](docs/THEORY_ARCHITECTURE.md)
- [Research status matrix](docs/RESEARCH_STATUS_MATRIX.md)
- [Control extension scope](docs/CONTROL_EXTENSION_SCOPE.md)
- [Wiener feedback scope](docs/WIENER_FEEDBACK_SCOPE.md)
- [Process-time scope](docs/PROCESS_TIME_SCOPE.md)
- [Two-metric scope](docs/TWO_METRIC_SCOPE.md)
- [Certificate DAG scope](docs/CERTIFICATE_DAG_SCOPE.md)
- [K=1 bridge scope](docs/K1_BRIDGE_SCOPE.md)

Historical and archive material:

- [Artifact index](docs/ARTIFACT_INDEX.md)
- [Releases](docs/releases/)
- [Archive notes](docs/archive/)

## Citation And Licences

The recommended reading version is the frozen v1.2.12 manuscript archived in
this repository. Its tag, GitHub Release, Zenodo version DOI, and release
commit are pending until publication:

- PDF: [`docs/manuscript/geometric_flow_v1_2_12_freeze_candidate.pdf`](docs/manuscript/geometric_flow_v1_2_12_freeze_candidate.pdf)
- source ZIP: [`docs/manuscript/geometric_flow_v1_2_12_source.zip`](docs/manuscript/geometric_flow_v1_2_12_source.zip)

Historical v1.2.9 public archive:

- DOI: [10.5281/zenodo.21882158](https://doi.org/10.5281/zenodo.21882158)
- Record: [https://zenodo.org/records/21882158](https://zenodo.org/records/21882158)

The historical version DOI
[10.5281/zenodo.21728432](https://doi.org/10.5281/zenodo.21728432)
identifies the earlier public manuscript boundary; it is not the preferred
current-manuscript citation.

Suggested citation for the local theorem and published paper boundary: until
the v1.2.12 Zenodo version DOI is created, cite the repository commit or
Draft/PR archive for v1.2.12 and identify the theorem-bearing software
boundary as v0.7.4 + v0.9.3.

Software is released under the [MIT license](LICENSE). The v1.2.12 manuscript
and manuscript source ZIP are intended to be released under Creative Commons Attribution 4.0
International (CC BY 4.0).

## 中文概览

<details>
<summary>展开摘要</summary>

本仓库归档并复现 v1.2.12 冻结文稿：在一个十四相位驱动量子比特模型中，
严格证明声明响应 \(\mathcal R_3\) 可被精确保持，同时独立目标 \(L_6\)
沿局部响应纤维 ODE 严格下降。

当前已严格证明局部 ODE 微步：已证明 v0.7.4 父盒证书和 v0.9.3 局部 ODE
微步；尚未证明第五框架、完整子域遍历、十图册延拓、任意端点连接、
硬件/QPU 行为或全局几何流。

v1.2.12 吸收了 v1.2.9 勘误和后续文字澄清；它不改变定理常数、证书或
v0.7.4 + v0.9.3 软件边界。v0.10.x、受控吸引、反馈、过程时间、双度量、
证书 DAG 和 K=1 相关内容是发表后研究路线，不扩大本地定理边界。
神经网络
响应纤维只是独立类比方向，不属于本发表论文定理。

</details>
