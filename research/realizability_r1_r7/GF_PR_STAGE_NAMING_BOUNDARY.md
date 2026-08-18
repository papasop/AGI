# GF/PR Stage Naming Boundary

This repository uses two separate naming layers.

`PR-R1` through `PR-R7` denote the prospective Principle R interface:
state-space declarations, response protocol, protocol-relative cost, admissible
processes, shrinking-family requirements, future R6 gates, and the R7 positive
control.

`GF-R5`, `R5-A`, `R5-B0`, `R5-B1e`, `R5-B2`, and later `R5-B3`--`R5-B6`
denote Geometric-Flow repository engineering stages for a possible R5 witness.
These stages are evidence-producing or diagnostic substeps. They do not by
themselves modify the published Geometric-Flow theorem boundary.

In particular:

```text
GF-R5 local leaf success != PR-R5 certified.
GF-R5 all-leaf local success != PR-R6 supplied.
R5-B2 success != full R5 tube certificate.
```

R5-B2 checks only whether the same frozen affine-Hessian Krawczyk construction
certifies one local normal root on each of the 16 frozen tube leaves. It does not
certify adjacent-leaf gluing, full-path continuity, exact zero cost on the full
path, positive-measure nonconstancy, R6, a global ODE flow, or normal K=1
residual recovery.
