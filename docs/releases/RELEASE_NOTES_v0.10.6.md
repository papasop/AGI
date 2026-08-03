# Geometric-Flow v0.10.6 update

This update corrects the v0.10.4-v0.10.5 fourth-chart domain binding and adds
the v0.10.6 ten-step Arb Lohner support-flowpipe milestone.

## Certified chain

| Version | Result |
| --- | --- |
| v0.10.4 | Rebuilds the parametric normal-graph Arb jet on the full v0.9.30 fourth-chart domain with real inner radius `1.5e-11`. |
| v0.10.5 | Rebuilds the repository-native same-expression intrinsic field `X` and `6x6 DX` on that same full domain. |
| v0.10.6 | Certifies ten fourth-chart Arb Lohner support-flowpipe steps and emits complete QR shape history. |

The strongest current result is:

```text
VALIDATED_TEN_STEP_FOURTH_CHART_LOHNER_SUPPORT_FLOWPIPE_CERTIFIED
```

## Reference metrics

```text
steps                         10
time step                     1e-14
total certified time          1e-13
maximum terminal support      1.3938448261845923e-11
real inner domain radius      1.5e-11
complex outer domain radius   2e-11
induced infinity |DX| upper   11510.000045776367
```

Every support tube is certified to remain inside the real `1.5e-11` domain and
the complex `2e-11` domain.

## Correction

The previously merged v0.10.4-v0.10.5 defaults could select a valid but smaller
`1e-11` preflight subdomain. Those earlier certificates remain valid on that
subdomain, but they are not sufficient to justify propagation of the full
fourth-chart initial set. This update prefers the actual v0.9.30 fourth Picard
certificate with inner radius `1.5e-11`.

## Claim boundary

This is a ten-step fourth-chart support-flowpipe certificate plus QR shape
history. It is not a directional QR-tightening result, fifth recenter/frame,
complete-child continuation, atlas-wide continuation, or global-flow theorem.
