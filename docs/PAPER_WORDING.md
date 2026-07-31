# Paper wording for v0.9.3

## Recommended strongest statement

> On a formally enclosed local response-fibre chart, outward-rounded 192-bit
> Arb arithmetic certifies existence and uniqueness of one intrinsic
> six-dimensional normalized projected-gradient ODE microstep. Along the
> validated solution, the matched response is preserved exactly and
> $dL_6/dt\le-0.6419529191591549<0$. The certified time interval is
> $0\le t\le10^{-14}$; this is a local microstep theorem, not a complete
> child, ten-chart, or global-flow theorem.

## Recommended relationship to v0.7.4

> A separate complete-parent-box certificate establishes strict descent on
> all sixteen child boxes of one serialized 1/64 atlas box, but does not prove
> ODE alignment. The v0.9.3 certificate closes ODE existence and uniqueness on
> a much smaller domain. We report both layers because their coverage and
> theorem content are complementary.

## Recommended artifact sentence

> The exact v0.9.3 source, frozen v0.7.4 backend, hash-bound atlas input,
> protocol, certificate, report, and verification script are archived in the
> associated GitHub release.

## Avoid these claims

- “We validate the complete response-fibre flow.”
- “Any two equivalent implementations are connected by the certified flow.”
- “The ODE is validated on the complete parent box or all ten charts.”
- “A global fibre or holonomy theorem is proved.”
- “The result has already been transferred to neural networks.”

## Suggested status labels

Use `validated intrinsic response-fibre ODE microstep` for v0.9.3 and
`certified complete-parent-box strict descent` for v0.7.4. Do not collapse the
two labels into `validated global geometric flow`.
