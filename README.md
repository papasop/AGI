# Computation as Geometric Flow

## Arb-certified continuation on a quantum-control response fibre

Geometric-Flow studies a simple but important question:

> If two controls produce the same ideal quantum response, can we move between
> them along a rigorously certified path while improving an independent
> objective?

The repository develops that question for a frozen 14-phase driven-qubit
model. The original v0.9.3 result proves one local intrinsic ODE microstep.
The current v0.9.23 development milestone extends the certified chain through
a second recentered local chart and a signed six-dimensional endpoint box.

Current status: strong local and finite-continuation results are certified
for one frozen chart/child instance. A complete-child, atlas-wide, or global
flow theorem is not claimed.

## Active backend scaffold: v0.9.46

The current development branch also includes a v0.9.46 repository-native
point/box Arb field backend refactor scaffold. Its status is
`IMPLEMENTATION_OPEN`.

This scaffold is **not** a certified point-dependent field, formal Jacobian,
QR/Lohner flowpipe, fifth frame, or global-flow theorem. The candidate module
intentionally retains `NotImplementedError` placeholders so that a fixed
envelope cannot be misreported as a point-dependent field.

See [docs/BACKEND_BINDING.md](docs/BACKEND_BINDING.md) and
[RELEASE_NOTES_v0.9.46.md](RELEASE_NOTES_v0.9.46.md).

## Latest result: v0.9.23

For the frozen chart-9 / child-15 instance, the repository-native 192-bit Arb
backend certifies:

- a second recentered complex response-fibre graph;
- a local Picard existence-and-uniqueness microstep in that chart;
- a 557-step scalar reachable tube that remains inside the declared domain;
- six signed intrinsic-field component intervals;
- a nonzero six-dimensional endpoint box after 557 microsteps; and
- inclusion of the complete endpoint box in the certified parametric
  fibre-graph domain.

The last item inherits a unique normal root for every tangent point in the
endpoint box.

The certified endpoint-box centre is approximately

```text
(-2.426e-13, +1.537e-12, +2.212e-12,
 +2.768e-12, +2.694e-12, -2.968e-12).
```

Including component uncertainty, its maximum absolute coordinate is about
`3.1814e-12`. The box therefore retains about `6.8186e-12` of strict margin
inside the declared real intrinsic radius `1e-11`.

This is the signed endpoint and parametric-root milestone v0.9.23: it
contains six signed intrinsic-field component intervals and a nonzero
six-dimensional endpoint box after 557 microsteps.

## Mathematical object

The frozen model uses fourteen phase coordinates
\(\theta\in\mathbb R^{14}\), an eight-component response constraint

$$
R_3(\theta)=
(\operatorname{Re}a_0,\operatorname{Re}a_1,
\operatorname{Re}a_2,\operatorname{Re}a_3,
\operatorname{Im}a_0,\operatorname{Im}a_1,
\operatorname{Im}a_2,\operatorname{Im}a_3),
$$

and an independent objective \(L_6\). Locally, the response fibre is written in
six intrinsic tangent coordinates:

$$
\theta(a)=\theta_0+Ta+N\psi(a),
\qquad a\in\mathbb{R}^6.
$$

With

$$
W=T+N D\psi,
\qquad H=W^\top W,
$$

the normalized projected-gradient field is

$$
\dot a=
-\frac{H^{-1}W^\top\nabla L_6}
{\sqrt{(W^\top\nabla L_6)^\top
H^{-1}(W^\top\nabla L_6)}}.
$$

The intended motion preserves the response while decreasing \(L_6\). All
theorem-bearing enclosures use outward-rounded Arb interval arithmetic at
192-bit precision. Floating-point SVDs or inverses are used only as frozen
preconditioners, not as proof objects.

## What has been certified

