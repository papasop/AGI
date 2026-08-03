# Computation as Geometric Flow

This repository develops computer-assisted proofs for response-preserving
intrinsic descent in a frozen fourteen-phase quantum-control model.

The central certified result is local: outward-rounded 192-bit Arb arithmetic
proves existence and uniqueness of an intrinsic six-dimensional
projected-gradient ODE microstep. Along the validated solution, the declared
response map \(\mathcal R_3\) is preserved exactly and \(L_6\) decreases
strictly.

Later certificates establish finite same-chart continuation and a ten-step
fourth-chart Lohner support flowpipe. A reindexed Taylor/affine-Lohner source
chain produces a terminal correlated set for the next recentering problem, but
that chain is not yet packaged as an independent repository reference result.
A fifth frame, complete-child traversal, arbitrary-endpoint connection, and
global response-fibre flow are not proved.

## Status At A Glance

| Layer | Milestone | Status |
| --- | --- | --- |
| Complete-parent descent | v0.7.4 | Certified |
| Intrinsic ODE microstep | v0.9.3 | Certified reference theorem |
| Repository-native \(X\) and same-expression \(DX\) | v0.10.5 | Certified |
| Ten-step fourth-chart support flowpipe | v0.10.6 | Latest repository reference certificate |
| Reindexed Taylor/affine-Lohner terminal set | v0.10.13.1 | Source-certified chain; reference-result packaging pending |
| Fifth nonlinear frame transition | v0.10.15 | Implementation-open fail-closed harness |
| Complete fibre/global flow | - | Not proved |

The distinction between "source-certified chain" and "repository reference
certificate" matters: v0.10.13.1 records source that can certify the reindexed
chain when its predecessor artifacts are available; v0.10.6 is the latest
independent reference certificate currently stored under `results/`.

## Main Theorem

For the frozen v0.9.3 instance, there exists a unique solution on

```text
0 <= t <= 1e-14
```

of the intrinsic normalized projected-gradient ODE. Along that solution,

```text
R_3(theta(t)) = R_3(theta(0))
dL_6/dt <= -0.6419529191591549 < 0
```

"Exact response preservation" refers specifically to the declared finite
response map \(\mathcal R_3=(a_0,\ldots,a_3)\) within the analytic pulse model.
It does not mean preservation of every higher-order coefficient or hardware
output.

## Finite Continuation

The strongest repository reference continuation result is v0.10.6:

```text
VALIDATED_TEN_STEP_FOURTH_CHART_LOHNER_SUPPORT_FLOWPIPE_CERTIFIED
```

Reference metrics:

```text
steps                          10
total certified time           1e-13
maximum terminal support       1.3938448261845923e-11
real inner domain radius       1.5e-11
complex outer domain radius    2e-11
induced infinity |DX| upper    11510.000045776367
```

The v0.10.13.1 source chain reindexes the ten true propagation input boxes
against their matching Hessian parent boxes and assembles the directional
Taylor/affine-Lohner terminal correlated set. It remains marked
`reference-result packaging pending` until its reference artifacts and hashes
are stored in the repository.

```text
VALIDATED_REINDEXED_TAYLOR_DIRECTIONAL_AFFINE_LOHNER_CERTIFIED
```

## Mathematical Construction

The frozen model uses fourteen phase coordinates
\(\theta\in\mathbb R^{14}\), an eight-component response constraint

```text
R_3(theta) =
(Re a_0, Re a_1, Re a_2, Re a_3,
 Im a_0, Im a_1, Im a_2, Im a_3),
```

and an independent objective \(L_6\). Locally, the response fibre is written in
six intrinsic tangent coordinates:

```text
theta(a) = theta_0 + T a + N psi(a),    a in R^6.
```

With

```text
W = T + N Dpsi
H = W^T W
```

the normalized projected-gradient field is

