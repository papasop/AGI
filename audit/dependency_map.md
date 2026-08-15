# Audit Dependency Map

## Read-Only Investigation Snapshot

- Repository URL: `https://github.com/papasop/Geometric-Flow.git`
- Investigation branch: `agent/external-audit-provenance-framework`
- Investigation base commit: `8900fbd4f0ae8532d5446b6ddb0f315bde9027c5`
- Initial working tree: clean in the temporary audit worktree
- Python structure: `src/`, `reproduce/`, `scripts/`, `tools/`, `archive/milestones/`, `research/`, `tests/`
- Existing CI: `.github/workflows/structural-checks.yml`,
  `.github/workflows/reproduce-validated-ode.yml`,
  `.github/workflows/reproduce-joint-geometric-flow.yml`,
  `.github/workflows/control-extension-c4.yml`
- Existing manifests/provenance: `SHA256SUMS.txt`, `SHA256SUMS-c4-e2b.txt`,
  `CONTROL_EXTENSION_SHA256SUMS.txt`, `PULSER_WIENER_SHA256SUMS.txt`,
  `docs/MANUSCRIPT_PROVENANCE.md`, `COLAB_RECOVERY.md`

The initial static scan found historical Colab/recovery absolute paths such as
`/content` and `/tmp` in archived drivers and documentation. These are recorded
as provenance warnings by the audit layer rather than silently accepted as
scientific inputs. The audit tool itself does not use those fallback paths.

## C4-E2b Chain

```text
C4-E2b v0.3.2 ladder checkpoint
  script: archive/milestones/c4_e2b_v0_3_4_1/C4_E2B_TRANSITION_12_ARB_LADDER_v0_3_2.py
  certificate: results/c4_e2b/c4_e2b_transition_12_arb_ladder_v0_3_2.json
  status: diagnostic / inconclusive for transition 1->2 complete endpoint box

    ↓

C4-E2b v0.3.3 local affine bridge candidate
  script: archive/milestones/c4_e2b_v0_3_4_1/C4_E2B_LOCAL_RECENTER_AFFINE_HANDOFF_v0_3_3.py
  certificate: results/c4_e2b/c4_e2b_local_bridge_candidate_v0_3_3.json
  status: development preflight / bridge promotion warranted

    ↓

C4-E2b v0.3.4.1 controller-covariance diagnostic
  script: archive/milestones/c4_e2b_v0_3_4_1/C4_E2B_HANDOFF_CONTROLLER_COVARIANCE_DIAGNOSTIC_v0_3_4_1.py
  certificate: results/c4_e2b/c4_e2b_handoff_controller_covariance_v0_3_4_1.json
  status: diagnostic / interval dependency dominates descent test

    ↓

C4-E2b v0.3.5 affine-correlated zero-time handoff
  script: archive/milestones/c4_e2b_v0_3_5/C4_E2B_AFFINE_CORRELATED_HANDOFF_SUBDIVISION_v0_3_5.py
  certificate: results/c4_e2b/c4_e2b_affine_correlated_handoff_v0_3_5.json
  status: certified zero-time chart 1->2 handoff only

    ↓

Next stage
  status: open
  target: v0.3.6 positive-time chart-2 Picard slab
```

## Hard-Coding Risk Classification

- A: mathematical or algorithmic definition constants, for example dimensions,
  radii appearing as declared local-domain definitions, and literal zero/one
  values in algebraic code.
- B: frozen protocol parameters, for example child index, precision bits,
  subdivision levels, beta, and maximum leaf count declared in protocol fields.
- C: test fixtures, for example expected transcript strings and intentionally
  malformed test manifests.
- D: upstream scientific results stored in certificate JSON files and bound by
  SHA-256.
- E: source literals whose provenance is not evident from nearby code or a
  manifest.

The first pass found no P0 issue requiring scientific-file modification before
adding this audit framework. Existing historical scripts do contain constants
and Colab/recovery path logic; the framework reports these as static audit
warnings so reviewers can inspect them without treating warnings as
certification.
