# Computation as Geometric Flow

## Projective-Jet Filtration and Arb-Certified Local Descent

Frozen research-software release **v0.7.4** for the repository
[`papasop/Geometric-Flow`](https://github.com/papasop/Geometric-Flow).

Archived Zenodo record:
[`10.5281/zenodo.21722267`](https://doi.org/10.5281/zenodo.21722267).

**Authors/Creators:** Y. Y. N. Li
([ORCID 0009-0002-6471-139X](https://orcid.org/0009-0002-6471-139X)).

This release audits a 14-phase driven-qubit model with the response constraint

$$
\mathcal R_3(\theta)
=(\Re a_0,\Re a_1,\Re a_2,\Re a_3,
  \Im a_0,\Im a_1,\Im a_2,\Im a_3)
$$

and the sixth-order symmetric-loss coefficient $L_6$.  All theorem-bearing
arithmetic in the audit is outward-rounded Arb arithmetic at 192-bit
precision. A floating midpoint solve is used only as a frozen preconditioner.

## Frozen scientific status

The reference v0.7.4 run reports:

```text
FORMAL_ARB_ORIENTED_DESCENT_CERTIFIED_ALIGNMENT_INCONCLUSIVE
```

Stage A closes on all 16 exact child boxes covering one complete serialized
1/64 parent box (chart 9, subdivision 32). It certifies, for this local box:

- full row rank of the response Jacobian;
- certified response near-tangency within the reported outward-rounded bound;
- nonstationarity of the projected $L_6$ gradient;
- a negative oriented projected-gradient pairing; and
- a uniform strict bound $dL_6/ds<0$ in the local Chebyshev coordinate $s$.

The frozen reference summary gives:

| quantity | certified/report value |
| --- | ---: |
| maximum right-inverse defect upper bound | `0.1299344388400178` |
| minimum projected-gradient norm lower bound | `0.6530784748107296` |
| maximum response-tangency norm upper bound | `2.3071147819354663e-09` |
| maximum $dL_6/ds$ upper bound | `-0.6530784697700559` |

The KKT-witness alignment gate does **not** close at its predeclared threshold:
the maximum relative residual upper bound is `0.008935710125297152`, versus a
gate of `2e-4`. Therefore `all_gates_pass` is false.

## What this release does not claim

- no validated ODE existence or uniqueness theorem;
- no complete ten-chart projected-gradient flow theorem;
- no formal exact gradient-alignment certificate;
- no global six-dimensional fibre, holonomy, cloud, or QPU theorem;
- no neural-network claim.

The correct description is **formal local strict descent near a regular
projective-response level on one complete local parameter box**, not “the full
geometric flow has been proved.” See
[`docs/CLAIM_SCOPE.md`](docs/CLAIM_SCOPE.md) and
[`docs/PAPER_WORDING.md`](docs/PAPER_WORDING.md).

## Research direction: neural-network response fibres

The response-level viewpoint suggests a possible extension beyond quantum
control. For a parameterized model, let $R_{\mathrm{train}}(\theta)$ represent
a declared collection of training responses, such as logits, predictions, or
input jets. When

$$
\operatorname{rank}DR_{\mathrm{train}}(\theta)=\dim R_{\mathrm{train}},
$$

the matched-response set is locally a smooth fibre near regular points:

$$
\mathcal F_r=R_{\mathrm{train}}^{-1}(r).
$$

Let $G(\theta)$ be a separate robustness or generalization objective. One may
then study constrained descent of the form

$$
\dot{\theta}
=-P_{\ker DR_{\mathrm{train}}(\theta)}^{\,g}\nabla_g G(\theta).
$$

The descended quantity here is the independent objective $G$, not the training
loss itself. If $L$ is the training loss and the motion is restricted to a loss
level set, then

$$
L|_{L^{-1}(c)}=c
\quad\Longrightarrow\quad
\nabla_{L^{-1}(c)}L=0,
$$

so the intrinsic descent problem for $L$ on its own level set is degenerate.
The response-fibre question is instead whether one can preserve a declared
training response while descending a distinct objective.

This separates motion that preserves the declared training response from
motion that changes it. It also raises the question of whether different
jet-matching orders define distinct notions of model equivalence.

This is a research direction, not a result of the present release. The
projective-jet no-go theorem, the Arb certificate, and the local descent
result have not been transferred to neural networks or to the NTK regime.
There is also no scalable Arb-certification method here for high-dimensional
neural networks.

## Repository layout

```text
src/
  response_fibre_arb_kkt_witness_alignment_v0_7_4.py
inputs/
  response_fibre_v0_6_2_backend_inputs.zip
results/reference_run_summary.json
results/reference/
  protocol.json
  certificate.json
  report.json
docs/CLAIM_SCOPE.md
docs/PAPER_WORDING.md
tools/verify_release.py
```

The input archive contains the hash-bound corrected Chebyshev atlas and its
supporting v0.5.2/v0.6.1 artifacts. It is included so the frozen audit can be
run without reconstructing earlier notebook state.

## Install

Python 3.12 is recommended.

```bash
python -m pip install -r requirements.txt
```

## Reproduce the frozen local audit

```bash
python src/response_fibre_arb_kkt_witness_alignment_v0_7_4.py \
  --inputs-zip inputs/response_fibre_v0_6_2_backend_inputs.zip \
  --chart 9 \
  --subdivision 32 \
  --output results/v0_7_4_run
```

Expected high-level result:

```text
stage_a_rank_descent_cover_certified = true
kkt_witness_alignment_cover_certified = false
validated_ODE_claimed = false
```

The output directory contains `protocol.json`, `certificate.json`, and
`report.json`. The committed `results/reference/` directory stores the frozen
reference machine output used to derive `results/reference_run_summary.json`;
elapsed time is intentionally excluded from reproducibility expectations.

## Verify the release package

```bash
python tools/verify_release.py
sha256sum -c SHA256SUMS.txt
```

GitHub Actions performs structural and hash verification. It does not rerun
the full 192-bit sixteen-subbox Arb audit.

## 中文说明

本版本冻结在 v0.7.4。可用于论文的结论是：在一个完整的局部 1/64 参数盒
上，响应秩、响应近切向性、投影梯度非驻点性及局部 Chebyshev 坐标
$dL_6/ds<0$ 的统一界已由 Arb 区间算术认证。KKT 对齐门未通过，因此不能称为
“完整几何流定理”或“已验证 ODE”。

神经网络“响应纤维”只作为未来研究方向：只有在
$\operatorname{rank}DR_{\mathrm{train}}=\dim R_{\mathrm{train}}$ 的正则点，
匹配响应集合才局部构成光滑纤维；下降对象应是独立目标 $G$，不是训练损失在
自身等值集上的退化下降。本版本没有把 projective-jet no-go theorem、Arb
证书或局部下降结果推广到神经网络、NTK 区域，也没有给出高维神经网络的可扩展
Arb 认证方法。

## Citation and license

Use [`CITATION.cff`](CITATION.cff) and cite the exact GitHub release or commit.
The code is released under the MIT License.
