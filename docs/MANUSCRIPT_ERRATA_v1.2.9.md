# Manuscript v1.2.9 - Clarifications and Errata

This document records textual clarifications to the frozen manuscript
`geometric_flow_v1_2_9_freeze_candidate.pdf`.

The frozen PDF and source archive are preserved unchanged. These
clarifications do not modify any theorem-bearing source, input, protocol,
certificate, JSON record, atlas, numerical enclosure, or gate threshold.
No Arb certificate rerun is required.

## 1. Initial condition in Theorem 1

The certified initial-value problem in Theorem 1 is Eq. (18) with

\[
a(0)=0,
\qquad
\theta(0)=\theta_0=\gamma_9(31/1024).
\]

Thus, "unique solution" means the unique solution of this initial-value
problem inside the certified Picard tube.

The associated Picard operator is

\[
(\mathcal T\phi)(t)
=
\int_0^t X(\phi(\sigma))\,d\sigma,
\]

acting on the closed tube

\[
\{\phi:\|\phi\|_\infty\le r\},
\qquad
r=10^{-11},
\qquad
0\le t\le10^{-14}.
\]

This clarification makes explicit the initial condition already fixed by
the chart construction and used by the frozen verification code.

## 2. Nominal target-state convention

The nominal target ray is generated from the frozen reference phase
vector by evaluating the declared analytic model at zero offset:

\[
|t\rangle
=
\frac{|\psi(0;\theta_{\rm ref})\rangle}
{\|\,|\psi(0;\theta_{\rm ref})\rangle\|}.
\]

The projective response and loss use this normalized target ray and its
declared projective orthogonal complement.

## 3. Complex tangent domain

The declared complex tangent domain used by the parametric Krawczyk
graph verification is the coordinate polydisc

\[
\{a\in\mathbb C^6: |a_i|\le R\},
\qquad
R=2\times10^{-11}.
\]

It contains the real Picard tube of radius

\[
r=10^{-11}.
\]

The frozen verifier uses the same outer radius in the graph enclosure and
the Cauchy estimate.

## 4. Meaning of obligation (R3)

In Theorem 1's namespace, obligation (R3) should be read as:

> the composite normal derivative \(BJN\) is uniformly invertible, and
> the pullback metric \(H=W^{T}W\) is positive definite throughout the
> certified tube.

Here \(H\) is real symmetric positive semidefinite by construction.
The certified Neumann invertibility therefore implies positive
definiteness.

The phrase "whitened response Gram matrix" in the frozen manuscript is
terminological shorthand and does not introduce an additional
certificate quantity.

## 5. Midpoint Stage-A rank certificate

The midpoint rank condition used in Theorem 1 is supported in two
compatible ways:

1. Theorem 2(i) supplies the complete-parent-box certificate.
2. The v0.9.3 verification run independently re-executes the Stage-A
   audit on child 15 and fails closed unless that audit passes.

Accordingly, the local theorem does not rely operationally on a failed
aggregate gate from another certificate namespace.

## 6. Location of the Theorem 2 certificate

The stored certificate used for the broader-domain Theorem 2 constants
is located in the repository at:

`results/reference/certificate.json`

Its identity and checksum are recorded in the repository checksum and
provenance records. It is not contained in the v0.9.3 GitHub Release
payload; the release remains the frozen delivery boundary for the
v0.9.3 local-ODE assets.

## 7. Table 2 aggregation convention

The quantities

- `tangent_projected_gradient_upper`,
- `curve_speed_square_lower`,
- `curve_speed_square_upper`

occur within the per-child `child_box_records`.

The manuscript values are conservative extrema over all sixteen
children. In particular, the displayed curve-speed interval combines
the minimum lower endpoint and maximum upper endpoint over the complete
set of children; its two endpoints need not come from the same child.

## 8. Withdrawal of a legacy parameter note

The v0.7.4 release metadata fields

- `certified_curve_parameter = "local Chebyshev coordinate s"`,
- `legacy_field_name_note` asserting that the certified derivative is
  with respect to \(s\),

are obsolete and should not be used.

The theorem-bearing derivative is with respect to affine atlas
arclength \(\ell\). The conversion is

\[
\frac{d\ell}{ds}=\frac{\ell_+-\ell_-}{2}.
\]

This is confirmed by the frozen source convention and the frozen
curve-speed values. The obsolete metadata does not alter any stored
interval enclosure or theorem-bearing numerical result.

## Scientific boundary

These clarifications are textual and provenance-level only. They do not
change:

- the frozen PDF or source archive;
- the v0.7.4 or v0.9.3 theorem-bearing numerical assets;
- the response map \(R_3\);
- the implementation objective \(L_6\);
- any interval bound or gate threshold;
- the local time interval \(0\le t\le10^{-14}\);
- the statement that global continuation remains open.