```text
dot a = - H^{-1} W^T grad L_6
        / sqrt((W^T grad L_6)^T H^{-1} (W^T grad L_6)).
```

The intended motion preserves the declared response while decreasing \(L_6\).
All theorem-bearing enclosures use outward-rounded Arb interval arithmetic at
192-bit precision. Floating-point SVDs or inverses are used only as frozen
preconditioners, not as proof objects.

## Claim Boundary

The repository certifies local strict ODE behavior and finite frozen-instance
continuation milestones. It does not currently certify:

- a fifth tangent/normal frame or fifth local fibre graph;
- a fifth-frame nonlinear transition certificate from the implementation-open
  v0.10.15 backend harness;
- a complete traversal of child 15;
- a successor atlas chart after terminal chart 9;
- complete ten-chart continuation;
- connectivity of arbitrary points in a response fibre; or
- a global geometric flow.

See [docs/CLAIM_SCOPE.md](docs/CLAIM_SCOPE.md) and
[docs/PAPER_WORDING.md](docs/PAPER_WORDING.md) for wording that is safe to cite.

## Reproduce

Python 3.12 and `python-flint==0.8.0` are recommended.

```bash
python scripts/reproduce_local_ode.py
python scripts/verify_reference_results.py
python scripts/reproduce_lohner_flowpipe.py
python scripts/audit_fifth_frame.py
```

The first command recomputes the frozen v0.9.3 local ODE theorem. The second
checks frozen hashes and stored reference results. The third reruns the latest
stored repository reference certificate, the v0.10.6 fourth-chart Lohner
support flowpipe. The fourth audits the implementation-open fifth-frame
scaffold without upgrading any claim.

```bash
python scripts/reproduce_finite_continuation.py
```

The longer finite-continuation wrapper is optional. All stable entry points
check the relevant frozen SHA-256 entries before
calling their underlying long versioned proof files.

## Repository Navigation

- [docs/MILESTONES.md](docs/MILESTONES.md): complete milestone table
- [docs/ARTIFACT_INDEX.md](docs/ARTIFACT_INDEX.md): stable entry points and archived frozen artifact classes
- [docs/PROOF_MAP.md](docs/PROOF_MAP.md): concise three-layer proof map
- [docs/PROOF_GRAPH.md](docs/PROOF_GRAPH.md): dependency graph and proof layers
- [docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md): full one-click script order
- [docs/CLAIM_SCOPE.md](docs/CLAIM_SCOPE.md): allowed and forbidden claims
- [docs/PAPER_WORDING.md](docs/PAPER_WORDING.md): publication wording
- [SUPERSEDED_RESULTS.md](SUPERSEDED_RESULTS.md): withdrawn and corrected statements
- [docs/BACKEND_BINDING.md](docs/BACKEND_BINDING.md): native Arb binding contract
- [CHANGELOG.md](CHANGELOG.md): file-level update history

## Citation And Licence

Cite the frozen v0.9.3 theorem for the local ODE result unless a later paper
version explicitly supersedes it. Treat the v0.10.14.1 material as a
development milestone, not as a global-flow theorem or fifth-frame theorem.

See [CITATION.cff](CITATION.cff) and [LICENSE](LICENSE).

## 中文摘要

本仓库研究：在量子控制中，如果多组脉冲参数产生相同的理想响应，能否沿着
“响应保持”的纤维移动，同时严格降低另一个目标函数。

v0.9.3 用 192-bit Arb 区间算术证明了一个六维内蕴 ODE 微步：解存在且唯一，
声明的 \(\mathcal R_3\) 响应精确保持，并且 \(L_6\) 严格下降。v0.10.6 是当前已入库
的最新 reference certificate：第四图十步 support flowpipe。v0.10.13.1 是
source-certified chain，尚未作为独立 reference result 入库。v0.10.15 只是第五图
非线性过渡的 fail-closed harness。当前不声明第五图、完整 child 遍历、任意端点连通
或全局几何流。
