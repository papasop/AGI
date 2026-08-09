# Pulser Shot-Delay Memory Stability Map

This directory stores prospective numerical emulator evidence. It is not part
of the published-paper theorem, the Arb/Krawczyk certificates, or the C4
controlled-attraction certificate chain.

## v1.3 Evidence Layer

`pulser_shot_delay_stability_map_v1_3.py` maps finite-shot recovery behavior
over a frozen 12-cell shot-delay grid using two frozen seeds and 48 replicate
runs. The run is full-sequence iterative calibration on
Pulser/QutipBackendV2. Exact emulator probabilities are used only as an audit
truth channel and are hidden from the controller.

The archived console transcript reports:

- protocol SHA-256:
  `d11a531e3dbeb71941ba0f3de58391f9ef94b860735198774572a4a153d4e79f`;
- 12 shot-delay grid cells;
- 48 replicate runs;
- low-shot memory benefit in both frozen seeds;
- cross-seed optimal-delay `agreement_fraction = 0.5`;
- observed `K` range `[-1.8939193922776065, 2.4447374950368252]`.

The evidence supports reproducible low-shot memory benefit in the two frozen
seeds. It does not support a single cross-seed optimal delay.

## Archived Artifacts

- `pulser_finite_shot_unit_recovery_law_audit_v1_1.py`: frozen v1.1 base model.
- `pulser_shot_delay_stability_map_v1_3.py`: v1.3 shot-delay stability map.
- `results/post_publication/prospective/pulser_wiener/pulser_shot_delay_stability_map_v1_3_console_transcript.md`:
  complete observed console transcript.

The original full canonical v1.3 report JSON was not present in the intake
archive and is not reconstructed from the transcript. A canonical JSON report
is pending until the unmodified script is rerun in a matching Pulser numerical
environment and the protocol SHA plus summary match the observed transcript.

## Next Step

The next numerical audit should compare hard delay against a train/freeze and
held-out causal exponential-memory estimator, then map the local `K=0`
boundary.
