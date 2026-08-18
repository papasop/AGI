# R5-B3 Adjacent-Leaf Gluing Boundary

R5-B3 tests the 15 internal seams of the 16-leaf frozen R5 tube. It is a
common-root and C0-gluing check only. It does not certify C1 gluing, full-path
response identity, full-path absolute continuity, zero response cost,
positive-measure nonconstancy, PR-R5, PR-R6, GF-R5, R6 search, normal K=1
residual recovery, or global ODE flow.

The seam list is mechanically derived from the B2 leaf list:

```text
seam i = right(I_i) = left(I_{i+1}), i=0,...,14
```

No periodic `15 -> 0` seam is included because the frozen protocol does not
predeclare a periodic closure check.

Each leaf predictor is first restored to the physical normal coordinate

```text
b_i(t) = b_C,i + S*(t-a_C,i) + eta_i,
||eta_i||_inf <= 1e-23.
```

The comparison object is the physical normal coordinate `b`, not the local
`eta` coordinate. For every seam, the left and right physical endpoint boxes are
intersected. Box overlap alone is not a success criterion. A seam can pass only
if the common endpoint equation

```text
G_i(b) = B*(R3(theta_0 + T*(s_i*v) + N*b) - c) = 0
```

has a strict Krawczyk self-map and a unique root in the intersection box, and if
that common root attaches to both B2-certified endpoint tubes.

Allowed record statuses are:

```text
R5_ADJACENT_LEAF_C0_GLUING_CERTIFIED
R5_ADJACENT_LEAF_C0_GLUING_NOT_CERTIFIED
R5_ADJACENT_LEAF_C0_GLUING_INCONCLUSIVE
R5_B3_INPUT_BOUNDARY_MISMATCH
R5_B3_IMPLEMENTATION_ERROR
```

Allowed seam statuses are:

```text
SEAM_CERTIFIED
SEAM_BOX_INTERSECTION_EMPTY
SEAM_INTERSECTION_NOT_STRICT
SEAM_EQUATION_MISMATCH
SEAM_COMMON_SELF_MAP_FAILED
SEAM_COMMON_UNIQUENESS_FAILED
SEAM_LEFT_ATTACHMENT_FAILED
SEAM_RIGHT_ATTACHMENT_FAILED
SEAM_COORDINATE_TRANSFORM_FAILED
SEAM_INCONCLUSIVE
SEAM_IMPLEMENTATION_ERROR
```

If all 15 internal seams pass, B3 may conclude that the 16 local root branches
form one single-valued C0 implicit root branch over the full interval. If any
seam fails, B3 must remain fail-closed and must not extrapolate from the passing
seams.
