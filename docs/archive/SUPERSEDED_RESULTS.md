# Superseded intermediate results

## v0.9.18

The reported 172-safe-step/173-failing-step limit is a correct reproduction of
the **overcounted adapter**, but not a capability limit of the certified flow.

## v0.9.19

The reported requirement to reduce the Jacobian bound by approximately
`5.985x` is conditional on the same overcount and is withdrawn.

## Resolution in v0.9.20

`cauchy_lipschitz_upper` was already an induced infinity-norm bound. Removing
the duplicated factor of six recovers:

```text
step 557: 9.9679185906e-12 < 1e-11
step 558: 1.0008559087e-11 > 1e-11
```

This agrees with the earlier v0.9.12 exhaustion calculation.
