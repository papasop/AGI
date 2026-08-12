# Paper Wording

Use three layers when describing the repository.

## Current Manuscript Wording

Use v1.2.12 as the recommended reading version:

> Manuscript v1.2.12 incorporates the recorded v1.2.9 errata and subsequent
> textual clarifications into a self-contained recommended reading version. It
> does not change the mathematical conclusions, theorem-bearing constants,
> frozen certificates, or the v0.7.4 + v0.9.3 theorem boundary. No Arb rerun
> was performed or required. The frozen v1.2.9 assets and their erratum remain
> immutable historical records.

Do not describe v1.2.12 as a new theorem, a certificate rerun, a global-flow
result, or a replacement for theorem-bearing software assets. Cite the
published version as DOI `10.5281/zenodo.21895917`, bound to the immutable
GitHub Release `paper-local-ode-v1.6`.

## Layer I: Unconditional Local Theorem

Recommended strongest statement:

> On a formally enclosed local response-fibre chart, outward-rounded 192-bit
> Arb arithmetic certifies existence and uniqueness of one intrinsic
> six-dimensional normalized projected-gradient ODE microstep. Along the
> validated solution, the declared finite response map \(\mathcal R_3\) is
> preserved exactly and \(dL_6/dt\le-0.6419529191591549<0\). The certified time
> interval is \(0\le t\le10^{-14}\); this is a local microstep theorem, not a
> complete-child, ten-chart, or global-flow theorem.

Use `validated intrinsic response-fibre ODE microstep` for v0.9.3 and
`certified complete-parent-box strict descent` for v0.7.4. Do not collapse the
two labels into `validated global geometric flow`.

When citing the v0.7.4 complete-parent-box descent certificate, state the loss
derivative bound as
`dL6/dell <= -0.6530784697700559`, where `ell` is the affine atlas arclength
coordinate. The serialized Chebyshev coordinate `s` remains a monotone local
chart parameter, so strict ordering in `s` is preserved by the affine map
`ell(s)`.

Long decimal values in the manuscript are outward-safe quotations of the
hash-bound certificate inequalities. When a certificate or script renders a
long value through binary64 formatting, that rendering is a nearest-rounded
display of the stored numerical certificate, not a new mathematical endpoint
or a relaxed proof gate. Prefer the manuscript's outward-safe decimal wording
when writing theorem statements, abstracts, conclusions, and public summaries.

Allowed framing:

> Response invisibility does not imply dynamical irrelevance: a direction
> invisible to the declared finite response may still support strict descent
> of an independent objective.

## Layer II: Frozen-Instance Finite Continuation

Safe wording:

> For the frozen chart-9/child-15 instance, later repository milestones certify
> finite same-chart continuation through the fourth local chart. The latest
> stored reference certificate is v0.10.6: ten fourth-chart Lohner support
> flowpipe steps remain inside the declared real and complex domains.

For v0.10.13.1, use:

> A reindexed Taylor/affine-Lohner source chain certifies the terminal
> correlated set when the required predecessor artifacts are present. Its
> reference-result packaging is pending, so it should not be cited as the
> latest stored repository reference certificate.

## Layer III: Conditional / Next-Frame Work

Safe wording:

> The v0.10.14.1 and v0.10.15 files define the terminal-set transition contract
> and a fail-closed fifth-frame backend harness. They do not certify a fifth
> frame until native Arb callbacks produce a certificate that passes all formal
> gates.

A separate analytic direction is a conditional continuation theorem. It does
not replace the missing fifth-frame certificate for the frozen numerical
instance.

## Reference-Certified Vs Source-Certified

- `Reference-certified` means the repository stores the result artifacts,
  certificate summaries, and hash-bound verification data under `results/`.
- `Source-certified` means the committed source is designed to reproduce the
  certificate when its predecessor artifacts are available, but the resulting
  reference package has not yet been stored and hash-bound in the repository.

v0.10.6 is currently reference-certified. v0.10.13.1 is currently
source-certified with reference-result packaging pending.

## Artifact Sentence

> The exact v0.9.3 source, frozen v0.7.4 backend, hash-bound atlas input,
> protocol, certificate, report, and verification script are archived in the
> associated GitHub release.

## Avoid These Claims

- “We validate the complete response-fibre flow.”
- “Any two equivalent implementations are connected by the certified flow.”
- “The ODE is validated on the complete parent box or all ten charts.”
- “The v0.10.13.1 chain is the latest stored reference certificate.”
- “The v0.10.15 harness certifies a fifth frame.”
- “A global fibre or holonomy theorem is proved.”
- “The result has already been transferred to neural networks.”
- “The response fibre is a gauge orbit.”
- “Gauge redundancy cannot be fixed.”
- “The response fibre is the unique driver of optimization.”
