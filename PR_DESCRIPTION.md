## Summary

This PR corrects the v0.10.4–v0.10.5 fourth-chart domain binding and adds the
v0.10.6 ten-step Arb Lohner support-flowpipe milestone.

## What changed

- v0.10.4 and v0.10.5 now prefer the actual v0.9.30 fourth Picard certificate
  with real inner radius `1.5e-11`.
- Full-domain v0.10.4 and v0.10.5 certificates are included.
- v0.10.6 checks the selected domain, rebuilds dependencies on the full domain
  when needed, and propagates ten certified support-flowpipe steps.
- Stepwise QR shape records and local-tail bounds are included.

## Why this correction is needed

The earlier default could select a valid `1e-11` preflight subdomain, while the
fourth-chart initial transformed set has support above `1e-11`. The old local
certificate is not invalid; its scope was simply too small for the later
ten-step propagation. This PR makes the claim/domain relationship explicit.

## Verified outcome

- 10 steps at `h = 1e-14`
- total certified time `1e-13`
- maximum terminal support about `1.39384482482934e-11`
- every support tube lies inside the real `1.5e-11` domain and complex
  `2e-11` domain
- same-expression six-component `X` and `6x6 DX` are bound to the selected
  full-domain certificate

## Claim boundary

No directional QR tightening, fifth recenter/frame, complete-child theorem, or
global-flow theorem is claimed.
