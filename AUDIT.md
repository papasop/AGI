# External Audit Guide

This repository now has a single lightweight audit entrypoint:

```bash
python audit/audit_repo.py --strict
```

To save a machine-readable report:

```bash
python audit/audit_repo.py --strict --report audit_report.json
```

## External AI Review Entry Point

Read in this order:

1. `AUDIT.md`
2. `audit/claims_manifest.yaml`
3. `audit/dependency_map.md`
4. the selected protocol
5. the producing script
6. the original certificate

Never infer:

- missing certificates from console logs;
- global validity from a local certificate;
- scientific truth from audit success;
- Arb enclosure from a binary64 computation;
- a current result from a historical milestone.

Required review output:

- repository commit SHA;
- files and hashes inspected;
- claim under review;
- complete dependency chain;
- certified/diagnostic/development/open classification;
- blocking issues;
- unchecked assumptions.

## Current Scientific Line

The strongest published theorem remains local: the v0.7.4 parent-box geometry
and strict-descent certificate plus the v0.9.3 intrinsic local-ODE microstep.
Post-publication C4 artifacts are control-geometry milestones. The C4-E2b
v0.3.5 artifact certifies a zero-time affine-correlated chart 1->2 handoff only.

## Certified, Diagnostic, Development, Open

- Certified: v0.7.4 + v0.9.3 local theorem boundary; C4-E2b v0.3.5 zero-time
  handoff as a post-publication control-geometry certificate.
- Diagnostic: C4-E2b v0.3.2 ladder and v0.3.4.1 controller-covariance report.
- Development: local bridge/recenter candidates and implementation scaffolds.
- Open: positive-time C4-E2b v0.3.6, transition 2->3, eight-chart
  continuation, complete response-fibre coverage, hardware validation, and
  global flow.

## Hashes and Claims

- `SHA256SUMS.txt` verifies repository file integrity.
- `audit/artifact_manifest.json` records artifact ids, paths, hashes, types,
  status, producers, inputs, and scientific scope.
- `audit/claims_manifest.yaml` maps claims to protocols, scripts, inputs,
  certificates, required certificate fields, and boundaries.
- `audit/dependency_map.md` gives a readable dependency summary.

Do not reconstruct a missing certificate from logs or prose. If an artifact is
missing, the audit must fail closed or mark the claim as missing/open. A log
summary is not a certificate.

## Commands That Do Not Rerun Expensive Computation

```bash
python audit/audit_repo.py --strict
sha256sum -c SHA256SUMS.txt
python scripts/verify_reference_results.py
python reproduce/published_paper.py
```

The full scientific reproducers are documented separately in
`docs/REVIEWER_REPRODUCTION.md` and `docs/REPRODUCIBILITY.md`.

## Reporting Audit Issues

When reporting an issue, include:

- the repository commit SHA;
- the audit command and JSON report if available;
- the failing artifact path and expected/actual SHA if relevant;
- whether the issue is a missing file, malformed JSON, claim-path break,
  hard-coded-result concern, or scientific-boundary concern.

Audit warnings are not scientific failures. They are prompts for reviewer
inspection.
