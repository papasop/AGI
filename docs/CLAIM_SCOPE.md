# Claim scope

## Supported

For the serialized fourteen-phase driven-qubit model and the declared Euclidean
phase metric:

1. the frozen exact response curve supplies the starting response-fibre data;
2. a response-corrected RK4 construction follows the unit-normalized projected
   negative \(L_6\) gradient to floating-point accuracy;
3. the 80-step and 160-step runs pass every predeclared construction gate;
4. every numerical step strictly decreases \(L_6\);
5. step halving changes the total \(L_6\) decrease by about \(5.36\times10^{-8}\).

## Not supported

The current calculations do not certify:

- existence and uniqueness of an exact ODE solution on the full interval;
- exact equality between the numerical derivative and the vector field;
- a uniform outward-rounded negative bound for \(dL_6/d\ell\);
- the complete global response fibre;
- holonomy or geometric memory;
- robustness under model discrepancy;
- PASQAL Cloud or QPU behavior.

## Required wording

Preferred:

> A floating-point, response-corrected projected-gradient reconstruction passes
> the declared 80-step and 160-step audits and is stable under step refinement.

Avoid:

> The geometric flow has been formally proved.

