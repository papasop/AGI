# R5-B2 All-Leaves Hessian Krawczyk Boundary

R5-B2 freezes a first-pass all-leaves preflight for the 16 initial leaves in the
subordinate R5 full-tube protocol. The leaf list, order, endpoint rule, centers,
fixed slope, Arb precision, candidate eta radii, formal eta radius, and
Krawczyk gates are declared before running the all-leaf check.

The frozen tube is:

```text
t in [-1e-12, 1e-12]
```

with 16 ordered leaves of width `1.25e-13`. Endpoints are recorded as closed
intervals for interval enclosure; later gluing work must treat adjacency and
branch consistency separately.

For leaf `i`, the center is:

```text
a_C,i = (left_i + right_i)/2
b_C,i = -P F(a_C,i, 0)
```

The fixed affine slope `S` is the B1c/B1e slope and is not refit per leaf. The
directional Hessian remainder is computed for:

```text
w = T*v + N*S
Y2_i <= 1/2 sup ||P*B*D2R3(theta_C,i + w*alpha)[w,w]||_inf * alpha_radius^2
```

The Krawczyk forcing bound is:

```text
Y_total_i = Y0_i + Y1_i + Y2_i + Y_eta_cross_i
```

where eta variation is not interval-subtracted into the forcing term; it is
handled by `Z_i*r_eta` over the full `(alpha, eta)` box.

Allowed scientific statuses:

```text
R5_ALL_LEAVES_HESSIAN_KRAWCZYK_CERTIFIED
R5_ALL_LEAVES_HESSIAN_KRAWCZYK_NOT_CERTIFIED
R5_ALL_LEAVES_HESSIAN_KRAWCZYK_INCONCLUSIVE
R5_B2_INPUT_BOUNDARY_MISMATCH
R5_B2_IMPLEMENTATION_ERROR
```

Even if all 16 leaves pass their local gates, this is not a full R5 certificate,
not PR-R5, not PR-R6, not a global flow result, and not normal K=1 recovery.
