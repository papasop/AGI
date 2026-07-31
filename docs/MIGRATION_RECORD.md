# Migration record for `papasop/Geometric-Flow`

Migration completed in commit `7f0c40c` on 2026-07-31.

The active `main` branch now contains the quantum response-fibre project.  The
previous PyTorch/LoRA optimizer mainline was preserved in Git history and in
the `legacy-geoflow-optim-v0.1` tag before the replacement commit was pushed.

The neural-network material was removed from the active README and source tree
because it is a different scientific object:

- old repository: quotient-aware PyTorch/LoRA optimization;
- new repository: a projected-gradient flow on a quantum response fibre.

Keeping both in one active tree made the repository title ambiguous, weakened
the paper-to-code chain, and made the claim scope difficult to audit.

## Preservation

The archived optimizer state is available at:

```text
legacy-geoflow-optim-v0.1
```

That tag points to the last public `main` snapshot before the repository
identity changed to quantum response-fibre geometric flow.

## Removed from the active `main` tree

The replacement commit removed or replaced the old active content:

```text
geometric_flow/
experiments/
examples/
notebooks/
tests/
docs/
results/
scripts/
tools/
117path.py
n=2.py
README_H14C3_6.md
几何流.txt
pyproject.toml
README.md
```

It also replaced `.github/workflows/tests.yml`; the PyTorch tests no longer
matched the new repository.

This was a working-tree deletion only.  The old files remain recoverable from
the legacy tag and Git history.

## Installed replacement tree

The replacement tree added the quantum response-fibre package files:

```text
README.md
README_RECOVERY.md
CITATION.cff
LICENSE
docs/
inputs/
results/reference/
scripts/
tools/
rebuild_all_artifacts.py
requirements.txt
.github/workflows/structural-checks.yml
```

The heavy recovery calculation remains manual because it regenerates the
formal v1.3.1 parameterization and the 80/160-step outputs.

## Release naming

Suggested GitHub release:

```text
v0.2.3-quantum-flow-reconstruction
```

Suggested release title:

```text
Projected-gradient reconstruction on a certified quantum response curve
```

Do not call this `v1.0` or a “formal geometric-flow theorem.”  Reserve that
language for the validated ODE/Taylor-model release.
