# Computation as Geometric Flow

## Arb-certified continuation on a quantum-control response fibre

Geometric-Flow studies a simple but important question:

> If two controls produce the same ideal quantum response, can we move between
> them along a rigorously certified path while improving an independent
> objective?

The repository develops that question for a frozen 14-phase driven-qubit
model. The original v0.9.3 result proves one local intrinsic ODE microstep.
The current v0.10.6 certified development milestone corrects the fourth-chart
domain binding and certifies ten Arb Lohner support-flowpipe steps using the
repository-native fourth-chart field `X` and same-expression Jacobian `DX`.

Current status: strong local and finite-continuation results are certified
for one frozen chart/child instance. A complete-child, atlas-wide, or global
flow theorem is not claimed.

## Latest certified support-flowpipe result: v0.10.6

The v0.10.1-v0.10.6 chain removes the earlier fixed-envelope adapter
bottleneck, constructs the fourth-chart intrinsic field and its Jacobian from
one formally differentiated repository-native Arb expression, corrects the
fourth-chart domain binding, and propagates ten certified Lohner support
flowpipe steps.

The strongest current result is:

```text
VALIDATED_TEN_STEP_FOURTH_CHART_LOHNER_SUPPORT_FLOWPIPE_CERTIFIED
```

The certified v0.10.6 object is a fourth-chart support-flowpipe enclosure:

- v0.10.1 retains the active repository-native Arb backend emitted by the
  frozen v0.9.30 chain;
- v0.10.2 extracts dependency-closed scalar Arb response,
  response-Jacobian, and L6-gradient primitives;
- v0.10.3 lifts those primitives to six-variable complex Arb jets without
  finite differences;
- v0.10.4 certifies the parametric normal-graph derivative
  `Dpsi = -(d_b F)^-1 d_a F` on the complete certified graph box; and
- v0.10.5 constructs `W`, `H`, normalized `X`, and the 6x6 `DX` from the
  same native Jet expression on the full fourth-chart domain; and
- v0.10.6 certifies ten fourth-chart Arb support-flowpipe steps and emits
  complete QR shape history.

Reference metrics:

```text
steps                          10
total certified time           1e-13
maximum terminal support       1.3938448261845923e-11
real inner domain radius       1.5e-11
complex outer domain radius    2e-11
induced infinity |DX| upper    11510.000045776367
```

This milestone certifies support radii and QR shape history. It deliberately
does not certify directional QR tightening, a fifth recenter/frame,
complete-child continuation, atlas-wide continuation, or a global-flow theorem.

## Implementation-open scaffold retained: v0.9.46

The repository also retains the v0.9.46 repository-native point/box Arb field
backend refactor scaffold. Its status is `IMPLEMENTATION_OPEN`.

This scaffold is **not** a certified point-dependent field, formal Jacobian,
QR/Lohner flowpipe, fifth frame, or global-flow theorem. The candidate module
intentionally retains `NotImplementedError` placeholders so that a fixed
envelope cannot be misreported as a point-dependent field.

See [docs/BACKEND_BINDING.md](docs/BACKEND_BINDING.md) and
[RELEASE_NOTES_v0.9.46.md](RELEASE_NOTES_v0.9.46.md).

## Latest certified finite-continuation result: v0.9.32

For the frozen chart-9 / child-15 instance, the repository-native 192-bit Arb
chain now additionally certifies:

- a third recentered tangent/normal frame and complex fibre graph;
- a third-chart Picard microstep and 263-step finite continuation;
- a signed six-component third-chart terminal endpoint box;
- a fourth parametric normal root and tangent/normal frame;
- a fourth complex fibre graph and Picard microstep;
- ten certified fourth-chart continuation steps; and
- a signed six-component fourth-chart terminal endpoint box.

The v0.9.32 endpoint box is strictly contained in the fourth local domain. Its
maximum absolute coordinate is `1.39387284131938755e-11`, compared with the
certified inner-domain radius `1.5e-11`.

