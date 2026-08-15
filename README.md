# Computation as Geometric Flow

[![Structural checks](https://github.com/papasop/Geometric-Flow/actions/workflows/structural-checks.yml/badge.svg)](https://github.com/papasop/Geometric-Flow/actions/workflows/structural-checks.yml)
[![Validated ODE reproduction](https://github.com/papasop/Geometric-Flow/actions/workflows/reproduce-validated-ode.yml/badge.svg)](https://github.com/papasop/Geometric-Flow/actions/workflows/reproduce-validated-ode.yml)
[![License: MIT](https://img.shields.io/badge/Software%20License-MIT-blue.svg)](LICENSE)

A computer-assisted local theorem: in a frozen fourteen-phase driven-qubit
model, exact preservation of a declared finite response can coexist with
strict decrease of an independent implementation objective along an intrinsic
response-fibre ODE.

The certified result is local. It does not claim a fifth frame, complete
child traversal, complete-atlas continuation, hardware/QPU behaviour,
arbitrary endpoint connection, or a global response-fibre flow.

## Start Here

| Purpose | Link or command |
| --- | --- |
| Read the recommended manuscript | [`docs/manuscript/geometric_flow_v1_2_13_disclosure_revision.pdf`](docs/manuscript/geometric_flow_v1_2_13_disclosure_revision.pdf) |
| Inspect the matching source ZIP | [`docs/manuscript/geometric_flow_v1_2_13_source.zip`](docs/manuscript/geometric_flow_v1_2_13_source.zip) |
| Cite the current public version | [DOI `10.5281/zenodo.21947745`](https://doi.org/10.5281/zenodo.21947745) |
| Download the GitHub release | [`paper-local-ode-v1.7`](https://github.com/papasop/Geometric-Flow/releases/tag/paper-local-ode-v1.7) |
| Verify the published theorem boundary | `python reproduce/published_paper.py` |
| Follow the proof map | [`docs/PROOF_NAVIGATION.md`](docs/PROOF_NAVIGATION.md) |

## Quick Start

```bash
git clone https://github.com/papasop/Geometric-Flow.git
cd Geometric-Flow
python -m pip install -r requirements.txt

# Identity and hash checks
python scripts/verify_reference_results.py

# Published theorem boundary check
python reproduce/published_paper.py

# Optional, slower Arb recomputation of the theorem pair
python reproduce/published_paper.py --run
```

Python 3.12 and `python-flint==0.8.0` are recommended. The default
`published_paper.py` mode checks stored frozen artifacts; only `--run`
recomputes the v0.7.4 + v0.9.3 theorem pair from frozen source.

## Published Result

The recommended v1.2.13 manuscript is frozen in scope. Its theorem-bearing
software boundary remains v0.7.4 + v0.9.3.

For the frozen model, the repository certifies existence and uniqueness of a
local initial-value problem over one Picard microstep,

\[
0 \le t \le 10^{-14}.
\]

The certified solution:

- preserves the declared finite response map \(\mathcal R_3\);
- strictly decreases the independent objective \(L_6\);
- remains inside a formally validated local response-fibre chart.

"Frozen" means the model parameters, atlas coefficients, code, inputs, and
reference artifacts are hash-bound. Changing any of them defines a different
computational statement.

The model is an analytic pulse model with fourteen phase coordinates
\(\theta\in\mathbb R^{14}\), exact segment propagators, and a projective jet
response produced by exact finite jet recurrences. "Exact preservation" means
preservation of this declared finite response only: not higher-order response
coefficients, not the full physical output, and not hardware behaviour.

## Claim Boundary

| Proved in the published local theorem | Not proved here |
| --- | --- |
| v0.7.4 complete-parent-box regularity, nonstationarity, and descent certificate | fifth frame |
| v0.9.3 local intrinsic ODE existence and uniqueness | complete child traversal |
| exact preservation of the declared finite response \(\mathcal R_3\) | complete ten-chart continuation |
| strict \(L_6\) descent over one local Picard microstep | arbitrary endpoint connection |
| `GLOBAL_FLOW_CLAIMED=false` | hardware/QPU validation or global flow |

For v0.7.4, all sixteen theorem-bearing rank, near-tangency,
nonstationarity, and descent boxes pass. A separate KKT-alignment diagnostic
misses its predeclared threshold, so the serialized parent-box atlas is not
claimed to be an ODE trajectory.

The affine atlas-arclength derivative-label correction is documented in
[`docs/PAPER_WORDING.md`](docs/PAPER_WORDING.md) and changes no frozen
certificate or strict-descent claim.

## Published Artifacts

Recommended reading version:

- Manuscript: v1.2.13 disclosure and notation revision
- PDF: [`docs/manuscript/geometric_flow_v1_2_13_disclosure_revision.pdf`](docs/manuscript/geometric_flow_v1_2_13_disclosure_revision.pdf)
- Source ZIP: [`docs/manuscript/geometric_flow_v1_2_13_source.zip`](docs/manuscript/geometric_flow_v1_2_13_source.zip)
- Zenodo record: [https://zenodo.org/records/21947745](https://zenodo.org/records/21947745)
- Version DOI: [10.5281/zenodo.21947745](https://doi.org/10.5281/zenodo.21947745)
- Concept DOI: [10.5281/zenodo.15879392](https://doi.org/10.5281/zenodo.15879392)
- GitHub Release: [`paper-local-ode-v1.7`](https://github.com/papasop/Geometric-Flow/releases/tag/paper-local-ode-v1.7)
- Release provenance: [`docs/manuscript/V1_2_13_RELEASE_PROVENANCE.md`](docs/manuscript/V1_2_13_RELEASE_PROVENANCE.md)

v1.2.13 is derived from v1.2.12 and incorporates the recorded v1.2.9 errata
and later textual clarifications. It changes no theorem-bearing constants,
certificates, protocols, JSON records, atlas data, gate thresholds, or Arb
computations.

## Reproduction And Audit

| Goal | Command |
| --- | --- |
| Verify stored certificate hashes | `python scripts/verify_reference_results.py` |
| Verify the published theorem boundary | `python reproduce/published_paper.py` |
| Recompute the published v0.7.4 + v0.9.3 theorem pair | `python reproduce/published_paper.py --run` |
| Recompute the v0.9.3 local ODE theorem only | `python reproduce/local_theorem.py` |
| Reproduce stored finite-continuation evidence | `python reproduce/finite_continuation.py` |
| Audit the open fifth-frame target | `python reproduce/open_next_frame_audit.py` |

Finite-continuation and fifth-frame commands are post-publication research
entry points. They are not part of the v1.2.13 published theorem boundary.

## Repository Shape

- `src/`: core geometric code and maintained formal backends.
- `reproduce/`: stable published-paper and research-line reproduction entry
  points.
- `archive/milestones/`: historical v0.9.x/v0.10.x milestone scripts with
  original filenames preserved.
- `docs/`: claim boundaries, proof navigation, release provenance, and
  post-publication research maps.
- `results/`: stored reference certificates and reports.

Avoid adding another user-facing versioned script. Prefer stable
`reproduce/` entry points and archive raw historical drivers under
`archive/milestones/`.

## Post-Publication Research

These tracks are useful research evidence but do not enlarge the local
published theorem:

- Stored finite-continuation evidence: v0.10.6 fourth-chart Lohner support
  flowpipe.
- Open global-continuation programme: v0.10.13.1 source chain and v0.10.15
  fail-closed fifth-frame harness.
- C4 controlled-attraction and C4-E2b research artifacts.
- Wiener-type memory feedback, process-time, two-metric, certificate-DAG, and
  K=1 bridge investigations.
- Neural-network response-fibre analogues.

The immediate continuation research direction is toward a global
response-fibre flow: certified chart overlaps, uniform rank bounds, and
uniform nonstationarity bounds across a complete response component remain
open.

See [`docs/ROADMAP.md`](docs/ROADMAP.md),
[`docs/THEORY_ARCHITECTURE.md`](docs/THEORY_ARCHITECTURE.md), and
[`docs/RESEARCH_STATUS_MATRIX.md`](docs/RESEARCH_STATUS_MATRIX.md) for the
full research-status map.

## Documentation

Published paper and claim boundary:

- [`docs/PUBLISHED_PAPER_BOUNDARY.md`](docs/PUBLISHED_PAPER_BOUNDARY.md)
- [`docs/CLAIM_SCOPE.md`](docs/CLAIM_SCOPE.md)
- [`docs/PAPER_WORDING.md`](docs/PAPER_WORDING.md)
- [`docs/MANUSCRIPT_PROVENANCE.md`](docs/MANUSCRIPT_PROVENANCE.md)
- [`docs/REVIEWER_REPRODUCTION.md`](docs/REVIEWER_REPRODUCTION.md)

Proof and reproduction:

- [`docs/PROOF_NAVIGATION.md`](docs/PROOF_NAVIGATION.md)
- [`docs/MATHEMATICS.md`](docs/MATHEMATICS.md)
- [`docs/REFERENCE_RESULTS.md`](docs/REFERENCE_RESULTS.md)
- [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md)
- [`docs/PROOF_MAP.md`](docs/PROOF_MAP.md)

Post-publication research and archive:

- [`docs/ROADMAP.md`](docs/ROADMAP.md)
- [`docs/THEORY_ARCHITECTURE.md`](docs/THEORY_ARCHITECTURE.md)
- [`docs/RESEARCH_STATUS_MATRIX.md`](docs/RESEARCH_STATUS_MATRIX.md)
- [`docs/CONTROL_EXTENSION_SCOPE.md`](docs/CONTROL_EXTENSION_SCOPE.md)
- [`docs/WIENER_FEEDBACK_SCOPE.md`](docs/WIENER_FEEDBACK_SCOPE.md)
- [`docs/PROCESS_TIME_SCOPE.md`](docs/PROCESS_TIME_SCOPE.md)
- [`docs/TWO_METRIC_SCOPE.md`](docs/TWO_METRIC_SCOPE.md)
- [`docs/CERTIFICATE_DAG_SCOPE.md`](docs/CERTIFICATE_DAG_SCOPE.md)
- [`docs/K1_BRIDGE_SCOPE.md`](docs/K1_BRIDGE_SCOPE.md)
- [`docs/ARTIFACT_INDEX.md`](docs/ARTIFACT_INDEX.md)
- [`docs/releases/`](docs/releases/)
- [`docs/archive/`](docs/archive/)

## Citation And Licences

Suggested citation for the local theorem and published paper boundary: cite
v1.2.13 using DOI `10.5281/zenodo.21947745` and identify the theorem-bearing
software boundary as v0.7.4 + v0.9.3.

Software is released under the [MIT license](LICENSE). The v1.2.13 manuscript
and manuscript source ZIP are released under Creative Commons Attribution 4.0
International (CC BY 4.0).

## Historical Releases

- v1.2.12 public archive: [DOI `10.5281/zenodo.21895917`](https://doi.org/10.5281/zenodo.21895917), [`paper-local-ode-v1.6`](https://github.com/papasop/Geometric-Flow/releases/tag/paper-local-ode-v1.6)
- v1.2.9 public archive: [DOI `10.5281/zenodo.21882158`](https://doi.org/10.5281/zenodo.21882158), [Zenodo record 21882158](https://zenodo.org/records/21882158), [`paper-local-ode-v1.5`](https://github.com/papasop/Geometric-Flow/releases/tag/paper-local-ode-v1.5)
- Earlier public boundary: [historical version DOI `10.5281/zenodo.21728432`](https://doi.org/10.5281/zenodo.21728432)

The historical version DOI `10.5281/zenodo.21728432` identifies an earlier
public manuscript boundary; it is not the preferred v1.2.13 citation. The raw
record URL `https://zenodo.org/records/21728432` is not the current paper
record.

## 中文概览

<details>
<summary>展开摘要</summary>

本仓库归档并复现 v1.2.13 冻结文稿：在一个十四相位驱动量子比特模型中，
严格证明声明响应 \(\mathcal R_3\) 可被精确保持，同时独立目标 \(L_6\)
沿局部响应纤维 ODE 严格下降。

当前已严格证明 v0.7.4 父盒证书和 v0.9.3 局部 ODE 微步；尚未证明第五框架、
完整子域遍历、十图册延拓、任意端点连接、硬件/QPU 行为或全局几何流。

v1.2.13 是从 v1.2.12 派生的 disclosure/notation 修订，吸收了 v1.2.9
勘误和后续文字澄清；它不改变定理常数、证书或 v0.7.4 + v0.9.3 软件边界。
v0.10.x、受控吸引、反馈、过程时间、双度量、证书 DAG 和 K=1 相关内容是
发表后研究路线，不扩大本地定理边界。神经网络响应纤维只是独立类比方向，
不属于本发表论文定理。

</details>
