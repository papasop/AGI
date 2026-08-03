# Geometric-Flow — validated continuation milestone v0.9.18

This update packages the repository-native formal continuation work built on
the frozen `v0.9.3` intrinsic response-fibre microstep certificate.

## Result in one sentence

The response-fibre flow has been formally continued from the original local
chart into a second recentered local chart, while the present conservative
global-Jacobian adapter is proved to support at most 172 validated Lohner steps
before exhausting the declared intrinsic domain.

## What is certified

| Version | Certified result |
|---|---|
| v0.9.8 | Unique eight-dimensional normal correction at the frozen recenter target |
| v0.9.9 | Full-row-rank response Jacobian and a recentered tangent/normal frame |
| v0.9.10 | Second complex fibre graph, endpoint inclusion and one recentered Picard microstep |
| v0.9.11 | Finite continuation inside the second local chart |
| v0.9.13 | Route correction: chart 9 is terminal; same-chart recentering is required |
| v0.9.14 | Separation of a scalar reachable tube from an identifiable trajectory endpoint |
| v0.9.15 | Six-dimensional Taylor/QR-Lohner core self-test |
| v0.9.16 | Executable-adapter hardening; rejection of truthy-JSON sham adapters |
| v0.9.17 | Executable repository-native conservative formal adapter |
| v0.9.18 | Quantitative global-`DX` bottleneck certificate: 172 safe steps, failure at 173 |

The v0.9.18 conservative propagation gives

```text
maximum_certified_steps = 172
first_failing_step      = 173
r_172                   = 9.8965e-12
r_173                   = 1.0112e-11
formal inner radius     = 1.0000e-11
```

## What is not certified

- a narrow, identifiable endpoint after 557 steps;
- complete traversal of child 15;
- a new atlas chart after chart 9;
- ten-chart continuation;
- a global response-fibre flow;
- connectivity of arbitrary points in a response fibre.

The 557-step result from v0.9.11 is a scalar reachable-tube certificate, not a
validated trajectory centre.  The failure of the conservative v0.9.18 adapter
to reach 557 steps is a limitation of the global Cauchy Jacobian enclosure, not
evidence that the geometric flow terminates.

## Frozen repository inputs

```text
v0.9.3 generator
3be3e07146ff0e505f08bae7bd0ec7f2895955f2540647fea3278fdba51db79c

v0.7.4 Arb backend
1f71c4918d1cd1d6c45dc0da4a7358e176baac9116c8f71f4a949a6d657520f8

v0.6.2 input ZIP
2efd863f5ff26da1067594f068bfe265678e6ebac480574ff0574ccc55f98666

corrected atlas canonical hash
c02acc1c76e0b670793340150d1a875fdc373e0ac7c46d3360a7824b66a3a5ef
```

## Reproduction

Python 3.12 and `python-flint==0.8.0` are recommended.  Each public script is
Colab/Jupyter aware and ignores the injected kernel `-f` argument.

Run the principal milestones in order:

```bash
python response_fibre_arb_normal_root_v0_9_8_oneclick.py
python response_fibre_recentered_frame_v0_9_9_oneclick.py
python response_fibre_second_chart_v0_9_10_oneclick.py
python response_fibre_lohner_stress_v0_9_18_oneclick.py
```

The one-click v0.9.18 script embeds the required preceding drivers, downloads
the frozen repository inputs, verifies their hashes, and fails closed when a
scientific gate is not met.

To verify the archive files:

```bash
sha256sum -c SHA256SUMS.txt
```

## Next formal milestone

Replace the sign-symmetric global bound

```text
|DX_ij| <= 3.4879e11
```

with point- or small-box-dependent Arb Taylor/automatic-differentiation
enclosures.  The target is a validated 557-step centre-radius endpoint narrow
enough to support another same-chart Krawczyk recentering.

## Citation and claim boundary

Until a new paper version is released, cite the frozen v0.9.3 theorem for the
original local existence result and identify this package as a development
milestone.  Do not cite this archive as a global-flow theorem.
