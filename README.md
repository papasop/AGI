# Geometric Flow on Quantum Response Fibres

> **Recovery package:** if the generated input and raw outputs are missing,
> follow [README_RECOVERY.md](README_RECOVERY.md) and run
> `python rebuild_all_artifacts.py`. The driver regenerates the formal v1.3.1
> input plus the 80/160-step result directories, verifies their recorded
> canonical hashes, and creates a GitHub-ready ZIP.

This repository studies a concrete geometric-flow construction in quantum
control.  The control space is a fourteen-phase driven-qubit model, the
constraint is equality of the projective response jet

$$
R_3(\theta)=(\Re a_0,\Im a_0,\ldots,\Re a_3,\Im a_3),
$$

and the potential is the sixth-order symmetric-loss coefficient $L_6$.

The candidate vector field in the declared Euclidean phase metric is

$$
X(\theta)=-
\frac{P_{\ker DR_3(\theta)}\nabla L_6(\theta)}
{\|P_{\ker DR_3(\theta)}\nabla L_6(\theta)\|}.
$$

The present release constructs and tests a response-corrected numerical
trajectory of this field.  It is a floating-point reconstruction, not yet a
validated ODE theorem.

## Current evidence

The frozen response-fibre parameterization has SHA-256

```text
e8ad8a6fbcab626b726082b570f59df6854d4a28259177783e1f5e3274b1cb84
```

The original ten-segment curve passed response preservation, fibre tangency,
and sampled strict $L_6$ descent, but failed the predeclared
gradient-alignment gate.  This motivated reconstruction by directly integrating
the projected-gradient vector field.

| reconstruction | steps | total change in $L_6$ | max response gap | min alignment cosine | status |
| --- | ---: | ---: | ---: | ---: | --- |
| v0.2.2 | 80 | `-0.3457666722306385` | `6.7502e-14` | `0.9999999984107195` | supported |
| v0.2.3 | 160 | `-0.3457666186470760` | `9.7700e-14` | `0.9999999989512591` | supported |

The two total decreases differ by approximately `5.36e-8`, or
`1.55e-7` relative to their magnitude.  Every declared step decreases
$L_6$, and the minimum projected-gradient norm remains above `0.641`.
This is step-refinement evidence for a continuous projected-gradient-flow
candidate.

## What this release establishes

- A response-corrected RK4 trajectory generated from the projected negative
  $L_6$ gradient.
- Response preservation to approximately $10^{-13}$ in the completed runs.
- Strict $L_6$ decrease at every one of 80 and 160 numerical steps.
- Near-unit midpoint alignment with the declared projected-gradient field.
- Stable total $L_6$ decrease under step halving.

## What this release does not establish

- No outward-rounded or interval ODE existence theorem.
- No exact continuous-time gradient-flow claim.
- No uniform certified bound for $dL_6/d\ell<0$ over the full interval.
- No global six-dimensional response-fibre theorem.
- No canonical physical metric, holonomy, PASQAL Cloud, or QPU claim.
- No neural-network or LoRA optimizer claim.

## Repository layout

```text
scripts/
  response_fibre_exact_root_descent_v1_3_1.py
  response_fibre_geometric_flow_preflight_v0_1.py
  response_fibre_projected_gradient_reconstruction_v0_2_2_oneclick.py
  response_fibre_projected_gradient_reconstruction_v0_2_3_steps160_oneclick.py
docs/
  CLAIM_SCOPE.md
  STEP_REFINEMENT.md
  FORMAL_ROADMAP.md
  MIGRATION_RECORD.md
results/reference/
  step_refinement_summary.json
inputs/
  README.md
tools/
  verify_release.py
README_RECOVERY.md
rebuild_all_artifacts.py
requirements.txt
CITATION.cff
LICENSE
```

## Requirements

```bash
python -m pip install -r requirements.txt
```

Python 3.12, NumPy 2.x, and SciPy 1.x are recommended.

## Reproduction paths

There are two supported ways to obtain the required
`global_parameterization.json`.

Fast path: use an existing parameterization whose canonical JSON hash equals
the frozen hash shown above.  This file is produced by the formally certified
local response-curve calculation in the companion
[Projective-Jet repository](https://github.com/papasop/projective-jet-quantum-control).
Place it at:

```text
inputs/global_parameterization.json
```

Complete recovery path: run the in-repository recovery driver.  It regenerates
the v1.3.1 parameterization and the 80/160-step raw outputs, verifies their
recorded canonical hashes, and packages a GitHub-ready release ZIP:

```bash
python rebuild_all_artifacts.py
```

The input is intentionally not inferred from finite-error or $L_6$ outcomes.

## Reproduce

First diagnose the older response-matched curve:

```bash
python scripts/response_fibre_geometric_flow_preflight_v0_1.py \
  --parameterization inputs/global_parameterization.json
```

Run the 80-step reconstruction:

```bash
python scripts/response_fibre_projected_gradient_reconstruction_v0_2_2_oneclick.py \
  --parameterization inputs/global_parameterization.json \
  --output results/run_80
```

Run the 160-step refinement:

```bash
python scripts/response_fibre_projected_gradient_reconstruction_v0_2_3_steps160_oneclick.py \
  --parameterization inputs/global_parameterization.json \
  --output results/run_160
```

Check the release files:

```bash
python tools/verify_release.py
```

## Next theorem-bearing milestone

The next release should replace floating-point reconstruction by a validated
Taylor/Chebyshev ODE atlas and certify, uniformly over the complete parameter
interval,

$$
R_3(\gamma(\ell))=R_3(\gamma(0)),
\qquad
\dot\gamma(\ell)=X(\gamma(\ell)),
$$

and

$$
\frac{dL_6}{d\ell}
=-\|P_{\ker DR_3}\nabla L_6\|<0.
$$

Until that validation closes, this repository should use the phrase
“projected-gradient curve reconstruction supported,” not “geometric-flow
theorem proved.”

Historical PyTorch/LoRA optimizer work is preserved at the
`legacy-geoflow-optim-v0.1` tag.
