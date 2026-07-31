# Claim scope for frozen v0.7.4

## Certified local statement

For the serialized corrected atlas with canonical JSON SHA-256
`c02acc1c76e0b670793340150d1a875fdc373e0ac7c46d3360a7824b66a3a5ef`,
v0.7.4 covers chart 9, subdivision 32 by 16 exact contiguous child boxes.
The reference run reports formal outward-rounded certification of:

1. full response-Jacobian row rank;
2. certified response near-tangency on the complete parent box;
3. nonzero projected $L_6$ gradient;
4. negative oriented projected-gradient pairing; and
5. the uniform inequality in the local Chebyshev coordinate $s$,
   $dL_6/ds\le -0.6530784697700559<0$.

The projected-gradient norm is bounded below by
`0.6530784748107296`, and the response-tangency norm is bounded above by
`2.3071147819354663e-09`.

## Open alignment gate

The frozen KKT-witness residual has certified relative upper bound
`0.008935710125297152`. This is small enough to imply the reported cosine
lower bound `0.9999600757453052`, but it does not meet the predeclared gate
`2e-4`. Consequently:

- `kkt_witness_alignment_cover_certified = false`;
- `formal_single_box_projected_gradient_alignment_certified = false`; and
- `all_gates_pass = false`.

This is a fail-closed outcome, not a numerical failure of descent.

## Explicit exclusions

The release does not establish ODE existence or uniqueness, a transverse
radii-polynomial tube, the complete ten-chart flow, a global response level,
holonomy, or hardware execution. The word “flow” in the repository name is a
research direction; the frozen theorem is local strict descent near a regular
projective-response level on one complete local parameter box.
