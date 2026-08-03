# Geometric-Flow v0.9.32

This package advances the frozen chart-9 / child-15 continuation chain from
v0.9.23 through the fourth same-chart local continuation milestone.

## Certified additions

- v0.9.24 freezes and audits the third-frame target.
- v0.9.25 generates the 192-bit Arb third tangent/normal frame certificate.
- v0.9.26 certifies the third complex fibre graph and Picard microstep.
- v0.9.27 certifies 263 finite continuation steps in the third chart.
- v0.9.28 encloses the signed six-component third-chart endpoint.
- v0.9.29 certifies the fourth parametric normal root and frame.
- v0.9.30 certifies the fourth complex fibre graph and Picard microstep.
- v0.9.31 certifies ten finite continuation steps in the fourth chart.
- v0.9.32 encloses the signed six-component fourth-chart endpoint.

The v0.9.32 endpoint box has maximum absolute coordinate
`1.39387284131938755e-11` and is strictly inside the fourth-chart inner radius
`1.5e-11`.

## Claim boundary

This release does not certify a sharp trajectory midpoint, a fifth local
chart, complete traversal of child 15, atlas-wide continuation, or a global
flow. The endpoint-box centre is an enclosure convention.

## Reproduction

Run the new one-click scripts in numerical order. Each driver is standalone
with respect to earlier milestone source: where necessary it materializes the
frozen source chain and checks source hashes before accepting downstream gates.

The package intentionally stops at v0.9.32. Later exploratory v0.9.33+
wrapping/adapter work is not part of this certified update.