| Version | Certified milestone |
| --- | --- |
| v0.7.4 | Rank, response tangency, projected-gradient nonstationarity, and strict descent on one complete subdivided parent box |
| v0.9.3 | Existence, uniqueness, exact response preservation, and strict \(L_6\) descent for one intrinsic ODE microstep |
| v0.9.8 | Unique normal correction at the first recenter target |
| v0.9.9 | Recentered tangent/normal frame |
| v0.9.10 | Second complex fibre graph, overlap inclusion, pullback metric, and local Picard microstep |
| v0.9.11-12 | 557-step scalar continuation and the exact local-domain exhaustion boundary |
| v0.9.13 | Route correction: chart 9 is terminal, so continuation requires same-chart recentering |
| v0.9.15-17 | Lohner core, hardened executable-adapter contract, and conservative formal adapter |
| v0.9.18-19 | Auditable diagnosis later superseded by the norm correction in v0.9.20 |
| v0.9.20 | Corrected the duplicated dimension factor and restored the 557-step scalar certificate |
| v0.9.21 | Six-component symmetric endpoint enclosure |
| v0.9.22 | Repository-native signed field and nonzero endpoint box |
| v0.9.23 | Complete endpoint-box inclusion and inherited unique parametric normal root |

The v0.7.4 and v0.9.3 results have different scopes: v0.7.4 covers broader
geometry but is not an ODE theorem; v0.9.3 is an ODE theorem but only for one
microscopic local step.

## Correction to v0.9.18-19

The frozen v0.9.3 source defines

```text
cauchy_lipschitz_upper = d*M/(R-r)
```

as an induced infinity-norm Lipschitz bound. The v0.9.17 adapter placed
this already-induced bound in every entry of a `6 x 6` Jacobian box, and
v0.9.18 then took the matrix infinity norm. This introduced a second factor of
six.

Consequently, the following earlier statements are withdrawn:

- "the formal continuation is limited to 172 steps"; and
- "the Jacobian must be tightened by 5.985x to reach 557 steps."

Those statements describe the overcounted adapter, not a limitation of the
certified geometric flow. v0.9.20 independently recovers step 557 as strictly
inside the domain and step 558 as the first non-strict step, in agreement with
v0.9.12. The v0.9.18-19 scripts remain only as an auditable correction history.
They must not be cited as current capability bounds.

See [SUPERSEDED_RESULTS.md](SUPERSEDED_RESULTS.md) for the correction record.

## What is not yet proved

The repository does not currently certify:

- a third tangent/normal frame;
- a third local fibre graph or Picard microstep;
- a sharp Taylor/Lohner stepwise flowpipe;
- complete traversal of child 15;
- a successor atlas chart after terminal chart 9;
- complete ten-chart continuation;
- connectivity of arbitrary points in a response fibre; or
- a global geometric flow.

This package is a formal-development milestone, not a global-flow theorem.
The precise wording boundary is recorded in
[docs/CLAIM_SCOPE.md](docs/CLAIM_SCOPE.md) and
[docs/PAPER_WORDING.md](docs/PAPER_WORDING.md).

## Quick start

### Requirements

- Python 3.12 recommended
- `python-flint==0.8.0` for the frozen formal backend

Install the repository requirements:

```bash
python -m pip install -r requirements.txt
```

### One-click reproduction

The latest drivers are single-file scripts and safely ignore the Jupyter or
Colab kernel argument `-f`.

Run the principal certified chain:

```bash
python response_fibre_second_chart_v0_9_10_oneclick.py
python response_fibre_cauchy_norm_correction_v0_9_20_oneclick.py
python response_fibre_signed_field_export_v0_9_22_oneclick.py
python response_fibre_third_recenter_inclusion_v0_9_23_oneclick.py
```

Run the frozen v0.9.3 local ODE theorem directly:

```bash
python src/response_fibre_intrinsic_picard_microstep_v0_9_3.py \
  --inputs-zip inputs/response_fibre_v0_6_2_backend_inputs.zip \
  --v074-source src/response_fibre_arb_kkt_witness_alignment_v0_7_4.py \
  --no-download \
  --output results/v0_9_3_reproduction
```

