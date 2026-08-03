# Changelog

## v0.9.46 — repository-native point-field backend refactor scaffold

- Add an implementation-open candidate module for the repository-native
  point/box Arb field backend.
- Add a strict binding harness that rejects fixed-envelope shortcuts, truthy
  JSON shams, invalid input handling, and candidates that leave
  `NotImplementedError` in place.
- Add contract tests that intentionally require the scaffold candidate to
  remain fail-closed until a real implementation replaces the placeholders.
- Add hash-bound frozen reference sources from the v0.9.30, v0.9.43.3,
  v0.9.44, and v0.9.45 development chain.
- Document the required `a_box -> root -> metric -> projected gradient ->
  normalized field` dependency chain in `docs/BACKEND_BINDING.md`.
- Explicitly exclude any claim of a certified point-dependent field, formal
  Jacobian, QR/Lohner flowpipe, fifth frame, or global flow.

## v0.9.32 — fourth-chart signed endpoint milestone

- Add certified third-centre frame, fibre graph, and Picard continuation.
- Add certified 263-step third-chart finite continuation and signed endpoint.
- Add certified fourth-centre root/frame, fibre graph, and Picard microstep.
- Add certified ten-step fourth-chart continuation and signed endpoint box.
- Preserve the explicit boundary against sharp trajectory-midpoint,
  complete-child, fifth-chart, atlas-wide, and global-flow claims.

## v0.9.23 — signed endpoint and parametric-root inclusion

- Correct the v0.9.18-v0.9.19 duplicated-dimension-factor diagnosis: the
  v0.9.3 `cauchy_lipschitz_upper` quantity was already an induced infinity-norm
  bound.
- Restore the 557-step scalar continuation result under the corrected norm
  interpretation.
- Add a six-component signed intrinsic endpoint enclosure after 557
  microsteps.
- Add repository-native Arb export of the signed intrinsic-field intervals.
- Certify that the complete endpoint box remains inside the parametric
  fibre-graph domain.
- Inherit unique normal-root existence for every tangent point in that endpoint
  box.
- Retain v0.9.18-v0.9.19 only as auditable correction history, not current
  capability bounds.
- Explicitly exclude a third frame, third Picard chart, complete-child
  traversal, atlas-wide continuation, arbitrary-point connectivity, and global
  flow.

## v0.9.18 — validated continuation milestone

- Certify a unique eight-dimensional normal correction at the frozen recenter
  target.
- Certify the recentered full-row-rank response Jacobian and tangent/normal
  frame.
- Add the second complex fibre graph, endpoint inclusion, and one recentered
  Picard microstep.
- Distinguish finite scalar reachability from a narrow identifiable trajectory
  endpoint.
- Harden the six-dimensional Lohner adapter interface against truthy-JSON sham
  adapters.
- Add the executable repository-native conservative formal adapter.
- Quantify the global Cauchy-Jacobian bottleneck: 172 validated steps remain
  inside the declared intrinsic domain, while step 173 exits it.
- Explicitly exclude a 557-step endpoint, complete-child traversal,
  ten-chart continuation, arbitrary-point connectivity, and global-flow
  claims.

## v0.9.3 — validated intrinsic ODE microstep

- Preserve the complete-parent-box v0.7.4 Stage-A descent certificate.
- Add the v0.9.2 centered mean-value Krawczyk construction, eliminating the
  independent response-interval subtraction that dominated earlier attempts.
- Certify a complex six-tangent/eight-normal fibre graph near child 15.
- Enclose $D\psi$, the pulled-back metric $H=W^TW$, and the intrinsic
  normalized projected-gradient field.
- Close a Cauchy/Picard existence and uniqueness proof for one $10^{-14}$
  microstep.
- Certify exact response preservation and
  $dL_6/dt\le-0.6419529191591549<0$ on the validated solution.
- Explicitly exclude complete-child, ten-chart and global-flow claims.

## v0.7.4 — frozen release

- Freeze the theorem-bearing Stage-A local descent audit.
- Certify rank, response tangency, projected-gradient nonstationarity, negative
  oriented pairing, and uniform strict $L_6$ descent in the local Chebyshev
  coordinate on one complete 1/64 parent box covered by 16 exact child boxes.
- Retain the failed KKT-witness alignment gate as a fail-closed result.
- Explicitly exclude validated ODE, complete ten-chart flow, global-fibre, and
  holonomy claims.
- Archive the exact backend-input bundle and its bound corrected-atlas hash.
