# Process Time Research Interface

This directory is reserved for future candidate process-time work. It contains
no process-time result, certificate, or experiment yet.

## Future Layout

```text
definitions/
protocols/
experiments/
certificates/
```

Future work must distinguish:

- `t_ext`: external integration or laboratory time;
- `tau_rec`: candidate accumulated recovery/process coordinate;
- `tau_phys`: hypothetical physical process time.

Do not call `tau_rec` physical time without coordinate invariance,
reparameterization consistency, and independent protocol equivalence tests.
Do not define time directly as `K_rec`.

See [../../docs/PROCESS_TIME_SCOPE.md](../../docs/PROCESS_TIME_SCOPE.md) and
[../../docs/THEORY_ARCHITECTURE.md](../../docs/THEORY_ARCHITECTURE.md).
