# Geometric-Flow v0.10.5 update

This update records the repository-native Arb refactor from v0.10.1 through
v0.10.5. The milestone removes the earlier fixed-enclosure adapter bottleneck
and constructs the fourth-chart intrinsic field and its Jacobian from one
formally differentiated expression.

## Certified chain

| Version | Result |
| --- | --- |
| v0.10.1 | Retains the active repository-native Arb backend emitted by the frozen v0.9.30 chain. |
| v0.10.2 | Extracts dependency-closed scalar Arb response, response-Jacobian, and L6-gradient primitives. |
| v0.10.3 | Lifts those primitives to six-variable complex Arb jets without finite differences. |
| v0.10.4 | Certifies the parametric normal-graph derivative `Dpsi = -(d_b F)^-1 d_a F` on the complete certified graph box. |
| v0.10.5 | Constructs `W`, `H`, normalized `X`, and the 6x6 `DX` from the same native Jet expression. |

The strongest current result is:

```text
VALIDATED_NATIVE_SAME_EXPRESSION_X_DX_CERTIFIED
```

This is a local fourth-chart field/Jacobian enclosure. It is not a QR/Lohner
flowpipe, fifth recenter, complete-child continuation, ten-chart continuation,
or global-flow theorem.

## Reference metrics

```text
descent square enclosure       [0.4 +/- 0.0340] + [+/- 7.43e-3]j
maximum |X| upper              0.5567255281
maximum |DX| upper             4834.8689
maximum |DR W| residual upper  0.0016352753
```

The complete `DX` enclosure is finite and comes from the same expression as
`X`. On the current wide box, no individual entry is certified to exclude
zero; this is not needed for its use as a formal QR/Lohner Jacobian enclosure.

## Next milestone

v0.10.6 should feed the certified `X, DX` callback into the frozen ten-step
fourth-chart QR/Lohner propagation and test strict complex-domain inclusion.
It is deliberately excluded from this update.
