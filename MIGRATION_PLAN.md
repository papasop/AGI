# Migration plan for `papasop/Geometric-Flow`

## Recommendation

Replace the current main-branch working tree with the quantum response-fibre
project in this package.  Preserve the current neural-network/LoRA repository
state in Git history and in an explicit legacy tag or branch.

The neural-network material should not remain mixed into the new README or
active source tree.  It is a different scientific object:

- old repository: quotient-aware PyTorch/LoRA optimization;
- new repository: a projected-gradient flow on a quantum response fibre.

Keeping both in one active tree makes the repository title ambiguous, weakens
the paper-to-code chain, and makes the claim scope difficult to audit.

## Safe preservation step

Before deleting anything from `main`, preserve the current tip:

```bash
git switch main
git pull --ff-only
git tag -a legacy-neural-geoflow-2026-07-31 \
  -m "Last PyTorch/LoRA Geometric-Flow snapshot before quantum-flow reorganization"
git branch legacy/neural-geoflow
git push origin legacy/neural-geoflow
git push origin legacy-neural-geoflow-2026-07-31
```

An even cleaner long-term option is to create a separate repository named
`geoflow-pytorch-legacy` from that tag.  This is optional; the tag and branch
already preserve the work.

## Remove from the active `main` tree

After the preservation step, remove or replace the following old active
content:

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

Also replace `.github/workflows/tests.yml`; its PyTorch tests no longer match
the new repository.

This is a working-tree deletion only.  The old files remain recoverable from
the legacy tag, legacy branch, and Git history.

## Install the replacement tree

Copy the contents of this ZIP into the repository root, not the enclosing ZIP
directory.  Then add a minimal workflow that runs:

```bash
python -m compileall -q scripts tools
python tools/verify_release.py
```

The heavy 80/160-step calculations should remain manual or scheduled because
they take several minutes and require the frozen parameterization input.

## Commit sequence

Use two commits so reviewers can distinguish archival cleanup from the new
science:

1. `Archive legacy PyTorch/LoRA GeoFlow implementation`
2. `Reorganize repository around quantum response-fibre geometric flow`

Do not squash these two commits if historical clarity matters.

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

