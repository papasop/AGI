# Formal certification roadmap

The next high-value step is not a 320-step floating-point run.  It is a
validated ODE atlas.

## Gate A: interval vector field

Construct outward-rounded enclosures for

\[
X(\theta)=-
\frac{P_{\ker DR_3(\theta)}\nabla L_6(\theta)}
{\|P_{\ker DR_3(\theta)}\nabla L_6(\theta)\|}.
\]

Certify a positive lower bound for the projected-gradient norm so the
normalization is well defined.

## Gate B: validated local flow

Fit a Taylor or Chebyshev model on each curve segment and use a radii-polynomial,
Krawczyk, or equivalent validated ODE inclusion to prove that one exact solution
lies in the tube.

## Gate C: response preservation

Either prove invariance directly from

\[
DR_3(\theta)X(\theta)=0
\]

throughout every tube, or propagate a rigorous enclosure for
\(R_3(\gamma(\ell))-R_3(\gamma(0))\).

## Gate D: uniform Lyapunov inequality

Prove on every tube that

\[
\frac{dL_6}{d\ell}
=\nabla L_6^\top X
=-\|P_{\ker DR_3}\nabla L_6\|
\le -c
\]

for one declared \(c>0\), or for segmentwise constants whose minimum is
positive.

## Gate E: overlap and chain closure

Validate all chart overlaps and endpoint handoffs.  Only after all segments
close should the release claim a continuous, certified local geometric flow.

