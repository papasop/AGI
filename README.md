# Geometric-Flow — signed endpoint and parametric-root milestone v0.9.23

This development release extends the frozen v0.9.3 local response-fibre ODE
theorem through a second recentered local chart and a certified signed
six-component endpoint enclosure.

## Strongest result

For the frozen chart-9/child-15 instance, the repository-native Arb backend
certifies:

1. a second recentered complex fibre graph and local Picard microstep;
2. a 557-step scalar reachable tube within that second chart;
3. six signed intrinsic-field component intervals;
4. a nonzero six-dimensional endpoint box after 557 microsteps; and
5. inclusion of the complete endpoint box in the certified parametric fibre
   graph, hence a unique normal root for every tangent point in that box.

The endpoint-box centre is approximately

```text
(-2.426e-13, +1.537e-12, +2.212e-12,
 +2.768e-12, +2.694e-12, -2.968e-12).
```

Its maximum absolute coordinate, including component uncertainty, is about
`3.1814e-12`, leaving about `6.8186e-12` of strict margin inside the declared
real intrinsic radius `1e-11`.

## Certified milestones

| Version | Result |
|---|---|
| v0.9.8 | Unique normal correction at the first recenter target |
| v0.9.9 | Recentered tangent/normal frame |
| v0.9.10 | Second complex fibre graph, overlap and Picard microstep |
| v0.9.11–12 | 557-step scalar continuation and exact local-domain exhaustion point |
| v0.9.13 | Route correction: chart 9 is terminal; same-chart recentering is required |
| v0.9.15–17 | Lohner core, hardened adapter contract and executable conservative adapter |
| v0.9.18 | Reproduced 172-step limit under an incorrectly overcounted adapter norm |
| v0.9.19 | Quantified the consequence of that overcount; superseded by v0.9.20 |
| v0.9.20 | Corrected the duplicated dimension factor and restored the 557-step scalar result |
| v0.9.21 | Six-component symmetric endpoint enclosure |
| v0.9.22 | Repository-native signed field and nonzero 557-step endpoint box |
| v0.9.23 | Complete endpoint-box inclusion and inherited unique parametric normal root |

## Important correction to v0.9.18–19

The frozen v0.9.3 source defines

```text
cauchy_lipschitz_upper = d*M/(R-r)
```

as the **induced infinity-norm** Lipschitz bound. v0.9.17 placed this already
induced bound into every entry of a `6x6` Jacobian box, and v0.9.18 then took
the matrix infinity norm, multiplying by six a second time.

Therefore these two earlier capability statements are withdrawn:

- “the formal continuation is limited to 172 steps”; and
- “the Jacobian must be tightened by 5.985x to reach 557 steps.”

They describe the overcounted adapter, not the certified geometric flow.
v0.9.20 independently recovers step 557 as strictly inside the domain and
step 558 as the first non-strict step, agreeing with v0.9.12.

The v0.9.18–19 scripts remain in this archive as an auditable correction
history. They must not be cited as current capability bounds.

## What is not certified

- a third tangent/normal frame;
- a third local fibre graph or Picard microstep;
- a Taylor/Lohner stepwise flowpipe;
- complete traversal of child 15;
- a successor atlas chart after terminal chart 9;
- ten-chart continuation or a global flow;
- connectivity of arbitrary points in a response fibre.

## Reproduction

Python 3.12 and `python-flint==0.8.0` are recommended. The latest scripts are
single-file Colab/Jupyter drivers and ignore the injected kernel `-f` option.

Principal commands:

```bash
python response_fibre_second_chart_v0_9_10_oneclick.py
python response_fibre_cauchy_norm_correction_v0_9_20_oneclick.py
python response_fibre_signed_field_export_v0_9_22_oneclick.py
python response_fibre_third_recenter_inclusion_v0_9_23_oneclick.py
```

Verify this package with:

```bash
sha256sum -c SHA256SUMS.txt
```

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

## Next milestone

Construct and Arb-certify a third tangent/normal frame at the frozen v0.9.23
centre, transform the complete endpoint box into that frame, and then certify
a third local fibre graph and Picard microstep.

This package is a formal-development milestone, not a global-flow theorem.
