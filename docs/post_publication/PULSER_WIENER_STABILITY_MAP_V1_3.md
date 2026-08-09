# Pulser Shot-Delay Stability Map v1.3

This is a post-publication prospective numerical evidence layer. It does not
modify the published paper, formal Arb/Krawczyk certificates, C4 certificates,
release artifacts, Zenodo records, or historical theorem boundary.

## Scope

The archived v1.3 run is a Wiener-type memory-noise preflight on a
quantum-control response fibre. It uses full-sequence iterative calibration on
Pulser/QutipBackendV2 with finite-shot estimators. Exact emulator probabilities
are retained only as a hidden audit truth channel and are not supplied to the
controller.

## Observed Transcript

The intake archive contains the complete console transcript, not the original
full canonical JSON report. Therefore this repository stores the transcript
and scripts only. The full canonical JSON report remains pending unless the
unmodified script is rerun in a matching numerical environment and reproduces
the frozen protocol SHA and observed summary.

Recorded transcript values:

| Item | Value |
| --- | --- |
| Protocol SHA-256 | `d11a531e3dbeb71941ba0f3de58391f9ef94b860735198774572a4a153d4e79f` |
| Shot-delay cells | 12 |
| Replicates | 48 |
| Exact-probability backend executions | 1,979 |
| Minimum estimated Jacobian singular value | `0.002623344893051062` |
| Positive net-recovery fraction | `0.75` |
| Low-shot memory-benefit seed fraction | `1.0` |
| Observed K range | `[-1.8939193922776065, 2.4447374950368252]` |
| Cross-seed optimal-delay agreement | `agreement_fraction = 0.5` |

The low-shot memory benefit appears in both frozen seeds. The seedwise optimal
delays do not agree, so the result supports reproducible memory benefit but
does not support a single cross-seed optimal delay.

## Boundaries

This evidence layer is not:

- formal Arb or Krawczyk certification;
- C4 validated-flowpipe continuation;
- within-shot feedback;
- K=1 validation;
- process-time evidence;
- QPU or hardware validation;
- a solution of the Wiener programme.

## Required Next Step

The next audit is a train/freeze and held-out causal exponential-memory
estimator comparison against hard delay, followed by a local `K=0` boundary
map.
