# Claim scope for frozen v0.9.3

## Theorem A: complete-parent-box strict descent (v0.7.4)

For the corrected atlas with canonical JSON SHA-256
`c02acc1c76e0b670793340150d1a875fdc373e0ac7c46d3360a7824b66a3a5ef`,
v0.7.4 covers chart 9, subdivision 32 by 16 exact child boxes. It certifies
response rank, response tangency, projected-gradient nonstationarity, negative
oriented pairing, and

$$
\frac{dL_6}{ds}\le-0.6530784697700559<0.
$$

Here $s$ is the local Chebyshev coordinate recorded by the v0.7.4 certificate.
Its KKT alignment gate remains open, so this layer is not a validated ODE.

## Theorem B: intrinsic ODE microstep (v0.9.3)

At child 15, v0.9.3 formally constructs a complex parametric fibre graph

$$
\theta(a)=\theta_0+Ta+N\psi(a)
$$

and validates the induced six-dimensional normalized projected-gradient ODE
for $0\le t\le10^{-14}$. The reference certificate establishes:

1. existence and uniqueness inside the declared Picard tube;
2. exact preservation of $R_3$;
3. projected-gradient norm at least `0.6419529191591549`; and
4. the uniform Lyapunov bound
   $$
   \frac{dL_6}{dt}\le-0.6419529191591549<0.
   $$

The Picard contraction factor is `0.00348785915675938`, and the self-mapping
utilization is `0.0005813098594598967`.

## Logical relationship

Theorem A has broader parameter coverage but does not validate an ODE.
Theorem B validates an ODE but only for one microscopic local step. Neither
statement implies the other, and neither may be silently promoted to a
complete-child or global theorem.

## Explicit exclusions

This release does not establish a validated traversal of a complete child,
the complete ten-chart flow, arbitrary endpoint connection, a global response
fibre, holonomy, neural-network transfer, or cloud/QPU execution. The term
“validated ODE” refers only to the exact microstep and domain recorded in the
v0.9.3 certificate.
