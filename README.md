# Computation as Geometric Flow

## Projective-Jet Filtration and Arb-Certified Local Descent

This repository accompanies the artifact-hardened **v0.7.4-r1** release.
The scientific model and claim scope are unchanged from v0.7.4; r1 adds
the complete reference certificate and stronger fail-closed verification.

> **Scientific status**
>
> Arb certifies local strict descent on one complete parameter box.
> Response rank, near-tangency, projected-gradient nonstationarity, and
> $dL_6/ds<0$ are certified.
>
> The KKT alignment gate remains open. This is **not** a validated
> projected-gradient ODE or a global geometric-flow theorem.

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

and the sixth-order symmetric-loss coefficient $L_6$. All theorem-bearing
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

| Gate | Bound | Threshold | Status |
| --- | ---: | ---: | --- |
| Right-inverse defect | `0.1299344388400178` | `< 0.8` | PASS |
| Projected-gradient norm | `0.6530784748107296` | `> 0.6` | PASS |
| Response tangency | `2.3071147819354663e-09` | `< 1e-6` | PASS |
| $dL_6/ds$ | `-0.6530784697700559` | `< -0.55` | PASS |
| KKT relative residual | `0.008935710125297152` | `< 2e-4` | OPEN |

The KKT-witness alignment gate does **not** close at its predeclared threshold,
so `all_gates_pass` is false.

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
docs/NEURAL_NETWORK_RESPONSE_FIBRES.md
docs/PAPER_WORDING.md
tools/verify_release.py
```

The input archive contains the hash-bound corrected Chebyshev atlas and its
supporting v0.5.2/v0.6.1 artifacts. It is included so the frozen audit can be
run without reconstructing earlier notebook state.

## Frozen artifact identifiers

| Artifact | SHA-256 |
| --- | --- |
| Source | `1f71c491...` |
| Backend inputs | `2efd863f...` |
| Corrected atlas | `c02acc1c...` |
| Protocol | `d935fb83...` |
| Reference certificate | `ed302725...` |

The complete file-level release manifest is [`SHA256SUMS.txt`](SHA256SUMS.txt).

## Install

Python 3.12 is recommended.

```bash
python -m pip install -r requirements.txt
```

## Fast structural verification

```bash
python tools/verify_release.py
sha256sum -c SHA256SUMS.txt
```

This verifies the archived source, inputs, reference machine outputs, key
reported bounds, README numerics, and complete file-level manifest.

## Full 192-bit Arb reproduction

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

GitHub Actions performs fast structural and hash verification by default. It
does not rerun the full 192-bit sixteen-subbox Arb audit.

## Future direction: neural-network response fibres

A possible extension replaces the quantum response map by a declared
training-response map $R_{\mathrm{train}}(\theta)$ and studies descent of an
independent objective $G$ along regular fibres
$R_{\mathrm{train}}^{-1}(r)$.

This is a research direction only. No neural-network, NTK, or scalable
high-dimensional Arb theorem is claimed here. See
[`docs/NEURAL_NETWORK_RESPONSE_FIBRES.md`](docs/NEURAL_NETWORK_RESPONSE_FIBRES.md).

## 中文说明

本仓库对应 artifact-hardened v0.7.4-r1 release。科学模型和声明边界与
v0.7.4 不变；r1 增加完整 reference certificate，并强化 fail-closed
校验。可用于论文的结论是：在一个完整的局部 1/64 参数盒上，响应秩、响应近
切向性、投影梯度非驻点性及局部 Chebyshev 坐标 $dL_6/ds<0$ 的统一界已由
Arb 区间算术认证。KKT 对齐门仍未通过，因此不能称为“完整几何流定理”或
“已验证 ODE”。

神经网络“响应纤维”只作为未来研究方向。本版本没有把 projective-jet no-go
theorem、Arb 证书或局部下降结果推广到神经网络、NTK 区域，也没有给出高维
神经网络的可扩展 Arb 认证方法。

## Citation and license

Use [`CITATION.cff`](CITATION.cff) and cite the exact GitHub release or commit.
The code is released under the MIT License.
