# Results

The `reference/step_refinement_summary.json` file records the final metrics
reported by the completed 80-step and 160-step runs.

For an archival release, also copy the unmodified generated directories:

```text
results/run_80/
  protocol.json
  reconstructed_curve.json
  report.json
  step_diagnostics.csv
  provenance.json

results/run_160/
  protocol.json
  reconstructed_curve.json
  report.json
  step_diagnostics.csv
  provenance.json
```

Do not synthesize certificates from console output.  Preserve the original
generated files and their hashes.

