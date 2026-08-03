# Claim scope for v0.10.6 plus earlier continuation milestones

## Strongest supported certified claim

The strongest current result is v0.10.6: a ten-step fourth-chart Arb Lohner
support flowpipe backed by the repository-native same-expression fourth-chart
field `X` and 6x6 Jacobian `DX`. All ten support tubes remain strictly inside
the real `1.5e-11` and complex `2e-11` fourth-chart domains.

The v0.10.6 milestone records support radii and QR shape history. It does not
certify directional QR tightening, a fifth recenter/frame, complete-child
continuation, atlas-wide continuation, or a global flow theorem.

## Strongest supported finite-continuation claim

For the frozen chart-9/child-15 instance, the repository certifies finite
same-chart continuation through the fourth recentered local chart. In
particular, v0.9.32 certifies a signed six-component fourth-chart terminal
endpoint box after ten fourth-chart continuation steps. The endpoint box is
strictly inside the declared fourth-chart inner radius.

This is a certified finite local-continuation result. The endpoint-box centre
is an interval-enclosure convention, not a sharp trajectory midpoint.

## Implementation-open scaffold

The v0.9.46 repository-native point/box Arb backend refactor is a fail-closed
binding scaffold only. Its candidate module intentionally retains
`NotImplementedError` placeholders. It must not be described as a certified
point-dependent field, formal Jacobian, QR/Lohner flowpipe, fifth frame, or
global-flow theorem.

## Correction boundary

The v0.9.18 172-step result and v0.9.19 5.985-fold tightening target arose from
applying a second factor of six to a quantity already defined as an induced
infinity norm. These are retained only as correction history and are not
current limits on the flow.

## Prohibited upgrades

This package does not establish directional QR tightening, a fifth frame, fifth
Picard chart, sharp Taylor/Lohner trajectory midpoint, complete-child traversal,
atlas-wide continuation, arbitrary-point connectivity, or global flow.

This package does not establish any global flow.
