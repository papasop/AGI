# Process Time Scope

The T layer is a candidate process-time research line. It is currently
definition-stage work only. This document creates a boundary for future
experiments and certificates; it does not add a process-time result.

## Time Coordinates

```text
t_ext    external integration or laboratory time
tau_rec  candidate accumulated recovery/process coordinate
tau_phys hypothetical physical process time
```

The current controlled ODE and emulator protocols use `t_ext`. They do not
establish `tau_rec` or `tau_phys`.

## Candidate Definition Drafts

A future protocol may define a candidate accumulated recovery coordinate, for
example:

```text
d tau_rec = kappa_rec(theta, xhat, u, history) dt_ext
```

or:

```text
tau_rec(t) = integral_0^t kappa_rec(s) ds
```

These are definition drafts, not claims.

## Stop Rules

- Without `kappa_rec > 0`, do not call the coordinate a time.
- Without coordinate invariance, do not call it a geometric scalar.
- Without a reparameterization law, do not call it an intrinsic clock.
- Without two independent external protocols producing the same process time,
  do not call it physical time.
- Do not define process time directly as `K_rec`.
- Do not claim a modification of time in relativity, thermodynamics, or
  quantum mechanics.

## Evidence Boundary

T depends conceptually on C, W, and M:

```text
(C, W, M) -> T
```

This is not a proof arrow. W-layer success does not automatically establish T,
and T-layer success does not automatically establish K=1.
