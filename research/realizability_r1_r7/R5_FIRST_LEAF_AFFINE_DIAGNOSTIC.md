# R5-B1c First-Leaf Affine-Correlated Diagnostic

This document defines the boundary for
`diagnostics/r5_first_leaf_affine_diagnostic_v1_0.json`.

The diagnostic studies only the first frozen R5 full-tube leaf. It asks whether
the large R5-B1a whole-leaf forcing enclosure is caused by natural interval
dependency after the normal center is fixed at zero.

The diagnostic representation is

```text
a = a_C + alpha
b = b_C + S alpha + eta
theta(alpha, eta) = theta_C + (T v + N S) alpha + N eta
```

where `a_C` is the first-leaf midpoint, `b_C` and `S` are non-theorem
candidates, and `eta` is a candidate normal remainder. The candidate remainder
radii are fixed before execution:

```text
1e-30, 1e-28, 1e-26, 1e-24, 1e-23, 1e-22, 1e-20
```

The script may use point or binary64 arithmetic to construct candidates, but
all recorded diagnostic enclosures and feasibility inequalities are recomputed
with 192-bit Arb interval arithmetic. Candidate data is not frozen, certified,
or promoted to a theorem.

The diagnostic must not modify `frozen_protocol_v1_0.json`,
`r5_full_tube_protocol_v1_0.json`, `theta_0`, `T`, `N`, `B`, `c`, `P`, `v`,
the first-leaf interval, the frozen `1e-23` normal box, or the published
Geometric-Flow theorem boundary. It must not run other leaves, a full R5 tube,
R6, or normal K=1 residual recovery.

Allowed final classifications are:

```text
AFFINE_CORRELATED_FIRST_LEAF_FEASIBLE
AFFINE_CORRELATED_REMAINDER_TOO_WIDE
CENTER_POINT_SOLVE_INCONCLUSIVE
FIRST_ORDER_CANCELLATION_INSUFFICIENT
IMPLEMENTATION_DEFECT_FOUND
R5_AFFINE_FIRST_LEAF_DIAGNOSIS_INCONCLUSIVE
```

Even the feasible status is only a feasibility diagnostic. It is not an R5
first-leaf certificate, not a full-tube certificate, and not R6 evidence.
