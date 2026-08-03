## Summary

This PR records the repository-native Arb backend refactor through v0.10.5.

It lifts the frozen scalar response and L6-gradient formulas to six-variable
complex Arb jets, certifies the parametric normal-graph derivative, and
constructs the intrinsic field `X` and its 6x6 Jacobian `DX` from the same
expression without finite differences.

## Validation

- Frozen source/hash chain checked at every stage.
- `python-flint/Arb` precision: 192 bits.
- Complete certified fourth-chart tangent and normal-graph boxes used.
- `(d_b F) Dpsi + d_a F` contains zero entrywise.
- `DR W` contains zero entrywise.
- Pullback metric inversion and analytic normalization branch certified.
- `X` overlaps the frozen repository-native Picard enclosure.
- The formal `DX` enclosure is finite and 6x6.

## Claim boundary

The strongest certified scope is one fourth-chart field/Jacobian enclosure.
This PR does not claim a QR/Lohner flowpipe, fifth recenter, complete-child
continuation, ten-chart continuation, or global flow.

## Next step

Run the ten-step fourth-chart QR/Lohner propagation as a separate v0.10.6
milestone so either success or fail-closed wrapping diagnostics cannot weaken
the completed v0.10.1-v0.10.5 result.

