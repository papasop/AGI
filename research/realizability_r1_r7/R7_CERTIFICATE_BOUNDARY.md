# R7 Positive-Control Certificate Boundary

This document scopes the R7 positive-control certificate for the prospective
model-level Principle R protocol in this directory.

The current certificate is `certificates/r7_positive_control_v1_1.json`.
It supersedes the PR #53 v1.0 certificate, which used an incomplete centered
enclosure of the declared path. Version v1.1 encloses the full displacement
interval `[0, delta]` with `theta_0[0] + arb(delta/2, delta/2)` and records
endpoint containment for both `theta_0` and `theta_0+delta`.

R7 has one purpose: exclude the trivial possibility that the protocol-relative
response-cost meter is identically zero. It does this only for the frozen
ambient normal control

```text
eta_delta(s)=theta_0+s*delta*n,  s in [0,1],
n=(1,0,...,0) in R^14,
delta in {1e-14,3e-14,1e-13,3e-13,1e-12}.
```

The cost meter is exactly the R3 meter declared by the frozen protocol,

```text
F_Pi(theta,v)=sqrt((D R_3(theta)v)^T W_Pi (D R_3(theta)v)),  W_Pi=I_8.
```

The certificate is prospective research evidence only. It is not an R5 or R6
certificate, not an empirical physical validation, not a physical-time,
energy, or action certificate, not a Lorentzian or general-relativistic claim,
not a hardware claim, and not a global geometric-flow theorem.

The certificate does not modify the published v1.2.13 Geometric-Flow theorem
boundary or any frozen theorem-bearing source, input, result, paper, tag,
Release, or Zenodo asset. The v0.7.4 and v0.9.3 artifacts remain design
references for the response model and do not become new R6 evidence here.

Acceptance is fail-closed:

```text
R7_CERTIFIED
```

is allowed only when every frozen delta passes protocol identity, full-path
endpoint containment, chart residence, nonconstancy, same-meter, strict
positive pointwise response, and strict positive total-cost gates using Arb
interval arithmetic.

If a strict lower bound contains zero, a chart/domain gate fails, or a required
dependency is incomplete, the correct outcome is

```text
R7_INCONCLUSIVE
```

If the frozen protocol identity, declared direction, delta sequence, W_Pi,
input hashes, or baseline commit identity do not match, the correct outcome is

```text
R7_REJECTED_PROTOCOL_MISMATCH
```

No R5 or R6 search, optimization, candidate selection, parameter tuning, or
certificate-producing script may be run by this R7 verifier.