Verify repository structure and frozen hashes:

```bash
python tools/verify_release.py
sha256sum -c SHA256SUMS.txt
```

For browser-based reproduction, use the
[joint Colab notebook](notebooks/reproduce_joint_v093.ipynb).

## Repository map

```text
src/                         frozen theorem-producing backends
inputs/                      frozen model and atlas inputs
results/                     reference certificates and reports
docs/                        claim scope, paper wording, extensions
notebooks/                   Colab/Jupyter reproduction entry points
tools/                       structural and hash verification
.github/workflows/           CI reproduction and consistency checks
response_fibre_*_oneclick.py continuation milestones v0.9.4-v0.9.23
src/*_v0_9_46*.py            implementation-open backend binding scaffold
frozen/                      hash-bound reference sources for v0.9.46
tests/                       contract checks for open backend scaffolds
```

Useful documents:

- [docs/CLAIM_SCOPE.md](docs/CLAIM_SCOPE.md): exact theorem boundary
- [docs/PAPER_WORDING.md](docs/PAPER_WORDING.md): safe paper language
- [SUPERSEDED_RESULTS.md](SUPERSEDED_RESULTS.md): corrected intermediate results
- [RELEASE_NOTES_v0.9.23.md](RELEASE_NOTES_v0.9.23.md): current milestone notes
- [RELEASE_NOTES_v0.9.46.md](RELEASE_NOTES_v0.9.46.md): backend scaffold notes
- [docs/BACKEND_BINDING.md](docs/BACKEND_BINDING.md): native Arb binding contract
- [CHANGELOG.md](CHANGELOG.md): version history

## Frozen inputs

The continuation chain is bound to the following repository artifacts:

| Artifact | SHA-256 |
| --- | --- |
| v0.9.3 generator | `3be3e07146ff0e505f08bae7bd0ec7f2895955f2540647fea3278fdba51db79c` |
| v0.7.4 Arb backend | `1f71c4918d1cd1d6c45dc0da4a7358e176baac9116c8f71f4a949a6d657520f8` |
| v0.6.2 input ZIP | `2efd863f5ff26da1067594f068bfe265678e6ebac480574ff0574ccc55f98666` |
| corrected canonical atlas | `c02acc1c76e0b670793340150d1a875fdc373e0ac7c46d3360a7824b66a3a5ef` |

Hash pinning detects unexpected input changes and makes later certificates
traceable to a precise source state. It does not, by itself, prove that later
code is mathematically correct; every new theorem step must still pass its own
formal gates.

## Next milestone

The next proof-producing step is to replace the v0.9.46 scaffold placeholders
with repository-native Arb closures that genuinely preserve the input `a_box`
through the complete chain:

- `implicit_fibre_root_solver(a_box)`;
- `pullback_metric(a_box, root_box)`;
- `projected_gradient(a_box, root_box, metric_box)`; and
- analytic normalization inside `formal_vector_field_X(a_box)`.

Only after the executable candidate passes its binding harness, and a separate
certificate audit exists, can the project begin claiming a completed
point/box-field backend. Complete-child traversal still requires repeated
recenter/overlap certificates to reach the child boundary.

## 中文摘要

本仓库研究：在量子控制中，如果多组脉冲参数产生相同的理想响应，能否沿着
“响应保持”的纤维移动，同时严格降低另一个目标函数。

v0.9.3 用 192-bit Arb 区间算术证明了一个六维内蕴 ODE 微步：解存在且唯一，
响应精确保持，并且 \(L_6\) 严格下降。v0.9.23 进一步认证了第二个重定中心局部图、
557 步可达管、六个带符号的向量场分量区间，以及非零六维终点盒；完整终点盒仍在
参数化纤维图的认证域内，因此对盒内每个切向点都继承唯一法向根。

目前仍未证明第三个局部图、完整 child 遍历、十图延拓或全局几何流。因而正确表述是
“局部严格定理与有限延拓里程碑”，不是“全局流已证明”。
