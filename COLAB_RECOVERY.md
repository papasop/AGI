# C4-E2b Colab recovery

## Fresh runtime

```python
!git clone https://github.com/papasop/Geometric-Flow.git /content/Geometric-Flow
%cd /content/Geometric-Flow
!python -u reproduce/c4_e2b_resume.py ladder --install --levels 32
```

The `-u` flag makes progress visible immediately. The ladder rerun is required
only when its checkpoint JSON has not been committed or downloaded from the
previous runtime.

## Continue after the level-32 checkpoint exists

```python
%cd /content/Geometric-Flow
!python -u reproduce/c4_e2b_resume.py recenter --level 32
!python -u reproduce/c4_e2b_resume.py diagnose --level 32
```

Or run both downstream stages:

```python
!python -u reproduce/c4_e2b_resume.py continue --level 32
```

Before ending Colab, download or commit the JSON files under
`results/c4_e2b/`. Those files are the resumable state; the Colab filesystem is
not persistent.

## Claim boundary

This workflow is a fail-closed investigation of one finite transition. It is
not an eight-chart continuation, a fifth-frame theorem, a global flow, K=1,
Pulser, hardware, or QPU claim.
