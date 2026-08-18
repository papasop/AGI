# R5-B1e First-Leaf Hessian Krawczyk Boundary

This boundary covers a diagnostic or certificate for leaf index 0 only:

```text
[-1e-12, -8.75e-13]
```

It reuses the frozen R5-A/R5-B0 objects and the B1c candidate affine center and
slope. The only new theorem-facing improvement over B1c is replacement of the
interval-subtracted pure-alpha remainder by the explicit B1d directional
Hessian Lagrange bound.

Allowed status values are:

```text
R5_FIRST_LEAF_HESSIAN_KRAWCZYK_CERTIFIED
R5_FIRST_LEAF_HESSIAN_KRAWCZYK_INCONCLUSIVE
R5_B1E_IMPLEMENTATION_OR_BOUNDARY_FAILURE
R5_B1E_INPUT_BOUNDARY_MISMATCH
```

Even if the first leaf is certified, this is not a full R5 tube certificate, not
an R6 result, and not normal K=1 residual recovery.
