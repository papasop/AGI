# Wiener Feedback Research Intake

This directory is reserved for future Wiener-type observation, memory, delay,
drift, saturation, and finite-shot feedback experiments.

No experiment is archived here yet. Local or external Pulser v1.0-v1.3 outputs
remain outside the repository evidence ledger until a dedicated intake PR adds
the required artifacts and claim boundary.

## Future Layout

```text
scripts/
protocols/
reports/
manifests/
```

Each experiment must include:

- executable script;
- preregistered protocol;
- JSON report;
- SHA-256 manifest;
- random seeds;
- software versions;
- evidence class;
- claim boundary;
- negative controls;
- failure status.

Failures must not be deleted. In particular, combined-stress feedback failure
or cases with `K_rec < 0` are part of the audit trail, not cleanup material.

See [../../../docs/WIENER_FEEDBACK_SCOPE.md](../../../docs/WIENER_FEEDBACK_SCOPE.md)
and [../../../docs/RESEARCH_STATUS_MATRIX.md](../../../docs/RESEARCH_STATUS_MATRIX.md).
