# External Audit Framework

Run the lightweight repository audit with:

```bash
python audit/audit_repo.py --strict
```

or:

```bash
python -m audit.audit_repo --strict
```

The audit is intentionally read-only. It verifies declared artifact presence,
SHA-256 bindings, certificate fields, claim paths, dependency declarations,
static provenance risks, and fail-closed missing-input behaviour. It does not
run Arb, Picard, Krawczyk, Lohner, or any other expensive scientific
computation.

Repository audit success is not a scientific theorem. It means only that the
declared files, hashes, provenance links, and static audit gates passed. The
field `all_audit_gates_pass` must not be confused with any scientific
certificate field named `all_gates_pass`.

Machine-readable output is available:

```bash
python audit/audit_repo.py --strict --report audit_report.json
```

The report records the audit version, repository commit, dirty status, UTC
timestamp, per-check status, evidence paths, and final audit-gate status.

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
