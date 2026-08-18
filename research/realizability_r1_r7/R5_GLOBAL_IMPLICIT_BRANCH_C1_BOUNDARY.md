# R5-B4 Global Implicit Branch C1 Boundary

R5-B4 is a subordinate Geometric-Flow R5 engineering stage. It starts from the
R5-B2 all-leaves local root certificate and the R5-B3b adjacent-leaf C0 gluing
certificate. It may certify only the prescribed regularity of the already
glued implicit branch.

The B4 physical equation is

```text
F(t,b)=B*(R3(theta_0+T*(t*v)+N*b)-c)=0.
```

On each frozen leaf, B4 verifies with 192-bit Arb arithmetic that `D_b F`
remains invertible on the B2 certified physical root tube and that the implicit
derivative is enclosed by

```text
b'(t) = -[D_b F(t,b(t))]^{-1} D_t F(t,b(t)).
```

At each internal seam, B4 uses the B3b common physical endpoint root. The left
and right derivative statements are attached to that same common equation and
the same unique physical root; derivative equality is not inferred from overlap
of unrelated coordinate enclosures.

Allowed status values are:

```text
R5_GLOBAL_IMPLICIT_BRANCH_C1_CERTIFIED
R5_GLOBAL_IMPLICIT_BRANCH_C1_NOT_CERTIFIED
R5_GLOBAL_IMPLICIT_BRANCH_C1_INCONCLUSIVE
R5_B4_INPUT_BOUNDARY_MISMATCH
R5_B4_IMPLEMENTATION_ERROR
```

B4 does not certify positive-measure nonconstancy, full-path zero response
cost, PR-R5, PR-R6, GF-R5, R6 search, normal K=1 residual recovery, or any
global ODE flow. If the frozen protocol has not predeclared an independent ODE
field, B4 must not invent one after seeing the implicit derivative.
