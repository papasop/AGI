# C4-E2b Colab recovery

## Fresh runtime

```python
!git clone https://github.com/papasop/Geometric-Flow.git /content/Geometric-Flow
%cd /content/Geometric-Flow
!sha256sum -c SHA256SUMS-c4-e2b.txt
!python archive/milestones/c4_e2b_v0_3_5/C4_E2B_AFFINE_CORRELATED_HANDOFF_SUBDIVISION_v0_3_5.py --help
```

The repository now stores the level-32 checkpoint and the v0.3.5
affine-correlated handoff certificate. A fresh runtime should first verify the
stored artifacts instead of rerunning the long ladder.

Run the ladder only if the committed checkpoint is absent or fails provenance
checks:

```python
!python -u reproduce/c4_e2b_resume.py ladder --install --levels 32
```

The `-u` flag makes progress visible immediately.

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

## Verify the stored v0.3.5 certificate

```python
%cd /content/Geometric-Flow
!python archive/milestones/c4_e2b_v0_3_5/C4_E2B_AFFINE_CORRELATED_HANDOFF_SUBDIVISION_v0_3_5.py \
  --parent archive/milestones/c4_e2b_v0_3_4_1/C4_E2B_B_EIGHT_CHART_ARB_FLOWPIPE_v0_3.py \
  --checkpoint results/c4_e2b/c4_e2b_transition_12_arb_ladder_v0_3_2.json \
  --candidate results/c4_e2b/c4_e2b_local_bridge_candidate_v0_3_3.json \
  --diagnostic results/c4_e2b/c4_e2b_handoff_controller_covariance_v0_3_4_1.json \
  --report /tmp/c4_e2b_affine_correlated_handoff_v0_3_5.json
```

This command recomputes the v0.3.5 report from the stored checkpoint,
candidate, and diagnostic inputs. It is not a v0.3.6 positive-time Picard slab
and must not be described as one.

Before ending Colab, download or commit the JSON files under
`results/c4_e2b/`. Those files are the resumable state; the Colab filesystem is
not persistent.

## Claim boundary

This workflow is a fail-closed investigation of one finite transition. It is
not an eight-chart continuation, a fifth-frame theorem, a global flow, K=1,
Pulser, hardware, or QPU claim.
