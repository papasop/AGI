# Normally Attracting Control Extension Scope

This document scopes the post-publication controlled-flow track. It is not part
of `paper-local-ode-v1.4` and does not enlarge the frozen v0.7.4 + v0.9.3
paper theorem.

## Boundary

The controlled field is a candidate extension:

$$
\dot{\theta}
=
-P_\theta\nabla L(\theta)
-\beta J_R(\theta)^\dagger
\bigl(R(\theta)-r_\ast\bigr).
$$

The tangential term follows the frozen local response-fibre descent theorem.
The normal feedback term is intended to repair deviations from a target
response. Current controlled-flow evidence is floating-point development
evidence only unless a future Arb certificate is committed with reviewed
scripts, protocol, and report.

## Evidence Classes

| Item | Status |
| --- | --- |
| v0.7.4 + v0.9.3 local theorem | Frozen/certified |
| v1.1-v1.3.1 controlled-flow tests | Floating-point development evidence |
| Normal attraction tube | Numerical only |
| Nonzero Arb-certified controlled tube | Open |
| Long-time controlled attraction | Open |

## C4 Closure Gate

C4 is the recommended closure milestone for the current control track. A C4
claim must certify all of the following before the control line is treated as
formally closed:

- `rho_certified > 0`;
- uniform full-row-rank margin;
- target-fibre invariance;
- strict inward tube-boundary condition;
- response Lyapunov contraction;
- preservation of objective descent;
- local existence and uniqueness;
- saturation inactive or rigorously enclosed.

## Stop Rules

- Do not call v1.1-v1.3.1 a theorem or PASS unless the corresponding scripts,
  protocol, and report are stored and independently reviewed.
- If C3 numerical boundaries are unstable under solver tolerances, stop and
  repair the numerical setup.
- After C4 is completed, pause the control line and turn to either the K=1
  bridge or a two-metric theorem.
- Do not write control evidence into the frozen paper theorem.

The control law selects dynamics; it does not by itself define geometry,
certificate-DAG soundness, K=1 criticality, matter-like residuals, or constants.
