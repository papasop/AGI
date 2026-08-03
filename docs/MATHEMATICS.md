# Mathematical Construction

The frozen model uses fourteen phase coordinates
\(\theta\in\mathbb R^{14}\), an eight-component response constraint

```text
R_3(theta) =
(Re a_0, Re a_1, Re a_2, Re a_3,
 Im a_0, Im a_1, Im a_2, Im a_3),
```

and an independent objective \(L_6\). Locally, the response fibre is written in
six intrinsic tangent coordinates:

```text
theta(a) = theta_0 + T a + N psi(a),    a in R^6.
```

With

```text
W = T + N Dpsi
H = W^T W
```

the normalized projected-gradient field is

```text
dot a = - H^{-1} W^T grad L_6
        / sqrt((W^T grad L_6)^T H^{-1} (W^T grad L_6)).
```

The intended motion preserves the declared response while decreasing \(L_6\).
All theorem-bearing enclosures use outward-rounded Arb interval arithmetic at
192-bit precision. Floating-point SVDs or inverses are used only as frozen
preconditioners, not as proof objects.

## Local Theorem

For the frozen v0.9.3 instance, there exists a unique solution on

```text
0 <= t <= 1e-14
```

of the intrinsic normalized projected-gradient ODE. Along that solution,

```text
R_3(theta(t)) = R_3(theta(0))
dL_6/dt <= -0.6419529191591549 < 0
```

"Exact response preservation" refers specifically to the declared finite
response map \(\mathcal R_3=(a_0,\ldots,a_3)\) within the analytic pulse model.
It does not mean preservation of every higher-order coefficient or hardware
output.
