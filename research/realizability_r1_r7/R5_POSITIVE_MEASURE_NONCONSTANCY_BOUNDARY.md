# R5-B5 Positive-Measure Nonconstancy Boundary

R5-B5 is a subordinate Geometric-Flow R5 engineering stage. It may use the
R5-B4 C1 implicit branch certificate, but it does not certify full-path zero
response cost, PR-R5, PR-R6, GF-R5, R6 search, normal K=1 residual recovery, or
any global ODE flow.

The only allowed nonconstancy design is the one frozen in
`r5_full_tube_protocol_v1_0.json`:

```text
a_epsilon(s)=epsilon*sin(2*pi*s)*v
I=[0,1/12]
a_dot(s)=epsilon*2*pi*cos(2*pi*s)*v
```

The future/non-theorem choices are not adjustable here. B5 must use the frozen
epsilon sequence, the frozen direction `v=(1,0,0,0,0,0)`, the frozen `T/N`
frames, and the B4 implicit derivative enclosure for the same full-tube
branch.

The certified physical velocity is

```text
dtheta/ds = (T*v + N*b'(t)) * epsilon*2*pi*cos(2*pi*s),
```

where `t=epsilon*sin(2*pi*s)` and `b'(t)` is the B4 physical normal derivative.
B5 proves nonconstancy only through a positive-measure interval and a strict
environment-coordinate speed lower bound. It must not use endpoint comparison,
sampling, binary64 differences, or a newly invented observable.

Allowed status values are:

```text
R5_POSITIVE_MEASURE_NONCONSTANCY_CERTIFIED
R5_POSITIVE_MEASURE_NONCONSTANCY_NOT_CERTIFIED
R5_POSITIVE_MEASURE_NONCONSTANCY_INCONCLUSIVE
R5_B5_INPUT_BOUNDARY_MISMATCH
R5_B5_IMPLEMENTATION_ERROR
```

Even if B5 passes, B6 is still required before any full GF-R5 or zero-cost
shrinking-family certificate can be considered.
