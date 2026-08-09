# Wiener Feedback Scope

The W layer is a future Wiener-type observation, memory, and delayed-feedback
research line. This document defines its boundary before evidence is imported.
It does not archive Pulser results or add a scientific claim.

## Scope

W-layer work may involve:

- noisy observations;
- state estimation;
- finite memory;
- delay;
- drift;
- saturation;
- feedback updates based on historical observations.

## C Layer Versus W Layer

The C layer is geometric feedback recovery:

```text
theta_dot = tangent_descent + normal_response_recovery
```

The W layer adds observation, estimation, memory, and delay state:

```text
xhat_{n+1} = estimator(xhat_n, y_n, u_n)
u_{n+1}    = controller(xhat_{n+1}, memory_n)
```

C4 is a geometric feedback-recovery track. It becomes Wiener-type only after
observation, estimation, memory, or delay state is part of the archived
protocol and claim boundary.

## Non-Claims

- This repository does not claim to solve or complete Wiener's historical
  cybernetics programme.
- Pulser emulator runs are not QPU evidence.
- Finite-shot simulation is not a hardware experiment.
- A structure with `K_rec != 1` is currently only a candidate modelled bias,
  not a new physical law.
- A reproducible memory benefit, if archived later, would not by itself prove
  a unique universal delay, process time, K=1, or global geometric flow.

## Future Intake Standard

Future W-layer experiments belong under
`research/control_extension/wiener_feedback/` and must include executable
scripts, predeclared protocols, JSON reports, manifests, random seeds,
software versions, an evidence class, a claim boundary, negative controls, and
failure status.
