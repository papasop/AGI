# v0.9.3 — Validated intrinsic response-fibre ODE microstep

## Release result

The frozen reference run reports
`VALIDATED_INTRINSIC_RESPONSE_FIBRE_ODE_MICROSTEP_CERTIFIED` with every
predeclared gate passing.

For one local microstep of duration $10^{-14}$ near child 15, the certificate
establishes ODE existence and uniqueness, exact preservation of the matched
response, and

$$
\frac{dL_6}{dt}\le-0.6419529191591549<0.
$$

## Reproducibility identifiers

- v0.9.3 source:
  `3be3e07146ff0e505f08bae7bd0ec7f2895955f2540647fea3278fdba51db79c`
- protocol:
  `6d0aaefabd71f1d2986515ed84673f0083ae90d0344b9a1e92d7697ac08d061a`
- corrected atlas:
  `c02acc1c76e0b670793340150d1a875fdc373e0ac7c46d3360a7824b66a3a5ef`
- frozen v0.7.4 backend:
  `1f71c4918d1cd1d6c45dc0da4a7358e176baac9116c8f71f4a949a6d657520f8`

## Boundary

This release validates one microscopic local ODE step. It does not validate a
complete child, the ten-chart atlas, arbitrary endpoint connection, or a
global geometric flow.
