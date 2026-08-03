# Repository-native Arb binding requirements

## Phase construction

For every six-dimensional Arb box `a_box`, construct the same active phase box

```text
theta_box = theta_c + T * a_box + N * b_box
```

where `b_box` is certified by a parametric Krawczyk inclusion for that exact
`a_box`.  A root box copied from the centre calculation is not a new
parametric-root proof.

## Pullback metric

Differentiate the same implicit graph used by the root solver and evaluate the
pullback metric on the complete input box.  Preserve Arb outward rounding and
the certified positive-definiteness/Neumann gate.

## Projected gradient and normalization

Evaluate the response Jacobian and the `L6` gradient at `theta_box`.  Project
onto the certified tangent graph, apply the pullback inverse, and use the same
analytic nonzero normalization branch as the frozen Picard proof.

## Acceptance boundary

Input-dependent outputs establish an executable point/box field callback, but
not a formal Jacobian.  `formal_jacobian_DX` requires differentiation of the
same expression with an Arb matrix enclosure.  Finite differences remain
diagnostic only.

Forbidden shortcuts:

1. Returning frozen `FIELD_MIDPOINTS/FIELD_RADII` for every input.
2. Adding artificial dependence to make displaced outputs differ.
3. Treating domain validation as geometric input dependence.
4. Dividing an induced infinity-norm bound equally among matrix entries.
5. Treating truthy JSON fields as executable proof callbacks.
