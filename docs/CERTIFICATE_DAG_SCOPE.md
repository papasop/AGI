# Certificate Execution DAG Scope

This document scopes the certificate-DAG track. It is a derived execution graph
for finite certification records, not a claim that the continuous response
fibre is itself a DAG.

## Semantics

| Object | Meaning |
| --- | --- |
| Node | A certified local region, chart, box, tube, or stored proof object |
| Edge | A validated transition, inclusion, refinement, or monotone proof step |
| DAG | A finite certificate/execution graph after acyclicity is proved |

Continuous response fibres may contain loops. Orientation alone does not prove
acyclicity. A strictly monotone certified quantity is required before a finite
execution graph can be called a DAG.

## Roadmap

| Stage | Objective | Status |
| --- | --- | --- |
| D0 | Certified regions as nodes | Design |
| D1 | Validated transitions as edges | Partial local ingredients only |
| D2 | Strict monotone certificate quantity | Open |
| D3 | Finite certificate DAG | Open |
| D4 | Continuous-trajectory/discrete-path correspondence | Open |
| D5 | Soundness and relative completeness theorem | Open |

## Stop Rules

- If C3 numerical boundaries are unstable under solver tolerances, stop and
  repair the boundary before recording them as graph edges.
- Do not treat the continuous response fibre as a DAG.
- Do not use directed notation as evidence of acyclicity.
- Do not infer K=1, matter-like residuals, or constants from graph semantics.

The DAG records finite certified execution. It does not replace the continuous
geometry or the controlled dynamics.
