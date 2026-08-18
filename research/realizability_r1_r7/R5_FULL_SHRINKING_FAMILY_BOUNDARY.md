# R5-B6 Full Shrinking-Family Boundary

R5-B6 is a subordinate Geometric-Flow R5 engineering stage. It may combine the
R5-B4 global C1 implicit branch certificate with the R5-B5 positive-measure
nonconstancy certificate to certify the frozen shrinking family inside the
model-level protocol.

The only admitted curve family is the frozen family

```text
a_epsilon(s)=epsilon*sin(2*pi*s)*v
```

with the frozen epsilon sequence and `v=(1,0,0,0,0,0)`. B6 must verify that
each loop is contained in the B4 full-tube interval `[-1e-12,1e-12]`.

The zero response cost conclusion is logical, not residual based:

```text
F(t,b)=B*(R3(theta_0+T*(t*v)+N*b)-c)=0
B is strictly invertible
therefore R3(theta(t))-c=0 exactly
therefore D R3(theta(t))*theta_dot(t)=0
therefore F_Pi(theta(t),theta_dot(t))=0
```

B6 must not replace this argument by a tolerance, a sampled residual, or the
claim that a residual interval merely contains zero.

Allowed status values are:

```text
R5_FULL_SHRINKING_FAMILY_CERTIFIED
R5_FULL_SHRINKING_FAMILY_NOT_CERTIFIED
R5_FULL_SHRINKING_FAMILY_INCONCLUSIVE
R5_B6_INPUT_BOUNDARY_MISMATCH
R5_B6_IMPLEMENTATION_ERROR
```

B6 may certify only the frozen model-level GF-R5 shrinking-family statement. It
does not supply PR-R6, does not run R6, does not perform normal K=1 residual
recovery, does not certify a global ODE flow, and does not modify the published
Geometric-Flow theorem boundary.
