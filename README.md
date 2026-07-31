# Certified Local Descent on a Quantum-Control Response Fibre

Frozen research-software release **v0.7.4** for the repository
[`papasop/Geometric-Flow`](https://github.com/papasop/Geometric-Flow).

This release audits a 14-phase driven-qubit model with the response constraint

\[
R_3(\theta)=(\Re a_0,\Im a_0,\ldots,\Re a_3,\Im a_3)
\]

and the sixth-order symmetric-loss coefficient \(L_6\).  All theorem-bearing
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
- response-fibre tangency within the reported outward-rounded bound;
- nonstationarity of the projected \(L_6\) gradient;
- a negative oriented projected-gradient pairing; and
- a uniform strict bound \(dL_6/d\ell<0\).

The frozen reference summary gives:

| quantity | certified/report value |
| --- | ---: |
| maximum right-inverse defect upper bound | `0.12993443903572463` |
| minimum projected-gradient norm lower bound | `0.6530784748107296` |
| maximum response-tangency norm upper bound | `2.3071147819354663e-09` |
| maximum \(dL_6/d\ell\) upper bound | `-0.6530784697700559` |

The KKT-witness alignment gate does **not** close at its predeclared threshold:
the maximum relative residual upper bound is `0.008935710124765316`, versus a
gate of `2e-4`. Therefore `all_gates_pass` is false.

## What this release does not claim

- no validated ODE existence or uniqueness theorem;
- no complete ten-chart projected-gradient flow theorem;
- no formal exact gradient-alignment certificate;
- no global six-dimensional fibre, holonomy, cloud, or QPU theorem;
- no neural-network claim.

The correct description is **formal local strict descent on a serialized
response-fibre box**, not “the full geometric flow has been proved.” See
[`docs/CLAIM_SCOPE.md`](docs/CLAIM_SCOPE.md) and
[`docs/PAPER_WORDING.md`](docs/PAPER_WORDING.md).

## Repository layout

```text
src/
  response_fibre_arb_kkt_witness_alignment_v0_7_4.py
inputs/
  response_fibre_v0_6_2_backend_inputs.zip
results/reference_run_summary.json
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
`report.json`. Compare the report with `results/reference_run_summary.json`;
elapsed time is intentionally excluded from reproducibility expectations.

## Verify the release package

```bash
python tools/verify_release.py
sha256sum -c SHA256SUMS.txt
```

## 中文说明

本版本冻结在 v0.7.4。可用于论文的结论是：在一个完整的局部 1/64 参数盒
上，响应秩、纤维切向性、投影梯度非驻点性及 \(dL_6/d\ell<0\) 的统一界已由
Arb 区间算术认证。KKT 对齐门未通过，因此不能称为“完整几何流定理”或“已验证
ODE”。

## Citation and license

Use [`CITATION.cff`](CITATION.cff) and cite the exact GitHub release or commit.
The code is released under the MIT License.

