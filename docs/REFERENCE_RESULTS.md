# Reference Results

This file collects numerical and packaging status that should not crowd the
repository homepage.

## Status Table

| Milestone | Status |
| --- | --- |
| v0.7.4 complete-parent descent | Certified |
| v0.9.3 intrinsic ODE microstep | Certified reference theorem |
| v0.10.5 repository-native \(X\) and same-expression \(DX\) | Certified |
| v0.10.6 ten-step fourth-chart support flowpipe | Latest stored repository reference certificate |
| v0.10.13.1 reindexed Taylor/affine-Lohner terminal set | Source-certified chain; reference-result packaging pending |
| v0.10.15 fifth nonlinear frame transition | Implementation-open fail-closed harness |
| Complete fibre/global flow | Not proved |

## v0.7.4 Numerical Source

The numerical constants printed in the archived manuscript are taken from
`results/reference_run_summary.json`, transcribed from the completed frozen
v0.7.4 reference run. The artifacts under `results/reference/` are local
recomputations and may differ in the final displayed digits because of
environment and outward-rounding details. These differences do not change any
theorem-bearing Boolean gate.

Until a single canonical v0.7.4 artifact package is designated, do not mix
displayed constants from `results/reference_run_summary.json` and
`results/reference/` in the same citation.

## v0.10.6 Reference Certificate

The strongest stored repository reference continuation result is v0.10.6:

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

## Reference Versus Source Certification

`Reference-certified` means the repository stores hash-bound result artifacts
under `results/`.

`Source-certified` means the source records proof-producing code for the
milestone, but the corresponding independent reference-result package is not
yet stored in the repository.