This is a finite local-continuation milestone. The endpoint-box centre is an
interval-enclosure convention, not a sharp trajectory midpoint.

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
| v0.9.24-26 | Third-centre proof target, Arb frame, complex graph, and Picard microstep |
| v0.9.27-28 | 263-step third-chart continuation and signed terminal endpoint box |
| v0.9.29-30 | Fourth parametric normal root, frame, complex graph, and Picard microstep |
| v0.9.31-32 | Ten-step fourth-chart continuation and signed terminal endpoint box |
| v0.9.46 | Implementation-open repository-native point/box field backend scaffold, not a certified field |
| v0.10.1-5 | Repository-native Arb field and same-expression 6x6 Jacobian `DX` |
| v0.10.6 | Corrected full fourth-chart domain binding and ten-step Arb Lohner support-flowpipe certificate; no directional QR gain |

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

- a fifth tangent/normal frame or fifth local fibre graph;
- a sharp, stepwise Taylor/Lohner trajectory midpoint or directional
  QR-tightened flowpipe;
- directional QR tightening;
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
python response_fibre_third_frame_backend_v0_9_25_oneclick.py
python response_fibre_third_picard_v0_9_26_oneclick.py
python response_fibre_third_chart_finite_continuation_v0_9_27_oneclick.py
python response_fibre_third_chart_signed_endpoint_v0_9_28_oneclick.py
python response_fibre_fourth_frame_v0_9_29_oneclick.py
python response_fibre_fourth_picard_v0_9_30_oneclick.py
python response_fibre_fourth_chart_finite_v0_9_31_oneclick.py
python response_fibre_fourth_chart_signed_endpoint_v0_9_32_oneclick.py
python src/geometric_flow_active_backend_export_v0_10_1_oneclick.py
python src/geometric_flow_scalar_primitives_extract_v0_10_2_oneclick.py
python src/geometric_flow_six_variable_jet_lift_v0_10_3_oneclick.py
python src/geometric_flow_parametric_normal_graph_jet_v0_10_4_oneclick.py
python src/geometric_flow_same_expression_field_dx_v0_10_5_oneclick.py
python src/geometric_flow_fourth_chart_qr_lohner_v0_10_6_oneclick.py
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
response_fibre_*_oneclick.py continuation milestones v0.9.4-v0.9.32
src/*_v0_9_46*.py            implementation-open backend binding scaffold
src/geometric_flow_*v0_10*.py repository-native Arb X/DX and support-flowpipe milestones
frozen/                      hash-bound reference sources for v0.9.46
results/v0_10_*/             v0.10.1-v0.10.6 reference summaries/certificates
tests/                       contract checks for open backend scaffolds
```

Useful documents:

- [docs/CLAIM_SCOPE.md](docs/CLAIM_SCOPE.md): exact theorem boundary
- [docs/PAPER_WORDING.md](docs/PAPER_WORDING.md): safe paper language
- [SUPERSEDED_RESULTS.md](SUPERSEDED_RESULTS.md): corrected intermediate results
- [RELEASE_NOTES_v0.9.32.md](RELEASE_NOTES_v0.9.32.md): latest certified milestone notes
- [RELEASE_NOTES_v0.9.23.md](RELEASE_NOTES_v0.9.23.md): second-chart milestone notes
- [RELEASE_NOTES_v0.9.46.md](RELEASE_NOTES_v0.9.46.md): backend scaffold notes
- [RELEASE_NOTES_v0.10.5.md](RELEASE_NOTES_v0.10.5.md): repository-native X/DX milestone notes
- [RELEASE_NOTES_v0.10.6.md](RELEASE_NOTES_v0.10.6.md): domain correction and support-flowpipe notes
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
响应精确保持，并且 \(L_6\) 严格下降。v0.9.32 进一步认证了第三和第四个同图
重定中心局部延拓阶段，包括第三图 263 步有限延拓、第四图 10 步有限延拓，
以及第四图带符号六维终点盒。

v0.10.6 修正了 v0.10.4/5 的第四图完整域绑定，并认证了十步 Arb Lohner
support flowpipe；所有支撑管都保持在实 `1.5e-11` 与复 `2e-11` 第四图域内。
v0.9.46 只是后端绑定重构脚手架，候选模块仍保留 fail-closed 的
`NotImplementedError`，不能表述为已认证的点依赖场。目前仍未证明 directional QR
tightening、第五个局部图、完整 child 遍历、十图延拓或全局几何流。因而正确表述是
“局部严格定理与有限延拓里程碑”，不是“全局流已证明”。
