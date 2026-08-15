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
